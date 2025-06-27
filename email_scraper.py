# Advanced Email Scraper with Pro Features (with suggestions applied)

import argparse
import hashlib
import json
import csv
import logging
import random
import re
import threading
import time
import urllib.parse
import yaml
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from urllib.robotparser import RobotFileParser
import requests
import signal
import sys

# Optional: use colorama for color output
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLOR = True
except ImportError:
    COLOR = False

# Global shared variables
emails = set()
scraped_urls = set()
visited_hashes = set()
failed_urls = []
lock = threading.Lock()
stopped = False

# User agents list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"
]

# Setup logging
logging.basicConfig(
    filename='email_scraper.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def hash_url(url):
    return hashlib.sha256(url.encode()).hexdigest()

def extract_emails(text, keywords=None):
    found = set(re.findall(r"[a-z0-9\.-+_]+@[a-z0-9\.-+_]+\.[a-z]+", text, re.I))
    if keywords:
        found = {email for email in found if any(k.lower() in email.lower() for k in keywords)}
    return {email.lower().strip() for email in found}

def normalize_url(base_url, link):
    full_url = urllib.parse.urljoin(base_url, link)
    return full_url.split('#')[0].rstrip('/')

def is_allowed(url, rp):
    return rp.can_fetch("*", url)

def get_random_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def graceful_exit(signum, frame):
    global stopped
    print("\n[!] Interrupted by user. Saving progress...")
    stopped = True

signal.signal(signal.SIGINT, graceful_exit)


def crawl_url(url, base_domain, rp, keywords, crawl_delay, dry_run=False, timeout=5):
    local_emails = set()
    local_links = []
    time.sleep(crawl_delay + random.uniform(0.5, 1.5))  # jitter for rate limiting

    if dry_run:
        logging.info(f"[DRY-RUN] {url}")
        return local_emails, local_links

    try:
        if not is_allowed(url, rp):
            logging.warning(f"[BLOCKED by robots.txt] {url}")
            return local_emails, local_links

        headers = get_random_headers()
        response = requests.get(url, headers=headers, timeout=timeout)

        if response.history:
            logging.warning(f"[REDIRECT] {url} → {response.url}")

        try:
            soup = BeautifulSoup(response.text, "lxml")
            title = soup.title.string.strip() if soup.title else ""
        except Exception:
            title = ""
        logging.info(f"[OK] {url} - {response.status_code} - {title}")

        new_emails = extract_emails(response.text, keywords)
        parts = urllib.parse.urlsplit(url)
        base_url = f"{parts.scheme}://{parts.netloc}"

        for anchor in soup.find_all("a"):
            link = anchor.get("href")
            if not link:
                continue
            if link.startswith('mailto:') or link.endswith(('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip')):
                continue
            link = normalize_url(base_url, link)
            if link.startswith("http") and urllib.parse.urlparse(link).netloc.endswith(base_domain):
                local_links.append(link)

        return new_emails, local_links

    except RequestException as e:
        logging.error(f"[FAILED] {url} - {e}")
        failed_urls.append(url)
        return local_emails, local_links

def crawl(start_url, max_urls, output_file, output_format, threads, keywords, dry_run, verbose, scope_only, quiet, timeout):
    urls = deque([start_url])
    base_domain = urllib.parse.urlparse(start_url).netloc

    rp = RobotFileParser()
    rp.set_url(f"https://{base_domain}/robots.txt")
    try:
        rp.read()
        crawl_delay = float(rp.crawl_delay("*")) if rp.crawl_delay("*") else 0
    except:
        crawl_delay = 0
        logging.warning("[robots.txt not available or malformed]")

    count = 0
    try:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            while urls and count < max_urls and not stopped:
                futures = {}
                batch_size = min(len(urls), threads)
                for _ in range(batch_size):
                    url = urls.popleft()
                    h = hash_url(url)
                    with lock:
                        if h in visited_hashes:
                            continue
                        visited_hashes.add(h)
                        scraped_urls.add(url)
                    futures[executor.submit(crawl_url, url, base_domain, rp, keywords, crawl_delay, dry_run, timeout)] = url

                for future in as_completed(futures):
                    if stopped:
                        break
                    url = futures[future]
                    count += 1
                    try:
                        new_emails, new_links = future.result()
                        with lock:
                            for email in new_emails:
                                if email not in emails:
                                    if not quiet:
                                        if verbose and COLOR:
                                            print(Fore.GREEN + f"[+] {email}")
                                        else:
                                            print(f"[+] {email}")
                                    logging.info(f"[EMAIL] {email}")
                            emails.update(new_emails)
                            for link in new_links:
                                if (not scope_only) or link.startswith(start_url):
                                    if hash_url(link) not in visited_hashes:
                                        urls.append(link)

                time.sleep(random.uniform(1, 2))  # pause between crawl waves

    except KeyboardInterrupt:
        print("\n[!] Manual interruption. Exiting...")

    if output_file:
        if not output_file.endswith(f".{output_format}"):
            output_file += f".{output_format}"

        if output_format == 'csv':
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Email'])
                for email in sorted(emails):
                    writer.writerow([email])
        elif output_format == 'json':
            with open(output_file, 'w') as f:
                json.dump(sorted(list(emails)), f, indent=4)
        else:
            with open(output_file, 'w') as f:
                for email in sorted(emails):
                    f.write(email + '\n')
        print(f"[✓] Emails saved to {output_file}")

    if not quiet:
        print("\n[*] Scan Summary:")
        print(f"[*] Pages Crawled: {count}")
        print(f"[*] Emails Found: {len(emails)}")
        print(f"[*] Failed URLs: {len(failed_urls)}")

    logging.info(f"[SUMMARY] Crawled: {count}, Emails: {len(emails)}, Failures: {len(failed_urls)}")

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="Pro Email Scraper")
    parser.add_argument("url", nargs="?", help="Starting URL")
    parser.add_argument("--config", help="YAML config file")
    parser.add_argument("--max", type=int, default=50, help="Max pages to crawl")
    parser.add_argument("--output", help="Output filename")
    parser.add_argument("--format", choices=['txt', 'csv', 'json'], default='txt', help="Output format")
    parser.add_argument("--threads", type=int, default=5)
    parser.add_argument("--keywords", help="Comma-separated keywords (e.g. admin,hr)")
    parser.add_argument("--dry-run", action="store_true", help="Preview URLs without crawling")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--scope-only", action="store_true")
    parser.add_argument("--quiet", action="store_true", help="Suppress output to console")
    parser.add_argument("--timeout", type=int, default=5, help="Request timeout in seconds")

    args = parser.parse_args()

    if args.config:
        cfg = load_config(args.config)
        url = cfg.get("url")
        max_urls = cfg.get("max", 50)
        output = cfg.get("output")
        format_ = cfg.get("format", 'txt')
        threads = cfg.get("threads", 5)
        keywords = cfg.get("keywords")
        if isinstance(keywords, str):
            keywords = keywords.split(',')
        timeout = cfg.get("timeout", 5)
        quiet = cfg.get("quiet", False)
    else:
        url = args.url
        max_urls = args.max
        output = args.output
        format_ = args.format
        threads = args.threads
        keywords = args.keywords.split(',') if args.keywords else None
        timeout = args.timeout
        quiet = args.quiet

    if not url:
        print("[!] URL is required.")
        return

    crawl(url, max_urls, output, format_, threads, keywords, args.dry_run, args.verbose, args.scope_only, quiet, timeout)

if __name__ == "__main__":
    main()
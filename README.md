# 📬 Email Scraper

An ethical command-line tool to extract emails from websites using multithreading, robots.txt compliance, and filtering options.

---

## 🚀 Features

- ✅ Multithreaded crawling
- ✅ Robots.txt with `crawl-delay`
- ✅ Scope restriction and URL deduplication
- ✅ User-Agent rotation and rate limiting
- ✅ Keyword-based email filtering
- ✅ Dry-run preview mode
- ✅ Colorized CLI and verbose logging
- ✅ YAML config support
- ✅ Export results to TXT, CSV, or JSON

---

## 📦 Installation

```bash
# Clone and install locally
git clone https://github.com/Aaftab231/email-scraper.git
cd email-scraper
pip install .
```

---

## ⚙️ Usage

```bash
# Basic usage
email-scraper https://example.com

# With keyword filtering
email-scraper https://example.com -k admin,hr

# Using config file
email-scraper --config config.yaml

# Save output as CSV or JSON
email-scraper https://example.com -o output.csv -f csv
```

---

## 🔧 Arguments

| Flag           | Description                               |
|----------------|-------------------------------------------|
| `url`          | Starting URL to crawl                     |
| `--max`        | Max pages to crawl                        |
| `--output`     | Output filename                           |
| `--format`     | Output format: `txt`, `csv`, or `json`    |
| `--threads`    | Number of threads (default: 5)            |
| `--keywords`   | Comma-separated email filter keywords     |
| `--dry-run`    | Preview crawl plan without making requests|
| `--verbose`    | Show verbose, colorized output            |
| `--scope-only` | Stay within base domain only              |
| `--config`     | Path to YAML config file                  |

---

## 🧪 Example with Config File

```yaml
# config.yaml
url: "https://example.com"
max: 100
output: "results.json"
format: "json"
threads: 10
keywords:
  - admin
  - hr
  - support
```

Run with:
```bash
email-scraper --config config.yaml
```

---

## 📁 Project Structure

```
email-scraper-pro/
├── email_scraper.py         # Main CLI tool
├── setup.py                 # For pip installation
├── requirements.txt         # Dependencies
├── README.md                # Project documentation
├── config.yaml              # Sample configuration
└── .gitignore               # Optional git ignore file
```

---

## 🛠 Development

Install dependencies in a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run locally:
```bash
python email_scraper.py https://example.com -t 5 -m 50
```

---

## 📝 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 💡 Customization

You may customize this tool according to your needs. Feel free to use, modify, or extend it for personal, educational, or professional purposes.

---

## 👨‍💻 Author

**** — Programmer & Python Developer  


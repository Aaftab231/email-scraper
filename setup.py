from setuptools import setup, find_packages

setup(
    name="email-scraper-pro",
    version="1.0.0",
    author="Your Name",
    author_email="you@example.com",
    description="Advanced CLI tool for scraping emails ethically and efficiently",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    py_modules=["email_scraper"],
    install_requires=[
        "requests",
        "beautifulsoup4",
        "lxml",
        "PyYAML",
        "colorama"
    ],
    entry_points={
        'console_scripts': [
            'email-scraper = email_scraper:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
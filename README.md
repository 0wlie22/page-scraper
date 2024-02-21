# SS.com Scraper

## Overview

This project is a web scraper written in Python for extracting information about flats available for rent on SS.com in Riga's center. The script checks for new listings every 10 minutes and notifies the user about flats meeting certain criteria.

## Features

- Web scraping with BeautifulSoup for parsing HTML
- Database storage using TinyDB to avoid duplicate entries
- Notification using HTTP POST requests to ntfy.sh

## Prerequisites

- Python 3.12
- Docker (if running as a Dockerized application)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/sscom-scraper.git
cd sscom-scraper
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Running as a standart script

```bash
python main.py
```

### Running as Dockerized application

```bash
docker build . -t page-scraper

docker run page-scraper

# Or with Kubernetes

kubectl apply -f cronjob.jaml
```

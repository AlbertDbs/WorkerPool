# WorkerPool - Distributed Web Scraping System

**WorkerPool** is a robust, distributed web scraping architecture designed to harvest data from high-security websites.

It utilizes a **Producer-Consumer** pattern with **Redis** as a message broker. The system is engineered to bypass advanced 
anti-bot protections (WAF/Cloudflare) using **Selenium** with **Undetected Chromedriver**, featuring self-healing capabilities and automatic failure recovery.

---

## 🚀 Key Features

* **Distributed Architecture:** Decouples the crawling logic (Master) from the processing logic (Workers), allowing for horizontal scaling.
* **Stealth Mode:** Uses modified `undetected-chromedriver` to mimic human behavior and bypass bot detection mechanisms (Semrush, Social Media, etc.).
* **Self-Healing Workers:** Automatically detects if the browser crashes, freezes, or is manually closed, and restarts the driver without crashing the application.
* **Fault Tolerance:** Implements "Dead Letter" handling. Failed downloads due to network issues are automatically re-queued with a back-off strategy.
* **Real-Time Monitoring:** Includes a CLI Dashboard (`monitor.py`) to track queue size, success rates, and retries in real-time.

---

## 🛠️ Tech Stack

* **Language:** Python 3.9+
* **Message Broker:** Redis
* **Browser Automation:** Selenium, Undetected-Chromedriver
* **Parsing:** BeautifulSoup4
* **Logging:** Structured Logging (Console + File)

---

## 📋 Prerequisites

Before running the system, ensure you have the following installed:

1.  **Python 3.9+**
2.  **Google Chrome** (Must be installed in the default system location).
3.  **Redis Server**

---

## ⚙️ Installation Guide

### 1. Clone the Repository
bash
git clone <your-repo-link>
cd WorkerPool

2. Set up the Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

# MacOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate

3. Install Dependencies
Create a requirements.txt file with the following content (if not present) and install it:
redis==5.0.1
requests==2.31.0
beautifulsoup4==4.12.2
fake-useragent==1.4.0
selenium==4.15.2
undetected-chromedriver==3.5.3
urllib3==1.26.15

Run the install command:
pip install -r requirements.txt

4. Start Redis
You need a running Redis instance. The easiest way is via Docker:
docker run -d -p 6379:6379 --name redis-workerpool redis

⚠️ Configuration Note (Chrome Path)
This project is currently configured for macOS. The scripts master.py and worker.py look for Google Chrome at: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome

If you are on Windows or Linux: Open master.py and worker.py, search for the setup_driver function, and remove or comment out the options.binary_location line.

▶️ Usage Instructions
To see the distributed system in action, open 3 separate terminal windows.

Terminal 1: Run the Monitor
Start the dashboard first to observe the process from the beginning.
python monitor.py

Terminal 2: Run the Master
The Master will scrape the source list (e.g., Top Websites) and populate the Redis queue.
# Example: Scrape top sites for Turkey
python master.py --country turkey
# Example: Scrape top sites for United States
python master.py --country united-states

Terminal 3: Run Workers
Start one or more workers to process the queue. Each worker will open a Chrome window.
python worker.py 1
To simulate parallelism, open another terminal (Terminal 4) and run:
python worker.py 2

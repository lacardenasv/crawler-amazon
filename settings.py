import os

current_dir = os.path.dirname(os.path.realpath(__file__))

# Database
database = "amazon_crawler_db"
host = "127.0.0.1"
user = "crawler_user"
password = "provacrawler123"
port = 4005

# Redis
redis_host = "127.0.0.1"
redis_port = 6379
redis_db = 0

# Request
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
}
allowed_params = ["node", "rh", "page", "language", "url"]

# Proxies
proxies = [
    # your list of proxy IP addresses goes here
    # check out https://proxybonanza.com/?aff_id=629
    # for a quick, easy-to-use proxy service
]
proxy_user = ""
proxy_pass = ""
proxy_port = ""

# Crawling Logic
start_file = os.path.join(current_dir, "start-urls.txt")
max_requests = 2 * 10**6  # two million
max_details_per_listing = 9999

# Threads
max_threads = 50

# Logging & Storage
log_stdout = True
image_dir = "/tmp/crawl_images"
export_dir = "/tmp"

# Selenium
SELENIUM_CHROME_DRIVER_PATH = os.path.join(current_dir, 'selenium/chromedriver')
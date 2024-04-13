import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from tqdm import tqdm

class Crawler:
    def __init__(self, start_url, max_depth=3):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.max_depth = max_depth
        self.visited_urls = set()
        self.headers = {
            'User-Agent': 'InspectionTool/1.0'
        }
        self.found_urls = set()

    def crawl(self):
        try:
            with tqdm(total=100) as pbar:
                self._crawl(self.start_url, depth=0, pbar=pbar)
        except KeyboardInterrupt:
            print("\nCrawling process interrupted by user.")

    def _crawl(self, url, depth, pbar):
        if depth > self.max_depth or url in self.visited_urls:
            return
        try:
            with requests.get(url, headers=self.headers, allow_redirects=True, stream=True) as response:
                if response.status_code == 200:
                    self.visited_urls.add(url)
                    self._extract_links(response.text, url, depth, pbar)
                    self._detect_suspicious_code(response.text, url)
        except Exception as e:
            print(f"Error crawling {url}: {e}")

    def _extract_links(self, html, url, depth, pbar):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http'):
                parsed_url = urlparse(href)
                if parsed_url.netloc == self.domain:
                    new_url = href
                else:
                    continue
            else:
                new_url = urljoin(url, href)
            self.found_urls.add(new_url)
            self._crawl(new_url, depth + 1, pbar=pbar)
        if self.found_urls:
            self._update_progress(pbar)

    def _update_progress(self, pbar):
        pbar.update(100 / len(self.found_urls))

    def _detect_suspicious_code(self, html, url):
        soup = BeautifulSoup(html, 'html.parser')
        script_tags = soup.find_all('script')
        for script in script_tags:
            script_content = script.get_text()
            if 'eval(' in script_content:
                print(f"Suspicious code found in {url}: eval() function")
            if 'setTimeout(' in script_content:
                print(f"Suspicious code found in {url}: setTimeout() function")
            if 'setInterval(' in script_content:
                print(f"Suspicious code found in {url}: setInterval() function")
            if 'document.cookie' in script_content:
                print(f"Suspicious code found in {url}: document.cookie usage")

    def save_found_urls(self, filename='found.txt'):
        with open(filename, 'w') as f:
            for url in self.found_urls:
                f.write(url + '\n')

if __name__ == "__main__":
    start_url = "https://example.com/"  # replace with your starting URL
    max_depth = 1  # adjust the maximum depth
    crawler = Crawler(start_url, max_depth)
    print("Starting crawling process...")
    crawler.crawl()
    print("Crawling process completed.")
    print("Saving found URLs to found.txt...")
    crawler.save_found_urls()
    print("Found URLs saved to found.txt.")

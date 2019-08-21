import re
from bs4 import BeautifulSoup
from helpers import make_request, enqueue_url, log


class CrawlerAmazonStrategy(object):
    def __init__(self, category_url):
        self.category_url = category_url
        self.count = 0

    def crawl_href_and_enqueue(self, element):
        link = element["href"]
        self.count += 1
        enqueue_url(link)

    def run(self):
        self.get_subcategories(self.category_url)

    def get_subcategories(self, category_url):
        pass

    def get_item(self):
        pass

    def get_items(self):
        pass


class CrawlerKitchenStrategy(CrawlerAmazonStrategy):
    def get_subcategories(self, category_url):
        subcategory_rgx = re.compile('merchandised-content.*')
        page, html = make_request(category_url)
        strip_html = html.replace('\n', '').replace('\t', '').replace('\r', '')
        subcategory_match = subcategory_rgx.search(strip_html)
        if subcategory_match:
            html_crawled = BeautifulSoup(subcategory_match.group(), "html.parser")
            container = html_crawled.find('div', class_="acsUxWidget").find('div', class_="bxc-grid__container")
            categories_rows = container.find_all('div', 'bxc-grid__row')[-3:]
            for row in categories_rows:
                subcategories = row.find_all('a')
                for subcategory in subcategories:
                    self.crawl_href_and_enqueue(subcategory)

        log("Found {} subcategories on {}".format(self.count, category_url))


class CrawlerBooksStrategy(CrawlerAmazonStrategy):
    def get_subcategories(self, category_url):
        subcategory_rgx = re.compile('(<div class=\"left_nav browseBox\").*Libros<.*class=\"left_nav_footer\"')
        page, html = make_request(category_url)
        subcategory_match = subcategory_rgx.search(html)
        if subcategory_match:
            html_crawled = BeautifulSoup(subcategory_match.group(), "html.parser")
            title_categories = html_crawled.find_all('a')

            for subcategory in title_categories:
                self.crawl_href_and_enqueue(subcategory)

        log("Found {} subcategories on {}".format(self.count, category_url))


class CrawlerToysStrategy(CrawlerAmazonStrategy):
    def get_subcategories(self, category_url):
        subcategory_rgx = re.compile('merchandised-content.*')
        page, html = make_request(category_url)
        strip_html = html.replace('\n', '').replace('\t', '').replace('\r', '')
        subcategory_match = subcategory_rgx.search(strip_html)
        if subcategory_match:
            html_crawled = BeautifulSoup(subcategory_match.group(), "html.parser")
            container = html_crawled.find_all('div', class_="acsUxWidget")[5].find('div', class_="bxc-grid__container")
            categories_rows = container.find_all('div', 'bxc-grid__row')[1:5:1]
            for row in categories_rows:
                subcategories = row.find_all('a')
                for subcategory in subcategories:
                    self.crawl_href_and_enqueue(subcategory)
        log("Found {} subcategories on {}".format(self.count, category_url))


class CrawlerMusicStrategy(CrawlerAmazonStrategy):
    def get_subcategories(self, category_url):
        subcategory_rgx = re.compile('(<h3>Browse by Genre).*(</ul>){1}<h3>Music on Amazon Devices')
        page, html = make_request(category_url)
        subcategory_match = subcategory_rgx.search(html)
        if subcategory_match:
            html_crawled = BeautifulSoup(subcategory_match.group(), "html.parser")
            title_categories = html_crawled.find_all('a')

            for subcategory in title_categories:
                self.crawl_href_and_enqueue(subcategory)

        log("Found {} subcategories on {}".format(self.count, category_url))


class CrawlerSportsStrategy(CrawlerAmazonStrategy):
    def get_subcategories(self, category_url):
        subcategory_rgx = re.compile('(<h3>Shop by Sport).*(</ul>){1}<h3>')
        page, html = make_request(category_url)
        subcategory_match = subcategory_rgx.search(html)
        if subcategory_match:
            html_crawled = BeautifulSoup(subcategory_match.group(), "html.parser")
            title_categories = html_crawled.find_all('a')

            for subcategory in title_categories:
                self.crawl_href_and_enqueue(subcategory)

        log("Found {} subcategories on {}".format(self.count, category_url))


class CrawlerComputersStrategy(CrawlerAmazonStrategy):
    def get_subcategories(self, category_url):
        subcategory_rgx = re.compile('Shop by Store.*(</ul>)')
        page, html = make_request(category_url)
        subcategory_match = subcategory_rgx.search(html)
        if subcategory_match:
            html_crawled = BeautifulSoup(subcategory_match.group(), "html.parser")
            category_container = html_crawled.find(string='Shop by Store').find_next_sibling('ul')
            title_categories = category_container.find_all('a')

            for subcategory in title_categories:
                self.crawl_href_and_enqueue(subcategory)

        log("Found {} subcategories on {}".format(self.count, category_url))


class CrawlerJewelryStrategy(CrawlerAmazonStrategy):
    def get_subcategories(self, category_url):
        subcategory_rgx = re.compile('Featured categories.*Featured deals')
        page, html = make_request(category_url)
        strip_html = html.replace('\n', '')
        subcategory_match = subcategory_rgx.search(strip_html)
        if subcategory_match:
            html_crawled = BeautifulSoup(subcategory_match.group(), "html.parser")
            title_categories = html_crawled.find_all('a', class_="a-link-normal octopus-pc-category-card-v2-subcategory-link")

            for subcategory in title_categories:
                self.crawl_href_and_enqueue(subcategory)

        log("Found {} subcategories on {}".format(self.count, category_url))


class CrawlerOfficeStrategy(CrawlerAmazonStrategy):
    def get_subcategories(self, category_url):
        subcategory_rgx = re.compile('Shop by category.*')
        page, html = make_request(category_url)
        strip_html = html.replace('\n', '')
        subcategory_match = subcategory_rgx.search(strip_html)
        if subcategory_match:
            html_crawled = BeautifulSoup(subcategory_match.group(), "html.parser")
            row = html_crawled.find_all('div', class_="bxc-grid__row", limit=2)
            for subcategory_container in row:
                subcategories = subcategory_container.find_all('a')
                for subcategory in subcategories:
                    self.crawl_href_and_enqueue(subcategory)

        log("Found {} subcategories on {}".format(self.count, category_url))


class CrawlerAmazonContext(object):
    CRAWLER_STRATEGY = {
        'Sports-Fitness': CrawlerSportsStrategy,
        'computer-pc-hardware': CrawlerComputersStrategy,
        'kitchen-dining': CrawlerKitchenStrategy,
        'books-used-books': CrawlerBooksStrategy,
        'toys': CrawlerToysStrategy,
        'music-rock': CrawlerMusicStrategy,
        'Jewelry': CrawlerJewelryStrategy,
        'Office-Products': CrawlerOfficeStrategy
    }

    def __init__(self, category_url):
        self.category_url = category_url

    def define_type_crawler(self):
        crawler_strategy = ''
        for key in self.CRAWLER_STRATEGY.keys():
            rgx_category = re.compile(key)
            category_ref = rgx_category.search(self.category_url)
            if category_ref:
                crawler_strategy = self.CRAWLER_STRATEGY[category_ref.group()]
                break
        return crawler_strategy

    def init_crawler(self):
        # choose strategy by url search category
        crawler_strategy = self.define_type_crawler()
        crawler_strategy(self.category_url).run()

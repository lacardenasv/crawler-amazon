import re
from bs4 import BeautifulSoup
from helpers import make_request, enqueue_url, log

KITCHEN_CATEGORY = 1
COMPUTER_CATEGORY = 2
TOY_CATEGORY = 3
BOOKS_CATEGORY = 4
MUSIC_CATEGORY = 5
SPORTS_CATEGORY = 6
FASHION_CATEGORY = 7
OFFICE_CATEGORY = 8
JEWELRY_CATEGORY = 9

CATEGORY_LABELS = {
    KITCHEN_CATEGORY:  'kitchen',
    COMPUTER_CATEGORY:  'computer',
    TOY_CATEGORY:  'toy',
    BOOKS_CATEGORY:  'books',
    MUSIC_CATEGORY:  'music',
    SPORTS_CATEGORY:  'sports',
    FASHION_CATEGORY:  'fashion',
    OFFICE_CATEGORY:  'office',
    JEWELRY_CATEGORY:  'jewelry'
}


class CrawlerAmazonStrategy(object):
    category_label = ''

    def __init__(self, category_url):
        self.category_url = category_url
        self.count = 0

    def crawl_href_and_enqueue(self, element):
        link = element["href"]
        self.count += 1
        enqueue_url(link, self.category_label)

    def run(self):
        self.get_subcategories(self.category_url)

    def get_subcategories(self, category_url):
        pass

    def get_item(self):
        pass

    def get_items(self):
        pass


class CrawlerKitchenStrategy(CrawlerAmazonStrategy):
    category_label = KITCHEN_CATEGORY

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
    category_label = BOOKS_CATEGORY

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
    category_label = TOY_CATEGORY

    def get_subcategories(self, category_url):
        subcategory_rgx = re.compile('merchandised-content.*')
        page, html = make_request(category_url)
        strip_html = html.replace('\n', '').replace('\t', '').replace('\r', '')
        subcategory_match = subcategory_rgx.search(strip_html)
        if subcategory_match:
            html_crawled = BeautifulSoup(subcategory_match.group(), "html.parser")
            container = html_crawled.find_all('div', class_="acsUxWidget")[4].find('div', class_="bxc-grid__container")
            categories_rows = container.find_all('div', 'bxc-grid__row')[1:5:1]
            for row in categories_rows:
                subcategories = row.find_all('a')
                for subcategory in subcategories:
                    self.crawl_href_and_enqueue(subcategory)
        log("Found {} subcategories on {}".format(self.count, category_url))


class CrawlerMusicStrategy(CrawlerAmazonStrategy):
    category_label = MUSIC_CATEGORY

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
    category_label = SPORTS_CATEGORY

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
    category_label = COMPUTER_CATEGORY

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
    category_label = JEWELRY_CATEGORY

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
    category_label = OFFICE_CATEGORY

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

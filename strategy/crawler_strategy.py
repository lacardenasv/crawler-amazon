import re
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import settings
from extractors import get_url
from helpers import make_request, enqueue_url, log, dequeue_url, ProductsRobot, format_url

import eventlet

from models import ProductRecord

pool = eventlet.GreenPool(settings.max_threads)
pile = eventlet.GreenPile(pool)

# CATEGORY VARIABLES
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


class ProductExtraInfo(object):
    dimensions_regex = r'(\d+\s|\s*\d+\.+\d+)'

    def get_product_extra_info(self, page):  # return dictionary
        product_info = self.get_product_extra_info_container(page)
        if not product_info:
            log('Product Extra Info not found!')
            return {}
        asin = self.get_product_asin(product_info)
        product_dimensions = self.get_product_dimensions(product_info)
        product_weight = self.get_product_weight(product_info)
        shipping_weight = self.get_shipping_weight(product_info)
        package_dimensions = self.get_package_dimensions(product_info)
        package_weight = self.get_package_weight(product_info)

        return {
            'asin': asin,
            'product_dimensions': product_dimensions,
            'product_weight': product_weight,
            'shipping_weight': shipping_weight,
            'package_dimensions': package_dimensions,
            'package_weight': package_weight
        }

    def get_package_dimensions(self, product_info):
        pass

    def get_package_weight(self, product_info):
        pass

    def get_product_extra_info_container(self, page):
        pass

    def get_shipping_weight(self, product_info):
        pass

    def get_product_asin(self, product_info):
        pass

    def get_product_dimensions(self, product_info):
        pass

    def get_product_weight(self, product_info):
        pass


class MarkedAProductExtraInfo(ProductExtraInfo):
    info_container_id = 'prodDetails'
    product_dimensions_labels = ('Product', 'Item')

    def get_product_extra_info_container(self, page):
        return page.find(id=self.info_container_id)

    def get_product_asin(self, product_info):
        asin_value = None
        asin_item = product_info.find(string=re.compile('ASIN'))
        if asin_item:
            asin_tag = asin_item.parent.parent.find('td', class_="value")
            asin_value = asin_tag.text if asin_tag else asin_item.parent.parent.find_all('td')[-1].text
        return asin_value

    def get_product_dimensions(self, product_info):
        dimensions_value = {}
        dimensions_item = product_info.find(string=re.compile(r'(Product|Item) Dimensions'))
        if dimensions_item:
            item_tag = dimensions_item.parent.parent.find('td', class_="value")
            item_value = item_tag.text if item_tag else dimensions_item.parent.parent.find_all('td')[-1].text
            dimensions_crawled = re.findall(self.dimensions_regex, item_value)
            dimensions_value = {
                "length": dimensions_crawled[0],
                "width": dimensions_crawled[1],
                "height": dimensions_crawled[2]
            }
        return dimensions_value

    def get_shipping_weight(self, product_info):
        shipping_value = None
        shipping_item = product_info.find(string=re.compile('Shipping Weight'))
        if shipping_item:
            shipping_tag = shipping_item.parent.parent.find('td', class_="value")
            shipping_value = shipping_tag.text if shipping_tag else shipping_item.parent.parent.find_all('td')[-1].text
            shipping_value = float(re.search(self.dimensions_regex, shipping_value).group())
        return shipping_value

    def get_product_weight(self, product_info):
        weight_value = None
        weight_item = product_info.find(string=re.compile('Item Weight'))
        if weight_item:
            weight_tag = weight_item.parent.parent.find('td', class_="value")
            weight_value = weight_tag.text if weight_tag else weight_item.parent.parent.find_all('td')[-1].text
            weight_value = float(re.search(self.dimensions_regex, weight_value).group())
        return weight_value

    def get_package_dimensions(self, product_info):
        package_dimensions_value = None
        package_info_item = product_info.find(string=re.compile('Package Dimensions'))
        if package_info_item:
            package_tag = package_info_item.parent.parent.find('td', class_="value")
            package_value = package_tag.text if package_tag else package_info_item.parent.parent.find_all('td')[-1].text
            dimensions_crawled = re.findall(self.dimensions_regex, package_value)
            package_dimensions_value = {
                "length": dimensions_crawled[0],
                "width": dimensions_crawled[1],
                "height": dimensions_crawled[2]
            }
        return package_dimensions_value


class CrawlerAmazonStrategy(object):
    category_label = ''
    product_type_mark = {
        KITCHEN_CATEGORY: MarkedAProductExtraInfo,
        COMPUTER_CATEGORY: MarkedAProductExtraInfo,
        TOY_CATEGORY: MarkedAProductExtraInfo,
        BOOKS_CATEGORY: MarkedAProductExtraInfo,
        MUSIC_CATEGORY: MarkedAProductExtraInfo,
        SPORTS_CATEGORY: MarkedAProductExtraInfo,
        FASHION_CATEGORY: MarkedAProductExtraInfo,
        OFFICE_CATEGORY: MarkedAProductExtraInfo,
        JEWELRY_CATEGORY: MarkedAProductExtraInfo
    }

    def __init__(self):
        self.category_url = None
        self.count = 0

    def crawl_href_and_enqueue(self, element):
        link = element["href"]
        self.count += 1
        enqueue_url(link, self.category_label)

    def run(self, category_url):
        self.category_url = category_url
        self.get_subcategories(self.category_url)

    def get_product_title(self, page):
        title = page.find(id="productTitle")
        if title:
            return title.string

    def get_product_primary_image(self, page):
        image_container = page.find(id="imgTagWrapperId")
        if image_container:
            return image_container.find('img')['src']

    def get_product_price(self, page):
        price = page.find(id="priceblock_ourprice")
        if price:
            return price.string.replace('$', '')

    def get_product_extra_info(self, page, category_code):
        get_extra_info_strategy = self.product_type_mark[int(category_code)]
        return get_extra_info_strategy().get_product_extra_info(page)


    def get_product_features(self, page):  # Info: Add array field to product model
        feature_list = page.find(id="feature-bullets")
        if feature_list:
            return [feature.text for feature in feature_list.find_all(class_="a-list-item") if feature.string]

    def get_product_info(self, url, page, category_code):
        url_sanitazed = format_url(url)
        title = self.get_product_title(page)
        primary_image = self.get_product_primary_image(page)
        price = self.get_product_price(page)
        features = self.get_product_features(page)
        extra_info = self.get_product_extra_info(page, category_code)

        if not primary_image:
            log("No product image detected, skipping")

        product = ProductRecord(
            title=title,
            product_url=url_sanitazed,
            listing_url=url_sanitazed, # TODO: delete attr
            price=price,
            primary_img=primary_image,
            crawl_time=None,
            category_code=category_code,
            category=CATEGORY_LABELS[int(category_code)],
            features=features,
            asin=extra_info.get('asin'),
            dimensions=extra_info.get('product_dimensions'),
            weight=extra_info.get('product_weight'),
            shipping_weight=extra_info.get('shipping_weight'),
            package_dimensions=extra_info.get('product_dimensions'),
            package_weight=extra_info.get('package_weight'),
        )
        product_id = product.save()

        if product_id: log('Product saved! {}'.format(product_id))


    def get_products_link(self, items, category_code):
        for item in items[:settings.max_details_per_listing]:
            product_url = get_url(item)
            enqueue_url(product_url, category_code, settings.PRODUCT_CRAWLER)
            pile.spawn(fetch_listing)

    def get_subcategories(self):  # Abstract method
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

    PRODUCT_CRAWLER_STRATEGY = {
        KITCHEN_CATEGORY: CrawlerKitchenStrategy,
        COMPUTER_CATEGORY: CrawlerComputersStrategy,
        TOY_CATEGORY: CrawlerToysStrategy,
        BOOKS_CATEGORY: CrawlerBooksStrategy,
        MUSIC_CATEGORY: CrawlerMusicStrategy,
        SPORTS_CATEGORY: CrawlerSportsStrategy,
        FASHION_CATEGORY: None, # TODO: Strategy!!
        OFFICE_CATEGORY: CrawlerOfficeStrategy,
        JEWELRY_CATEGORY: CrawlerJewelryStrategy,
    }

    def __init__(self):
        self.category_url = None

    def define_type_crawler(self):
        crawler_strategy = ''
        for key in self.CRAWLER_STRATEGY.keys():
            rgx_category = re.compile(key)
            category_ref = rgx_category.search(self.category_url)
            if category_ref:
                crawler_strategy = self.CRAWLER_STRATEGY[category_ref.group()]
                break
        return crawler_strategy

    def define_type_product_detail_crawler(self, category_code):
        crawler_strategy = self.PRODUCT_CRAWLER_STRATEGY[int(category_code)]
        return crawler_strategy()

    def init_crawler(self, category_url):
        self.category_url = category_url
        # choose strategy by url search category
        crawler_strategy = self.define_type_crawler()
        crawler_strategy().run(self.category_url)


def fetch_listing():

    global crawl_time
    url, category_code, mode = dequeue_url()
    if not url:
        log("WARNING: No URLs found in the queue. Retrying...")
        pile.spawn(fetch_listing)
        return

    # make request through selenium
    products_robot = ProductsRobot().run(url)
    page = BeautifulSoup(products_robot.page_source, "html.parser")
    try:
        element = WebDriverWait(products_robot, 2).until(
            EC.presence_of_element_located((By.ID, "prodDetails"))
        )
    except TimeoutException as e:
        pass
    finally:
        products_robot.quit()
    # put this login in get_products_link
    items = []
    items_container = page.find(id="mainResults")

    if items_container:
        items = items_container.find_all(id=re.compile('result_\d*'))

    log("Found {} items on {}".format(len(items), url))

    crawler = CrawlerAmazonContext().define_type_product_detail_crawler(category_code)
    if mode == settings.LINK_DETAIL_PRODUCT:
        crawler.get_products_link(items, category_code)
    elif mode == settings.PRODUCT_CRAWLER:
        crawler.get_product_info(url, page, category_code)

    # page, html = make_request(url) TODO: delete
    # if not page:
    #     return
    #
    # items = page.findAll("li", "s-result-item")
    '''
    for item in items[:settings.max_details_per_listing]:

        product_image = get_primary_img(item)
        if not product_image:
            log("No product image detected, skipping")
            continue

        product_title = get_title(item)
        product_url = get_url(item)
        product_price = get_price(item)

        product = ProductRecord(
            title=product_title,
            product_url=format_url(product_url),
            listing_url=format_url(url),
            price=product_price,
            primary_img=product_image,
            crawl_time=crawl_time,
            category_code=category_code,
            category=CATEGORY_LABELS[int(category_code)]
        )
        product_id = product.save()
        # download_image(product_image, product_id)
    '''
    # add next page to queue
    next_link = page.find("a", id="pagnNextLink")
    if next_link:
        log(" Found 'Next' link on {}: {}".format(url, next_link["href"]))
        enqueue_url(next_link["href"],  category_code)
        pile.spawn(fetch_listing)

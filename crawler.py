import re
import sys
from datetime import datetime

import eventlet
from bs4 import BeautifulSoup

import settings
from models import ProductRecord
from helpers import make_request, log, format_url, enqueue_url, dequeue_url, ProductsRobot
from extractors import get_title, get_url, get_price, get_primary_img
from strategy.crawler_strategy import CrawlerAmazonContext, CATEGORY_LABELS, CrawlerAmazonStrategy, pile, pool, \
    fetch_listing

crawl_time = datetime.now()


def begin_crawl():

    # explode out all of our category `start_urls` into subcategories
    with open(settings.start_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # skip blank and commented out lines
            crawler_context = CrawlerAmazonContext().init_crawler(line)

            # page, html = make_request(line) TODO: delete comment code
            # count = 0
            # '''
            # INFO IMPORTANT!: Depends on the markup of the page we should search different elements on the html to
            # get it right
            # '''
            # # look for subcategory links on this page
            # subcategories = page.findAll("div", "bxc-grid__image")  # downward arrow graphics
            # subcategories.extend(page.findAll("li", "sub-categories__list__item"))  # carousel hover menu
            # sidebar = page.find("div", "browseBox")
            # if sidebar:
            #     subcategories.extend(sidebar.findAll("li"))  # left sidebar
            #
            # for subcategory in subcategories:
            #     link = subcategory.find("a")
            #     if not link:
            #         continue
            #     link = link["href"]
            #     count += 1
            #     enqueue_url(link)

           # log("Found {} subcategories on {}".format(count, line))


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == "start":
        log("Seeding the URL frontier with subcategory URLs")
        begin_crawl()  # put a bunch of subcategory URLs into the queue

    log("Beginning crawl at {}".format(crawl_time))
    [pile.spawn(fetch_listing) for _ in range(settings.max_threads)]
    pool.waitall()

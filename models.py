import psycopg2
import json

import settings

conn = psycopg2.connect(database=settings.database, host=settings.host, user=settings.user, password=settings.password, port=settings.port)
cur = conn.cursor()


class ProductRecord(object):
    """docstring for ProductRecord"""       #TODO: delete listing_url
    def __init__(
        self,
        title,
        product_url,
        listing_url,
        price,
        primary_img,
        crawl_time,
        category_code,
        category,
        features,
        asin,
        dimensions,
        weight,
        shipping_weight,
        package_dimensions,
        package_weight
    ):
        super(ProductRecord, self).__init__()
        self.title = title
        self.product_url = product_url
        self.listing_url = listing_url
        self.price = price
        self.primary_img = primary_img
        self.crawl_time = crawl_time
        self.category_code = category_code
        self.category = category
        self.features = features
        self.asin = asin
        self.dimensions = json.dumps(dimensions)
        self.weight = weight
        self.shipping_weight = shipping_weight
        self.package_dimensions = json.dumps(package_dimensions)
        self.package_weight = package_weight

    def save(self):
        cur.execute('''INSERT INTO marketplace_crawledamazonproduct (title, product_url, listing_url, price, primary_img, crawl_time, category_code, category, features, asin, dimensions, weight, shipping_weight, package_dimensions, package_weight
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id''', (
            self.title,
            self.product_url,
            self.listing_url,
            self.price,
            self.primary_img,
            self.crawl_time,
            self.category_code,
            self.category,
            self.features,
            self.asin,
            self.dimensions,
            self.weight,
            self.shipping_weight,
            self.package_dimensions,
            self.package_weight
        ))
        conn.commit()
        return cur.fetchone()[0]


if __name__ == '__main__':

    # setup tables
    cur.execute("DROP TABLE IF EXISTS marketplace_crawledamazonproduct")
    cur.execute("""CREATE TABLE marketplace_crawledamazonproduct (
        id          serial PRIMARY KEY,
        title       varchar(2056),
        product_url         varchar(2056),
        listing_url varchar(2056),
        price       varchar(128),
        primary_img varchar(2056),
        crawl_time timestamp,
        category_code integer,
        asin varchar(256) null,
        category varchar(256),
        features text[] null default '{}',
        dimensions jsonb DEFAULT '{}' NULL, 
        weight double precision NULL,
        shipping_weight double precision NULL,
        package_dimensions jsonb DEFAULT '{}' NULL,
        package_weight double precision NULL
    );""")
    conn.commit()

from HTMLParser import HTMLParser

htmlparser = HTMLParser()


def get_title(item):
    title = item.find("h2", "s-access-title")
    if title:
        return htmlparser.unescape(title.text.encode("utf-8"))
    else:
        return "<missing product title>"


def get_url(item):
    link = item.find("a", class_="s-access-detail-page")
    if link:
        return link["href"]
    else:
        return "<missing product url>"


def get_price(item):
    price = item.find("span", "sx-price")
    if price:
        return price.text
    return None


def get_primary_img(item):
    thumb = item.find("img", "s-access-image")
    if thumb:
        src = thumb["src"]

        p1 = src.split("/")
        p2 = p1[-1].split(".")

        base = p2[0]
        ext = p2[-1]

        return "/".join(p1[:-1]) + "/" + base + "." + ext

    return None
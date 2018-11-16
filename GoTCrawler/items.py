# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GotcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    seasons = scrapy.Field()
    status = scrapy.Field()
    allegiance = scrapy.Field()
    pass

class GotGraphItem(scrapy.Item):
    name = scrapy.Field()
    got_type = scrapy.Field()
    node_type = scrapy.Field()
    status = scrapy.Field()
    edges = scrapy.Field()
    properties = scrapy.Field()
    url = scrapy.Field()
    redirected_urls = scrapy.Field() # all urls that finally got redirected to this object's main url
    pass
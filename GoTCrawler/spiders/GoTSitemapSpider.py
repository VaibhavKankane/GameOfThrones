# -*- coding: utf-8 -*-
from scrapy.spiders import SitemapSpider
from scrapy.selector import Selector
from GoTCrawler.items import GotcrawlerItem


class GotsitemapspiderSpider(SitemapSpider):
    name = 'GoTSitemapSpider'
    sitemap_urls = [
        'https://gameofthrones.fandom.com/sitemap-newsitemapxml-NS_0-p1.xml'
    ]
    considered_attributes = {
        'Season(s)': 'seasons',
        'Status': 'status',
        'Allegiance': 'allegiance',
    }

    def parse(self, response):
        aside_tag_start = response.text.find('<aside')
        aside_tag_end = response.text.find('</aside>') + 8

        # if the html contains <aside> tag
        if aside_tag_start > -1 and aside_tag_end > 8:

            # parse the aside tag html only. This is really faster than parsing whole page and extracting aside tag
            aside_tag = Selector(text=response.text[aside_tag_start:aside_tag_end])

            # get all attributes in the table
            attrs = aside_tag.css('div.pi-item')  # recommended  css selector for class

            # check if the first attribute is 'Season(s)'
            # considering this check to ensure collection of characters only, and not of actors/other types
            if attrs[0].xpath('./h3/text()').extract()[0] != 'Season(s)':
                return

            item = GotcrawlerItem()
            # get the name on the top of the table (character name)
            item['name'] = aside_tag.xpath('//h2/text()').extract_first()

            # iterate all attributes in the table and extract the values of important ones
            for attr in attrs:

                property_name = attr.xpath('./h3/text()').extract()[0]
                if property_name in GotsitemapspiderSpider.considered_attributes.keys():
                    property_value = GotsitemapspiderSpider.get_values(attr)
                    item[GotsitemapspiderSpider.
                         considered_attributes[property_name]] = property_value
            
            return item
        pass

    @staticmethod
    def get_values(attributes):
        #Extract the value div
        attribute_values = attributes.css('div.pi-data-value')

        # div.pi-data-value html contains values. One pattern is to extract all text-nodes & <br> tags.
        # then join the contiguous text nodes.
        nodes = attribute_values.xpath('.//text()|.//br').extract()

        #remove nodes that end with ':' as they are not actual values. also trim ' {}' chars to remove brackets and get proper value
        nodes = [
            node.strip(' {}"') for node in nodes if node.endswith(':') is False
        ]

        #join the contiguous text nodes split by <br> tag to constitute value
        values = ' '.join(nodes).split('<br>')

        #format the string-values slightly
        formatted_values = [
            value.strip(' ') for value in values if value != ''
        ]

        return formatted_values
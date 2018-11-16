# -*- coding: utf-8 -*-
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from GoTCrawler.items import GotGraphItem
import logging


class GotGraphSpider(CrawlSpider):
    name = 'GotGraphSpider'
    allowed_domains = ['gameofthrones.fandom.com']
    start_urls = ['https://gameofthrones.fandom.com/wiki/Game_of_Thrones_Wiki']

    rules = (
        Rule(
            LinkExtractor(
                allow_domains=('gameofthrones.fandom.com'),
                allow=('https://gameofthrones.fandom.com/wiki/[^?:#]+$'),   # skip urls with '?' present. (edit links)
                deny=('https://gameofthrones.fandom.com/wiki/Category*'),
                ),
            callback='parse_box',  #ensure classback is not 'parse'
            follow=True), )
    
    #This is the list of attributes for which relationship (edge) is skipped
    black_list = ['song', 'Role', 'Job', 'Statuses', 'Birthplace', 'Cast', 'yearsactive', 'artist']  # 'Statuses' is for relationship nodes (currently 12)
    
    def parse_box(self, response):
        aside_tag_start = response.text.find('<aside')
        aside_tag_end = response.text.find('</aside>') + 8

        # if the html contains <aside> tag
        if aside_tag_start > -1 and aside_tag_end > 8:

            # parse the aside tag html only. This is really faster than parsing whole page and extracting aside tag
            aside_tag = Selector(text=response.text[aside_tag_start:aside_tag_end])

            item = GotGraphItem()
            # get the name on the top of the table (character name)
            item['name'] = aside_tag.xpath('//h2//text()').extract_first()
            if item['name'] is None:
                return None
            
            item['url'] = response.url[32:]
            item['redirected_urls'] = GotGraphSpider.get_redirected_urls(response)

            # get all attributes in the table
            attrs = aside_tag.css('div.pi-item')  # recommended  css selector for class

            item['edges'] = []
            item['properties'] = []
            allLinks = aside_tag.xpath('.//a/@href').extract()
            # if there is an external 
            allLinks = [link for link in allLinks if link.startswith('http') == False]  # remove external links

            prop_links = [] # this will help in putting Label on edges (relationships)
            # iterate all attributes in the table and extract the values of important ones
            for attr in attrs:

                property_name = attr.xpath('./h3//text()').extract()[0]
                property_name = property_name.strip(' :')

                # check if its a blacklisted property
                if property_name in GotGraphSpider.black_list:
                    return None

                item['properties'].append(property_name)
                if property_name == 'Status':
                    item['status'] = GotGraphSpider.get_values(attr)
                elif property_name == 'Type':
                    item['got_type'] = GotGraphSpider.get_values(attr)
                else:
                    this_prop_links = GotGraphSpider.get_links(attr)
                    prop_links += this_prop_links
                    for link in this_prop_links:
                        item['edges'].append({
                            'Source': item['url'],
                            'Label': property_name,
                            'Target': link
                        })

            # add remaining links as edges with Label=Referred
            remaining_links = [item for item in allLinks if item not in prop_links]
            for link in remaining_links:
                item['edges'].append({
                    'Source': item['url'],
                    'Label': 'Referred',
                    'Target': link
                })

            item['node_type'] = GotGraphSpider.get_node_type(item)

            # check if its an actor node, remove it
            if (item['node_type'] == 'node'):
                return None
                
            yield item

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

    @staticmethod
    def get_links(attributes):
        attribute_values = attributes.css('div.pi-data-value')
        links = attribute_values.xpath('.//a/@href').extract()
        return links

    @staticmethod
    def get_redirected_urls(response):
        r_urls = response.request.meta.get('redirect_urls')
        if r_urls is not None:
            r_urls = [url[32:] for url in r_urls]
        return r_urls
    
    @staticmethod
    def get_node_type(item):
        if 'Narrated by' in item['properties']:
            return 'HistoriesNLore'
        elif ('Sigil' in item['properties']) | (item['name'].startswith('House')):  #Some Houses are actually from Histories&Lore so ordering is important
            return 'House'
        elif 'Premiere' in item['properties']:
            return 'Season'
        elif 'Air date' in item['properties']:
            return 'Episode'
        elif ('Center' in item['properties']) | ('Leader' in item['properties']) | ('Notable Members' in item['properties']):
            return 'Organization'   # Organization before Location. Else unsullied is of type=Location
        elif ('Geography' in item['properties']) | ('Places of Note' in item['properties']) | ('Date of Founding' in item['properties']) | ('Military' in item['properties']) | ('Rulers' in item['properties']) | ('Founder' in item['properties']) | ('Capital' in item['properties']):
            return 'Location'
        elif 'Outcome' in item['properties']:
            return 'Event'
        elif 'Owner' in item['properties']:
            return 'Weapon'
        elif 'Species' in item['properties']:
            return 'Animal'
        elif 'Habitat' in item['properties']:
            return 'Animal'    #Animal_Type=Animal for now
        elif 'Clergy' in item['properties']:
            return 'Religion'
        elif ('Season(s)' in item['properties']) | ('Titles' in item['properties'])  | ('Death' in item['properties']) | ('Portrayed by' in item['properties']) | ('Spouse' in item['properties']):   # spouse is important. see tysha
            return 'Person'
        elif ('Ruler' in item['properties']) | ('Distinctive features' in item['properties']) | ('Society' in item['properties']):
            return 'PersonType'
        elif ('Location' in item['properties']) | ('Place' in item['properties']):
            return 'Location'
        else:
            return 'node'
        
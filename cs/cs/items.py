# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class FlatItem(scrapy.Item):
    rooms = Field()
    title = Field()
    area = Field()
    floor = Field()
    address = Field()
    price = Field()
    id = Field()
    page = Field()
    test = Field()

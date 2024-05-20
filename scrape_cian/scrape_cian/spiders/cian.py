import scrapy


class CianSpider(scrapy.Spider):
    name = "cian"
    allowed_domains = ["k"]
    start_urls = ["https://k"]

    def parse(self, response):
        pass

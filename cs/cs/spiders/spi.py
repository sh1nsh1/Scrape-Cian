import scrapy
from time import sleep
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from ..items import FlatItem


class SpiSpider(scrapy.Spider):
    name = "spi"
    comp = []
    current_page = 0
    start_urls = [
        f"https://kazan.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p={current_page + 1}&region=4777&room1=1/"
    ]

    def parse(self, response: Response, **kwargs):
        self.current_page += 1

        next_page = response.xpath(f'//nav[@data-name="Pagination"]/a[{1 + int(self.current_page != 1)}]/@href').get()

        if next_page:
            # parse each flat on page
            flats = response.xpath("//div/article[@data-name='CardComponent']")
            for flat in flats:
                rel_url = flat.xpath('.//div/a/@href').get()
                yield response.follow(url=rel_url, callback=self.parse_page)

            # go to next page
            yield response.follow(next_page, callback=self.parse)
        else:
            # get dynamic data
            html = self.get_dynamic_data(response.url)
            response = response.replace(body=bytes(html, 'utf-8'))
            # then parse it
            flats = response.xpath("//div/article[@data-name='CardComponent']")
            for flat in flats:
                rel_url = flat.xpath('.//div/a/@href').get()
                yield response.follow(url=rel_url, callback=self.parse_page)

        # raise Exception(self.comp)

    def get_dynamic_data(self, url) -> str:
        # configure driver (chrome does not work headless)
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        sleep(2)
        while True:
            try:
                show_more_btn = driver.find_element(By.XPATH, '//a[@class="_93444fe79c--more-button--nqptt"]')
                driver.execute_script("arguments[0].scrollIntoView();", show_more_btn)
                driver.execute_script("window.scrollTo(0, window.scrollY - 200)")
                show_more_btn.click()
                sleep(3)
            except:
                break
        sleep(5)
        html = driver.page_source
        driver.close()
        return html

    def parse_page(self, response: Response):
        item = FlatItem()
        main_header = response.xpath(".//div[@data-name = 'OfferTitleNew']/h1/text()").get()
        address = list(map(
            lambda x: x.xpath(".//text()").get(),
            response.xpath(
                "//div[@data-name='AddressContainer']//a")
        ))
        link = response.url

        item["title"] = main_header
        item["rooms"] = main_header[main_header.find("-") - 1] if "Студия" not in main_header else "Студия"
        item["area"] = response.xpath('//span[contains(text(),"Общая площадь")]/../span[2]/text()').get().replace(" ", '')
        item["floor"] = response.xpath('//span[contains(text(),"Этаж")]/../span[2]/text()').get().replace(" из ","/")
        item["address"] = ", ".join(address)
        item["price"] = response.xpath('//div[@data-testid="price-amount"]/span/text()').get().replace(" ", '')
        item["id"] = link[link[:-1].rfind('/') + 1:-1]
        item["page"] = str(self.current_page)
        yield item

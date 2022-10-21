import scrapy


class WxcSpider(scrapy.Spider):
    name = 'wxc'
    allowed_domains = ['bbs.wenxuecity.com']
    start_urls = ['http://bbs.wenxuecity.com/']

    def parse(self, response):
        pass

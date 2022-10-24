"""In a typical page, each <div> will contain a thread,
    within each thread, each <p> tag contains a single post title,
    majority of the information are extracted from this <p> tag, thus we will have 
    two loops:
    
    """

import scrapy

# from scrapy.shell import inspect_response
# inspect_response(response, self)    

class WxcSpider(scrapy.Spider):
    name = 'wxc'
    allowed_domains = ['bbs.wenxuecity.com']
    start_urls = ['https://bbs.wenxuecity.com/myhouse/']
    # start_urls = ['https://bbs.wenxuecity.com/xinhai/']

    def parse(self, response):
        # divs = response.xpath("//div[@class='odd' or @class='even']")
        divs = response.xpath("//div[@id='postlist']/div")
        
        for div in divs:

            parent = list()
            threads = div.xpath('.//p')  # here we have all posts in a thread
            for p in threads:
                
                i = {}
                # Category information
                
                i['cat_slug'] = response.url.split('/')[-2]

                # i['cat_name'] = response.xpath("normalize-space(//h1/text())").get()
                i['cat_name'] = response.xpath(
                    "string(//h1)").get().replace(" ", "")
                
                # Post inforamtion
                
                # i['url'] = p.xpath('./a/@href').re_first(r'\d+')
                i['url'] = response.urljoin(p.xpath('./a/@href').get())            
                i['title'] = p.xpath('normalize-space(./a/text())').get()
                
                s = p.xpath("normalize-space(.//small)")
                i['post_date'] = " ".join(
                    s.re(r'(\d+:\d+:\d+)|(\d+/\d+/\d+)')).strip()
                
                try:
                    i['bytes'] = int(s.re_first(r'\d+'))
                except TypeError:
                    i['bytes'] = 0
                
                # Not implemented
                i['hits'] = 0
                i['votes'] = 0
                    
                # Nick information
                i['nick'] = p.xpath('.//a[@class="b"]/text()').get()
                gender = p.xpath('text()').re_first(r'.*(♂|♀).*')
                i['gender'] = 0 if gender == '♂' else 1 if gender == '♀' else None                
                i['blog_url'] = p.xpath('.//a[contains(@title, "博客首页")]/@href').get()
                i['group_url'] = p.xpath('.//a[contains(@title, "个人群组")]/@href').get()
                
                # Posts relationship                  
                try:
                    i['tier'], i['reply_to'] = len(parent), parent.pop()
                except IndexError:
                    i['tier'], i['reply_to'] = 0, None
                    
                if p.xpath('./@style').re_first(r'.* (\d+)px;.*'):
                    margin = int(p.xpath(
                        './@style').re_first(r'.* (\d+)px;.*'))
                else:
                    margin = 20
                    
                try:
                    next_p = p.xpath('./following-sibling::p[1]')

                    if next_p.xpath('./@style').re_first(r'.* (\d+)px;.*'):
                        next_margin = int(next_p.xpath(
                            './@style').re_first(r'.* (\d+)px;.*'))
                    else:
                        next_margin = 20
                    if next_margin > margin:
                        if i['reply_to']:
                            parent.append(i['reply_to'])
                        parent.append(
                            i['title']
                        )

                    elif next_margin == margin:
                        parent.append(i['reply_to'])
                    else:
                        for _ in range(int((margin - next_margin) / 20 - 1)):
                            parent.pop()
                except IndexError:
                    pass

                yield i

        # try:
        #     next_page = response.xpath('//a[contains(text(), "下一页")]')[0]
        # except IndexError:
        #     next_page = None

        # if next_page is not None:
        #     yield response.follow(next_page, self.parse)

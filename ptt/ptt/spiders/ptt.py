from ..items import PttItem
import scrapy
import time

class PTTSpider(scrapy.Spider):
    name = 'ptt'
    allowed_domains = ['ptt.cc']
    start_urls = ['https://www.ptt.cc/bbs/Stock/index.html']

    condition_words = ['聯電', '2303', '聯華電子']

    def parse(self, response):        
        for i in range(1):    # number of page 
            time.sleep(0.1)
            url = "https://www.ptt.cc/bbs/Stock/index" + str(5020 - i) + ".html"
            yield scrapy.Request(url, cookies={'over18': '1'}, callback=self.parse_page)

    def parse_page(self, response):
        target = response.css("div.r-ent")
        for tag in target:            
            try:
                url = "https://www." + str(self.allowed_domains[0] + tag.css('div.title a::attr(href)')[0].extract())
                yield scrapy.Request(url, callback=self.parse_content)
            except IndexError:
                print("IndexError!!!")

    def parse_content(self, response):
        comments, score = self.get_comment(response.xpath('//div[@class="push"]'))

        item = PttItem()
        item['title'] = response.xpath('//meta[@property="og:title"]/@content')[0].extract()
        item['author'] = response.xpath('//div[@class="article-metaline"]/span[text()="作者"]/following-sibling::span[1]/text()')[0].extract().split(' ')[0]
        item['date'] = response.xpath('//div[@class="article-metaline"]/span[text()="時間"]/following-sibling::span[1]/text()')[0].extract()
        item['content'] = response.xpath('//div[@id="main-content"]/text()')[0].extract()
        item['comments'] = comments
        item['score'] = score
        item['url'] = response.request.url

        if self.check_condition(item):
        	yield item	
		
    
    def check_condition(self, items):   	

        for word in self.condition_words:
        	if word in str(items['comments']):
        		return True
        	if word in str(items['title']):
        		return True
        	if word in str(items['content']):
        		return True

        return False


    def get_comment(self, comments):
        comments_bundle = []
        total_score = 0

        push_tag = comments[0].xpath('//span[contains(@class, "push-tag")]/text()').extract()
        push_user = comments[0].xpath('//span[contains(@class, "push-userid")]/text()').extract()
        push_content = comments[0].xpath('//span[contains(@class, "push-content")]/text()').extract()

        for i in range(len(push_tag)):
            if '推' in push_tag[i]:
                score = 1
            elif '噓' in push_tag[i]:
                score = -1
            else:
                score = 0
            total_score += score

            comments_bundle.append({'user': push_user[i],
                                    'content': push_content[i],
                                    'score': score})

        return comments_bundle, total_score

    

    # def parse_post(self, response):
    #     item = PttItem()
    #     target = response.css("div.r-ent")

    #     for tag in target:
    #         try:
    #             item['title'] = tag.css("div.title a::text")[0].extract()
    #             item['author'] = tag.css('div.author::text')[0].extract()
    #             item['date'] = tag.css('div.date::text')[0].extract()
    #             item['push'] = tag.css('span::text')[0].extract()
    #             item['url'] = tag.css('div.title a::attr(href)')[0].extract()

    #             yield item

    #         except IndexError:
    #             pass
    #         continue
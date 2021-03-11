import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import NordfyItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class NordfySpider(scrapy.Spider):
	name = 'nordfy'
	start_urls = ['https://nordfynsbank.dk/category/nyheder/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="clearfix cl-knap cl-knap1"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = '-'
		title = response.xpath('//div[@class="site-main-content"]/h3/strong/text() | //h1/text()').get()
		if not title:
			title = 'NordfynsBank'
		content = response.xpath('//div[@class="site-main-content"]//text()[not (ancestor::strong) and not(ancestor::h1)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=NordfyItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()

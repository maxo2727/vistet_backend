# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class VistetScraperItem(scrapy.Item):
  name = scrapy.Field()
  price = scrapy.Field()
  description = scrapy.Field()
  image_url = scrapy.Field()
  link = scrapy.Field()
  brand = scrapy.Field()
  category = scrapy.Field()
  sub_category = scrapy.Field()
  color = scrapy.Field()
  sku = scrapy.Field()
  size = scrapy.Field()
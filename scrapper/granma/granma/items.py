# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PrintEditionItem(scrapy.Item):
    date = scrapy.Field()
    page = scrapy.Field()
    link = scrapy.Field()
    file_urls = scrapy.Field()

class LetterToDirectionItem(scrapy.Item):
    is_response = scrapy.Field()
    body = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    original_letter_link = scrapy.Field()
    date = scrapy.Field()
    comments = scrapy.Field()
    
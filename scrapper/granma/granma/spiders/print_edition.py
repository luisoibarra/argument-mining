from pathlib import Path
from ..items import PrintEditionItem
import scrapy
from datetime import date, timedelta

class PrintEditionSpider(scrapy.Spider):
    name = 'print_edition'
    allowed_domains = ['www.granma.cu']

    base_url = 'http://www.granma.cu'

    def __init__(self, start_date = "2020-01-01", end_date="2022-09-02", **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def _parse_date(self, date: str) -> tuple:
        s_year, s_month, s_day = [int(x) for x in date.split("-")]
        return s_year, s_month, s_day
        
    def start_requests(self):
        s_year, s_month, s_day = self._parse_date(self.start_date)
        e_year, e_month, e_day = self._parse_date(self.end_date)
        
        current_date = date(s_year, s_month, s_day)
        day_delta = timedelta(1)
        # Extra day to include the original end_date in the loop
        end_date = date(e_year, e_month, e_day) + day_delta
        
        while current_date != end_date:
            # Zero padded date
            year = "{:0>4d}".format(current_date.year)
            month = "{:0>2d}".format(current_date.month)
            day = "{:0>2d}".format(current_date.day)
            yield scrapy.Request(url=f"{self.base_url}/impreso/{year}-{month}-{day}", callback=self.parse)
            current_date += day_delta

    def parse(self, response):
        links_to_printed_edition = response.xpath('//a[contains(@href, ".pdf")]')
        date_str = response.url.split("/")[-1]
        for link in links_to_printed_edition:
            file_link = link.xpath('@href').get()
            file_link = self.base_url + file_link
            
            # Skipping ending .pdf and getting the page number from link
            page = int(file_link[-6:-4])
            self.log(f"Edition {file_link}")
            
            yield scrapy.Request(
                url=file_link, 
                callback=lambda x: self.download_pdf(x, date_str)    
            )
            
            item = PrintEditionItem(
                date=date_str,
                page=page,
                link=file_link
            )
            yield item
    
    def download_pdf(self, response, date):
        path = Path(__file__, "..", "..", "..", "data", "printed", date, response.url.split('/')[-1]).resolve()
        self.logger.info('Saving PDF %s', path)
        with open(path, 'wb') as f:
            f.write(response.body)
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from .items import LetterToDirectionItem, PrintEditionItem
from itemadapter import ItemAdapter

from pathlib import Path

class JsonWriterPipeline:

    def __init__(self) -> None:
        self.data_path = Path(__file__, "..", "..", "data").resolve()
        self.data_path.mkdir(parents=True, exist_ok=True)

    def process_item(self, item, spider):

        if isinstance(item, PrintEditionItem):
            file = self.data_path / "printed" / item['date'] / (str(item['page']) + ".json")
        elif isinstance(item, LetterToDirectionItem):
            file = self.data_path / "letters" / item['date'] / (str(item['title']) + ".json")
        else:
            file = None

        if file:
            (file / "..").resolve().mkdir(parents=True, exist_ok=True)
            line = json.dumps(ItemAdapter(item).asdict()) + "\n"
            file.write_text(line)

        return item

class GranmaPipeline:
    def process_item(self, item, spider):
        return item

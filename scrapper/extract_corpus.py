from pathlib import Path
import json

def export_letter_corpus(source_path: Path, dest_path: Path):
    """
    Transform the letter json corpus into a txt corpus. The
    exported text will have the following name convention:
    
    `date`|`letter-name`|`response-to-name`
    
    If the letter isn't a response then the last section will
    be empty.
    
    source_path: Letter corpus directory
    dest_path: Destination corpus directory 
    """
    for path in source_path.rglob("*.json"):
        if path.is_file():
           letter_item = json.loads(path.read_text())
           date, name = letter_item['link'].split('/')[-2:]
           title = letter_item['title']
           body = letter_item['body'] 
           file_name = date + "|" + name
           if letter_item['original_letter_link']:
               file_name += "|" + letter_item['original_letter_link'].split('/')[-1]
           corpus_file = dest_path / (file_name + ".txt")
           corpus_file.write_text(f"{title}\n\n{body}")

if __name__ == "__main__":
    SOURCE_PATH = Path(__file__, "..", "granma", "data", "letters").resolve()
    DEST_PATH = Path(__file__, "..", "..", "data", "to_process", "granma_letters").resolve()
    
    DEST_PATH.mkdir(parents=True, exist_ok=True)
    
    export_letter_corpus(SOURCE_PATH, DEST_PATH)
    
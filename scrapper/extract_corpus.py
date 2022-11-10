from pathlib import Path
import json

def export_letter_corpus(source_path: Path, dest_path: Path, export_only_response_and_responded_letters=False):
    """
    Transform the letter json corpus into a txt corpus. The
    exported text will have the following name convention:
    
    `date`|`letter-name`|`response-to-name`
    
    If the letter isn't a response then the last section will
    be empty.
    
    source_path: Letter corpus directory
    dest_path: Destination corpus directory 
    """

    jsons = [json.loads(x.read_text()) for x in source_path.rglob("*.json") if x.is_file() and x.name != "stats.json"]
    jsons_dict = {item['link']: item for item in jsons}
    if export_only_response_and_responded_letters:
        responded_letters = set(x['original_letter_link'] for x in jsons if x['original_letter_link'])
        jsons_dict = {key: item for key, item in jsons_dict.items() if item['original_letter_link'] or item['link'] in responded_letters}
    
    for link, letter_item in jsons_dict.items():
        if letter_item['original_letter_link']:
            try:
                letter_item['original_letter_info'] = jsons_dict[letter_item['original_letter_link']]
            except KeyError:
                print(f"WARNING: Original link {letter_item['original_letter_link']} not found")
        
        date, name = letter_item['link'].split('/')[-2:]
        title = letter_item['title']
        body = letter_item['body'] 
        file_name = date + "|" + name
        if letter_item['original_letter_link']:
            file_name += "|" + letter_item['original_letter_link'].split('/')[-1]
        corpus_file = dest_path / (file_name + ".txt")
        corpus_file.write_text(f"{title}\n\n{body}")
        
        json_file = dest_path / (file_name + ".json")
        json.dump(letter_item, json_file.open("w"))
        
if __name__ == "__main__":
    export_only_response_and_responded_letters = True

    SOURCE_PATH = Path(__file__, "..", "granma", "data", "letters").resolve()
    DEST_PATH = Path(__file__, "..", "..", "data", "to_process", "granma_letters_responded_response" if export_only_response_and_responded_letters else "granma_letters").resolve()

    DEST_PATH.mkdir(parents=True, exist_ok=True)
    
    export_letter_corpus(SOURCE_PATH, DEST_PATH)
    
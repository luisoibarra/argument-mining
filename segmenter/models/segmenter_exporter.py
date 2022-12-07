from pathlib import Path
if __name__ == "__main__":
    import sys
    path = str(Path(__file__, "..", "..", "..").resolve())
    if path not in sys.path:
        print(path)
        sys.path.insert(0, path)

from typing import List
import nltk
from pos_tagger.pos_tagger import SpacyPOSTagger, NLTKPOSTagger


def convert_to_tuples(data:Path, all_words: set, all_tags: set, all_chars: set, bioes=True, meta_tags_level=99, meta_tags_separator="-", use_sentence_split=False):
    tags = []
    current_paragraph_tags = []
    current_paragraph_words = []
    for i, line in enumerate(data.read_text().splitlines()):
        if not line: # Empty line dataset
            if use_sentence_split:
                if bioes:
                    current_paragraph_tags = convert_bio_to_bioes(current_paragraph_tags)
                all_tags.update(current_paragraph_tags)
    
                # Add sentence separator
                current_paragraph_tags.append("") 
                current_paragraph_words.append("") 
    
                tags.append([x for x in zip(current_paragraph_words, current_paragraph_tags)])
                current_paragraph_tags = []
                current_paragraph_words = []
            else:
                # Add sentence separator
                current_paragraph_tags.append("") 
                current_paragraph_words.append("") 
            continue

        word, annotation = line.split("\t")

        if len(word) >= 3 and word[-3] == "_": # word with _LN tag
            word = word[:-3]

        all_words.add(word)
        all_chars.update(word)

        tag = meta_tags_separator.join(annotation.split(meta_tags_separator)[:meta_tags_level+1])
        current_paragraph_tags.append(tag)
        current_paragraph_words.append(word)
    if current_paragraph_words:
        if bioes:
            current_paragraph_tags = convert_bio_to_bioes(current_paragraph_tags, (i, line, data))
        all_tags.update(current_paragraph_tags) 
        tags.append([x for x in zip(current_paragraph_words, current_paragraph_tags)])
    return tags

def convert_bio_to_bioes(bio_tags: list, trace_info=None):
    bioes_tags = []
    current_entity_tags = []
    for full_tag in bio_tags:
        if not full_tag:
            bioes_tags.append("")
            continue
        
        tag = full_tag[0]
        meta = full_tag[1:]
        if tag == "O":
            if len(current_entity_tags) == 0:
                bioes_tags.append("O" + meta) # Empty current entity and outside
            elif len(current_entity_tags) == 1:
                last_meta = current_entity_tags[-1][1:]
                bioes_tags.append("S" + last_meta) # Single tag entity and outside
                bioes_tags.append("O" + meta) # Add current tag
                current_entity_tags.clear()
            else:
                last_meta = current_entity_tags[-1][1:]
                current_entity_tags[-1] = "E" + last_meta # Multiple tag entity and outside
                bioes_tags.extend(current_entity_tags) # Add all entity tags
                bioes_tags.append("O" + meta) # Add current tag
                current_entity_tags.clear()
        elif tag == "B":
            if len(current_entity_tags) == 0:
                current_entity_tags.append("B" + meta) # Empty current entity and begin a new one
            elif len(current_entity_tags) == 1:
                last_meta = current_entity_tags[-1][1:]
                bioes_tags.append("S" + last_meta) # Sinlge tag entity and begining
                current_entity_tags.clear()
                current_entity_tags.append("B" + meta) # New current entity
            else:
                last_meta = current_entity_tags[-1][1:]
                current_entity_tags[-1] = "E" + last_meta # Multiple tag entity and begin
                bioes_tags.extend(current_entity_tags) # Add all entity tags
                current_entity_tags.clear()
                current_entity_tags.append("B" + meta) # New current entity
        elif tag == "I":
            if len(current_entity_tags) == 0:
                error_msg = "Invalid BIO format, I tag can be at the begining of a segment."
                if trace_info:
                    error_msg += f"\n{trace_info}"
                raise Exception(error_msg)
            else:
                current_entity_tags.append("I" + meta) # Continue the entity
        else:
            error_msg = f"Unsupported {tag} in BIO tagset."
            if trace_info:
                error_msg += f"\n{trace_info}"
            raise Exception(error_msg)

    if len(current_entity_tags) == 1: # Residual tags
        meta = current_entity_tags[0][1:]
        bioes_tags.append("S" + meta) # Single tag entity and outside
    elif len(current_entity_tags) > 1:
        meta = current_entity_tags[-1][1:]
        current_entity_tags[-1] = "E" + meta # Multiple tag entity and outside
        bioes_tags.extend(current_entity_tags)
  
    return bioes_tags

def export(conll_file: Path, dest_sentence_file: Path, dest_tag_file: Path, dest_pos_file: Path, all_words: set, all_tags: set, all_chars: set, all_pos: set, language: str="english", meta_tags_level=99, meta_tags_separator="-", use_sentence_split=True, use_nltk=True, spacy_pos=True):
    """
    Creates from `conll_file` three files, `dest_sentence_file`, 
    `dest_tag_file` and `dest_pos_file`, containing the sentences splitted by `nltk` 
    , its corresponding tags and the POS tags respectively. In each file the tokens
    are separated with a blank space.
    
    conll_file: Original conll file
    dest_sentence_file: File containing the sentences.
    dest_tag_file: File containing the tags.
    dest_pos_file: File containing the POS tags.
    with_meta_tags: If the output should conserve the meta tags
    use_sentence_split: If the empty lines should be analyzed as sentence separators
    spacy_pos: If use Spacy for POS annotation, if false NLTK will be used.
    """
    
    conll_paragraph_tuples = convert_to_tuples(conll_file, all_words, all_tags, all_chars, meta_tags_level=meta_tags_level, meta_tags_separator=meta_tags_separator, use_sentence_split=use_sentence_split)

    dest_sentence_content = []
    dest_tag_content = []
    current_sentence = []
    current_tags = []
    token_transforms = {
        "``": ['"', "''"],
        "''": '"'
    }
    for sentence_tuples in conll_paragraph_tuples:
        current_sentence = [word for word, _ in sentence_tuples]
        current_tags = [tag for _, tag in sentence_tuples if tag]
        
        if use_nltk:
            sentences = nltk.sent_tokenize(" ".join(current_sentence), language=language)
        else:
            sentences = " ".join(current_sentence).split("  ")
        
        current_sentence = [word for word, _ in sentence_tuples if word]
        
        current_tag_index = 0
        current_word_index = 0
        for sent in sentences:
            current_word: str = current_sentence[current_word_index]
            current_tag: str = current_tags[current_tag_index]
            if use_nltk:
                toks = nltk.word_tokenize(sent, language=language)
            else:
                toks = sent.split()
            dest_sentence_content.append([])
            dest_tag_content.append([])
            for j, tok in enumerate(toks, 1):
                if not current_word.startswith(tok):
                    temp_toks = token_transforms.get(tok, [])
                    if not any(current_word.startswith(temp_tok) for temp_tok in temp_toks):
                        # Add exceptions here
                        start_exceptions = {
                            '"': ["´´", "``"],
                        }
                        if not (current_word in start_exceptions and \
                            tok in start_exceptions[current_word]):
                            assert False
                    else:
                        tok = [temp_tok for temp_tok in temp_toks if current_word.startswith(temp_tok)][0]
                        
                current_word = current_word[len(tok):]
                dest_sentence_content[-1].append(tok)
                dest_tag_content[-1].append(current_tag)
                if not current_word:
                    current_word_index += 1
                    current_tag_index += 1
                    if j < len(toks):
                        current_word = current_sentence[current_word_index]
                        current_tag = current_tags[current_tag_index]
        
        assert current_tag_index == len(current_tags)
        assert current_word_index == len(current_sentence)
        assert current_tag_index == current_word_index
        current_sentence.clear()
        current_tags.clear()
    
    text = "\n".join(" ".join(sentence) for sentence in dest_sentence_content)
    export_pos(dest_sentence_content, dest_pos_file, all_pos, language, spacy_pos)
    dest_sentence_file.write_text(text)
    dest_tag_file.write_text("\n".join(" ".join(tags) for tags in dest_tag_content))

def export_vocabs(base_path: Path, all_words: set, all_chars: set, all_tags: set, all_pos: set, language: str):
    
    with (base_path / f'{language}_vocab.words.txt').open('w') as f:
        for w in sorted(all_words):
            if w:
                f.write(f'{w}\n')
    with (base_path / f'{language}_vocab.chars.txt').open('w') as f:
        for w in sorted(all_chars):
            if w:
                f.write(f'{w}\n')
    with (base_path / f'{language}_vocab.tags.txt').open('w') as f:
        for w in sorted(all_tags):
            if w:
                f.write(f'{w}\n')
    with (base_path / f'{language}_vocab.pos.txt').open('w') as f:
        for w in sorted(all_pos):
            if w:
                f.write(f'{w}\n')

def export_from_directory(source_directory: Path, dest_sent_file: Path, dest_tag_file: Path, dest_pos_file: Path, all_words: set, all_tags: set, all_chars: set, all_pos: set, language: str="english", meta_tags_level=99, meta_tags_separator="-", spacy_pos=True):
    temp_sent_file = Path("tempsentence16916312639")
    temp_tag_file = Path("temptag16916312639")
    temp_pos_file = Path("temppos16916312639")
    temp_sent_file.touch()
    temp_tag_file.touch()
    temp_pos_file.touch()
    
    dest_sent_file.touch()
    dest_tag_file.touch()
    dest_pos_file.touch()
    try:
        with dest_sent_file.open("w") as dest_sent, dest_tag_file.open("w") as dest_tag, dest_pos_file.open("w") as dest_pos:
            for file in source_directory.iterdir():
                if file.suffix == ".conll":
                    export(file, temp_sent_file, temp_tag_file, temp_pos_file, all_words, all_tags, all_chars, all_pos, language, meta_tags_level, meta_tags_separator, use_sentence_split=False, use_nltk=False, spacy_pos=spacy_pos)
                    dest_sent.write(temp_sent_file.read_text().replace("\n", " "))
                    dest_tag.write(temp_tag_file.read_text().replace("\n", " "))
                    dest_pos.write(temp_pos_file.read_text().replace("\n", " "))
                    dest_sent.write("\n")
                    dest_tag.write("\n")
                    dest_pos.write("\n")
    finally:
        temp_sent_file.unlink()
        temp_tag_file.unlink()
        temp_pos_file.unlink()

def export_pos(sentences: List[List[str]], dest_pos_file: Path, all_pos: set, language: str, with_spacy=True):
    """
    Export the POS tags from `content` into `dest_pos_file`.
    Each sententce will be in a independent line
    
    sentences: Text to extract the POS tags
    dest_pos_file: File to save the POS tags
    """
    dest_pos_file.touch(exist_ok=True)
    
    if with_spacy:
        pos_tagger = SpacyPOSTagger()
    else:
        pos_tagger = NLTKPOSTagger()

    sentences = pos_tagger.pos_tags_sents(sentences, language)
    pos_text = "\n".join(" ".join(x for x in sentence) for sentence in sentences)
    all_pos.update(pos for sentence in pos_text.splitlines() for pos in sentence.split())
    dest_pos_file.write_text(pos_text)

def export_files(data_dir: Path, dest_dir: Path, language: str, meta_tags_level: int, meta_tag_separator="-", spacy_pos=True):
    """
    Creates a dataset for the files in `data_dir`, this directory must contain 3 .conll
    annotated files called train, dev and test. The separation between samples is an 
    empty line. The data is saved in `dest_dir`
    
    data_dir: Data's directory
    dest_dir: Directory to save the proccessed data
    language: Language of the data
    meta_tags_level: Level of annotation to get: 0: BIOES, 1: BIOES-OtherTag, 2: BIOES-Tag1-Tag2, ...
    meta_tag_separator: Conll annotation separator 
    spacy_pos: If use Spacy for POS annotation, if false NLTK will be used.
    """

    all_words = set()
    all_tags = set()
    all_chars = set()
    all_pos = set()

    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Train Block
    train_file = data_dir / "train.conll"
    train_dest_sent_file = dest_dir / f"{language}_train.words.txt"
    train_dest_tag_file = dest_dir / f"{language}_train.tags.txt"
    train_dest_pos_file = dest_dir / f"{language}_train.pos.txt"
    export(train_file, train_dest_sent_file, train_dest_tag_file, train_dest_pos_file, all_words, all_tags, all_pos, all_chars, language, meta_tags_level, meta_tag_separator, use_sentence_split=True, use_nltk=False, spacy_pos=spacy_pos)

    # Test Block
    testa_file = data_dir / "test.conll"
    testa_dest_sent_file = dest_dir / f"{language}_testa.words.txt"
    testa_dest_tag_file = dest_dir / f"{language}_testa.tags.txt"
    testa_dest_pos_file = dest_dir / f"{language}_testa.pos.txt"
    export(testa_file, testa_dest_sent_file, testa_dest_tag_file, testa_dest_pos_file, all_words, all_tags, all_pos, all_chars, language, meta_tags_level, meta_tag_separator, use_sentence_split=True, use_nltk=False, spacy_pos=spacy_pos)

    # Validation Block
    testb_file = data_dir / "dev.conll"
    testb_dest_sent_file = dest_dir / f"{language}_testb.words.txt"
    testb_dest_tag_file = dest_dir / f"{language}_testb.tags.txt"
    testb_dest_pos_file = dest_dir / f"{language}_testb.pos.txt"
    export(testb_file, testb_dest_sent_file, testb_dest_tag_file, testb_dest_pos_file, all_words, all_tags, all_pos, all_chars, language, meta_tags_level, meta_tag_separator, use_sentence_split=True, use_nltk=False, spacy_pos=spacy_pos)

    # Export vocabularies
    export_vocabs(dest_dir, all_words, all_chars, all_tags, language)

def export_directory(data_dir: Path, dest_dir: Path, language: str, meta_tags_level: int, meta_tag_separator="-", only_train=True, spacy_pos=True):
    """
    Creates a dataset for the files in `data_dir`, this directory must contain 3 directories
    train, dev and test with .conll annotated files. The data is saved in `dest_dir`
    
    data_dir: Data's directory
    dest_dir: Directory to save the proccessed data
    language: Language of the data
    meta_tags_level: Level of annotation to get: 0: BIOES, 1: BIOES-OtherTag, 2: BIOES-Tag1-Tag2, ...
    meta_tag_separator: Conll annotation separator 
    only_train: If only the train file will be used to export the words, chars and tags files. Prevents information leaking
    spacy_pos: If use Spacy for POS annotation, if false NLTK will be used.
    """
    
    all_words = set()
    all_tags = set()
    all_chars = set()
    all_pos = set()
    
    dest_dir.mkdir(parents=True, exist_ok=True)

    testb_sent_file = dest_dir / f"{language}_testb.words.txt"
    testb_tag_file = dest_dir / f"{language}_testb.tags.txt"
    testb_pos_file = dest_dir / f"{language}_testb.pos.txt"
    export_from_directory(data_dir / "dev", testb_sent_file, testb_tag_file, testb_pos_file, all_words, all_tags, all_chars, all_pos, language, meta_tags_level, meta_tag_separator, spacy_pos=spacy_pos)
    
    testa_sent_file = dest_dir / f"{language}_testa.words.txt"
    testa_tag_file = dest_dir / f"{language}_testa.tags.txt"
    testa_pos_file = dest_dir / f"{language}_testa.pos.txt"
    export_from_directory(data_dir / "test", testa_sent_file, testa_tag_file, testa_pos_file, all_words, all_tags, all_chars, all_pos, language, meta_tags_level, meta_tag_separator, spacy_pos=spacy_pos)

    if only_train:
        all_words = set()
        all_tags = set()
        all_chars = set()

    train_sent_file = dest_dir / f"{language}_train.words.txt"
    train_tag_file = dest_dir / f"{language}_train.tags.txt"
    train_pos_file = dest_dir / f"{language}_train.pos.txt"
    export_from_directory(data_dir / "train", train_sent_file, train_tag_file, train_pos_file, all_words, all_tags, all_chars, all_pos, language, meta_tags_level, meta_tag_separator, spacy_pos=spacy_pos)

    # Export vocabularies
    export_vocabs(dest_dir, all_words, all_chars, all_tags, all_pos, language)

if __name__ == "__main__":

    data_dir = Path(__file__, "..", "..", "..", "data").resolve()
    data_dir = data_dir / "parsed_to_conll" / "persuasive_essays_paragraph"
    
    dest_dir = Path(__file__, "..", "data", "english_paragraph").resolve()
    
    language = "english"
    meta_tags_level = 1
    meta_tag_separator = "-"
    
    export_directory(data_dir, dest_dir, language, meta_tags_level, meta_tag_separator, spacy_pos=False)
    

    # data_dir = Path(__file__, "..", "..", "..", "data").resolve()
    # data_dir = data_dir / "corpus" / "Org_PE_english"

    # dest_dir = Path(__file__, "..", "data", "test_data").resolve()

    # language = "english"
    # meta_tags_level = 1
    # meta_tag_separator = "-"
    
    # export_files(data_dir, dest_dir, language, meta_tags_level, meta_tag_separator)


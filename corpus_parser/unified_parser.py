import json
from corpus_parser.cdcp_parser import CDCPParser
import re
from corpus_parser.brat_parser import BratParser
from corpus_parser.conll_parser import ConllParser
import logging
from pathlib import Path
from typing import Dict, Iterable, Optional

from .parser import AnnotatedRawTextInfo, ArgumentationInfo, Parser


class UnifiedParser(Parser):
    """
    Automatically selects te propper way to parse a file.
    The selection can be manual by setting the selected_parser property or
    automatic by parsing a file.
    """
    
    
    def __init__(self, accepted_files: Iterable[str] = (".conll", ".ann", ".ann.json"), **kwargs) -> None:
        super().__init__(accepted_files, suffix=None)
        self.conll_parser = ConllParser(**kwargs)
        self.brat_parser = BratParser(**kwargs)
        self.cdcp_parser = CDCPParser(**kwargs)
        self.selected_parser = None
    
    def __get_parser(self, content: str, file: Optional[Path] = None) -> Parser:
        """
        Return the parser to parse the given content
        """
        if file is not None:
            if file.suffix == ".conll":
                return self.conll_parser
            if file.suffix == ".ann":
                return self.brat_parser
            if file.name.endswith(".ann.json"):
                return self.cdcp_parser
            raise Exception(f"Couldn't guess parser for file {file}")
        line = content.splitlines()[0]
        if self.brat_parser.argumentative_unit_regex.match(line) \
            or self.brat_parser.relation_regex.match(line):
            return self.brat_parser
        if self.conll_parser.annotation_regex.match(line):
            return self.conll_parser
        try:
            json.loads(content)
            return self.cdcp_parser
        except:
            pass
        raise Exception(f"Couldn't guess parser for line {line}")
        
    def parse(self, content: str, file: Optional[Path] = None, **kwargs) -> ArgumentationInfo:
        """
        Parse `content` returning DataFrames containing
        the argumentative unit and the relation information.
        
        content: text containing the content to parse
        file: Content's original file
        
        argumentative_units columns: 
          - `prop_id` Proposition ID inside the document
          - `prop_type` Proposition type
          - `prop_init` When the proposition starts in the original text
          - `prop_end` When the proposition ends in the original text
          - `prop_text` Proposition text
          
        relations columns:
          - `relation_id` Relation ID inside the document
          - `relation_type` Relation type
          - `prop_id_source` Relation's source proposition id 
          - `prop_id_target` Relation's target proposition id
          
        non_argumentative_units columns:
          - `prop_init` When the proposition starts in the original text
          - `prop_end` When the proposition ends in the original text
          - `prop_text` Proposition text
          
        return: (argumentative_units, relations, non_argumentative_units)
        """
        if not self.selected_parser:
            self.selected_parser = self.__get_parser(content, file)
        return self.selected_parser.parse(content, file=file, **kwargs)

    def from_dataframes(self, dataframes: Dict[str, ArgumentationInfo], language="english", **kwargs) -> Dict[str, AnnotatedRawTextInfo]:
        """
        Creates a Brat annotated corpus representing the received DataFrames. 
        
        dataframes: The result from calling a parse function in any Parser class
        the keys aren't important, so a mock key can be passed.
        language: Language for tokenization process
        
        returns: Brat annotated string, Raw text
        """
        if not self.selected_parser:
            raise Exception("No parser has been selected. Parse a file or set selected_parser field to a Parser")
        return self.selected_parser.from_dataframes(dataframes, language, **kwargs)
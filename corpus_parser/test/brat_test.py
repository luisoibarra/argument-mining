import sys
from pathlib import Path

sys.path.append(str((Path(__file__)/".."/".."/"..").resolve()))


from corpus_parser.brat_parser import BratParser


def test_parse():
    base = Path(__file__) / ".." / "test_data" / "test_brat"
    base = base.resolve()

    parser = BratParser()
    result = parser.parse_dir(base)
    result1, result2, result3 = next(x for x in result.values())


def test_from_dataframe():
    base = Path(__file__) / ".." / "test_data" / "test_brat"
    base = base.resolve()

    parser = BratParser()
    result = parser.parse_dir(base)
    result2 = parser.from_dataframes(result)
    key = next(iter(result2.keys()))
    result3 = parser.parse(result2[key][0], file=Path(key))

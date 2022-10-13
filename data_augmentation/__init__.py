from pathlib import Path
import sys

path = str(Path(__file__, "..", ".."))

if path not in sys.path:
    sys.path.append(path)

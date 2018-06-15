from polyglot_detector import PolyglotLevel, scan
from polyglot_detector.magic import magic_scan


class AnalysisEntry:
    def __init__(self, type: str, level: PolyglotLevel, found_by_magic: bool, was_embedded: bool=False):
        self.type = type
        self.level = level
        self.found_by_magic = found_by_magic
        self.was_embedded = was_embedded


class Analysis:
    """Represent the analysis result of a file"""
    def __init__(self, filename, path):
        self.filename = filename
        self.scan_results = scan(path, use_magic=True)
        self.results = []
        magic_scan_results = magic_scan(path)

        for type, level in self.scan_results.items():
            level_without_embedded = level & ~PolyglotLevel.EMBED
            for embedded_type in level.embedded:
                self.results.append(AnalysisEntry(embedded_type, level_without_embedded, embedded_type in magic_scan_results))
            self.results.append(AnalysisEntry(type, level_without_embedded, type in magic_scan_results))
        self.results.sort(key=lambda entry: entry.type)

    def __iter__(self):
        return self.results.__iter__()

    @property
    def is_suspicious(self):
        return any(entry.level != PolyglotLevel.VALID for entry in self.results)

    @property
    def is_dangerous(self):
        return len(self.results) > 1

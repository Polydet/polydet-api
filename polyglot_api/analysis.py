import logging
import re
import os
import subprocess
import time

from polydet import PolyglotLevel, scan
from polydet.magic import magic_scan

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AnalysisEntry:
    def __init__(self, ext: str, level: PolyglotLevel):
        self.ext = ext
        self.level = level


class Analysis:
    """Represent the analysis result of a file"""
    def __init__(self, filename, path):
        self.filename = filename
        start_time = time.time()
        self.scan_results = scan(path, use_magic=True)
        self.elapsed_time = time.time() - start_time
        self.results = []

        self.magic_scan_results = magic_scan(path)
        self.trid_scan_results = trid_scan(path)

        for type, level in self.scan_results.items():
            level_without_embedded = PolyglotLevel(is_valid=level.is_valid, suspicious_chunks=level.suspicious_chunks)
            for embedded_type in level.embedded:
                self.results.append(AnalysisEntry(embedded_type, level_without_embedded))
            self.results.append(AnalysisEntry(type, level))
        self.results.sort(key=lambda entry: entry.ext)

    def __iter__(self):
        return self.results.__iter__()

    @property
    def is_suspicious(self):
        return any(entry.level != PolyglotLevel() for entry in self.results)

    @property
    def is_dangerous(self):
        return len(self.results) > 1


TRID_RESULT_RE = re.compile('^\s*(\d+\.\d+)% \(\.([^)]+)\) ')


def trid_scan(path: str) -> {str: float}:
    output = subprocess.check_output(['trid', '-n:5', path],
                                     env={'PATH': os.getenv('PATH'), 'LC_ALL': 'C.UTF-8'})
    output = output.decode('ascii')
    result_lines = output.split('\n')[6:]
    results = {}
    for line in result_lines:
        result = parse_trid_output(line)
        if result is None:
            break
        percentage, ext = result
        results[ext] = results.get(ext, 0.0) + percentage
    logger.debug('TRiD results: %s' % results)
    return results


def parse_trid_output(line: str) -> (float, str):
    matches = TRID_RESULT_RE.match(line)
    if not matches:
        return None
    percentage, ext = float(matches.group(1)), matches.group(2).lower()
    # TODO Find better way to avoid this sort of case. Maybe use mime ?
    if ext == 'tif/tiff':
        ext = 'tiff'
    return percentage, ext

from pydriller.domain.commit import Modification
from typing import List, Dict, Tuple


class MethodMetrics():

    def __init__(self, source: str, src_start: int, src_stop: int):
        self.source = source
        self.src_start = src_start
        self.src_stop = src_stop

    def get_method_source(self) -> str:
        src_lines = self.source.split('\n')
        return '\n'.join(src_lines[self.src_start - 1:self.src_stop])

    def get_number_of_lines(self):
        return len(self.source.split('\n'))

    def get_add_lines(self, lines: Dict[str, List[Tuple[int, str]]]):
        count = 0
        added = lines['added']
        for a_line, a_text in added:
            if self.src_start <= a_line <= self.src_stop:
                count += 1
        return count

    def get_removed_lines(self, lines: Dict[str, List[Tuple[int, str]]]):
        count = 0
        deleted = lines['deleted']
        for a_line, a_text in deleted:
            if self.src_start <= a_line <= self.src_stop:
                count += 1
        return count


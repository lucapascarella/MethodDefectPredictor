from typing import List, Dict, Tuple


class MethodMetrics():

    def __init__(self, source: str, src_start: int, src_stop: int, lines: Dict[str, List[Tuple[int, str]]], buggy: bool):
        self.source = source
        self.src_start = src_start
        self.src_stop = src_stop
        self.lines = lines
        self.buggy = buggy

    def get_method_source(self) -> str:
        src_lines = self.source.split('\n')
        return '\n'.join(src_lines[self.src_start - 1:self.src_stop])

    def get_number_of_lines(self) -> int:
        return len(self.source.split('\n'))

    def is_touched(self):
        added = self.lines['added']
        deleted = self.lines['deleted']
        for a_line, a_text in added:
            if self.src_start <= a_line <= self.src_stop:
                return True
        for d_line, d_text in deleted:
            if self.src_start <= d_line <= self.src_stop:
                return True
        return False

    def is_buggy(self):
        if self.buggy and self.is_touched():
            return True
        return False

    def get_added_lines(self) -> int:
        count = 0
        added = self.lines['added']
        for a_line, a_text in added:
            if self.src_start <= a_line <= self.src_stop:
                count += 1
        return count

    def get_removed_lines(self) -> int:
        count = 0
        deleted = self.lines['deleted']
        for a_line, a_text in deleted:
            if self.src_start <= a_line <= self.src_stop:
                count += 1
        return count

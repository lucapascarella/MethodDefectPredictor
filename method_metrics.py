from typing import List, Dict, Tuple
import datetime

class MethodMetrics():

    def __init__(self, source: str, src_start: int, src_stop: int, lines: Dict[str, List[Tuple[int, str]]], buggy: bool, fix: bool):
        self.source = source
        self.src_start = src_start
        self.src_stop = src_stop
        self.lines = lines
        self.buggy = buggy
        self.fix = fix

    def get_method_source(self) -> str:
        src_lines = self.source.split('\n')
        return '\n'.join(src_lines[self.src_start - 1:self.src_stop])

    def get_number_of_lines(self) -> int:
        return len(self.source.split('\n'))

    def is_touched(self) -> bool:
        added = self.lines['added']
        deleted = self.lines['deleted']
        for a_line, a_text in added:
            if self.src_start <= a_line <= self.src_stop:
                return True
        for d_line, d_text in deleted:
            if self.src_start <= d_line <= self.src_stop:
                return True
        return False

    def is_buggy(self) -> bool:
        if self.buggy and self.is_touched():
            return True
        return False

    def is_fix(self) -> bool:
        if self.fix and self.is_touched():
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


class MetricsBean:
    def __init__(self, git_hash: str, git_committer_date: datetime, file_name: str, method_name: str, method_start_line: int, change_type: str,
                 file_count: int, file_added: int, file_removed: int, file_nloc: int, file_comp: int, file_token_count: int,
                 method_count: int, method_added: int, method_removed: int, method_nlco: int, method_comp: int, method_token: int,
                 file_buggy: bool, file_fix: bool,
                 method_number_of_lines: int, method_fan_in: int, method_fan_out: int, method_general_fan_out: int, method_parameters_count: int,
                 author_email: str,
                 method_touched: bool, method_fix: bool, method_buggy: bool):
        self.git_hash = git_hash
        self.git_committer_date = git_committer_date
        self.file_name = file_name
        self.method_name = method_name
        self.method_start_line = method_start_line
        self.change_type = change_type

        self.file_count = file_count
        self.file_added = file_added
        self.file_removed = file_removed
        self.file_nloc = file_nloc
        self.file_comp = file_comp
        self.file_token_count = file_token_count
        self.file_buggy = file_buggy
        self.file_fix = file_fix

        self.method_count = method_count
        self.method_added = method_added
        self.method_removed = method_removed
        self.method_nloc = method_nlco
        self.method_comp = method_comp
        self.method_token = method_token

        self.method_number_of_lines = method_number_of_lines
        self.method_fan_in = method_fan_in
        self.method_fan_out = method_fan_out
        self.method_general_fan_out = method_general_fan_out
        self.method_parameters_count = method_parameters_count

        self.author_email = author_email
        self.method_touched = method_touched
        self.method_fix = method_fix
        self.method_buggy = method_buggy

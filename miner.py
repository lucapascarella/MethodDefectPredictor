import os
from typing import List, Dict, Set
from pydriller import RepositoryMining, GitRepository
from pydriller.domain.commit import ModificationType

from method_metrics import MethodMetrics, MetricsBean
from saver import Saver


class Miner:
    def __init__(self, repo_path: str, allowed_extensions: List[str], csv_path: str, bic_commits: Set[str] = [str], fix_commits: Set[str] = [str]):
        if repo_path is None:
            print('A local repository path must be specified')
            exit(-1)
        elif os.path.isdir(repo_path):
            self.repo_path = repo_path
            self.csv_file = csv_path
            self.allowed_extensions = allowed_extensions
            self.bic_commits = bic_commits
            self.fix_commits = fix_commits
        else:
            print('The following path does not exist: ' + repo_path)
            exit(-1)

    def mine_methods(self, start_commit: str, stop_commit: str, filter_methods: Set[str] = None, filter_files: Set[str] = None) -> int:
        methods = {}  # Dict[str, List[MinerBean]]
        commits_to_analyze = -1
        print('Mining: ' + self.repo_path)
        gr = GitRepository(self.repo_path)

        # Redefine start and stop commits
        print('Adjust start and stop commits.')
        first_commit = start_commit
        if start_commit is None:
            first_commit = gr.get_head().hash
        last_commit = stop_commit

        # Print start and stop commits info
        c1 = gr.get_commit(first_commit)
        print('Start: {} Author date: {} Committer date: {}'.format(c1.hash, c1.author_date, c1.committer_date))
        c2 = gr.get_commit(last_commit)
        print('Stop:  {} Author date: {} Committer date: {}'.format(c2.hash, c2.author_date, c2.committer_date))

        # Unnecessary in production
        # # Count commits to analyze
        # print('Retrieve commits to analyze.')
        # commits = []
        # for commit in RepositoryMining(self.repo_path, from_commit=last_commit, to_commit=first_commit, reversed_order=True).traverse_commits():
        #     commits.append(commit)
        #     print('{}) {} {}'.format(len(commits), commit.hash, commit.author_date))
        # commits_to_analyze = len(commits)

        # Open CSV file and write header
        saver = Saver(self.csv_file)
        saver.create_csv_file()
        saver.print_csv_header()

        # Traverse commits and calculate metrics
        commit_count = 0
        # for commit in RepositoryMining(self.repo_path, from_commit=last_commit, to_commit=first_commit, reversed_order=True, only_modifications_with_file_types=self.allowed_extensions).traverse_commits():
        for commit in RepositoryMining(self.repo_path, from_commit=last_commit, to_commit=first_commit, reversed_order=True).traverse_commits():
            buggy = True if commit.hash in self.bic_commits else False
            fix = True if commit.hash in self.fix_commits else False
            mod_analyzed_count = 0
            count_files_per_commit = len(commit.modifications)
            for mod in commit.modifications:
                # Filter out unnecessary files
                if filter_files is None or mod.new_path in filter_files:
                    if mod.filename.endswith(tuple(self.allowed_extensions)):
                        mod_analyzed_count += 1
                        # Update key entry on rename
                        if mod.change_type is ModificationType.RENAME:
                            methods = self.update_keys(methods, mod.new_path, mod.old_path)
                            if filter_files is not None:
                                filter_files.add(mod.old_path)
                        count_methods_per_file = len(mod.methods)
                        for method in mod.methods:
                            key = self.get_unique_key(mod.new_path, mod.old_path, method.name)
                            # For unwanted keys prevent metric calculation
                            if filter_methods is None or key in filter_methods:
                                lines = gr.parse_diff(mod.diff)
                                method_metrics = MethodMetrics(mod.source_code, method.start_line, method.end_line, lines, buggy, fix)
                                m_touched = method_metrics.is_touched()
                                m_fix = method_metrics.is_fix()
                                m_buggy = method_metrics.is_buggy()
                                mb = MetricsBean(commit.hash, commit.author_date, mod.new_path, method.name, method.start_line, mod.change_type.name,
                                                 count_files_per_commit, mod.added, mod.removed, mod.nloc, mod.complexity, mod.token_count,
                                                 count_methods_per_file, method_metrics.get_added_lines(), method_metrics.get_removed_lines(), method.nloc, method.complexity, method.token_count,
                                                 buggy, fix,
                                                 method_metrics.get_number_of_lines(), method.fan_in, method.fan_out, method.general_fan_out, len(method.parameters),
                                                 commit.author.email,
                                                 m_touched, m_fix, m_buggy)
                                # Append new bean
                                if key not in methods:
                                    methods[key] = []
                                methods.get(key, []).append(mb)
                                # Going back in the past ADD is the moment in which the a file, consequently a method, is added therefore it can be removed from the disc and flushed into the CSV to save RAM
                                if mod.change_type is ModificationType.ADD:
                                    self.flush_methods(methods, key, saver)
            commit_count += 1
            print('Methods: {:>8} | Commit {:>6}/{:<6} {} Date: {} Mods: {:>4}/{:<4} | Bug: {} Fix: {}'.format(len(methods), commit_count, commits_to_analyze, commit.hash, commit.author_date.strftime('%d/%m/%Y'),
                                                                                                               len(commit.modifications), mod_analyzed_count, buggy, fix))
        for key, value in methods.items():
            saver.add_method_to_csv(key, value)
        saver.close_csv_file()
        print('Mining ended')
        return commit_count

    def get_unique_key(self, new_path: str, old_path: str, method_name: str) -> str:
        if new_path is not None and new_path is not '':
            key = new_path + '$$' + method_name
        elif old_path is not None and old_path is not '':
            key = old_path + '$$' + method_name
        else:
            key = 'unexpected_key'
        return key

    def update_keys(self, methods: Dict[str, List[MetricsBean]], new_path: str, old_path: str) -> Dict[str, List[MetricsBean]]:
        new_methods = {}
        for key, value in methods.items():
            old_key_path, method_name = key.split('$$')
            if old_key_path == new_path:
                key = old_path + '$$' + method_name
            new_methods[key] = value
        methods.clear()  # Reduce here Python garbage collector pressure
        del methods
        return new_methods

    def flush_methods(self, methods: Dict[str, List[MetricsBean]], key: str, saver: Saver):
        m = methods.pop(key, None)
        if m is not None:
            saver.add_method_to_csv(key, m)
        else:
            print('Unexpected key entry: ' + key)

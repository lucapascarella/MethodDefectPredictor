import datetime, os
import statistics as st
from typing import List, Dict
from pydriller import RepositoryMining, GitRepository
from pydriller.domain.commit import ModificationType
from method_metrics import MethodMetrics


class MinerBean:
    def __init__(self, git_hash: str, git_commiter_date: datetime, file_name: str, method_name: str, change_type: ModificationType,
                 file_count: int, file_added: int, file_removed: int, file_nloc: int, file_comp: int, file_token_count: int,
                 method_count: int, method_added: int, method_removed: int, method_nlco: int, method_comp: int, method_token: int,
                 file_buggy: bool,
                 method_number_of_lines: int, method_fan_in: int, method_fan_out: int, method_general_fan_out: int, method_parameters_count: int,
                 author_email: str,
                 method_touched: bool, method_buggy: bool):
        self.git_hash = git_hash
        self.git_commiter_date = git_commiter_date
        self.file_name = file_name
        self.method_name = method_name
        self.change_type = change_type

        self.file_count = file_count
        self.file_added = file_added
        self.file_removed = file_removed
        self.file_nloc = file_nloc
        self.file_comp = file_comp
        self.file_token_count = file_token_count
        self.file_buggy = file_buggy

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
        self.method_buggy = method_buggy


class MinerGit:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def count_commits(self, recent_commit: str, oldest_commit: str) -> int:
        cmd = 'git -C ' + self.repo_path + ' rev-list ' + recent_commit + ' ^' + oldest_commit + ' --count'
        ret = os.popen(cmd).read()
        if ret.strip().isdigit():
            return int(ret)
        return 0


class Miner:
    def __init__(self, repo_path: str, allowed_extensions: List[str], bic_commits: List[str] = [str]):
        if repo_path is None:
            print('A local repository path must be specified')
            exit(0)
        elif os.path.isdir(repo_path):
            self.repo_path = repo_path
            self.allowed_extensions = allowed_extensions
            self.bic_commits = bic_commits
        else:
            print('The following path does not exist: ' + repo_path)
            exit(0)

    def mine_methods(self, start_commit: str, stop_commit: str, filter_methods: List[str] = [str]) -> Dict[str, List[MinerBean]]:
        methods = {}
        first_commit = start_commit
        if start_commit is None:
            first_commit = GitRepository(self.repo_path).get_head().hash
        commit_count = MinerGit(self.repo_path).count_commits(first_commit, stop_commit)

        count = 0
        print('Mining: ' + self.repo_path)
        gr = GitRepository(self.repo_path)
        for commit in RepositoryMining(self.repo_path, from_commit=stop_commit, to_commit=start_commit, reversed_order=True, only_modifications_with_file_types=self.allowed_extensions).traverse_commits():
            print('{:06}/{:06}) Commit: {} Date: {} Mods: {:}'.format(count, commit_count, commit.hash, commit.author_date.strftime('%d/%m/%Y'), len(commit.modifications)))
            for mod in commit.modifications:
                if mod.filename.endswith(tuple(self.allowed_extensions)):
                    # print('{:06}/{:06}) Commit: {} Date: {} Type: {:6} File: {}'.format(count, commit_count, commit.hash, commit.author_date.strftime('%d/%m/%Y'), mod.change_type.name, mod.filename))
                    if mod.change_type is ModificationType.RENAME:
                        new_methods = {}
                        for key, value in methods.items():
                            old_path, method = key.split('$$')
                            if old_path == mod.new_path:
                                key = mod.old_path + '$$' + method
                            new_methods[key] = value
                        methods = new_methods
                    # if mod.change_type is not ModificationType.DELETE:
                    for method in mod.methods:
                        buggy = True if commit.hash in self.bic_commits else False
                        lines = gr.parse_diff(mod.diff)
                        method_metrics = MethodMetrics(mod.source_code, method.start_line, method.end_line, lines, buggy)
                        m_touched = method_metrics.is_touched()
                        m_buggy = method_metrics.is_buggy()
                        mb = MinerBean(commit.hash, commit.author_date, mod.new_path, method.name, mod.change_type,
                                       len(commit.modifications), mod.added, mod.removed, mod.nloc, mod.complexity, mod.token_count,
                                       len(mod.methods), method_metrics.get_added_lines(), method_metrics.get_removed_lines(), method.nloc, method.complexity, method.token_count,
                                       buggy,
                                       method_metrics.get_number_of_lines(), method.fan_in, method.fan_out, method.general_fan_out, len(method.parameters),
                                       commit.author.email,
                                       m_touched, m_buggy
                                       )
                        key = mod.new_path + '$$' + method.name

                        if key not in filter_methods: # Filter methods is no longer needed
                            if key not in methods:
                                methods[key] = []
                            methods.get(key, []).append(mb)
            count += 1
        print('Mining ended')
        return methods

    def get_touched_methods_per_commit(self, commit_hash: str) -> List[str]:
        methods = []
        # gr = GitRepository(self.repo_path)
        # commit = gr.get_commit(commit_hash)
        # for mod in commit.modifications:
        #     if mod.change_type is not ModificationType.DELETE:
        #         for method in mod.methods:
        #             method_metrics = MethodMetrics(mod.source_code, method.start_line, method.end_line)
        #             lines = gr.parse_diff(mod.diff)
        #             added = method_metrics.get_added_lines(lines)
        #             removed = method_metrics.get_removed_lines(lines)
        #             if added > 0 or removed > 0:
        #                 method_key = mod.new_path + '$$' + method.name
        #                 methods.append(method_key)
        return methods

    def print_metrics_per_method(self, csv_path: str, methods: Dict[str, List[MinerBean]]):
        print('Saving ' + str(len(methods)) + ' methods')
        output = open(csv_path, 'w')

        header = 'key,git_hash,file_name,method_name,file_rename_count,method_rename_count,change_type_count,' \
                 'file_count_last,file_count_max, file_count_mean, file_count_sum,' \
                 'file_added_last, file_added_max, file_added_mean, file_added_sum,' \
                 'file_removed_last, file_removed_max, file_removed_mean, file_removed_sum,' \
                 'file_nloc_last, file_nloc_max, file_nloc_mean, file_nloc_sum,' \
                 'file_comp_last, file_comp_max, file_comp_mean, file_comp_sum,' \
                 'file_token_count_last, file_token_count_max, file_token_count_mean, file_token_count_sum,' \
                 'method_count_last, method_count_max, method_count_mean, method_count_sum,' \
                 'method_added_last, method_added_max, method_added_mean, method_added_sum,' \
                 'method_removed_last, method_removed_max, method_removed_mean, method_removed_sum,' \
                 'method_nloc_last, method_nloc_max, method_nloc_mean, method_nloc_sum,' \
                 'method_comp_last, method_comp_max, method_comp_mean, method_comp_sum,' \
                 'method_token_last, method_token_max, method_token_mean, method_token_sum,' \
                 'method_method_number_of_line_last, method_method_number_of_line_max, method_method_number_of_line_mean, method_method_number_of_line_sum,' \
                 'method_fan_in_last, method_fan_in_max, method_fan_in_mean, method_fan_in_sum,' \
                 'method_fan_out_last, method_fan_out_max, method_fan_out_mean, method_fan_out_sum,' \
                 'method_general_fan_out_last, method_general_fan_out_max, method_general_fan_out_mean, method_general_fan_out_sum,' \
                 'method_parameters_counts_last, method_parameters_counts_max, method_parameters_counts_mean, method_parameters_counts_sum,' \
                 'author_email_mean, author_email_sum,' \
                 'file_buggy,method_bug_sum,method_bug_mean,method_buggy\n'
        output.write(header)

        for key, value in methods.items():
            git_hashs = []
            file_names = []
            method_names = []
            change_types = []
            file_counts = []
            file_addeds = []
            file_removeds = []
            file_nlocs = []
            file_comps = []
            file_token_counts = []
            method_counts = []
            method_addeds = []
            method_removeds = []
            method_nlcos = []
            method_comps = []
            method_tokens = []
            method_number_of_lines = []
            method_fan_ins = []
            method_fan_outs = []
            method_general_fan_outs = []
            method_parameters_counts = []
            author_emails = []
            buggys = []
            touches = []

            # Identifiers
            git_hash = value[0].git_hash
            file_name = value[0].file_name
            file_buggy = value[0].file_buggy
            method_name = value[0].method_name
            method_touched = value[0].method_touched
            method_buggy = value[0].method_buggy

            # List of process metrics
            for n in range(0, len(value)):
                git_hashs.append(value[n].git_hash)
                file_names.append(value[n].file_name)
                method_names.append(value[n].method_name)
                change_types.append(value[n].change_type)
                file_counts.append(value[n].file_count)
                file_addeds.append(value[n].file_added)
                file_removeds.append(value[n].file_removed)
                file_nlocs.append(value[n].file_nloc)
                file_comps.append(value[n].file_comp)
                file_token_counts.append(value[n].file_token_count)
                # Method
                method_counts.append(value[n].method_count)
                method_addeds.append(value[n].method_added)
                method_removeds.append(value[n].method_removed)
                method_nlcos.append(value[n].method_nloc)
                method_comps.append(value[n].method_comp)
                method_tokens.append(value[n].method_token)
                method_number_of_lines.append(value[n].method_number_of_lines)
                method_fan_ins.append(value[n].method_fan_in)
                method_fan_outs.append(value[n].method_fan_out)
                method_general_fan_outs.append(value[n].method_general_fan_out)
                method_parameters_counts.append(value[n].method_parameters_count)
                author_emails.append(value[n].author_email)

                buggys.append(int(value[n].method_buggy))

            # Other process metrics
            file_rename_count = len(set(file_names))
            method_rename_count = len(set(method_names))
            change_type_count = len(set(change_types))

            # File metrics
            file_count_last = value[0].file_count
            file_count_max = max(file_counts)
            file_count_mean = st.mean(file_counts)
            file_count_sum = sum(file_counts)

            file_added_last = value[0].file_added
            file_added_max = max(file_addeds)
            file_added_mean = st.mean(file_addeds)
            file_added_sum = sum(file_addeds)

            file_removed_last = value[0].file_removed
            file_removed_max = max(file_removeds)
            file_removed_mean = st.mean(file_removeds)
            file_removed_sum = sum(file_removeds)

            file_nloc_last = value[0].file_nloc
            file_nloc_max = max(file_nlocs)
            file_nloc_mean = st.mean(file_nlocs)
            file_nloc_sum = sum(file_nlocs)

            file_comp_last = value[0].file_comp
            file_comp_max = max(file_comps)
            file_comp_mean = st.mean(file_comps)
            file_comp_sum = sum(file_comps)

            file_token_count_last = value[0].file_token_count
            file_token_count_max = max(file_token_counts)
            file_token_count_mean = st.mean(file_token_counts)
            file_token_count_sum = sum(file_token_counts)

            # Methods metrics
            method_count_last = value[0].method_count
            method_count_max = max(method_counts)
            method_count_mean = st.mean(method_counts)
            method_count_sum = sum(method_counts)

            method_added_last = value[0].method_added
            method_added_max = max(method_addeds)
            method_added_mean = st.mean(method_addeds)
            method_added_sum = sum(method_addeds)

            method_removed_last = value[0].method_removed
            method_removed_max = max(method_removeds)
            method_removed_mean = st.mean(method_removeds)
            method_removed_sum = sum(method_removeds)

            method_nloc_last = value[0].method_nloc
            method_nloc_max = max(method_nlcos)
            method_nloc_mean = st.mean(method_nlcos)
            method_nloc_sum = sum(method_nlcos)

            method_comp_last = value[0].method_comp
            method_comp_max = max(method_comps)
            method_comp_mean = st.mean(method_comps)
            method_comp_sum = sum(method_comps)

            method_token_last = value[0].method_token
            method_token_max = max(method_tokens)
            method_token_mean = st.mean(method_tokens)
            method_token_sum = sum(method_tokens)

            method_method_number_of_line_last = value[0].method_number_of_lines
            method_method_number_of_line_max = max(method_number_of_lines)
            method_method_number_of_line_mean = st.mean(method_number_of_lines)
            method_method_number_of_line_sum = sum(method_number_of_lines)

            method_fan_in_last = value[0].method_fan_in
            method_fan_in_max = max(method_fan_ins)
            method_fan_in_mean = st.mean(method_fan_ins)
            method_fan_in_sum = sum(method_fan_ins)

            method_fan_out_last = value[0].method_fan_out
            method_fan_out_max = max(method_fan_outs)
            method_fan_out_mean = st.mean(method_fan_outs)
            method_fan_out_sum = sum(method_fan_outs)

            method_general_fan_out_last = value[0].method_general_fan_out
            method_general_fan_out_max = max(method_general_fan_outs)
            method_general_fan_out_mean = st.mean(method_general_fan_outs)
            method_general_fan_out_sum = sum(method_general_fan_outs)

            method_parameters_counts_last = value[0].method_parameters_count
            method_parameters_counts_max = max(method_parameters_counts)
            method_parameters_counts_mean = st.mean(method_parameters_counts)
            method_parameters_counts_sum = sum(method_parameters_counts)

            author_email_last = len(set(author_emails)) / len(value)
            author_email_sum = len(set(author_emails))

            method_buggy_sum = sum(buggys)
            method_buggy_mean = sum(buggys) / len(value)

            # Append process metrics to CSV file
            out_string = '{},{},{},{},{},{},{},' \
            \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
            \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
                         '{},{},{},{},' \
            \
                         '{},{},' \
            \
                         '{},{},{},{}\n'.format(
                key.replace(',', '-comma-'), git_hash, file_name.replace(',', '-comma-'), method_name.replace(',', '-comma-'), file_rename_count, method_rename_count, change_type_count,

                file_count_last, file_count_max, file_count_mean, file_count_sum,
                file_added_last, file_added_max, file_added_mean, file_added_sum,
                file_removed_last, file_removed_max, file_removed_mean, file_removed_sum,
                file_nloc_last, file_nloc_max, file_nloc_mean, file_nloc_sum,
                file_comp_last, file_comp_max, file_comp_mean, file_comp_sum,
                file_token_count_last, file_token_count_max, file_token_count_mean, file_token_count_sum,

                method_count_last, method_count_max, method_count_mean, method_count_sum,
                method_added_last, method_added_max, method_added_mean, method_added_sum,
                method_removed_last, method_removed_max, method_removed_mean, method_removed_sum,
                method_nloc_last, method_nloc_max, method_nloc_mean, method_nloc_sum,
                method_comp_last, method_comp_max, method_comp_mean, method_comp_sum,
                method_token_last, method_token_max, method_token_mean, method_token_sum,
                method_method_number_of_line_last, method_method_number_of_line_max, method_method_number_of_line_mean, method_method_number_of_line_sum,
                method_fan_in_last, method_fan_in_max, method_fan_in_mean, method_fan_in_sum,
                method_fan_out_last, method_fan_out_max, method_fan_out_mean, method_fan_out_sum,
                method_general_fan_out_last, method_general_fan_out_max, method_general_fan_out_mean, method_general_fan_out_sum,
                method_parameters_counts_last, method_parameters_counts_max, method_parameters_counts_mean, method_parameters_counts_sum,

                author_email_last, author_email_sum,

                (1 if file_buggy else 0), method_buggy_sum, method_buggy_mean, (1 if method_buggy else 0))
            output.write(out_string)
            output.flush()
        output.close()
        # print(out_string)

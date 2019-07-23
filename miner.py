import datetime, os
import statistics as st
from typing import List, Dict, Set
from pydriller import RepositoryMining, GitRepository
from pydriller.domain.commit import ModificationType
from method_metrics import MethodMetrics


class MinerBean:
    def __init__(self, git_hash: str, git_commiter_date: datetime, file_name: str, method_name: str, change_type: str,
                 file_count: int, file_added: int, file_removed: int, file_nloc: int, file_comp: int, file_token_count: int,
                 method_count: int, method_added: int, method_removed: int, method_nlco: int, method_comp: int, method_token: int,
                 file_buggy: bool, file_fix: bool,
                 method_number_of_lines: int, method_fan_in: int, method_fan_out: int, method_general_fan_out: int, method_parameters_count: int,
                 author_email: str,
                 method_touched: bool, method_fix: bool, method_buggy: bool):
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

    def mine_methods(self, start_commit: str, stop_commit: str, filter_methods: List[str] = None) -> Dict[str, List[MinerBean]]:
        methods = {}
        first_commit = start_commit
        if start_commit is None:
            first_commit = GitRepository(self.repo_path).get_head().hash
        commit_count = MinerGit(self.repo_path).count_commits(stop_commit, first_commit)

        self.create_csv_file(self.csv_file)
        self.print_csv_header()

        count = 0
        print('Mining: ' + self.repo_path)
        gr = GitRepository(self.repo_path)
        for commit in RepositoryMining(self.repo_path, from_commit=stop_commit, to_commit=first_commit, reversed_order=True, only_modifications_with_file_types=self.allowed_extensions).traverse_commits():
            buggy = True if commit.hash in self.bic_commits else False
            fix = True if commit.hash in self.fix_commits else False
            print('Methods: {:-8} | {:-7}/{:7} | Commit: {} Date: {} Mods: {:4} | Bug/Fix {} {}'.format(len(methods), count, commit_count, commit.hash, commit.author_date.strftime('%d/%m/%Y'), len(commit.modifications),
                                                                                                        buggy, fix))
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

                    for method in mod.methods:
                        if mod.new_path is not None and mod.new_path is not '':
                            key = mod.new_path + '$$' + method.name
                        elif mod.old_path is not None and mod.old_path is not '':
                            key = mod.old_path + '$$' + method.name
                        else:
                            key = 'unexpected_key'

                        # For unwanted keys prevent metric calculation
                        if filter_methods is None or key in filter_methods:
                            lines = gr.parse_diff(mod.diff)
                            method_metrics = MethodMetrics(mod.source_code, method.start_line, method.end_line, lines, buggy, fix)
                            m_touched = method_metrics.is_touched()
                            m_fix = method_metrics.is_fix()
                            m_buggy = method_metrics.is_buggy()
                            mb = MinerBean(commit.hash, commit.author_date, mod.new_path, method.name, mod.change_type.name,
                                           len(commit.modifications), mod.added, mod.removed, mod.nloc, mod.complexity, mod.token_count,
                                           len(mod.methods), method_metrics.get_added_lines(), method_metrics.get_removed_lines(), method.nloc, method.complexity, method.token_count,
                                           buggy, fix,
                                           method_metrics.get_number_of_lines(), method.fan_in, method.fan_out, method.general_fan_out, len(method.parameters),
                                           commit.author.email,
                                           m_touched, m_fix, m_buggy
                                           )

                            if key not in methods:
                                methods[key] = []
                            methods.get(key, []).append(mb)
                            # Going back in the past ADD is the moment in which the a file, consequently a method, is added therefore it can be removed from the disc and flushed into the CSV to save RAM
                            if mod.change_type is ModificationType.ADD:
                                m = methods.pop(key, None)
                                if m is not None:
                                    self.add_method_to_csv(key, m)
                                else:
                                    print('This key is not present into the dict: ' + key)
            count += 1
        for key, value in methods.items():
            self.add_method_to_csv(key, value)
        self.close_csv_file()
        print('Mining ended')
        return methods

    def create_csv_file(self, csv_path: str):
        self.out_file = open(csv_path, 'w')

    def print_csv_header(self):
        header = 'key,git_hash,file_name,method_name,file_rename_count,method_rename_count,change_type_count,' \
                 'file_count_last,file_count_max,file_count_mean,file_count_sum,' \
                 'file_added_last,file_added_max,file_added_mean,file_added_sum,' \
                 'file_removed_last,file_removed_max,file_removed_mean,file_removed_sum,' \
                 'file_nloc_last,file_nloc_max,file_nloc_mean,file_nloc_sum,' \
                 'file_comp_last,file_comp_max,file_comp_mean,file_comp_sum,' \
                 'file_token_count_last,file_token_count_max,file_token_count_mean, file_token_count_sum,' \
                 'method_count_last,method_count_max,method_count_mean,method_count_sum,' \
                 'method_added_last,method_added_max,method_added_mean,method_added_sum,' \
                 'method_removed_last,method_removed_max,method_removed_mean,method_removed_sum,' \
                 'method_nloc_last,method_nloc_max,method_nloc_mean,method_nloc_sum,' \
                 'method_comp_last,method_comp_max,method_comp_mean,method_comp_sum,' \
                 'method_token_last,method_token_max,method_token_mean,method_token_sum,' \
                 'method_method_number_of_line_last,method_method_number_of_line_max,method_method_number_of_line_mean,method_method_number_of_line_sum,' \
                 'method_fan_in_last,method_fan_in_max,method_fan_in_mean,method_fan_in_sum,' \
                 'method_fan_out_last,method_fan_out_max,method_fan_out_mean,method_fan_out_sum,' \
                 'method_general_fan_out_last,method_general_fan_out_max,method_general_fan_out_mean,method_general_fan_out_sum,' \
                 'method_parameters_counts_last,method_parameters_counts_max,method_parameters_counts_mean,method_parameters_counts_sum,' \
                 'author_email_mean,author_email_sum,' \
                 'method_touched_sum,method_touched_mean,method_fixes_sum,method_fixes_mean,'\
                 'file_buggy,file_fix,method_bug_sum,method_bug_mean,method_fix,method_buggy\n'
        self.out_file.write(header)

    def add_method_to_csv(self, key: str, method: List[MinerBean]):

        # git_hashs = []
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
        touches = []
        fixes = []
        buggys = []

        # Identifiers
        git_hash = method[0].git_hash
        file_name = method[0].file_name
        file_buggy = method[0].file_buggy
        file_fix = method[0].file_fix
        method_name = method[0].method_name
        method_touched = method[0].method_touched
        method_fix = method[0].method_fix
        method_buggy = method[0].method_buggy

        # List of process metrics
        for n in range(0, len(method)):
            # git_hashs.append(method[n].git_hash)
            file_names.append(method[n].file_name)
            method_names.append(method[n].method_name)
            change_types.append(method[n].change_type)
            file_counts.append(method[n].file_count)
            file_addeds.append(method[n].file_added)
            file_removeds.append(method[n].file_removed)
            file_nlocs.append(method[n].file_nloc)
            file_comps.append(method[n].file_comp)
            file_token_counts.append(method[n].file_token_count)
            # Method
            method_counts.append(method[n].method_count)
            method_addeds.append(method[n].method_added)
            method_removeds.append(method[n].method_removed)
            method_nlcos.append(method[n].method_nloc)
            method_comps.append(method[n].method_comp)
            method_tokens.append(method[n].method_token)
            method_number_of_lines.append(method[n].method_number_of_lines)
            method_fan_ins.append(method[n].method_fan_in)
            method_fan_outs.append(method[n].method_fan_out)
            method_general_fan_outs.append(method[n].method_general_fan_out)
            method_parameters_counts.append(method[n].method_parameters_count)
            author_emails.append(method[n].author_email)

            touches.append(int(method[n].method_touched))
            fixes.append(int(method[n].method_fix))
            buggys.append(int(method[n].method_buggy))

        # Other process metrics
        file_rename_count = len(set(file_names))
        method_rename_count = len(set(method_names))
        change_type_count = len(set(change_types))

        # File metrics
        file_count_last = method[0].file_count
        file_count_max = max(file_counts)
        file_count_mean = st.mean(file_counts)
        file_count_sum = sum(file_counts)

        file_added_last = method[0].file_added
        file_added_max = max(file_addeds)
        file_added_mean = st.mean(file_addeds)
        file_added_sum = sum(file_addeds)

        file_removed_last = method[0].file_removed
        file_removed_max = max(file_removeds)
        file_removed_mean = st.mean(file_removeds)
        file_removed_sum = sum(file_removeds)

        file_nloc_last = method[0].file_nloc
        file_nloc_max = max(file_nlocs)
        file_nloc_mean = st.mean(file_nlocs)
        file_nloc_sum = sum(file_nlocs)

        file_comp_last = method[0].file_comp
        file_comp_max = max(file_comps)
        file_comp_mean = st.mean(file_comps)
        file_comp_sum = sum(file_comps)

        file_token_count_last = method[0].file_token_count
        file_token_count_max = max(file_token_counts)
        file_token_count_mean = st.mean(file_token_counts)
        file_token_count_sum = sum(file_token_counts)

        # Methods metrics
        method_count_last = method[0].method_count
        method_count_max = max(method_counts)
        method_count_mean = st.mean(method_counts)
        method_count_sum = sum(method_counts)

        method_added_last = method[0].method_added
        method_added_max = max(method_addeds)
        method_added_mean = st.mean(method_addeds)
        method_added_sum = sum(method_addeds)

        method_removed_last = method[0].method_removed
        method_removed_max = max(method_removeds)
        method_removed_mean = st.mean(method_removeds)
        method_removed_sum = sum(method_removeds)

        method_nloc_last = method[0].method_nloc
        method_nloc_max = max(method_nlcos)
        method_nloc_mean = st.mean(method_nlcos)
        method_nloc_sum = sum(method_nlcos)

        method_comp_last = method[0].method_comp
        method_comp_max = max(method_comps)
        method_comp_mean = st.mean(method_comps)
        method_comp_sum = sum(method_comps)

        method_token_last = method[0].method_token
        method_token_max = max(method_tokens)
        method_token_mean = st.mean(method_tokens)
        method_token_sum = sum(method_tokens)

        method_method_number_of_line_last = method[0].method_number_of_lines
        method_method_number_of_line_max = max(method_number_of_lines)
        method_method_number_of_line_mean = st.mean(method_number_of_lines)
        method_method_number_of_line_sum = sum(method_number_of_lines)

        method_fan_in_last = method[0].method_fan_in
        method_fan_in_max = max(method_fan_ins)
        method_fan_in_mean = st.mean(method_fan_ins)
        method_fan_in_sum = sum(method_fan_ins)

        method_fan_out_last = method[0].method_fan_out
        method_fan_out_max = max(method_fan_outs)
        method_fan_out_mean = st.mean(method_fan_outs)
        method_fan_out_sum = sum(method_fan_outs)

        method_general_fan_out_last = method[0].method_general_fan_out
        method_general_fan_out_max = max(method_general_fan_outs)
        method_general_fan_out_mean = st.mean(method_general_fan_outs)
        method_general_fan_out_sum = sum(method_general_fan_outs)

        method_parameters_counts_last = method[0].method_parameters_count
        method_parameters_counts_max = max(method_parameters_counts)
        method_parameters_counts_mean = st.mean(method_parameters_counts)
        method_parameters_counts_sum = sum(method_parameters_counts)

        author_email_last = len(set(author_emails)) / len(method)
        author_email_sum = len(set(author_emails))

        # method_touched_last  = touches[0]
        method_touched_sum = sum(touches)
        method_touched_mean = sum(touches) / len(method)

        method_fixes_sum = sum(fixes)
        method_fixes_mean = sum(fixes) / len(method)

        method_buggy_sum = sum(buggys)
        method_buggy_mean = sum(buggys) / len(method)

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
                     '{},{},{},{},' \
 \
                     '{},{},{},{},{},{}\n'.format(
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
            method_touched_sum, method_touched_mean, method_fixes_sum, method_fixes_mean,

            (1 if file_buggy else 0), (1 if file_fix else 0), method_buggy_sum, method_buggy_mean, (1 if method_fix else 0), (1 if method_buggy else 0))
        self.out_file.write(out_string)
        self.out_file.flush()

    def close_csv_file(self):
        self.out_file.flush()
        self.out_file.close()

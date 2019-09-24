import statistics as st
from typing import List

from method_metrics import MetricsBean


class Saver:

    def __init__(self, filename: str):
        self.filename = filename

    def create_csv_file(self):
        self.out_file = open(self.filename, 'w')

    def print_csv_header(self):
        header = 'key,git_hash,file_name,method_name,method_start_line,file_rename_count,method_rename_count,change_type_count,' \
 \
                 'file_count_last,file_count_max,file_count_mean,file_count_sum,' \
                 'file_added_last,file_added_max,file_added_mean,file_added_sum,' \
                 'file_removed_last,file_removed_max,file_removed_mean,file_removed_sum,' \
                 'file_nloc_last,file_nloc_max,file_nloc_mean,file_nloc_sum,' \
                 'file_comp_last,file_comp_max,file_comp_mean,file_comp_sum,' \
                 'file_token_count_last,file_token_count_max,file_token_count_mean,file_token_count_sum,' \
 \
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
 \
                 'author_email_mean,author_email_sum,' \
                 'method_touched_sum,method_touched_mean,method_fixes_sum,method_fixes_mean,' \
 \
                 'file_buggy,file_fix,method_bug_sum,method_bug_mean,method_fix,method_buggy\n'
        # print('Header count: {}'.format(header.count(',')))
        self.out_file.write(header)

    def add_method_to_csv(self, key: str, method: List[MetricsBean]):

        # git_hashs = []
        file_names = []
        method_names = []
        method_start_lines = []
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
        method_start_line = method[0].method_start_line
        method_touched = method[0].method_touched
        method_fix = method[0].method_fix
        method_buggy = method[0].method_buggy

        # List of process metrics
        for n in range(0, len(method)):
            start_time = method[n].git_committer_date
            stop_time = method[len(method) - 1].git_committer_date
            diff_time = abs(start_time - stop_time)
            if diff_time.total_seconds() < 10368000:  # Reduce analysis to 4 Months only
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
            else:
                print("Discarded!!!!")

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

        author_email_last = len(set(author_emails)) / len(author_emails)
        author_email_sum = len(set(author_emails))

        method_touched_last = touches[0]
        method_touched_sum = sum(touches)
        method_touched_mean = sum(touches) / len(touches)

        method_fixes_sum = sum(fixes)
        method_fixes_mean = sum(fixes) / len(fixes)

        method_buggy_sum = sum(buggys)
        method_buggy_mean = sum(buggys) / len(buggys)

        # Append process metrics to CSV file
        out_string = '{},{},{},{},{},{},{},{},' \
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
            key.replace(',', '-comma-'), git_hash, file_name.replace(',', '-comma-'), method_name.replace(',', '-comma-'), method_start_line, file_rename_count, method_rename_count, change_type_count,

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

        # print('Line count: {}'.format(out_string.count(',')))
        self.out_file.write(out_string)
        self.out_file.flush()

    def close_csv_file(self):
        self.out_file.flush()
        self.out_file.close()

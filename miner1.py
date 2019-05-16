import csv

from pydriller import RepositoryMining, GitRepository
from pydriller.domain.commit import ModificationType
from method_metrics import MethodMetrics

repo = '/Users/luca/PycharmProjects/BIMFinder/test-repos/test-repo-C++'
stop_commit = start_commit = None


# repo = '/Users/luca/TUProjects/Mozilla/gecko-dev'
# stop_commit = '5192e340815e9aad5a59b350b9772319e4518417'  # Excluded
# start_commit = '49dbdb7f535106aa96e952222fd42ea6b91074fb'  # Excluded


def get_bic_commits():
    bic_commits = []
    bics = csv.DictReader(open('/Users/luca/TUProjects/Mozilla/bic_commit_results.csv', 'r', newline='', encoding="utf-8"), delimiter=',')
    for bic in bics:
        bic_commits.append(bic['bic_commit'])
    return bic_commits


def print_metrics_per_method(methods):
    output = open('output.csv', 'w')
    output.write('hash,key,file,method,changes,'
                 'file_count,max_file_count,avg_file_count,added,max_added,avg_added,'
                 'removed,max_removed,avg_removed,'
                 'loc,max_loc,avg_loc,'
                 'complexity,max_complexity,avg_complexity,'
                 'token_count,max_token_count,avg_token_count,'
                 'methods,max_methods,avg_methods,'
                 'm_token,max_m_token,avg_m_token,'
                 'm_fan_in,m_fan_out,m_g_fan_out,'
                 'm_loc,max_m_loc,avg_m_loc,'
                 'm_length,max_m_length,avg_m_length,'
                 'm_comp,max_m_comp,avg_m_comp,'
                 'm_param_count,max_m_param_count,avg_m_param_count,'
                 'm_added,max_m_added,avg_m_added,'
                 'm_removed,max_m_removed,avg_m_removed,'
                 'authors,'
                 'bug_count,buggy\n'.format())

    for key, value in methods.items():
        n_changes = len(value)
        hash = value[0]['hash']
        file = value[0]['file']
        method = value[0]['method']

        file_count = value[0]['file_count']
        max_file_count = max(x['file_count'] for x in value)
        avg_file_count = float(sum(x['file_count'] for x in value)) / n_changes

        added = value[0]['added']
        max_added = max(x['added'] for x in value)
        avg_added = float(sum(x['added'] for x in value)) / n_changes
        removed = value[0]['removed']
        max_removed = max(x['removed'] for x in value)
        avg_removed = float(sum(x['removed'] for x in value)) / n_changes
        loc = value[0]['loc']
        max_loc = max(x['loc'] for x in value)
        avg_loc = float(sum(x['loc'] for x in value)) / n_changes
        token_count = value[0]['token_count']
        max_token_count = max(x['token_count'] for x in value)
        avg_token_count = float(sum(x['token_count'] for x in value)) / n_changes
        methods = value[0]['methods']
        max_methods = max(x['methods'] for x in value)
        avg_methods = float(sum(x['methods'] for x in value)) / n_changes
        comp = value[0]['comp']
        max_comp = max(x['comp'] for x in value)
        avg_comp = float(sum(x['comp'] for x in value)) / n_changes

        m_token = value[0]['m_token']
        max_m_token = max(x['m_token'] for x in value)
        avg_m_token = float(sum(x['m_token'] for x in value)) / n_changes
        m_fan_in = value[0]['m_fan_in']
        m_fan_out = value[0]['m_fan_out']
        m_g_fan_out = value[0]['m_g_fan_out']
        m_loc = value[0]['m_loc']
        max_m_loc = max(x['m_loc'] for x in value)
        avg_m_loc = float(sum(x['m_loc'] for x in value)) / n_changes
        m_length = value[0]['m_length']
        max_m_length = max(x['m_length'] for x in value)
        avg_m_length = float(sum(x['m_length'] for x in value)) / n_changes
        m_comp = value[0]['m_comp']
        max_m_comp = max(x['m_comp'] for x in value)
        avg_m_comp = float(sum(x['m_comp'] for x in value)) / n_changes

        m_param_count = len(value[0]['m_param_count'])
        max_m_param_count = max(len(x['m_param_count']) for x in value)
        avg_m_param_count = float(sum(len(x['m_param_count']) for x in value)) / n_changes
        m_added = value[0]['m_added']
        max_m_added = max(x['m_added'] for x in value)
        avg_m_added = float(sum(x['m_added'] for x in value)) / n_changes
        m_removed= value[0]['m_removed']
        max_m_removed = max(x['m_removed'] for x in value)
        avg_m_removed = float(sum(x['m_removed'] for x in value)) / n_changes

        author_number = len(set(x['author_email'] for x in value))
        bug_count = sum(x['buggy'] for x in value)
        buggy = value[0]['buggy']
        # Append process metrics to CSV file
        out_string = '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(
            hash, key, file, method, n_changes,
            file_count, max_file_count, avg_file_count,

            added, max_added, avg_added,
            removed, max_removed, avg_removed,
            loc, max_loc, avg_loc,
            comp, max_comp, avg_comp,
            token_count, max_token_count, avg_token_count,
            methods, max_methods, avg_methods,

            m_token, max_m_token, avg_m_token,
            m_fan_in, m_fan_out, m_g_fan_out,
            m_loc, max_m_loc, avg_m_loc,
            m_length, max_m_length, avg_m_length,
            m_comp, max_m_comp, avg_m_comp,
            m_param_count, max_m_param_count, avg_m_param_count,
            m_added, max_m_added, avg_m_added,
            m_removed, max_m_removed, avg_m_removed,
            author_number,
            bug_count, buggy)
        output.write(out_string)
        # print(out_string)


def calculate_metrics_per_method(bic_commits):
    methods = {}
    gr = GitRepository(repo)
    for commit in RepositoryMining(repo, from_commit=start_commit, to_commit=stop_commit, reversed_order=True, only_modifications_with_file_types='.cpp').traverse_commits():
        for mod in commit.modifications:
            print('Commit: ' + commit.hash + ' mod type: ' + str(mod.change_type))
            if mod.change_type is ModificationType.RENAME:
                new_methods = {}
                for key, value in methods.items():
                    old_path, method = key.split('$$')
                    if old_path == mod.new_path:
                        key = mod.old_path + '$$' + method
                    new_methods[key] = value
                methods = new_methods
            if mod.change_type is not ModificationType.DELETE:
                for method in mod.methods:
                    buggy = True if commit.hash in bic_commits else False
                    lines = gr.parse_diff(mod.diff)  # From PyDriller
                    method_metrics = MethodMetrics(mod.source_code, method.start_line, method.end_line)
                    process_metrics = {'hash': commit.hash, 'file': mod.new_path, 'method': method.name, 'change': mod.change_type,
                                       'file_count': len(commit.modifications), 'added': mod.added, 'removed': mod.removed,
                                       'loc': mod.nloc, 'comp': mod.complexity, 'token_count': mod.token_count, 'methods': len(mod.methods),
                                       'm_token': method.token_count, 'm_fan_in': method.fan_in, 'm_fan_out': method.fan_out, 'm_g_fan_out': method.general_fan_out,
                                       'm_loc': method.nloc, 'm_comp': method.complexity, 'm_length': method.length, 'm_param_count': method.parameters,
                                       'source': method_metrics.get_method_source(), 'm_lines': method_metrics.get_number_of_lines(), 'm_added': method_metrics.get_add_lines(lines),'m_removed': method_metrics.get_removed_lines(lines),
                                       'author_email': commit.committer.email,
                                       'buggy': buggy}
                    key = mod.new_path + '$$' + method.name
                    if key not in methods:
                        methods[key] = []
                    methods.get(key, []).append(process_metrics)
    return methods


# Main
bic_commits = get_bic_commits()
methods = calculate_metrics_per_method(bic_commits)
print_metrics_per_method(methods)

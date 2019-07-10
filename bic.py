import argparse, csv
import os

from pydriller import GitRepository


def get_method_count(modifications):
    count = 0
    for mod in modifications:
        count += len(mod.methods)
    return count


def get_bic_count(bic_mods):
    count = 0
    for mod, bics in bic_mods.items():
        count += len(bics)
    return count


# Main
if __name__ == '__main__':
    print("*** BIC started ***\n")
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', type=str, help='Local absolute or relative path to a valid GIT repository.', default=None)
    parser.add_argument('-i', '--input', type=str, help='A CSV file that contains a list of commit fixes, the fix must be identified with a valid HASH belonging to the -r or --repo otion', default='data/fix_commits.csv')
    parser.add_argument('-n', '--notuse', type=str, help='Absolute path of a text file that contains a list of commits, one per line, to ignore', default=None)  # 'data/ignore_commits.txt'
    parser.add_argument('-d', '--delimiter', type=str, help='The CSV delimiter', default=',')
    parser.add_argument('-f', '--fix', type=str, help='The name of the column in the input CSV file used to identify the GIT HASH of a fix commit.', default='git_hash')
    parser.add_argument('-o', '--output', type=str, help='A CSV file where save bug inducing commits found with SZZ algorithm.', default='data/bic_commits.csv')
    args, unknown = parser.parse_known_args()

    # Check that a valid repos is specified
    if args.repo is None or not os.path.isdir(args.repo):
        print('A valid path to a local GIT repository must be specified!')
        exit(-1)
    # Check that a valid input is specified
    if not os.path.isfile(args.input):
        print('A valid path to an input (CSV file) must be given as input!')
        exit(-1)
    # Check that a valid ignore file is specified
    if args.notuse is not None:
        if not os.path.isfile(args.notuse):
            print('A valid path to a input text must be given as input!')
            exit(-1)

    # Read the column names of the input file
    input_file = open(args.input, 'r', encoding="utf-8")
    header = input_file.readline()
    input_columns = header.strip().split(args.delimiter)

    # Prepare the column names for the output file
    header = input_columns + ['git_timestamp', 'git_modifications', 'git_methods', 'bic_count', 'bic_commit', 'bic_timestamp', 'bic_modifications', 'bic_methods']
    out_file = open(args.output, 'w', newline='', encoding="utf-8")
    writer = csv.DictWriter(out_file, delimiter=args.delimiter, fieldnames=header)
    writer.writeheader()

    # Perform Git blame to retrieve the list of BIC commits
    gr = GitRepository(args.repo)
    fixes = csv.DictReader(open(args.input, 'r', newline='', encoding="utf-8"), delimiter=args.delimiter)
    count = 0
    for fix in fixes:
        git_hash = fix['git_hash']
        print('{}) Processing {} '.format(count, git_hash))
        fix_commit = gr.get_commit(git_hash)
        if args.notuse:
            bic_mods = gr.get_commits_last_modified_lines(fix_commit, hashes_to_ignore_path=args.notuse)
        else:
            bic_mods = gr.get_commits_last_modified_lines(fix_commit)
        print('{}) {} has {} MOD, {} BIC'.format(count, git_hash, len(bic_mods), get_bic_count(bic_mods)))

        dout = {'git_timestamp': fix_commit.committer_date,
                'git_modifications': len(fix_commit.modifications),
                'git_methods': get_method_count(fix_commit.modifications),
                'bic_count': len(bic_mods)}
        # Append the ancillary data contained in the input file
        for ic in input_columns:
            dout[ic] = fix[ic]

        for mod, bic_commit_hashs in bic_mods.items():
            for bic_commit_hash in bic_commit_hashs:
                bic_commit = gr.get_commit(bic_commit_hash)
                dout['bic_commit'] = bic_commit_hash
                dout['bic_timestamp'] = bic_commit.committer_date
                dout['bic_modifications'] = len(bic_commit.modifications)
                dout['bic_methods'] = get_method_count(bic_commit.modifications)
                writer.writerow(dout)
        count += 1
        out_file.flush()
    out_file.close()

    print("\n*** BIC ended ***")

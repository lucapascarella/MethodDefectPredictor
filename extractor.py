import argparse, csv, os
from typing import Set

from miner import Miner


def get_bic_commits(bic_path: str, column_name: str) -> Set[str]:
    bic_commits = []
    if bic_path is not None:
        print('Collecting BIC from: ' + bic_path)
        if os.path.isfile(bic_path):
            for bic in csv.DictReader(open(bic_path, 'r', newline='', encoding="utf-8"), delimiter=','):
                bic_commits.append(bic[column_name])
        else:
            print('The following path does not exist: ' + bic_path)
    print('Found {} bug inducing commits ({} unique BIC)\n'.format(len(bic_commits), len(set(bic_commits))))
    return set(bic_commits)


def get_fix_commits(fix_path: str, column_name: str) -> Set[str]:
    fix_commits = []
    if fix_path is not None:
        print('Collecting FIX from: ' + fix_path)
        if os.path.isfile(fix_path):
            for fix in csv.DictReader(open(fix_path, 'r', newline='', encoding="utf-8"), delimiter=','):
                fix_commits.append(fix[column_name])
        else:
            print('The following path does not exist: ' + fix_path)
    print('Found {} fix commits ({} unique FIX)\n'.format(len(fix_commits), len(set(fix_commits))))
    return set(fix_commits)


# Main
# Extractor is a tool designed for extracting both product and process metrics at method level from a GIT repository
if __name__ == '__main__':
    print("*** Extractor started ***\n")
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', type=str, help='Local absolute or relative path to a valid GIT repository.', default=None)
    parser.add_argument('-s', '--start', type=str, help='The start commit represents the latest commit in chronological order. If not specified, it starts from the most recent commit in the repository.', default=None)
    parser.add_argument('-p', '--stop', type=str, help='The stop commit represents the oldest commit in chronological order. If not specified, it stops with the first commit in the repository.', default=None)
    parser.add_argument('-e', '--ext', type=str, help='List of allowed extensions. Eg. .cpp .c', default='.cpp')
    parser.add_argument('-b', '--bic', type=str, help='Path of the CSV file containing the list of bug inducing commits', default=None)
    parser.add_argument('-f', '--fix', type=str, help='Path of the CSV file containing the list of bug inducing commits', default=None)
    parser.add_argument('-bn', '--bic_name', type=str, help='The name of the column in the input CSV file used to identify the GIT HASH of a bic commit.', default='bic_commit')
    parser.add_argument('-fn', '--fix_name', type=str, help='The name of the column in the input CSV file used to identify the GIT HASH of a bic commit.', default='git_hash')
    parser.add_argument('-o', '--output', type=str, help='Path of the CSV file where to save results.', default='data/method_metrics_geko-dev-2.csv')
    args, unknown = parser.parse_known_args()

    # Check that a valid repos is specified
    if args.repo is None or not os.path.isdir(args.repo):
        print('A valid path to a GIT repository must be specified!')
        exit(-1)

    bic_commits = get_bic_commits(args.bic, args.bic_name)
    fix_commits = get_fix_commits(args.fix, args.fix_name)
    miner = Miner(args.repo, args.ext, args.output, bic_commits, fix_commits)
    miner.mine_methods(args.start, args.stop)
    print("\n*** Extractor ended ***")

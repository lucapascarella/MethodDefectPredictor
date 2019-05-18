import argparse, csv, os
from typing import List
from miner import Miner


def get_bic_commits(bic_path: str) -> List:
    bic_commits = []
    if bic_path is not None:
        print('Collect BIC from: ' + bic_path)
        if os.path.isfile(bic_path):
            for bic in csv.DictReader(open(bic_path, 'r', newline='', encoding="utf-8"), delimiter=','):
                bic_commits.append(bic['bic_commit'])
        else:
            print('The following path does not exist: ' + bic_path)
    print('Found ' + str(len(bic_commits)) + ' bug inducing commits\n')
    return bic_commits


# Main
if __name__ == '__main__':
    print("*** Extractor started ***\n")
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', type=str, help='Local absolute or relative path to a valid GIT repository.', default=None)
    parser.add_argument('-s', '--start', type=str, help='Start HASH commit, if not specified it starts from latest commit.', default=None)  # '49dbdb7f535106aa96e952222fd42ea6b91074fb'  # Excluded
    parser.add_argument('-p', '--stop', type=str, help='Stop HASH commit, if not specified it analyzes up to the end.', default=None)  # '5192e340815e9aad5a59b350b9772319e4518417'  # Excluded
    parser.add_argument('-e', '--ext', type=str, help='List of allowed extensions. Eg. .cpp .c', default='.cpp')
    parser.add_argument('-i', '--input', type=str, help='Path of the CSV file containing the list of bug inducing commits', default=None)
    parser.add_argument('-b', '--bic', type=str, help='The name of the column in the input CSV file used to identify the GIT HASH of a bic commit.', default='git_bic')
    parser.add_argument('-o', '--output', type=str, help='Path of the CSV file where to save results.', default='data/method_metrics.csv')
    args, unknown = parser.parse_known_args()

    # Check that a valid repos is specified
    if args.repo is None or not os.path.isdir(args.repo):
        print('A valid path to a GIT repository must be specified!')
        exit(-1)

    bic_commits = get_bic_commits(args.bic)
    miner = Miner(args.repo, args.ext, bic_commits)
    methods = miner.get_methods(args.start, args.stop)
    miner.print_metrics_per_method(args.output, methods)
    print("\n*** Extractor ended ***")

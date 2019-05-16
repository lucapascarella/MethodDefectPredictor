import argparse, os
from pydriller import GitRepository
from pydriller.domain.commit import ModificationType
from miner import Miner

# Main
if __name__ == '__main__':
    print("*** Tester started ***\n")

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', type=str, help='Absolute GIT repository path', default='/Users/luca/PycharmProjects/BIMFinder/test-repos/test-repo-C++')
    parser.add_argument('-e', '--ext', type=str, help='List of allowed extensions. Eg. .cpp .c', default='.cpp')
    parser.add_argument('-c', '--commit', type=str, help='Commit HASH to analyze', default=None)
    args, unknown = parser.parse_known_args()

    commit_hash = args.commit
    if commit_hash is not None:
        miner = Miner(args.repo, args.ext)
        methods = miner.get_methods_per_commit(args.commit)
        print(args.commit + ' changed ' + str(len(methods)) + ' methods')

    else:
        print('A commit HASH must be passes as input argument!')

    print("\n*** Tester ended ***")

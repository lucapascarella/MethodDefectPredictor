import argparse, os
from pydriller import GitRepository
from pydriller.domain.commit import ModificationType
from miner import Miner
from tensorflow import keras

# Main
if __name__ == '__main__':
    print("*** Tester started ***\n")

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', type=str, help='Absolute GIT repository path', default='/Users/luca/PycharmProjects/BIMFinder/test-repos/test-repo-C++')
    parser.add_argument('-e', '--ext', type=str, help='List of allowed extensions. Eg. .cpp .c', default='.cpp')
    # parser.add_argument('-c', '--commit', type=str, help='Commit HASH to analyze', default=None)
    parser.add_argument('-c', '--commit', type=str, help='Commit HASH to analyze', default='89bc0cc12332ebc8359547c6ebf72fea5a65a74f')
    parser.add_argument('-p', '--stop', type=str, help='Stop HASH commit, if not specified it analyzes up to the end.', default=None)
    parser.add_argument('-o', '--output', type=str, help='Path of the CSV file where to save results.', default='testing_output.csv')
    parser.add_argument('-m', '--model', type=str, help='Path of the machine learning model.', default='model.h5')
    args, unknown = parser.parse_known_args()

    commit_hash = args.commit
    if commit_hash is None:
        print('A commit HASH must be passes as input argument!')
        exit(-1)
    model_path = args.model
    if not os.path.isfile(model_path):
        print('A valid trained model must be passed ad input argument!')
        exit(-1)

    miner = Miner(args.repo, args.ext)
    methods = miner.get_touched_methods_per_commit(args.commit)
    print(args.commit + ' has changed ' + str(len(methods)) + ' methods')
    metrics = miner.get_methods(args.commit, args.stop, methods)
    miner.print_metrics_per_method(args.output, metrics)
    print('Found metrics for ' + str(len(metrics)) + ' methods')

    print('Load trained model: ' + model_path)
    model = keras.models.load_model('my_model.h5')
    model.summary()

    print("\n*** Tester ended ***")

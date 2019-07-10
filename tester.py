import argparse, os, numpy
import csv

from pydriller import GitRepository
from pydriller.domain.commit import ModificationType
from miner import Miner
from tensorflow import keras


def skipper(fname, header=False):
    with open(fname) as fin:
        no_comments = (line for line in fin if not line.lstrip().startswith('#'))
        if header:
            next(no_comments, None)  # skip header
        for row in no_comments:
            yield row


# Main
if __name__ == '__main__':
    print("*** Tester started ***\n")

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', type=str, help='Absolute GIT repository path', default=None)
    parser.add_argument('-e', '--ext', type=str, help='List of allowed extensions. Eg. .cpp .c', default='.cpp')
    parser.add_argument('-s', '--start', type=str, help='Commit HASH to analyze', default='a32b3797428598d02798384a6f657d90d17821f7')
    parser.add_argument('-p', '--stop', type=str, help='Stop HASH commit, if not specified it analyzes up to the end.', default='33af9598d8e98940f3942bbd7db2dec1e4526a50')
    parser.add_argument('-o', '--output', type=str, help='Path of the CSV file where to save results.', default='data/testing_output.csv')
    parser.add_argument('-m', '--model', type=str, help='Path of the machine learning model.', default='data/model.h5')
    args, unknown = parser.parse_known_args()

    temp_csv = 'temp.csv'

    if args.start is None or args.stop is None:
        print('A pair of commit HASHs must be passed as input!')
        exit(-1)
    if not os.path.isfile(args.model):
        print('A valid trained model must be passed ad input argument!')
        exit(-1)

    miner = Miner(args.repo, args.ext)
    # # methods = miner.get_touched_methods_per_commit(args.commit)
    # # print(args.commit + ' has changed ' + str(len(methods)) + ' methods')
    metrics = miner.mine_methods(args.start, args.stop)
    miner.print_metrics_per_method(temp_csv, metrics)
    print('Found metrics for ' + str(len(metrics)) + ' methods')

    print('Load trained model: ' + args.model)
    model = keras.models.load_model(args.model)
    model.summary()

    # Count columns to split dataset
    fin = open(temp_csv)
    columns = fin.readline().split(",")
    count = len(columns)
    fin.close()

    # Read CSV file that contains headers
    dataset = numpy.loadtxt(skipper(temp_csv, True), delimiter=",", usecols=(range(4, count - 4)))
    # split into input (X) and output (Y) variables
    x = dataset[:, :]

    y_pred = model.predict(x)
    y_pred = (y_pred > 0.5)

    # Read CSV file
    with open(temp_csv, mode='r') as infile:
        with open(args.output, mode='w') as outfile:
            header = infile.readline() + ',' + 'Prediction\n'
            outfile.write(header)
            i = 0
            lines = infile.readlines()
            for line in lines:
                columns = line.split(',')
                if y_pred[i]:
                    print('Commit: {} File: {} Method: {} Is: {}'.format(columns[1], columns[2], columns[3], y_pred[i]))
                outfile.write('{},{}'.format(line, ('TRUE' if y_pred[i] else 'FALSE')))
                i += 1

    print("\n*** Tester ended ***")

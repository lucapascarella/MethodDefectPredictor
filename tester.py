import argparse, os, numpy

from sklearn.preprocessing import StandardScaler
from miner import Miner
from sklearn.externals import joblib
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
    parser.add_argument('-s', '--start', type=str, help='Commit HASH to analyze', default='db6ecd1b6eb514cc5bf327d101d5cf861dd73926')
    parser.add_argument('-p', '--stop', type=str, help='Stop HASH commit, if not specified it analyzes up to the end.', default='11fbfb6d5381726bbc55472bbf0b816d9859ee79')
    parser.add_argument('-o', '--output', type=str, help='Path of the CSV file where to save results.', default='data/testing_output.csv')
    parser.add_argument('-m', '--model', type=str, help='Path of the machine learning model.', default='data/model.h5')
    args, unknown = parser.parse_known_args()

    temp1_csv = 'temp1.csv'
    temp2_csv = 'temp2.csv'

    if args.start is None or args.stop is None:
        print('A pair of commit HASHs must be passed as input!')
        exit(-1)
    if not os.path.isfile(args.model):
        print('A valid trained model must be passed ad input argument!')
        exit(-1)

    # Get method's metrics
    miner = Miner(args.repo, args.ext, temp1_csv)
    metrics = miner.mine_methods(args.stop, args.start)

    # Count the number of columns into which split dataset and filter out other commits
    fin = open(temp1_csv, mode='r')
    header = fin.readline()
    fout = open(temp2_csv, mode='w')
    fout.write(header)
    lines = fin.readlines()
    for line in lines:
        cols = line.split(',')
        # Exclude other commits and not touched methods
        if cols[1] == args.start: # and cols[77] == '1':
            fout.write(line)
    fin.close()
    fout.close()

    fin = open(temp2_csv, mode='r')
    count = len(fin.readline().split(','))
    fin.close()

    # Read the CSV file that contains fresh mined metrics
    dataset = numpy.loadtxt(skipper(temp2_csv, True), delimiter=",", usecols=(range(4, count - 4)))
    # split into input (X) and output (Y) variables
    x = dataset[:, :]
    # Standardizing the input feature
    sc = StandardScaler()
    x = sc.fit_transform(x)

    # Load TensorFlow pre-trained model and perform a prediction
    print('Load trained model: ' + args.model)
    # model = keras.models.load_model(args.model)
    # model.summary()
    model = joblib.load(args.model)
    y_pred = model.predict(x)
    y_pred = (y_pred > 0.5)

    # Read CSV file
    defective_methods = 0
    with open(temp2_csv, mode='r') as infile:
        with open(args.output, mode='w') as outfile:
            header = infile.readline().strip().split(',')
            header = ','.join(header[:-4]) + ',' + 'Prediction' + '\n'
            outfile.write(header)
            i = 0
            lines = infile.readlines()
            for line in lines:
                columns = line.strip().split(',')
                if y_pred[i]:
                    print('Commit: {} File: {} Method: {} Is: {}'.format(columns[1], columns[2], columns[3], y_pred[i]))
                    defective_methods += 1
                buggy = 'TRUE' if y_pred[i] else 'FALSE'
                outfile.write('{},{}\n'.format(','.join(columns[:-4]), buggy))
                i += 1
    print('Found {} defective methods'.format(defective_methods))

    print("\n*** Tester ended ***")

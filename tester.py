import argparse, os, numpy

from sklearn.preprocessing import StandardScaler
from miner import Miner
from sklearn.externals import joblib
from tensorflow import keras
import shap


def skipper(fname, header=False):
    with open(fname) as fin:
        no_comments = (line for line in fin if not line.lstrip().startswith('#'))
        if header:
            next(no_comments, None)  # skip header
        for row in no_comments:
            yield row


def get_important_features(cutoff, shap_values):
    # Calculate the values that represent the fraction of the model output variability attributable
    # to each feature across the whole dataset.
    shap_sums = shap_values.sum(0)
    abs_shap_sums = numpy.abs(shap_values).sum(0)
    rel_shap_sums = abs_shap_sums / abs_shap_sums.sum()

    cut_off_value = cutoff * numpy.amax(rel_shap_sums)

    # Get indices of features that pass the cut off value
    top_feature_indices = numpy.where(rel_shap_sums >= cut_off_value)[0]
    # Get the importance values of the top features from their indices
    top_features = numpy.take(rel_shap_sums, top_feature_indices)
    # Gets the sign of the importance from shap_sums as boolean
    is_positive = (numpy.take(shap_sums, top_feature_indices)) >= 0
    # Stack the importance, indices and shap_sums in a 2D array
    top_features = numpy.column_stack((top_features, top_feature_indices, is_positive))
    # Sort the array (in decreasing order of importance values)
    top_features = top_features[top_features[:, 0].argsort()][::-1]

    return top_features


# Main
if __name__ == '__main__':
    print("*** Tester started ***\n")

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', type=str, help='Absolute GIT repository path', default=None)
    parser.add_argument('-e', '--ext', type=str, help='List of allowed extensions. Eg. .cpp .c', default='.cpp')
    parser.add_argument('-s', '--start', type=str, help='Commit HASH to analyze', default='e1d724d2f50763136a691752a09a929fa3e6d2dc')
    parser.add_argument('-p', '--stop', type=str, help='Stop HASH commit, if not specified it analyzes up to the end.', default='3a01a56056138755d0efa832a76321295c680601')
    parser.add_argument('-o', '--output', type=str, help='Path of the CSV file where to save results.', default='data/testing_output.csv')
    parser.add_argument('-m', '--model', type=str, help='Path of the machine learning model.', default='data/joblib.dump')
    args, unknown = parser.parse_known_args()

    temp1_csv = 'temp1.csv'

    if args.start is None or args.stop is None:
        print('A pair of commit HASHs must be passed as input!')
        exit(-1)
    if not os.path.isfile(args.model):
        print('A valid trained model must be passed ad input argument!')
        exit(-1)

    # Get a list of touched methods in the last commit
    miner = Miner(args.repo, args.ext, temp1_csv)
    metrics = miner.mine_methods(args.start, args.start)
    allowed_methods = []
    for key, val in metrics.items():
        if val[0].method_touched == 1:
            allowed_methods.append(key)
    print('Check for ' + str(len(allowed_methods)) + ' methods')

    # Calculate metrics for touched commits only up to stop commit
    metrics = miner.mine_methods(args.start, args.stop, allowed_methods)

    # Count the number of columns into which split dataset
    fin = open(temp1_csv, mode='r')
    header = fin.readline()
    features = header.split(',')
    count = len(features)
    fin.close()

    # Read the CSV file that contains fresh mined metrics
    dataset = numpy.loadtxt(skipper(temp1_csv, True), delimiter=",", usecols=(range(4, count - 8)))
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

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(x)

    if isinstance(shap_values, list):
        shap_values = numpy.sum(numpy.abs(shap_values), axis=0)

    importance_cutoff = 0.15
    top_importances = get_important_features(importance_cutoff, shap_values)

    top_indexes = [int(index) for importance, index, is_positive in top_importances]

    top_feature = features[top_indexes[0] + 4]

    # Read CSV file
    defective_methods = 0
    with open(temp1_csv, mode='r') as infile:
        with open(args.output, mode='w') as outfile:
            header = infile.readline().strip().split(',')
            header = ','.join(header[:-4]) + ',' + 'Prediction' + ',' + 'top_feature_1' + '\n'
            outfile.write(header)
            i = 0
            lines = infile.readlines()
            for line in lines:
                columns = line.strip().split(',')
                if y_pred[i]:
                    print('Commit: {} File: {} Method: {} Is: {}'.format(columns[1], columns[2], columns[3], y_pred[i]))
                    defective_methods += 1
                buggy = 'TRUE' if y_pred[i] else 'FALSE'
                outfile.write('{},{},{}\n'.format(','.join(columns[:-4]), buggy, top_feature))
                i += 1
    print('Found {} defective methods'.format(defective_methods))

    print("\n*** Tester ended ***")

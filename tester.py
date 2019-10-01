import argparse, os, numpy

from sklearn.preprocessing import StandardScaler
from miner import Miner
from sklearn.externals import joblib
import shap


def skipper(fname: str, header=False):
    with open(fname) as fin:
        no_comments = (line for line in fin if not line.lstrip().startswith('#'))
        if header:
            next(no_comments, None)  # skip header
        for row in no_comments:
            yield row


def get_important_features(cutoff, shap_values):
    # Calculate the values that represent the fraction of the model output variability attributable to each feature across the whole dataset.
    shap_sums = shap_values
    abs_shap_sums = numpy.abs(shap_values)
    rel_shap_sums = abs_shap_sums / abs_shap_sums.sum(0).sum()

    cut_off_value = []
    for e in rel_shap_sums:
        cut_off_value.append(cutoff * numpy.amax(e))

    top_feature_indices = []
    top_features_list = []
    for i in range(len(cut_off_value)):
        # Get indices of features that pass the cut off value
        top_feature_indices.append(numpy.where(rel_shap_sums[i] >= cut_off_value[i])[0])
        # Get the importance values of the top features from their indices
        top_features = numpy.take(rel_shap_sums[i], top_feature_indices[i])
        # Gets the sign of the importance from shap_sums as boolean
        is_positive = (numpy.take(shap_sums[i], top_feature_indices[i])) >= 0
        # Stack the importance, indices and shap_sums in a 2D array
        top_features = numpy.column_stack((top_features, top_feature_indices[i], is_positive))
        # Sort the array (in decreasing order of importance values)
        top_features = top_features[top_features[:, 0].argsort()][::-1]
        top_features_list.append(top_features)

    return top_features_list


def build_message(file_name, method_name, top_features_name, top_features_value, i):
    ''' TODO Working on this method to show coherent messages '''
    feature_1_name = top_features_name[0][i]
    feature_1_value = top_features_value[0][i]
    feature_2_name = top_features_name[1][i]
    feature_2_value = top_features_value[1][i]
    feature_3_name = top_features_name[2][i]
    feature_3_value = top_features_value[2][i]
    feature_4_name = top_features_name[3][i]
    feature_4_value = top_features_value[3][i]
    feature_5_name = top_features_name[4][i]
    feature_5_value = top_features_value[4][i]

    return "{} method in {} file is prone to be defective due to {} value too high for the feature {}".format(method_name, file_name, feature_1_value, feature_1_name)


# Main
if __name__ == '__main__':
    print("*** Tester started ***\n")

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', type=str, help='Absolute path of a GIT repository.', default=None)
    parser.add_argument('-e', '--ext', type=str, help='List of allowed file extensions. Eg. .cpp .c', default='.cpp')
    parser.add_argument('-s', '--start', type=str, help='Commit HASH to analyze', default='91efc5a86caadc97d087869129441f9d6c4e4bf9')
    parser.add_argument('-p', '--stop', type=str, help='Stop HASH commit, if not specified it analyzes up to the end.', default='be898d03269ba282bea19d90643adaf09ec21de2')
    parser.add_argument('-o', '--output', type=str, help='Path of the CSV file where to save results.', default='data/testing_output.csv')
    parser.add_argument('-m', '--model', type=str, help='Path of the machine learning model.', default='data/joblib.dump')
    args, unknown = parser.parse_known_args()

    temp_csv = 'temp.csv'
    temp2_csv = 'temp2.csv'

    if args.start is None or args.stop is None:
        print('A pair of commit HASHs must be passed as input!')
        exit(-1)
    if not os.path.isfile(args.model):
        print('A valid trained model must be passed ad input argument!')
        exit(-1)

    # Get a list of touched methods in the last commit
    miner = Miner(args.repo, args.ext, temp_csv)
    miner.mine_methods(args.start, args.start)

    # Count the number of columns into which split dataset
    fin = open(temp_csv, mode='r')
    header = fin.readline()
    features = header.split(',')
    column_count = len(features)

    # Read remaining rows to extract files and methods
    allowed_methods = set()
    allowed_files = set()
    for line in fin.readlines():
        cols = line.split(',')
        touched = int(cols[78])  # Touched sum (this is a binary value since at this point only one commit is inspected)
        if touched > 0:
            allowed_methods.add(cols[0])  # Entire key
            allowed_files.add(cols[2])  # Full paths
    fin.close()
    print('Check for ' + str(len(allowed_methods)) + ' methods in ' + str(len(allowed_files)) + ' files')

    # Calculate metrics for touched commits only up to stop commit
    miner = Miner(args.repo, args.ext, temp2_csv)
    miner.mine_methods(args.start, args.stop, allowed_methods, allowed_files)

    # Read the CSV file that contains fresh mined metrics
    dataset = numpy.loadtxt(skipper(temp2_csv, True), delimiter=",", usecols=(range(5, column_count - 8)))
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
    y_pred_bin = model.predict(x)
    y_pred_proba = model.predict_proba(x)
    y_pred_bin = (y_pred_bin > 0.5)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(x)

    if isinstance(shap_values, list):
        shap_values = numpy.sum(numpy.abs(shap_values), axis=0)

    importance_cutoff = 0.15
    top_importances = get_important_features(importance_cutoff, shap_values)

    top_features_name = ([], [], [], [], [])
    top_features_value = ([], [], [], [], [])
    for i in range(len(x)):
        top_indexes = [int(index) for importance, index, is_positive in top_importances[i]]
        top_importance = [importance for importance, index, is_positive in top_importances[i]]
        for j in range(5):
            if len(top_indexes) > j:
                feature = features[top_indexes[j] + 5]
                importance = top_importance[j]
            else:
                feature = "None"
                importance = -1
            top_features_name[j].append(feature)
            top_features_value[j].append(importance)

    # Read CSV file
    defective_methods = 0
    with open(temp2_csv, mode='r') as infile:
        with open(args.output, mode='w') as outfile:
            header = infile.readline().strip().split(',')
            header = ','.join(header[:-4]) + ',prediction,prediction_false,prediction_true,' \
                     + 'top_feature_1' + ',' + 'top_feature_1_val,' \
                     + 'top_feature_2' + ',' + 'top_feature_2_val,' \
                     + 'top_feature_3' + ',' + 'top_feature_3_val,' \
                     + 'top_feature_4' + ',' + 'top_feature_4_val,' \
                     + 'top_feature_5' + ',' + 'top_feature_5_val,' \
                     + 'message' + '\n'
            outfile.write(header)
            i = 0
            lines = infile.readlines()
            for line in lines:
                columns = line.strip().split(',')
                if y_pred_bin[i]:
                    print(build_message(columns[2], columns[3], top_features_name, top_features_value, i))
                    defective_methods += 1
                buggy = 'TRUE' if y_pred_bin[i] else 'FALSE'
                outfile.write('{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(','.join(columns[:-4]), buggy, y_pred_proba[i][0],y_pred_proba[i][1],
                                                                                   top_features_name[0][i], top_features_value[0][i],
                                                                                   top_features_name[1][i], top_features_value[1][i],
                                                                                   top_features_name[2][i], top_features_value[2][i],
                                                                                   top_features_name[3][i], top_features_value[3][i],
                                                                                   top_features_name[4][i], top_features_value[4][i],
                                                                                   build_message(columns[2], columns[3], top_features_name, top_features_value, i)))
                i += 1
    print('Found {} defective methods'.format(defective_methods))

    print("\n*** Tester ended ***")

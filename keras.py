import argparse

import numpy
from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn import metrics

import tensorflow as tf
from tensorflow import keras
from tensorflow.python.keras import Sequential
from tensorflow.python.keras.layers import Dense, Dropout

from sklearn.model_selection import StratifiedKFold
from typing import List

from xgboost import XGBClassifier
import shap
import matplotlib


def skipper(fname, header=False):
    with open(fname) as fin:
        no_comments = (line for line in fin if not line.lstrip().startswith('#'))
        if header:
            next(no_comments, None)  # skip header
        for row in no_comments:
            yield row


def get_human_readable_feature_names(features_as_header):

    # for full_feature_name in feature_names:
    #     type_, feature_name = full_feature_name.split("__", 1)
    #
    #     if type_ == "desc":
    #         feature_name = f"Description contains '{feature_name}'"
    #     elif type_ == "title":
    #         feature_name = f"Title contains '{feature_name}'"
    #     elif type_ == "first_comment":
    #         feature_name = f"First comment contains '{feature_name}'"
    #     elif type_ == "comments":
    #         feature_name = f"Comments contain '{feature_name}'"
    #     elif type_ == "text":
    #         feature_name = f"Combined text contains '{feature_name}'"
    #     elif type_ == "data":
    #         if " in " in feature_name and feature_name.endswith("=True"):
    #             feature_name = feature_name[: len(feature_name) - len("=True")]
    #     else:
    #         raise Exception(f"Unexpected feature type for: {full_feature_name}")
    #
    #     cleaned_feature_names.append(feature_name)

    return features_as_header


def read_data(input_path: str) -> (List[List[float]], List[int]):
    # Count columns to split dataset
    fin = open(input_path)
    columns = fin.readline().split(",")
    count = len(columns)
    fin.close()

    # Select only metrics and buggy columns
    usecols = list(range(4, count - 4))
    usecols.append(count - 1)

    features = []
    for i in usecols:
        features.append(columns[i])

    dataset = numpy.loadtxt(skipper(input_path, True), delimiter=",", usecols=usecols)
    # split into input (X) and output (Y) variables
    x = dataset[:, 0:-1]
    y = dataset[:, -1]
    # standardizing the input feature
    # sc = StandardScaler()
    # x = sc.fit_transform(x)
    return len(x[0]), features, x, y


def create_tensorflow_model(count):
    # Define our classifier
    model = Sequential()
    # First Layer
    model.add(Dense(count, activation=tf.nn.relu, kernel_initializer='random_normal', input_dim=count))
    # Second  Hidden Layer
    model.add(Dense(50, activation='relu', kernel_initializer='random_normal'))
    # model.add(Dropout(rate=0.2))
    model.add(Dense(20, activation='relu', kernel_initializer='random_normal'))
    # model.add(Dense(6, activation='relu', kernel_initializer='random_normal'))
    # Output Layer
    model.add(Dense(1, activation='sigmoid', kernel_initializer='random_normal'))
    # Compiling the neural network
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model


def create_xgboost_model():
    # Define our classifier
    model = XGBClassifier()
    return model


if __name__ == '__main__':
    print("*** Keras started ***\n")

    print('TensorFlow version: ' + tf.__version__)
    print('Is GPU available: ' + str(tf.test.is_gpu_available()))
    print('Is CUDA built: ' + str(tf.test.is_built_with_cuda()))
    print('Is eager enabled: ' + str(tf.executing_eagerly()))

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help='Local absolute or relative path to a valid CSV dataset.', default='data/method_metrics.csv')
    parser.add_argument('-k', '--kfolds', type=str, help='Number of k-folds', default=1)
    parser.add_argument('-t', '--type', type=str, help='Model type: tensorflow or xgboost', default='xgboost')
    parser.add_argument('-s', '--save', type=str, help='Save model', default='data/model.h5')
    args, unknown = parser.parse_known_args()

    # Read and split in X and Y data from CSV file
    count, features, x, y = read_data(args.input)
    print('Features count: ' + str(count))
    print('Instances count: ' + str(len(x)))

    feature_names = get_human_readable_feature_names(features)

    # Standardizing the input feature
    sc = StandardScaler()
    x = sc.fit_transform(x)

    if args.kfolds == 1:
        # Single training case
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3)

        # Fitting the data to the training dataset
        if args.type == 'tensorflow':
            model = create_tensorflow_model(count)
            model.fit(x_train, y_train, batch_size=10, epochs=10, verbose=1)
            loss, accuracy = model.evaluate(x_test, y_test)
            model.summary()
            print('Loss: {:.2f} Accuracy: {:.2f}'.format(loss, accuracy))
        elif args.type == 'xgboost':
            model = create_xgboost_model()
            model.fit(x_train, y_train, verbose=1)

        y_pred = model.predict(x_test)
        y_pred = (y_pred > 0.5)

        cm = metrics.confusion_matrix(y_test, y_pred)
        print('Confusion metrics:')
        print(cm)

        f1 = metrics.f1_score(y_test, y_pred)
        print('F1: {0:.2f}'.format(f1))

        mcc = metrics.matthews_corrcoef(y_test, y_pred)
        print('MCC: {0:.2f}'.format(mcc))

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(x_train)

        shap.summary_plot(
            shap_values,
            x_train,
            feature_names=feature_names,
            # class_names=class_names,
            plot_type="bar"
            if not isinstance(shap_values, list)
            else None,
            show=False,
        )

        matplotlib.pyplot.savefig("feature_importance.png", bbox_inches="tight")

        # Save entire model to a HDF5 file
        if args.save is not None:
            if args.type == 'tensorflow':
                model.save(args.save)
            elif args.type == 'xgboost':
                joblib.dump(model, args.save)
    else:
        # Use k-fold cross validation test harness
        kfold = StratifiedKFold(n_splits=args.kfolds, shuffle=True)
        scores = {'Accuracy': [], 'F-score': [], 'MCC': []}
        for train, test in kfold.split(x, y):
            # Split dataset in training and testing part
            model = create_tensorflow_model(count)
            # Fitting the data to the training dataset
            model.fit(x[train], y[train], batch_size=10, epochs=5, verbose=1)
            loss, accuracy = model.evaluate(x[test], y[test])
            # model.summary()
            print('Loss: {:.2f} Accuracy: {:.2f}'.format(loss, accuracy))

            y_pred = model.predict(x[test])
            y_pred = (y_pred > 0.5)
            f1 = metrics.f1_score(y[test], y_pred)
            print('F-score: {0:.2f}'.format(f1))
            mcc = metrics.matthews_corrcoef(y[test], y_pred)
            print('MCC: {0:.2f}'.format(mcc))
            scores['Accuracy'].append(accuracy)
            scores['F-score'].append(f1)
            scores['MCC'].append(mcc)

        print()
        print('Accuracy {:.2f} (+/- {:.2f})'.format(numpy.mean(scores['Accuracy']), numpy.std(scores['Accuracy'])))
        print('F-score {:.2f} (+/- {:.2f})'.format(numpy.mean(scores['F-score']), numpy.std(scores['F-score'])))
        print('MCC {:.2f} (+/- {:.2f})'.format(numpy.mean(scores['MCC']), numpy.std(scores['MCC'])))

    print("\n*** Keras ended ***")

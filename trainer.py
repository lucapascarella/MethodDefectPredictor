import argparse

if __name__ == '__main__':
    print("*** Trainer started ***\n")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help='Path of the CSV with training date.', default='extractor.csv')
    parser.add_argument('-o', '--output', type=str, help='Path of the machine learning model.', default='model.model')
    args, unknown = parser.parse_known_args()


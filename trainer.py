import argparse, csv

if __name__ == '__main__':
    print("*** Trainer started ***\n")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help='Path of the CSV with training date.', default='extractor.csv')
    parser.add_argument('-o', '--output', type=str, help='Path of the machine learning model.', default='model.h5')
    args, unknown = parser.parse_known_args()

    header = 'hash,key,file,method,changes,' \
             'file_count,max_file_count,avg_file_count,added,max_added,avg_added,' \
             'removed,max_removed,avg_removed,' \
             'loc,max_loc,avg_loc,' \
             'complexity,max_complexity,avg_complexity,' \
             'token_count,max_token_count,avg_token_count,' \
             'methods,max_methods,avg_methods,' \
             'm_token,max_m_token,avg_m_token,' \
             'm_fan_in,m_fan_out,m_g_fan_out,' \
             'm_loc,max_m_loc,avg_m_loc,' \
             'm_length,max_m_length,avg_m_length,' \
             'm_comp,max_m_comp,avg_m_comp,' \
             'm_param_count,max_m_param_count,avg_m_param_count,' \
             'm_added,max_m_added,avg_m_added,' \
             'm_removed,max_m_removed,avg_m_removed,' \
             'authors,' \
             'bug_count,buggy'

    features = ['changes', 'file_count']

    instances =[]
    for row in csv.DictReader(open(args.input, 'r', newline='', encoding="utf-8"), delimiter=','):
        d = {}
        for feature in features:
            d[feature] = row[feature]
        instances.append(d)

    print("\n*** Trainer ended ***")
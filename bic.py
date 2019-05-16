import argparse, csv

from pydriller import GitRepository


def get_method_count(modifications):
    count = 0
    for mod in modifications:
        count += len(mod.methods)
    return count


# Main
if __name__ == '__main__':
    print("*** BIC started ***\n")

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', type=str, help='Absolute GIT repository path', default='/Users/luca/TUProjects/Mozilla/gecko-dev')
    parser.add_argument('-i', '--input', type=str, help='Input CSV file with the list of fix commits', default='/Users/luca/TUProjects/Mozilla/commit_results.csv')
    parser.add_argument('-o', '--output', type=str, help='Output CSV file where save bug inducing commits', default='/Users/luca/TUProjects/Mozilla/bic_commit_results.csv')
    args, unknown = parser.parse_known_args()

    header = 'mercurial_hash', 'git_hash', 'git_mods', 'git_methods', 'git_timestamp', 'type', 'bic_count', 'bic_commit', 'bic_mods', 'bic_methods', 'bic_timestamp'
    out_file = open(args.output, 'w', newline='', encoding="utf-8")
    writer = csv.DictWriter(out_file, delimiter=',', fieldnames=header)
    writer.writeheader()

    gr = GitRepository(args.repo)
    fixes = csv.DictReader(open(args.input, 'r', newline='', encoding="utf-8"), delimiter=',')
    for fix in fixes:
        count = 0
        git_hash = fix['git_hash']
        fix_commit = gr.get_commit(git_hash)
        bic_commits = gr.get_commits_last_modified_lines(fix_commit)
        print('{}) {} has {} BIC'.format(count, git_hash, len(bic_commits)))

        dout = {'mercurial_hash': fix['mercurial_hash'],
                'git_hash': fix['git_hash'],
                'git_mods': len(fix_commit.modifications),
                'git_methods': get_method_count(fix_commit.modifications),
                'git_timestamp': fix_commit.committer_date,
                'type': fix['type'],
                'bic_count': len(bic_commits)}
        for bic_commit_hash in bic_commits:
            bix_commit = gr.get_commit(bic_commit_hash)
            dout['bic_commit'] = bic_commit_hash
            dout['bic_mods'] = len(bix_commit.modifications)
            dout['bic_methods'] = get_method_count(bix_commit.modifications)
            dout['bic_timestamp'] = bix_commit.committer_date
            writer.writerow(dout)
        count =+ 1
        out_file.flush()
    out_file.close()

    print("\n*** BIC ended ***")

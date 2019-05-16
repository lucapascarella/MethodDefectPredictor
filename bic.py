import csv

from pydriller import GitRepository


def get_method_count(modifications):
    count = 0
    for mod in modifications:
        count += len(mod.methods)
    return count


# Main
header = 'mercurial_hash', 'git_hash', 'git_mods', 'git_methods', 'git_timestamp', 'type', 'bic_count', 'bic_commit', 'bic_mods', 'bic_methods', 'bic_timestamp'
writer = csv.DictWriter(open('/Users/luca/TUProjects/Mozilla/bic_commit_results.csv', 'w', newline='', encoding="utf-8"), delimiter=',', fieldnames=header)
writer.writeheader()

gr = GitRepository('/Users/luca/PycharmProjects/BIMFinder/test-repos/gecko-dev')
fixes = csv.DictReader(open('/Users/luca/TUProjects/Mozilla/commit_results.csv', 'r', newline='', encoding="utf-8"), delimiter=',')
for fix in fixes:
    git_hash = fix['git_hash']
    fix_commit = gr.get_commit(git_hash)
    bic_commits = gr.get_commits_last_modified_lines(fix_commit)
    print('{} has {} BIC'.format(git_hash, len(bic_commits)))

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

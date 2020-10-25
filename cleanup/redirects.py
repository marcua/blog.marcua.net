import os
import re


HYPHEN_DATE_RE = re.compile('\d{4}-\d{2}-\d{2}')


def clean_redirects(filename):
    with open(filename) as read_file:
        content = read_file.read()
    search = HYPHEN_DATE_RE.search(content)
    if not search:
        raise Exception('Bad match')
    hyphen_date = search.group(0)
    slash_date = hyphen_date.replace('-', '/') 
    for prefix in ('href="', 'url='):
        content = content.replace(
            '{}/2020/10/25/'.format(prefix),
            '{}/{}/'.format(prefix, slash_date))
    content = content.replace('{}-'.format(hyphen_date), '')
    with open(filename, 'w+') as write_file:
        write_file.write(content)
        write_file.flush()
            


def main():
    for subdir, dirs, files in os.walk('post'):
        for file in files:
            clean_redirects(os.path.join(subdir, file))

if __name__ == '__main__':
    main()

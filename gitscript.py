
#  Converted  from  gitscript.sh using https://www.codeconvert.ai/convert-from-bash

import os
import re
import subprocess
import sys
from pathlib import Path

print('This is git directory script assuming that parent is git repositories.')

def is_valid_url(url: str) -> bool:
    # A robust regex to match a wide range of URLs
    url_regex = re.compile(
        r'^(https?|ftp|file)://[-A-Za-z0-9\+&@#/%?=~_|!:,.;]*[-A-Za-z0-9\+&@#/%=~_|]\.[-A-Za-z0-9\+&@/%?=~_|]*[-A-Za-z0-9\+&@#/%=~_|]$'
    )
    return bool(url_regex.match(url))

def check_url_reachability(url: str) -> bool:
    # Use curl with specific flags to check URL reachability
    result = subprocess.run(
        ['curl', '--output', '/dev/null', '--silent', '--head', '--fail', url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

def main():
    if len(sys.argv) < 2 or sys.argv[1] == "":
        print('Init is completed, change dir to parent to run gitscript.sh commands.')
        sys.exit()

    command = sys.argv[1]

    if command == "gitrepourl":
        print('Read git remote entries in your repositories if available.')
        gitrepos = []

        # Read git remote URLs from ../*/.git/config
        parent_dir = Path('..')
        for repo_dir in parent_dir.iterdir():
            git_config = repo_dir / '.git' / 'config'
            if git_config.is_file():
                with git_config.open() as f:
                    for line in f:
                        if line.strip().startswith('url = '):
                            url = line.strip()[6:]
                            gitrepos.append(url)

        # Find directories in .. that do not contain .git directory
        dirs_without_git = []
        for entry in parent_dir.iterdir():
            if entry.is_dir() and not (entry / '.git').exists():
                dirs_without_git.append(str(entry)[3:])  # remove leading ../

        # Combine and sort
        gitrepos = sorted(set(gitrepos))
        dirs_without_git = sorted(dirs_without_git)

        # Write to ./gitrepos
        with open('gitrepos', 'w') as f:
            for url in gitrepos:
                f.write(url + '\n')
            for d in dirs_without_git:
                f.write(d + '\n')

        # Output the content of gitrepos
        with open('gitrepos') as f:
            print(f.read(), end='')

        sys.exit()

    elif command == "gitrepozip":
        print('Read the git directory and zip it.')
        parent_dir = Path('..')
        if len(sys.argv) > 2 and sys.argv[2]:
            repo = parent_dir / sys.argv[2]
            if repo.exists():
                print("The second argument exists and is not empty.")
                print(f"zip it {repo}")
                # Build zip exclude patterns
                exclude_patterns = [
                    "target/*", "**/target/*", ".git/*", ".idea/*", "**/.idea/*",
                    ".classpath/*", ".project/*", "node_modules/*", "**/node_modules/*"
                ]
                exclude_args = []
                for pattern in exclude_patterns:
                    exclude_args.extend(['-x', str(repo / pattern)])

                subprocess.run(['zip', '-q', '-r', str(repo), str(repo)] + exclude_args)
            else:
                print(f"Repository path {repo} does not exist.")
        else:
            print("The second argument does not exist or is empty, zip all.")
            for entry in parent_dir.iterdir():
                if entry.is_dir():
                    print(f"zip it {entry}")
                    exclude_patterns = [
                        "target/*", "**/target/*", ".git/*", ".idea/*", "**/.idea/*",
                        ".classpath/*", ".project/*", "node_modules/*", "**/node_modules/*"
                    ]
                    exclude_args = []
                    for pattern in exclude_patterns:
                        exclude_args.extend(['-x', str(entry / pattern)])

                    subprocess.run(['zip', '-q', '-r', str(entry), str(entry)] + exclude_args)
        sys.exit()

    elif command == "gitrepoclone":
        print("Read git remote repositories from gitrepos file and clone them all.")
        input_file = "gitrepos"
        my_array = []

        if not os.path.isfile(input_file):
            print(f"File {input_file} does not exist.", file=sys.stderr)
            sys.exit(1)

        with open(input_file, 'r') as f:
            for line in f:
                my_array.append(line.strip())

        print("Clone repositories.")
        start_char = "/"
        end_char = "."

        for entry in my_array:
            print(entry)
            temp = entry.rsplit(start_char, 1)[-1]
            repo = temp.split(end_char, 1)[0]

            if is_valid_url(entry):
                print("has a valid format.")
                if check_url_reachability(entry):
                    print("server is up.")
                    subprocess.run(['git', 'clone', entry, str(Path('..') / repo)])
                else:
                    print("server is down or does not exist.", file=sys.stderr)
            else:
                print("does not have a valid format.", file=sys.stderr)
        sys.exit()

    else:
        print('Wrong command', command)
        sys.exit()

if __name__ == "__main__":
    main()
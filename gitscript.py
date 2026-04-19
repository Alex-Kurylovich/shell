#
#  Converted from gitscript.sh using https://www.codeconvert.ai/convert-from-bash
#  run from terminal python3 gitscript.py
#

import os
import re
import subprocess
from pathlib import Path

print('This is git directory script assuming that parent is git repositories.')

def is_valid_url(url):
    # A robust regex to match a wide range of URLs
    url_regex = re.compile(r'^(https?|ftp|file)://[-A-Za-z0-9\+&@#/%?=~_|!:,.;]*[-A-Za-z0-9\+&@#/%=~_|]\.[-A-Za-z0-9\+&@/%?=~_|]*[-A-Za-z0-9\+&@#/%=~_|]$')
    return bool(url_regex.match(url))

def check_url_reachability(url):
    # Use curl with specific flags:
    # -f, --fail: Fail silently (no output at all) on server errors (HTTP status >= 400)
    # -s, --silent: Silent mode (disables progress meter and error messages)
    # -o /dev/null: Redirect output to /dev/null
    # --head: Fetch only HTTP headers (faster than downloading the whole page)
    result = subprocess.run(
        ['curl', '--output', os.devnull, '--silent', '--head', '--fail', url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

import sys

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

    gitrepos = sorted(gitrepos)

    # Find directories that do not contain .git directory
    dirs_without_git = []
    for entry in parent_dir.iterdir():
        if entry.is_dir() and not (entry / '.git').exists():
            dirs_without_git.append(entry.name)
    dirs_without_git = sorted(dirs_without_git)

    # Combine results
    gitrepos.extend(dirs_without_git)

    # Write to ./gitrepos
    with open('gitrepos', 'w') as f:
        for item in gitrepos:
            f.write(f"{item}\n")

    # Print gitrepos content
    print('\n'.join(gitrepos))
    sys.exit()

elif command == "gitrepozip":
    print('Read the git directory and zip it.')
    import zipfile

    def zip_directory(zipf, folder_path, base_path):
        exclude_patterns = [
            "target/", "**/target/",
            ".git/", ".idea/", "**/.idea/",
            ".classpath/", ".project/",
            "node_modules/", "**/node_modules/"
        ]
        # Normalize exclude patterns for matching
        exclude_patterns = [p.rstrip('/') for p in exclude_patterns]

        for root, dirs, files in os.walk(folder_path):
            # Compute relative path from base_path
            rel_root = os.path.relpath(root, base_path)
            # Skip excluded directories
            skip_dir = False
            for pattern in exclude_patterns:
                # Check if rel_root matches pattern or is under pattern
                if rel_root == pattern or rel_root.startswith(pattern + os.sep):
                    skip_dir = True
                    break
            if skip_dir:
                dirs[:] = []  # Don't recurse into subdirs
                continue

            for file in files:
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, base_path)
                # Check if file matches exclude patterns
                skip_file = False
                for pattern in exclude_patterns:
                    if rel_file_path == pattern or rel_file_path.startswith(pattern + os.sep):
                        skip_file = True
                        break
                if not skip_file:
                    zipf.write(file_path, rel_file_path)

    if len(sys.argv) > 2 and sys.argv[2]:
        REPO = Path('..') / sys.argv[2]
        if REPO.exists() and REPO.is_dir():
            print("The second argument exists and is not empty.")
            print(f"zip it {REPO}")
            zip_path = REPO.with_suffix('.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zip_directory(zipf, str(REPO), str(REPO))
        else:
            print(f"Repository path {REPO} does not exist or is not a directory.")
    else:
        print("The second argument does not exist or is empty, zip all.")
        parent_dir = Path('..')
        for entry in parent_dir.iterdir():
            if entry.is_dir():
                print(f"zip it {entry}")
                zip_path = entry.with_suffix('.zip')
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zip_directory(zipf, str(entry), str(entry))
    sys.exit()

elif command == "gitrepoclone":
    print("Read git remote repositories from gitrepos file and clone them all.")
    INPUT_FILE = "gitrepos"
    my_array = []
    if not os.path.isfile(INPUT_FILE):
        print(f"{INPUT_FILE} file does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(INPUT_FILE, 'r') as f:
        for line in f:
            my_array.append(line.strip())

    print("Clone repositories.")
    START_CHAR = "/"
    END_CHAR = "."

    for entry in my_array:
        print(entry)
        temp = entry.rsplit(START_CHAR, 1)[-1]
        REPO = temp.split(END_CHAR, 1)[0]
        if is_valid_url(entry):
            print("has a valid format.")
            if check_url_reachability(entry):
                print("server is up.")
                subprocess.run(['git', 'clone', entry, str(Path('..') / REPO)])
            else:
                print("server is down or does not exist.", file=sys.stderr)
        else:
            print("does not have a valid format.", file=sys.stderr)
    sys.exit()

else:
    print('Wrong command', command)
    sys.exit()
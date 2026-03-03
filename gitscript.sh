#!/bin/bash

echo 'This is git directory script assuming that parent is git repositories.'

is_valid_url() {
    local url=$1
    # A robust regex to match a wide range of URLs
    local url_regex='^(https?|ftp|file)://[-A-Za-z0-9\+&@#/%?=~_|!:,.;]*[-A-Za-z0-9\+&@#/%=~_|]\.[-A-Za-z0-9\+&@/%?=~_|]*[-A-Za-z0-9\+&@#/%=~_|]$'
    if [[ "$url" =~ $url_regex ]]; then
        return 0 # Valid format
    else
        return 1 # Invalid format
    fi
}

check_url_reachability() {
    local url=$1
    # Use curl with specific flags:
    # -f, --fail: Fail silently (no output at all) on server errors (HTTP status >= 400)
    # -s, --silent: Silent mode (disables progress meter and error messages)
    # -o /dev/null: Redirect output to /dev/null
    # --head: Fetch only HTTP headers (faster than downloading the whole page)
    if curl --output /dev/null --silent --head --fail "$url"; then
        return 0 # url is up/reachable
    else
        return 1 # url is down/unreachable or invalid
    fi
}

case "$1" in
  "")
      echo 'Init is completed, change dir to parent to run gitscript.sh commands.'
      exit
      ;;
  "gitrepourl")
      echo 'Read git remote entries in your repositories if available.'
      cat ../*/.git/config | grep "url = " | sort | awk '{print substr($0, 8)}' > ./gitrepos
      # Find directories that do not contain .git directory
      find .. -maxdepth 1 -type d '!' -exec test -d "{}/.git" \; -print | sort | sed '1d' | awk '{print substr($0, 4)}' >> ./gitrepos
      cat gitrepos
      exit
      ;;
  "gitrepozip")
      echo 'Read the git directory and zip it.'
      REPO=../$2
      if [ -n "$2" ]; then
          echo "The second argument exists and is not empty."
          echo "zip it $REPO"
          zip -q -r $REPO $REPO -x "$REPO/target/*" "$REPO/**/target/*" "$REPO/.git/*" "$REPO/.idea/*" "$REPO/**/.idea/*" "$REPO/.classpath/*" "$REPO/.project/*"  "$REPO/node_modules/*" "$REPO/**/node_modules/*"
      else
          echo "The second argument does not exist or is empty, zip all."
          for entry in ../*; do
            if [ -d $entry ]; then
              echo "zip it $entry"
              zip -q -r $entry $entry -x "$entry/target/*" "$entry/**/target/*" "$entry/.git/*" "$entry/.idea/*" "$entry/**/.idea/*" "$entry/.classpath/*" "$entry/.project/*" "$entry/node_modules/*" "$entry/**/node_modules/*"
            fi
          done
      fi
      exit
      ;;
  "gitrepoclone")
      echo "Read git remote repositories from gitrepos file and clone them all."
      # A common, secure permission for a text file is 644: chmod 644 gitrepos
      INPUT_FILE="gitrepos"
      my_array=() # Declare an empty array
      # Use a while loop to read each line
      while IFS= read -r line; do
          # Append the line to the array. Quoting "$line" preserves spaces.
          my_array+=("$line")
      done < "$INPUT_FILE"
      echo "Clone repositories."
      START_CHAR="/"
      END_CHAR="."
      for entry in "${my_array[@]}"; do
          echo "$entry"
          temp="${entry##*$START_CHAR}"
          REPO="${temp%%$END_CHAR*}"
          if is_valid_url "$entry"; then
              echo "has a valid format."
              if check_url_reachability "$entry"; then
                  echo "server is up."
                  git clone $entry ../$REPO
              else
                  echo "server is down or does not exist." >&2
              fi
          else
              echo "does not have a valid format." >&2
          fi
      done
      exit
      ;;
  *)
      echo 'Wrong command' "$1"
      exit
esac



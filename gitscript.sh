#!/bin/bash

echo 'This is git directory script assuming that parent is git repositories.'

rm -f ../gitrepos
cp -f ./gitscript.sh ../gitscript.sh

case "$1" in
  "")
      echo 'Init is completed, change dir to parent to run gitscript.sh commands.'
      exit
      ;;
  "gitrepourl")
      echo 'Read git remote entries in your repositories.'
      echo 'Read ./git/config url from all projects and create git urls file gitrepos'
      cat ./*/.git/config | grep "url = " | sort | awk '{print substr($0, 8)}' > gitrepos
      echo 'Print gitrepos'
      cat gitrepos
      exit
      ;;
  "gitrepozip")
      echo 'Read the git directory and zip it.'
      if [ -n "$2" ]; then
          echo "The second argument exists and is not empty."
          echo "zip it $2"
          zip -q -r $2 $2 -x "$2/target/*" "$2/**/target/*" "$2/.git/*" "$2/.idea/*" "$2/.classpath/*" "$2/.project/*" "$2/**/node_modules/*"
      else
          echo "The second argument does not exist or is empty, zip all."
          for entry in ./*; do
            if [ -d $entry ]; then
              echo "zip it $entry"
              zip -q -r $entry $entry -x "$entry/target/*" "$entry/**/target/*" "$entry/.git/*" "$entry/.idea/*" "$entry/.classpath/*" "$entry/.project/*" "$entry/**/node_modules/*"
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
      for entry in "${my_array[@]}"; do
          git clone $entry
      done
      exit
      ;;
  *)
      echo 'Wrong command' "$1"
      exit
esac

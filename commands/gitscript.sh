#!/bin/bash

printf '\nThis is git directory script\n\n'

case "$1" in 
  "gitrepourl")
      echo 'Read git remote entries.'
      echo 'Read ./git/config url from all projects and create git urls file gitrepos'
      cat ./*/.git/config | grep "url = " | sort | awk '{print substr($0, 8)}' > gitrepos
      echo 'Print gitrepos'
      cat gitrepos
      exit
      ;;
  "gitrepozip")
      echo 'Read the git directory and zip it.'
      search_dir=.
      for entry in "$search_dir"/*; do
        if [ -d $entry ]; then
          echo "zip it $entry"
          zip -q -r $entry $entry -x "$entry/target/*" "$entry/**/target/*" "$entry/.git/*" "$entry/.idea/*" "$entry/.classpath/*" "$entry/.project/*" "$entry/**/node_modules/*"
        fi
      done
      exit
      ;;
  *)
      echo 'Wrong command' "$1"
      exit
esac

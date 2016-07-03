#!/bin/bash
WINDOWSLOCK=/home/vkoshura/.windows.lock
RESULTS=/home/vkoshura/tests.results
USRFILE=/home/vkoshura/spelbuildbot.usr
ARCH=/home/vkoshura/windowslogs.7z

if [ -f "$WINDOWSLOCK" ]; then
  if [ -f "$RESULTS" ]; then
    while IFS= read -r LINE || [[ -n "$LINE" ]]; do
      [[ "$LINE" =~ \[[[:space:]]{7}OK[[:space:]]\][[:space:]](.+)[[:space:]]\(.+\) ]]
      if [ -n "${BASH_REMATCH[1]}" ]; then
        mysql -u root -pXXXXXXXX -e "insert into pose_mediawiki.unittests (testname) select * from (select '"${BASH_REMATCH[1]}"') as t where not exists (select 1 from pose_mediawiki.unittests where testname = '"${BASH_REMATCH[1]}"');"
        mysql -u root -pXXXXXXXX -e "update pose_mediawiki.unittests set windows=1 where testname = '"${BASH_REMATCH[1]}"';"
      fi
      [[ "$LINE" =~ \[[[:space:]]{2}FAILED[[:space:]]{2}\][[:space:]](.+)[[:space:]]\(.+\) ]]
      if [ -n "${BASH_REMATCH[1]}" ]; then
        mysql -u root -pXXXXXXXX -e "insert into pose_mediawiki.unittests (testname) select * from (select '"${BASH_REMATCH[1]}"') as t where not exists (select 1 from pose_mediawiki.unittests where testname = '"${BASH_REMATCH[1]}"');"
        mysql -u root -pXXXXXXXX -e "update pose_mediawiki.unittests set windows=0 where testname = '"${BASH_REMATCH[1]}"';"
      fi
    done < "$RESULTS"
    if [ -f "$USRFILE" ]; then 
      if [ -f "$ARCH" ]; then
        while IFS='' read -r LINE || [[ -n "$LINE" ]]; do
         mutt -a "$ARCH" -s "SPEL Build Bot: Windows Report" "$LINE" < "$RESULTS"
        done < "$USRFILE"
      fi
    fi
    rm "$ARCH"
    rm "$RESULTS"
    rm "$WINDOWSLOCK"
  fi
fi

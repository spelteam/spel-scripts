#!/bin/bash

CWD=$(pwd)
LOGFILE=/home/vkoshura/spelbuild.log
TESTSFILE=/home/vkoshura/spelbuildtests.log
USRFILE=/home/vkoshura/spelbuildbot.usr
LOCKFILE=/home/vkoshura/spelbuild.lock
TESTSSUMMARYFILE=/home/vkoshura/testssummary.log
SEPARATETESTFILE=/home/vkoshura/separatetest.log
LOGS=/home/vkoshura/linuxlogs.7z
ERRORFLAG=0

if mkdir "$LOCKFILE"; then
  echo "Start SPEL Build"
else
  exit 1
fi

cd /home/vkoshura/pose/

echo -e "Start build:\n\n" > "$LOGFILE"

hg pull &>> "$LOGFILE"
if [ $? -eq 0 ]; then
  hg up &>> "$LOGFILE"
  if [ $? -eq 0 ]; then
    cd build
    make clean &>> "$LOGFILE"
    if [ $? -eq 0 ]; then
      cmake ../src/ &>> "$LOGFILE"
      if [ $? -eq 0 ]; then
        make -j2 &>> "$LOGFILE"
        if [ $? -eq 0 ]; then
          cd tests
          ./speltests &> "$TESTSFILE"
          if [ -f "$TESTSFILE" ]; then
            echo -e "Tests Summary:\n\n" > $TESTSSUMMARYFILE
            while IFS= read -r LINE || [[ -n "$LINE" ]]; do
              [[ "$LINE" =~ (\[[-=[:alpha:][:space:]]{10}\].+) ]]
              if [ -n "${BASH_REMATCH[1]}" ]; then
                echo -e "${BASH_REMATCH[1]}" >> $TESTSSUMMARYFILE
              fi
              if [ -f "$SEPARATETESTFILE" ]; then
                rm "$SEPARATETESTFILE"
              fi
              [[ "$LINE" =~ \[[[:space:]]RUN[[:space:]]{6}\][[:space:]](.+) ]]
              if [ -n "${BASH_REMATCH[1]}" ]; then
                mysql -u root -pXXXXXXXX -e "insert into pose_mediawiki.unittests (testname) select * from (select '"${BASH_REMATCH[1]}"') as t where not exists (select 1 from pose_mediawiki.unittests where testname = '"${BASH_REMATCH[1]}"');"
                ./speltests --gtest_filter="${BASH_REMATCH[1]}" &> "$SEPARATETESTFILE" 
                if [ -f "$SEPARATETESTFILE" ]; then
                  while IFS= read -r LINE || [[ -n "$LINE" ]]; do
                    [[ "$LINE" =~ \[[[:space:]]{7}OK[[:space:]]\][[:space:]](.+)[[:space:]]\(.+\) ]]
                    if [ -n "${BASH_REMATCH[1]}" ]; then
                      mysql -u root -pXXXXXXXX -e "update pose_mediawiki.unittests set linux=1 where testname = '"${BASH_REMATCH[1]}"';"
                      break
                    fi
                    [[ "$LINE" =~ \[[[:space:]]{2}FAILED[[:space:]]{2}\][[:space:]](.+)[[:space:]]\(.+\) ]]
                    if [ -n "${BASH_REMATCH[1]}" ]; then
                      mysql -u root -pXXXXXXXX -e "update pose_mediawiki.unittests set linux=0 where testname = '"${BASH_REMATCH[1]}"';"
                      break
                    fi
                  done < "$SEPARATETESTFILE" 
                fi
              fi
            done < "$TESTSFILE"
          fi
        else
          ERRORFLAG=4
        fi
      else
        ERRORFLAG=3
      fi
    else
      ERRORFLAG=2
    fi
  else
    ERRORFLAG=1
  fi
else
  ERRORFLAG=1
fi

if [ "$ERRORFLAG" -eq 0 ]; then
  STATUS="SUCCESSFULL"
elif [ "$ERRORFLAG" -eq 1 ]; then
  STATUS="FAILED: Repository update failed"
elif [ "$ERRORFLAG" -eq 2 ]; then
  STATUS="FAILED: Clean failed"
elif [ "$ERRORFLAG" -eq 3 ]; then
  STATUS="FAILED: CMake rebuild failed"
elif [ "$ERRORFLAG" -eq 4 ]; then
  STATUS="FAILED: SPEL rebuild failed"
else
  STATUS="FAILED: Unknown reason"
fi

if [ -f "$LOGS" ]; then
  rm "$LOGS"
fi

if [ "$ERRORFLAG" -eq 0 ]; then
  if [ -f "$TESTSFILE" ]; then
    7z a "$LOGS" "$LOGFILE" "$TESTSFILE" 
    if [ -f "$LOGS" ]; then
      if [ -f "$USRFILE" ]; then
        while IFS='' read -r LINE || [[ -n "$LINE" ]]; do
          if [ -f "$TESTSSUMMARYFILE" ]; then
            mutt -a "$LOGS" -s "SPEL Build Bot: Build Report: $STATUS" -- "$LINE" < "$TESTSSUMMARYFILE" 
          else
            echo -e "Build complete\n" | mutt -a "$LOGS" -s "SPEL Build Bot: Build Report: $STATUS" -- "$LINE"
          fi
        done < "$USRFILE"
      fi
    fi
  else
    7z a "$LOGS" "$LOGFILE"
    if [ -f "$LOGS" ]; then
      if [ -f "$USRFILE" ]; then 
        while IFS='' read -r LINE || [[ -n "$LINE" ]]; do
          echo -e "Tests log is not present" | mutt -a "$LOGS" -s "SPEL Build Bot: Build Report: $STATUS" -- "$LINE"
        done < "$USRFILE"
      fi
    fi
  fi
else
  7z a "$LOGS" "$LOGFILE"
  if [ -f "$LOGS" ]; then
    if [ -f "$USRFILE" ]; then 
      while IFS='' read -r LINE || [[ -n "$LINE" ]]; do
        echo -e "Tests log is not present" | mutt -a "$LOGS" -s "SPEL Build Bot: Build Report: $STATUS" -- "$LINE"
      done < "$USRFILE"
    fi
  fi
fi
if [ -f "$LOGS" ]; then
  rm "$LOGS"
fi
if [ -f "$LOGFILE" ]; then
  rm "$LOGFILE"
fi
if [ -f "$TESTSFILE" ]; then
  rm "$TESTSFILE"
fi
if [ -f "$TESTSSUMMARYFILE" ]; then
  rm "$TESTSSUMMARYFILE"
fi
if [ -f "$EPARATETESTFILE" ]; then
  rm "$SEPARATETESTFILE"
fi
rm -r "$LOCKFILE"

cd "$CWD"


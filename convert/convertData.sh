#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
ALL='false'

while getopts a: FLAG
do
    case "${FLAG}" in
        a) ALL='true'
           break
           ;;
        *) echo "Wrong flag!"
    esac
done

if [[ $ALL == 'true' ]]
then
    PERSON_DIR=$2
    PERSON_DIR=$(echo "$PERSON_DIR" | sed 's:/*$::')
    PEOPLE_ARR=("$PERSON_DIR"/*)
else
    PERSON_DIR=$1
    PERSON_DIR=$(echo "$PERSON_DIR" | sed 's:/*$::')
    PEOPLE_ARR=("$PERSON_DIR")
fi

for PERSON in "${PEOPLE_ARR[@]}"
do
    if [[ -d "$PERSON" && ! -L "$PERSON" ]]
    then
        POSES=("$PERSON"/*)

        for POSE in "${POSES[@]}"
        do
            if [[ -d "$POSE" && ! -L "$POSE" ]]
            then
	            "$SCRIPT_DIR/../local_extract/local_extract.sh" "$POSE"
	            "$SCRIPT_DIR/toASL.sh" "$POSE"
            fi
        done
    fi
done

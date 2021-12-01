#!/bin/bash

if [[ $(rosversion -d) != "noetic" ]]
then
    echo "Your ROS version is not supported!"
    exit 1
fi

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
                DIR="$POSE/smartphone_video_frames"
                python3 "$SCRIPT_DIR/asl_to_ros.py" --input_path "$DIR" --output_path "$DIR/data.bag"
            fi
        done
    fi
done

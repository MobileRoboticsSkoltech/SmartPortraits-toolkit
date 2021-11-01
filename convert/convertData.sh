#!/bin/bash

SCRIPT_DIR=$(dirname $(readlink -f $0))
ALL='false'

while getopts a: FLAG
do
    case "${FLAG}" in
        a) ALL='true'
    esac
done

if [[ $ALL == 'true' ]]
then
    PERSON_DIR=$2
    PERSON_DIR=$(echo "$PERSON_DIR" | sed 's:/*$::')
    PERSON_DIR=$PERSON_DIR/*
else
    PERSON_DIR=$1
    PERSON_DIR=$(echo "$PERSON_DIR" | sed 's:/*$::')
fi

for PERSON in $PERSON_DIR
do
    if [[ -d "$PERSON" && ! -L "$PERSON" ]]
    then
        POSES=$PERSON/*

        for POSE in $POSES
        do
            if [[ -d "$POSE" && ! -L "$POSE" ]]
            then
                echo $POSE
	            ../local_extract/local_extract.sh $POSE
	            ./toASL.sh $POSE
            fi
        done
    fi
done

#!/bin/bash

# This script runs a docker instance and mounts the given directory as
# /root in the instance. This means we need to be careful where this script is
# run, especially since the docker instance has root privilages on everything 
# in the mounted directory.

# Because of some issues with docker, any output from the docker instance is
# always written to a file named 'output' (i.e. if you want to save the output,
# copy this file somewhere before running this script again).

if [ $# -ne 4 ]
then
	echo "dockerscript <repo directory> <tests directory> <name of test file> <output file>"
	exit
fi

# Absolute path to the repo directory
DIR=$1

# Absolute path to any test files
TESTS=$2

# Name of testfile
TESTFILE=$3

# File created for writing output
OUTPUT=${4}

# Image to use
IMAGE="root/grader"

## Option functionality for stringing together multiple commands. It seems
## to work unless we add a command like `cat "abc" > file`. Either the quotes
## or the redirect mess it up (escaping one or both didn't seem to help. Since
## it's likely some testcases will want to use `>`, `<`, or quotes, we'll have 
## do this using files instead.
##COMMAND=""
##OFS=$IFS
##IFS=';'
##read -ra TEMP <<< "$EXE"
##IFS=$OFS
##for command in "${TEMP[@]}"
##do
##	COMMAND="$COMMAND su -c \"/home/launch.sh $command\" root;"
##done
##echo "COMMAND=$COMMAND"

# -v mounts take DIR:LOC and mounts DIR at LOC
# -i keeps stdin open
# -t makes a pseudo-tty DO NOT INCLUDE THIS IF WE WANT TO RUN IN THE BACKGROUND *AND* REDIRECT TO A FILE
# -n=false disables networking on the container
# Run it in the background to cut off infinite loops
# command format is `su -c <command> <user to run as>`
COMMAND="/home/launch.sh $TESTFILE"
DOCKERID=$DIR/dockerID_$OUTPUT
echo "COMMAND=$COMMAND"
echo "OUTPUT=$OUTPUT"
echo "DIR=$DIR"
echo "---"
rm -f $DOCKERID
echo "---"
sudo docker run -i -v $DIR:/repo -v $TESTS:/testfiles $IMAGE su -c "$COMMAND" root &> $OUTPUT &
echo "---"

# Sleep for X seconds. This should be enough time for a test to finish.
sleep 1

# First line of output is the ID of the docker instance.
FIRST=$(head -n 1 $DOCKERID)
echo "FIRST=$FIRST"
echo "lbaasdf"

# If it is still running, show no mercy and kill it.
# Okay, a little bit of mercy
sudo docker stop -t 1 $FIRST &>/dev/null
echo "lbaasdf"
sudo docker kill $FIRST &>/dev/null
echo "lbaasdf"
rm -f $DOCKERID &>/dev/null
echo "lbaasdf"


# check the running docker instances
#RUNNING=$(sudo docker ps | tail -n +2)
#echo "RUNNING=$RUNNING"

#readarray -t LINES <<< "${RUNNING}"
#for line in "${LINES[@]}"
#do
#	INSTANCE=$(echo $line | cut -d ' ' -f 1)
#	#echo "instance=$INSTANCE"
#	sudo docker stop -t 1 $INSTANCE &>/dev/null
#	sudo docker kill $INSTANCE &>/dev/null
#done

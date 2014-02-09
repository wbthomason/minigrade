#!/bin/bash

# This script runs a docker instance and mounts the given directory as
# /root in the instance. This means we need to be careful where this script is
# run, especially since the docker instance has root privilages on everything 
# in the mounted directory.

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

# -v mounts take DIR:LOC and mounts DIR at LOC
# -i keeps stdin open
# -t makes a pseudo-tty DO NOT INCLUDE THIS IF WE WANT TO RUN IN THE BACKGROUND *AND* REDIRECT TO A FILE
# -n=false disables networking on the container
# Run it in the background to cut off infinite loops
# command format is `su -c <command> <user to run as>`
COMMAND="/home/launch.sh $TESTFILE"
DOCKERID=$DIR/dockerID_$OUTPUT
#echo "COMMAND=$COMMAND"
#echo "OUPUT=$OUTPUT"
#echo "DIR=$DIR"
rm -f $DOCKERID
sudo docker run -cidfile $DOCKERID -i -v $DIR:/repo -v $TESTS:/testfiles $IMAGE su -c "$COMMAND" root 1> $OUTPUT 2>/dev/null &

# Sleep for X seconds. This should be enough time for a test to finish.
sleep 1

# If it is still running, show no mercy and kill it.
CID=$(head -n 1 $DOCKERID)
#echo $CID

sudo docker stop -t 1 $CID &>/dev/null
sudo docker kill $CID &>/dev/null

# Override any bad exit statuses from the stop and kill commands
exit 0 

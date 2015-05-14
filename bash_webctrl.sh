#!/bin/bash
# The following script is used in cases where the server with
# access to webctrl is different the the server running smap.
#
# usage: ./script [getValue/setValue] [bacnet server address] [device path] [state | OPTIONAL]
# state is only necessary if we are setting a value.

RSA_KEY="/home/abeltran2/.ssh/id_rsa_flash"
SERVER="mercury"
PYTHON="python"
DIRECTORY="/home/abeltran2/git/webCTRLsMap/webctrlSOAP.py"
FLAG=$1
SERVERADDR=$2
BACADDRPATH=$3
NEWVAL=$4

#echo ssh -i $RSA_KEY -t $SERVER $PYTHON $DIRECTORY $FLAG $SERVERADDR $BACADDRPATH $NEWVAL
RETURN_VAL=$(ssh -i $RSA_KEY -t $SERVER $PYTHON $DIRECTORY $FLAG $SERVERADDR "$BACADDRPATH" $NEWVAL)
echo $RETURN_VAL

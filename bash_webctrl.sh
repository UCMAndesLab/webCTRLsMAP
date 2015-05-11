#!/bin/bash

RSA_KEY="/home/lsequeira2/.ssh/id_rsa_smap"
SERVER="lsequeira2@mercury.ucmerced.edu"
PYTHON="python"
DIRECTORY="/home/lsequeira2/svn/misc/trunk/lsequeira2/webctrlSOAP.py"
FLAG=$1
SERVERADDR=$2
BACADDRPATH=$3
NEWVAL=$4

RETURN_VAL=$(ssh -i $RSA_KEY -t $SERVER $PYTHON $DIRECTORY $FLAG $SERVERADDR $BACADDRPATH $NEWVAL)
echo $RETURN_VAL

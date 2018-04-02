#!/bin/bash
if [ $# -lt 2 ]; then
  echo "Error: Missing arguments:"
  echo "usage: analyze.sh DIRECTORY SHORTCUT [1|2|3]"
  exit 1
fi

# command line arguments
DIRECTORY=$1
SHORTCUT=$2
COMMAND=$3

# folders
BMP=${DIRECTORY}/${SHORTCUT}colored-roots/
ROOT=${DIRECTORY}/${SHORTCUT}white-roots/
SKEL=${DIRECTORY}/${SHORTCUT}skeletons/
COLS=${DIRECTORY}/${SHORTCUT}colored-skeletons/

# commands
C1="python analyze-background.py $BMP $ROOT"
C2="fiji -batch skeleton.ijm $ROOT:$SKEL"
C3="python analyze-skeleton.py $BMP $SKEL $COLS $COLS${SHORTCUT}barevnekostry.csv"

if [ $COMMAND ] ; then
	# if the third argument was provided, run only specific script
	case "$COMMAND" in
		1) $C1 ;;
		2) $C2 ;;
		3) $C3 ;;
	    *) echo Error: Third argument must be one of numbers 1, 2 or 3.; exit 1;;
	esac
else
	# if the third argument was not provided run all scripts
	$C1
	$C2
	$C3
fi


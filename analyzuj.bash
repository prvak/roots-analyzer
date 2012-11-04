#!/bin/bash
if [ $# -lt 2 ]; then
  echo "Error: Missing arguments:"
  echo "usage: analyzuj.bash SLOZKA ZKRATKA [1|2|3]"
  exit 1
fi

# command line arguments
SLOZKA=$1
ZKRATKA=$2
PRIKAZ=$3

# folders
BMP=$SLOZKA/${ZKRATKA}prekreslene/
ROOT=$SLOZKA/${ZKRATKA}cernobile/
SKEL=$SLOZKA/${ZKRATKA}kostry/
COLS=$SLOZKA/${ZKRATKA}barevnekostry/

# commands
C1="python analyzuj-pozadi.py $BMP $ROOT"
C2="fiji -batch kostra.ijm $ROOT:$SKEL"
C3="python analyzuj-kostru.py $BMP $SKEL $COLS $COLS${ZKRATKA}barevnekostry.csv"

if [ $PRIKAZ ] ; then
	# if the third argument was provided, run only specific script
	case "$PRIKAZ" in
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


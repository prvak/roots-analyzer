#!/bin/bash
if [ $# -lt 2 ]; then
  echo "Missing arguments:"
  echo "usage: analyzuj.bash SLOZKA ZKRATKA"
  exit 1
fi

# command line arguments
SLOZKA=$1
ZKRATKA=$2

# folders
BMP=$SLOZKA/${ZKRATKA}prekreslene/
ROOT=$SLOZKA/${ZKRATKA}cernobile/
SKEL=$SLOZKA/${ZKRATKA}kostry/
COLS=$SLOZKA/${ZKRATKA}barevnekostry/

# run the commands
python analyzuj-pozadi.py $BMP $ROOT
fiji -batch kostra.ijm "$ROOT:$SKEL"
python analyzuj-kostru.py $BMP $SKEL $COLS $COLS${ZKRATKA}barevnekostry.csv

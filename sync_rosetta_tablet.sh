#!/bin/bash

SERVERPATH=/home/levtim/Dropbox/scans/RosettaTablet/
LOCALPATH=/home/levtim/RosettaTablet

rsync -avzh --del $SERVERPATH $LOCALPATH

python sound_download.py

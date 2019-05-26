#!/bin/bash

# copyNAS2EOS_dat.sh
#
# Created by: Kalpanie Madara Liyanage
#
# Usage: Copy QC8 runs from NAS to EOS

RUN=$(printf "%06d" $1)
DIRECTORY=/eos/cms/store/group/dpg_gem/comm_gem/QC8_Commissioning/run$RUN
src=/data/bigdisk/GEM-Data-Taking/GE11_QC8/Cosmics/run$RUN
COUNT=0
COPY=0

if [ ! -d "$DIRECTORY" ]; then
echo "Creating Directory: "$DIRECTORY
mkdir $DIRECTORY
else
echo "Existing Directory: "$DIRECTORY
fi

#Get the list of files to send
FILES=$(ssh gemuser@gem904qc8daq ls ${src}"_Cosmic_CERNQC8"*".dat")

#Tell the user which group of files will be copied
echo "The list of files to be copied is:"
for f in $FILES\;
do
echo $f
((COUNT++))
done

#Copy the files
echo "Copying files"
for f in $FILES;
do
echo "Processing " $f
scp "gemuser@gem904qc8daq:$f" $DIRECTORY
done

#Confirm for the user that the files were copied
echo "Showing the contents of " $DIRECTORY
ls -1 | wc -l $DIRECTORY"/"*".dat"
COPIED=$(ls $DIRECTORY)


for c in $COPIED;
do
((COPY++))
done

if [ $COUNT -eq $COPY ]; then
echo "All files have been copied!"
else
echo "Some files are missing!"
fi

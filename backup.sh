#!/bin/sh

#This script will backup all files listed in 
#backup_list file, with backup path being the 
#first listed path.

FILE="$HOME/scripts/backup_list"

PATHS=($(awk '/\// {	if (NR > 1) { print $1;} }' $FILE))

DIR=$(awk '/Path/ {print $2;}' $FILE)
DIR=${DIR/\~/$HOME}

if [ ! -d $DIR ] 
then
	mkdir $DIR
	echo "Backup directory \"$DIR\" created"
fi


for i in "${PATHS[@]}"
do
	#replace ~ with $HOME
	i=${i/\~/$HOME}
	
	if [ -d $DIR ] 
	then
		echo "Writing $i"		
		cp -R $i $DIR
	else
		echo "Path $DIR does not exist, no action taken"
	fi
done	


exit 0;

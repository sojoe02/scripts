#!/bin/bash

#This script will write a predefined header to all
#files listed in a source directory as pointed to by this file.
#backup_list file, with backup path being the 
#first listed path.

#print usage if no arguments are provided:
[[ -n "$2" ]] || { echo "Usage: insert_license.sh <license-file> <project-directory>" ; exit 0 ; }

#define license file and source dir:
LICENSE_FILE=$1
SOURCE_DIR=$2

#define temporary files:
SRC_TMP='out.tmp'
LICENSE_TMP='lic.tmp'

#search for relevant source files using a regular expression pattern:
EXT='(\.h$)|(\.cpp$)|(\.hpp$)|(\.lua$)'

#language specific extension expressions:
C_EXT='(\.h$)|(\.cpp$)|(\.hpp$)'
LUA_EXT='(\.lua$)'
BASH_EXT='(\.sh$)'

#define sed scripts that remove licenses based om language comment types:
SED_C='/\/\/--begin-license/,/\/\/--end-license/d'
SED_LUA='/----begin-license/,/----end-license/d'

#Insert or update relevant files license information:
#and take newline and spaces into account:
find $SOURCE_DIR -type f -not -path "${SOURCE_DIR}build/*" -not -path "${SOURCE_DIR}bin/*" | grep -P $EXT | 
while IFS='' read -r file; do
	#write licensing file to all c type source files:	
	if [[ $file =~ $C_EXT ]]; then
		echo "file, $file, is c type file, applying license..."
		#remove obsolete license:
		sed -e $SED_C $file > $SRC_TMP
		#insert language specific commenting:
		sed -e "s/^/\/\//" $LICENSE_FILE > $LICENSE_TMP
		#concatonate license and sourcefile:
		cat $LICENSE_TMP $SRC_TMP > $FILE
	#now do it all again for the Lua files:
	elif [[ $file =~ $LUA_EXT ]]; then
		echo "file, $file, is lua type file, applying license.."
		sed -e $SED_LUA $file > $SRC_TMP
		sed -e "s/^/--/" $LICENSE_FILE > $LICENSE_TMP
		cat $LICENSE_TMP $SRC_TMP > $FILE
	#just as a precaustion do an echo if the file isn't know (can be used to detect errors in the EXT regex):
	else
		echo "file, $file type not known, not applying license!"
	fi
done

#cleanup temporary files:
[[ -f $SRC_TMP ]] || { rm $SRC_TMP; }
[[ -f $LICENSE_TMP ]] || { rm $LICENSE_TMP; }

exit 0


#!/bin/bash
ReplaceSSID ()
{

	echo "replacing ssid" 
}


AddSSID ()
{
	echo "nothing to sseeee" 
}


#This script 
#Warning:: this will assume that the networks SSID is the first entry of each of the given entries!

#define the paths:
WPA_PATH='loco_wifi'
TMP_FILE='/home/sojoe/scripts/out.tmp'
WLAN='wlp3s0'

SSID=''
SECURITY=''

#Define the Sed scripts:
SED_REPLACE="SSID"
SED_NETWORK="network={}"

#First scan the network:
#iwlist "wlp3s0" scanning > $TMP_FILE

#Find the instances of existing SSIDs and save it to an array:
NETWORKS=($(grep -s 'ESSID' $TMP_FILE | sed 's/\s*ESSID:"//' | sed 's/"//' | sort | uniq)  )

for i in "${NETWORKS[@]}"
do 
	echo $i
done

#echo "The security protocol (Wpa or Wep):"
#SEC_OPTIONS=(WEP WPA)
#select opt in ${SEC_OPTIONS[@]}; do
#	SECURITY=($opt)
#	break
#done

PS3="Choose the network you want to connect to: "
select opt in ${NETWORKS[@]}; do	
	[[ $opt > ${#NETWORKS[@]-1} ]] || { echo "Invalid Option... Goodbye!"; exit; }
	SSID=($opt)
	break
done 

#Detect encryption:
LINE_NUMBER=($(grep -n "ESSID:\"$SSID\"" $TMP_FILE | cut -d : -f 1 ) )
LINE_NUMBER=`expr $LINE_NUMBER - 1`

ENCRYPTION=$(awk "NR==$LINE_NUMBER, NR==$LINE_NUMBER" $TMP_FILE)
ENCRYPTION=$(sed -s 's/\s*Encryption\skey://' <<< $ENCRYPTION)

#Detect the encryption type:
if [ "$ENCRYPTION" == "on" ]; then
	
	awk "NR>$LINE_NUMBER" $TMP_FILE |
	while read line; do 
		if grep -q -n "WPA2" <<< $line; then
			echo  $line
			echo "Encryption is WPA" 
		elif grep -q -n "WEP" <<< $line; then
			echo $line
			echo "Encryption is WEP"
		fi	
		
		#continue until next Encryption information, for the next SSID on the list!
		if grep -q -n "Encryption" <<< $line; then
			break;
		fi
	done

fi

ReplaceSSID
#echo "line number : $LINE_NUMBER"

#echo "$SSID"

#Get the linenumber of a specific SSID ... if it exists:
#grep -n '\sssid="locokit"' $WPA_PATH | cut -d : -f 1



#!/bin/bash

#This script 
#Warning:: this will assume that the networks SSID is the first entry of each of the given entries!

#define the paths:
WPA_PATH='loco_wifi.tmp'
WPA_ORIG='loco_wifi'
TMP_FILE='/home/sojoe/scripts/out.tmp'
WLAN='wlp3s0'

#Make a temporary file to manipulate on:
`cp $WPA_ORIG $WPA_PATH`

#Catch the currently active terminal:
TTY=$(tty)

#Network variabes:
SSID=''
SECURITY=''
PASSPHRASE=''
GROUP=''
CIPHER=''
PRIORITY='10'
PROTOCOL='WPA2'

#---------------------------------------------#
#FUNCTIONS:
#---------------------------------------------#
#Connection function:
Connect() 
{
 	echo "l"
}

#Add an entry to the wpa path:
Add_Entry()
{

	echo "network={" >> $WPA_PATH

	echo -e "\tssid=\"$SSID\"" >> $WPA_PATH

	for i in "${CELL[@]}" 
	do
		#insert the correct cipher(s):
		if grep -q -P "^(\s*Pairwise\sCiphers)" <<< $i; then

			if [ -z "$CIPHER" ]; then
				#CIPHER=$(echo -e "\tpairwise=")
				CIPHER="pairwise="
				CIPHER="$CIPHER$(sed -e 's/Pairwise\sCiphers\s.*\s:\s//' <<< $i)"
			else
				CIPHER="$CIPHER $(sed -e 's/Pairwise\sCiphers\s.*\s:\s//' <<< $i)"
			fi
		fi

		if grep -q -P "^(\s*Group\sCipher)" <<< $i; then
			
			if [ -z "$GROUP" ]; then
				GROUP="group="
				GROUP="$GROUP$(sed -e 's/Group\sCipher\s:\s//' <<< $i)"

			else 
				GROUP="$GROUP $(sed -e 's/Group\sCipher\s:\s//' <<< $i)"
			fi

		fi

		if grep -q -P "IE:\.*WPA2\s" <<< $i; then
			PROTOCOL="WPA2"
		fi

		if grep -q -P "IE:\.*WPA\s" <<< $i; then
			PROTOCOL="WPA"
		fi
	
		#echo "$i"
	done

	echo -e "\tproto=$PROTOCOL" >> $WPA_PATH
	

	if [ -n "$CIPHER" ]; then
		echo -e "\t$CIPHER" >> $WPA_PATH
	fi

	if [ -n "$GROUP" ]; then
		echo -e "\t$GROUP" >> $WPA_PATH
	fi

	local priority=0	
	echo "Enter the priority press enter for default(10):"
	read priority < $TTY
	if [ -n "$priority" ]; then
		PRIORITY=$priority
	fi
	echo -e "\tpriority=$PRIORITY" >> $WPA_PATH

	local pass=1234
	echo "Enter the networks passphrase:"
	read pass < $TTY
	echo -e "\tpsk=$pass" >> $WPA_PATH

		

	echo "}" >> $WPA_PATH

	exit
}

#Wait Animation function:
Waiter()
{
	local pid=$1
	local delay=0.25
	
	while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
		local temp=${sprinstr#?}
		printf "."
		sleep $delay
	done

	echo "$CELL"
	printf "\n"
}


#---------------------------------------------#


#First scan the network:
echo "Scanning for visible networks:"
#(`iwlist "wlp3s0" scanning > $TMP_FILE`)& 
#Waiter $!

if grep -s 'No\sscan\sresults' $TMP_FILE; then
	echo "Nothing on scan... exiting."
	exit
fi

#Find the instances of existing SSIDs and save it to an array:
NETWORKS=($(grep -s 'ESSID' $TMP_FILE | sed 's/\s*ESSID:"//' | sed 's/"//' | sort | uniq)  )

#for i in "${NETWORKS[@]}"
#do 
#	echo $i
#done

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

CELL=''

#Detect the encryption type:
if [ "$ENCRYPTION" == "on" ]; then

	while read line; do 
		if grep -q -n "WPA2" <<< $line; then
			SECURITY='WPA2'
			echo "Encryption is WPA2"	
		elif grep -q -n "WPA" <<< $line; then
			SECURITY='WPA'
		elif grep -q -n "WEP" <<< $line; then
			SECURITY='WEP'
		fi	
		
		#[[ "$PRINT" == "on" ]] || { echo $line; }
		#continue until next Cell information, for the next SSID on the list!
		if grep -q -n "Cell\s[0-9]" <<< $line; then break; fi

	done < <(awk "NR>$LINE_NUMBER" $TMP_FILE )

else 
	SECURITY='none'

fi

echo "-----------------------------------------------"
echo "Chosen Network Information:"
echo "-----------------------------------------------"

#Retrieve the cell information:
COUNTER=1
#echo $LINE_NUMBER

CELL[0]=$(awk "NR==$LINE_NUMBER-4" $TMP_FILE | sed -e 's/^\s*//' -e '/^$/d' )

while read -r line; do
	
	if grep -q -P "Cell\s(\d+)" <<< $line; then break; fi

	if grep -q -v -P "^(\s*IE:\sUnknown:)" <<< $line; then
		CELL[$COUNTER]="$line"
		COUNTER=$(expr $COUNTER + 1)
	fi

done < <(awk "NR>=$LINE_NUMBER-3" $TMP_FILE ) #process substitution
	
#Print Cell information:
( IFS=$'\n'; echo "${CELL[*]}" )
echo "-----------------------------------------------"
Add_Entry
#Now check if the network allready has an entry in wpa_supplicant.conf:

#Get the linenumber of a specific SSID ... if it exists:
LINE_NUMBER=($(grep -n "ssid=\"$SSID\"" $WPA_PATH | cut -d : -f 1) )
OPTIONS=''
BOOL=false
if [ $LINE_NUMBER ]; then 
	echo "Network is known"
	OPTIONS=('Re-Connect' 'Reenter Password' 'Remove and Replace')
	PS3="Make your choice..."
	select opt in "${OPTIONS[@]}"; do

		case "$REPLY" in

			1 )
				echo "Reconnecting"
				break
				;;
			2 )
				echo "New Passphrase:"
				#Unleash the powers of awk and sed:
				_line_number=$LINE_NUMBER
				while read -r line; do
				   	
					_line_number=$(expr $_line_number + 1)
					if grep -q -P "^(\s*psk=)" <<< $line; then
						#echo "Line number of passphrase stuff: $_line_number"
						echo "Please input a new Passphrase:"
						read input < $TTY	
						sed -i "$_line_number s/.*/\tpsk=$input/" $WPA_PATH
						break

					elif grep -q -P "^(\s*})" <<< $line; then
						echo "No existing passphrase found."
						echo "Please input a Passphrase:"
						#insert new line:
						read input < $TTY
						_line_number=$(expr $LINE_NUMBER + 1)
						sed -i "$LINE_NUMBER s/.*/&\\n/g" $WPA_PATH
						sed -i "$_line_number s/.*/\tpsk=$input/" $WPA_PATH
						break
					fi
										
				done  < <(awk "NR>$LINE_NUMBER" "$WPA_PATH" )
				
				break
				;;

				
			3 )
				echo "Removing the existing entry, get ready for a replacement prompt:"
				#first remove the old entry entirely:
				_line_number=$(expr $LINE_NUMBER - 1)
				sed -i "$_line_number,$_line_number d" $WPA_PATH
				sed -i "/ssid=\"$SSID\"/,/}/d" $WPA_PATH

				Add_Entry $SSID	

				break
				;;
				
    		* ) echo "Invalid option. Try another one."; continue;;


		esac
	done

	
else
	echo "Network is unknown, adding a new one!"


fi



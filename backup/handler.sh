#!/bin/bash
# Default acpi script that takes an entry for all actions

case "$1" in
	button/power)
		case "$2" in
			PBTN|PWRF)
				logger 'PowerButton pressed'
				;;
			*)
				logger "ACPI action undefined: $2"
				;;
		esac
		;;
	button/sleep)
		case "$2" in
			SLPB|SBTN)
				logger 'SleepButton pressed'
				;;
			*)
				logger "ACPI action undefined: $2"
				;;
		esac
		;;
	ac_adapter)
		case "$4" in
			00000000)
				;;
			00000001)
				;;
			*)
				;;
		esac
		;;
	ibm/hotkey)
		case "$2" in
			LEN0068:00)
				case "$4" in
					00004011)
						su sojoe -c 'xrandr -d :0.0 --output LVDS1 --auto --primary --output HDMI3 --off --output HDMI2 --off'
						;;
					00004010)
						su sojoe -c 'xrandr -d :0.0 --output LVDS1 --off --output HDMI2 --auto --primary --output HDMI3 --auto --right-of HDMI2' 
						#DISPLAY=:0.0 su sojoe -c 'i3-msg workspace 2'&
						#sleep 1
						#su sojoe -c 'i3-msg move workspace to output HDMI3'
						;;
				esac
				;;
		esac
		;;
	battery)
		case "$2" in
			BAT0)
				case "$4" in
					00000000)
						logger 'Battery online'
						;;
					00000001)
						logger 'Battery offline'
						;;
				esac
				;;
			CPU0)
				;;
			*)  logger "ACPI action undefined: $2" ;;
		esac
		;;
	button/lid)
		case "$3" in
			close)
				DISPLAY=:0.0 su sojoe -c /usr/bin/i3lock &	
				#usr/bin/sleep 1 &
				logger 'LID closed' 
				;;
			open)
				logger 'LID opened'
				;;
			*)
				logger "ACPI action undefined: $3"
				;;
		esac
		;;
	*)
		logger "ACPI group/action undefined: $1 / $2" &

		;;
esac

# vim:set ts=4 sw=4 ft=sh et:

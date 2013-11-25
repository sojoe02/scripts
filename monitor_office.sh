#!/bin/bash

IN="LVDS1"
EXT="VGA1"


if (xrandr | grep "$EXT disconnected") ; then
	xrandr --output $IN --auto --output $EXT --off 
elif [ $# -gt 0 ]; then
	if [ $1 == "off" ]; then
		xrandr --output $IN --auto --output $EXT --off 
	fi
else
	xrandr --output $IN --auto --primary --output $EXT --auto --right-of $IN
	sleep(2)	
	feh --bg-scale /home/sojoe/dropbox/wallpaper-2684320.jpg
fi

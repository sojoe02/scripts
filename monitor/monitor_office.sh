#!/bin/bash

IN="eDP1"
EXT="DP2-3"
EXT2="DP2-2"

if (xrandr | grep "$EXT disconnected") ; then
	xrandr --output $IN --auto --output $EXT --off --outout $EXT2 --off
	xmodmap ~/.Xmodmap
elif [ $# -gt 0 ]; then
	if [ $1 == "off" ]; then
		xrandr --output $IN --auto --output $EXT --off --output $EXT2 --off
		modmap ~/.Xmodmap
	fi
else
	xrandr --output $IN --auto --output $EXT --auto --right-of $IN --primary
        sleep 2s	
	xrandr --output $IN --auto --output $EXT2 --auto --right-of $EXT
	sleep 1s
	xmodmap ~/.XmodmapErgo
	#feh --bg-scale /home/sojoe/dropbox/wallpaper-2684320.jpg
fi

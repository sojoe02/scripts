#!/bin/sh
#
# ~/.xinitrc
#
# Executed by startx (run your window manager from here)



# Make sure this is before the 'exec' command or it won't be sourced.
[ -f ~/.xprofile ] && source ~/.xprofile
    

if [ -d /etc/X11/xinit/xinitrc.d ]; then
  for f in /etc/X11/xinit/xinitrc.d/*; do
    [ -x "$f" ] && . "$f"
  done
  unset f
fi

if [ -s ~/.Xmodmap ]; then 
	xmodmap ~/.Xmodmap
fi
# eval $(gpg-agent --daemon) &
#udiskie &
#exec awesome
exec i3

# exec gnome-session
# exec startkde
# exec startxfce4
# ...or the Window Manager of your choice

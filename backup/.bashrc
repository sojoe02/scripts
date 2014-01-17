#
# ~/.bashrc
#

#svim () { sudo vim -u /home/sojoe/.vimrc @$ };          

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
# PS1='[\u@\h \W]\$ '
PS1='\[\033[00;32m\]\u\[\033[00;32m\]@\[\033[00;32m\]\h\[\033[00;34m\][\[\033[00;31m\]\w\[\033[00;34m\]]\[\033[00;32m\]> \[\033[00m\]'

export EDITOR=/usr/bin/vim
export TERMINAL=/usr/bin/xterm

XDG_DATA_HOME=/home/sojoe/scripts
XDG_CONFIG_HOME=/home/sojoe/.config

	
if [ -d $HOME/bin ] ; then
	PATH="$PATH:$HOME/bin"
fi

if [ -d $HOME/scripts ] ; then
	PATH="$PATH:$HOME/scripts"
fi

export PATH

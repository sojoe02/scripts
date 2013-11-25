#!/bin/bash
apt-get update
apt-get purge xserver* -y
apt-get purge ^x11 -y
apt-get purge ^libx -y
apt-get purge ^lx -y
apt-get purge samba* -y
apt-get autoremove -y
apt-get upgrade -y
apt-get clean

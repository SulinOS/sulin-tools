#!/bin/sh
if [ ! -d "$1/dev/pts" ]
then
  mount -B /dev/ "$1/dev"
  mount -B /dev/pts "$1/dev/pts"
  mount -B /sys/ "$1/sys"
  mount -B /proc/ "$1/proc"
  mount -B /run "$1/run"
  exit
fi
chroot $1 dbus-daemon --system
chroot $1 scom --print --debug &
chroot $1

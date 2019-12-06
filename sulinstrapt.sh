#!/bin/sh
#sulinstrapt betiği ile sulinos chroot oluşturabilirsiniz veya diskinize kurulum yapabilirsiniz
sulin="$1"
if which inary
then
  echo "inary not found"
  exit 1
fi
if [ -d "$sulin" ]
then
  echo "$sulin alreay exist"
fi
inary ar sulin https://master.dl.sourceforge.net/project/sulinos/SulinRepository/inary-index.xml -D$sulin
inary it -c system.base -D$sulin -y --ignore-scom
cp -prf $sulin/usr/share/baselayout/* $sulin/etc/

#!/bin/sh
sulin="$1"
if [ ! -f "/usr/bin/inary" ]
then
  echo "inary not found"
  exit 1
fi
if [ -d "$sulin" ]
then
  echo "$sulin alreay exist"
fi
inary ar sulin https://downloads.sourceforge.net/project/sulinos/SulinRepository/inary-index.xml -D$sulin
inary it -c system.base -D$sulin -y --ignore-scom

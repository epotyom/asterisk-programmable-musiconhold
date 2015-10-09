#!/usr/bin/env bash
#echo $BALANCE > /tmp/balance
BALANCE=$1
if [ ! -e /tmp/$BALANCE.mp3 ] ; then
	gtts-cli -t "Ваш баланс $BALANCE руб" -l ru /tmp/$BALANCE.mp3
fi
echo /tmp/$BALANCE.mp3

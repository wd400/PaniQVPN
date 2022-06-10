#!/bin/bash
hs=$(/bin/echo "$1" | /bin/sed -n 's/\([a-z2-7]\{16\}\)/\1/p')
priv=$(/bin/echo "$2" | /bin/sed -n 's/\([A-Z2-7]{22}\)/\1/p')
if /usr/bin/test -n "$hs" ; then
    /bin/echo HidServAuth "$1".onion "$2" >> /etc/tor/torrc
	/bin/echo 0
else
	/bin/echo 1
fi

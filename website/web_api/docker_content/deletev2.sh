#!/bin/bash
hs=$(/bin/echo "$1" | /bin/sed -n 's/\([a-z2-7]\{16\}d\)/\1/p')
if /usr/bin/test -n "$hs" ; then
	/bin/sed -i "/^HidServAuth $1.onion/d" /etc/tor/torrc
	/bin/echo 0
else
	/bin/echo 1
fi

#!/bin/bash
hs=$(/bin/echo "$1" | /bin/sed -n 's/\([a-z2-7]\{55\}d\)/\1/p')
priv=$(/bin/echo "$2" | /bin/sed -n 's/\([A-Z2-7]{52}\)/\1/p')
if /usr/bin/test -n "$hs" -a /usr/bin/test -n "$priv" ; then
	/bin/echo "$1:descriptor:x25519:$2" > "/var/lib/tor/onion_auth/$1.auth_private"
	/bin/echo 0
else
	/bin/echo 1
fi

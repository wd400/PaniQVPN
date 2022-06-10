#!/bin/bash
hs=$(/bin/echo "$1" | /bin/sed -n 's/\([a-z2-7]\{55\}d\.onion\)/\1/p')
if /usr/bin/test -n "$hs" ; then
	/bin/rm "/var/lib/tor/onion_auth/$1.auth_private"
	/bin/echo 0
else
	/bin/echo 1
fi

#!/bin/bash
/bin/echo "Content-type: text/plain"
/bin/echo ""


read -r POST_STRING


oLang=$LANG oLcAll=$LC_ALL
LANG=C LC_ALL=C
bytlen=${#POST_STRING}
LANG=$oLang LC_ALL=$oLcAll

if  /usr/bin/test  "$bytlen" -ge 200 -o "$CONTENT_LENGTH" -ge 200; then
    /bin/echo 1
    exit 1
fi

if /usr/bin/test "$SERVER_PROTOCOL" != 'HTTP/1.1' -o  "$REQUEST_METHOD" != 'POST' -o "$SCRIPT_NAME" != '/addUser.sh' -o  "$SERVER_PORT" != "8080"  ; then
    /bin/echo 1
    exit 1
fi

saveIFS=$IFS
IFS='=&'
parm=($POST_STRING)
IFS=$saveIFS

#check length
oLang=$LANG oLcAll=$LC_ALL
LANG=C LC_ALL=C
bytlen="${#parm[@]}"
LANG=$oLang LC_ALL=$oLcAll
if  /usr/bin/test  bytlen -ne 6 ; then
    /bin/echo 1
    exit 1
fi


for ((i=0; i<${#parm[@]}; i+=2))
do
    declare var_"${parm[i]}"="${parm[i+1]}"
done


#url decoding 
var_user=$(/bin/echo "$var_user" | /bin/sed -e "s/%\([0-9A-F][0-9A-F]\)/\\\\\x\1/g" | /usr/bin/xargs -0 /bin/echo -e)
var_pass=$(/bin/echo "$var_pass" | /bin/sed -e "s/%\([0-9A-F][0-9A-F]\)/\\\\\x\1/g" | /usr/bin/xargs -0 /bin/echo -e)
var_duration=$(/bin/echo "$var_duration" | /bin/sed -e "s/%\([0-9A-F][0-9A-F]\)/\\\\\x\1/g" | /usr/bin/xargs -0 /bin/echo -e)

#regex
var_user=$(/bin/echo "$var_user" | /bin/sed -n 's/^\([A-Za-z0-9]\{20\}\)$/\1/p')
var_pass=$(/bin/echo "$var_pass" | /bin/sed -n 's/^\(\$6\$[A-Za-z0-9\\.\/]\{16\}\$[A-Za-z0-9\\.\/]\{86\}\)$/\1/p')
var_duration=$(/bin/echo "$var_duration" | /bin/sed -n 's/^\([1-9][0-9]\{9,10\}\)$/\1/p')
echo regex
echo $var_user
echo $var_pass
echo $var_duration

if /usr/bin/test -n "$var_duration" -a -n "$var_pass" -a -n "$var_user" ; then
    if /bin/echo "/usr/bin/sudo /usr/sbin/userdel -f \"$var_user\"" | /usr/bin/sudo /usr/bin/at "$(/bin/date -d @"$var_duration" '+%H:%M %F')"; then
        if /usr/bin/sudo /usr/sbin/useradd -p "$var_pass" "$var_user" --no-log-init --no-create-home --no-user-group --shell /bin/false ; then
            /bin/echo 0
            exit 0
        fi
    fi
fi

/bin/echo 1
exit 1
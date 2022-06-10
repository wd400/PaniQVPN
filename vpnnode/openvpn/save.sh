#!/bin/bash
JOB=$(atq |  awk '{ print $1; }')
TIMESTAMPS=($(atq |  awk '{ print $3, $4, $5; }' |  date -f -  '+%s' ))
i=0
for jobid in $JOB;
do echo "echo '`at -c $jobid | tail -2`' | at \`date -d '@${TIMESTAMPS[i]}' '+%H:%m %D'\`";
i=$((i+1));
 done


 echo 'echo <<< EOL'
 cat /etc/shadow
 echo 'EOL > /etc/shadow'

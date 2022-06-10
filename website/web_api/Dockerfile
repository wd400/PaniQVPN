FROM python:3
RUN apt-get update && apt-get upgrade -y && apt-get install -y tor sudo
RUN mkdir -p /app/
WORKDIR /app
RUN pip install cmake
ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
COPY docker_content/ .

RUN chmod +x addv2.sh && chmod +x deletev2.sh && chmod +x restart.sh && echo "www-data    ALL=(root) NOPASSWD:/usr/sbin/service tor restart,/usr/sbin/killall tor" >> /etc/sudoers

RUN mkdir -p /var/lib/tor/onion_auth  && chown debian-tor /var/lib/tor/onion_auth

RUN echo "\n\
ControlPort 9051\n\
ClientOnionAuthDir /var/lib/tor/onion_auth \n\
SocksPort 9050 IsolateDestAddr OnionTrafficOnly IsolateDestPort NoDNSRequest\n\
#SocksPort 9000 IsolateDestAddr OnionTrafficOnly IsolateDestPort NoDNSRequest\n\
#SocksPort 9001 IsolateDestAddr OnionTrafficOnly IsolateDestPort NoDNSRequest\n\
#SocksPort 9002 IsolateDestAddr OnionTrafficOnly IsolateDestPort NoDNSRequest\n\
#SocksPort 9003 IsolateDestAddr OnionTrafficOnly IsolateDestPort NoDNSRequest\n\
#SocksPort 9004 IsolateDestAddr OnionTrafficOnly IsolateDestPort NoDNSRequest\n\
HashedControlPassword 16:35666162EA79D542609E5C6B036D428A8B52EA82A6B532C25E77FA13C1\n\
#Sandbox 1\n\
NoExec 1\n\
ClientOnly 1\n\
SafeSocks 1" >> /etc/tor/torrc

RUN (/usr/bin/crontab -l 2>/dev/null; /bin/echo "*/5 * * * * /usr/bin/find /app/captcha/ -type f -path '/app/captcha/*.png' -mmin +5 -exec /bin/rm -rf {} \;") | /usr/bin/crontab -

#RUN apt-get update && apt-get -y install cron
CMD /usr/sbin/service tor start && /usr/sbin/service cron start && python3 -u api.py
#uvicorn api:app --host 0.0.0.0  --log-level debug 
#python3 -u init.py &
#CMD gunicorn api:app --reload -b 0.0.0.0:8000 --log-level debug --timeout 90
#  -k uvicorn.workers.UvicornWorker
#,"--forwarded-allow-ips","nginx"
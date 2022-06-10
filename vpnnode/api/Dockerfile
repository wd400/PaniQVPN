FROM python:3

RUN pip install --no-cache-dir flask stem gunicorn uvicorn uvloop httptools requests requests_tor requests[socks]
RUN apt update && apt install -y tor
#RUN pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
COPY api.py .

#COPY files /var/lib/tor/
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
Sandbox 1\n\
NoExec 1\n\
ClientOnly 1\n\
SafeSocks 1" >> /etc/tor/torrc

RUN mkdir -p /var/lib/tor/onion_auth/ && chown debian-tor /var/lib/tor/onion_auth && \
echo "auttahjeahn2rqoss47wfh6wczmquqqca2cr4rxufrhmtrgphy2oz3yd:descriptor:x25519:SAA6TG6QML2ZRBSEEYYDHFVCWJALVTUYF62UQ3MYHFVIRMTB6J4A" > /var/lib/tor/onion_auth/1.auth_private

EXPOSE 5000

CMD service tor start && python3 -u api.py
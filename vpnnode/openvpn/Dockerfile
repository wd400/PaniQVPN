FROM ubuntu:18.04

#install openvpn
RUN apt-get update && apt-get install -y cmake gcc libtool libssl-dev make ninja-build git net-tools at lighttpd sudo tor iptables tcpdump
#RUN update-alternatives --config iptables
RUN git clone --branch OQS-OpenSSL_1_1_1-stable https://github.com/open-quantum-safe/openssl.git /opt/openssl
WORKDIR /tmp
RUN git clone --branch main https://github.com/open-quantum-safe/liboqs.git && cd liboqs && mkdir build && cd build && cmake -GNinja -DCMAKE_INSTALL_PREFIX=/opt/openssl/oqs .. && ninja && ninja install

WORKDIR /opt/openssl/
RUN ./Configure no-shared linux-x86_64 -lm && make -j

RUN apt-get remove -y cmake gcc libtool libssl-dev make ninja-build git openssh-client

COPY pq-openvpn-linux-staged.tar.gz /tmp/
WORKDIR /
RUN tar xvzf /tmp/pq-openvpn-linux-staged.tar.gz

#RUN sed "s/aaa=.*/aaa=xxx/g" /etc/ssl/openssl.cnf keyEncipherment

#add openvpn config
COPY server.ovpn /usr/local/openvpn/etc/
COPY keys /usr/local/openvpn/etc/keys
RUN chmod 600 /usr/local/openvpn/etc/keys/server.key
RUN chmod 600 /usr/local/openvpn/etc/keys/ta.key
#COPY keypass.pass /usr/local/openvpn/etc/keypass.pass
#RUN chmod 600 /usr/local/openvpn/etc/keypass.pass


#add api service
COPY distaddUser.sh /usr/lib/cgi-bin/addUser.sh
COPY lighttpd.conf /etc/lighttpd/lighttpd.conf
RUN chmod +x /usr/lib/cgi-bin/addUser.sh && echo "www-data    ALL=(root) NOPASSWD:/usr/sbin/useradd, /usr/sbin/userdel, /usr/sbin/chpasswd, /usr/bin/at" >> /etc/sudoers


#configure tor proxy
RUN echo SocksPort 9150 PreferSOCKSNoAuth >> /etc/tor/torrc

EXPOSE 1194/tcp
#EXPOSE 1194/tcp
EXPOSE 8080

RUN echo 'VirtualAddrNetwork 10.192.0.0/10\n\
AutomapHostsOnResolve 1\n\
DNSPort 10.8.0.1:53530\n\
TransPort 10.8.0.1:9040'  >> /etc/tor/torrc

COPY iptables.sh /tmp/
RUN chmod +x /tmp/iptables.sh
#RUN sudo /tmp/iptables.sh && rm /tmp/iptables.sh
#RUN sudo iptables -A INPUT -i eth0 -m state --state ESTABLISHED,RELATED -j ACCEPT
#RUN ufw reject from 2001:db8:0:123::/64 to any
#
CMD /tmp/iptables.sh 

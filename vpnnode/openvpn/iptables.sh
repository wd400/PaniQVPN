#!/bin/bash
echo "[loading rules]"

# Load the Kernel modules
#modprobe ip_tables
#modprobe ip_nat_ftp
#modprobe ip_nat_irc
#modprobe ip_conntrack_irc
#modprobe ip_conntrack_ftp
#modprobe iptable_filter
#modprobe iptable_nat
#modprobe ipt_REJECT
#modprobe xt_recent
#modprobe ipt_mac

# Forward


# Remove all rules
iptables -F
iptables -t nat -F
iptables -X

# Default Policy
#iptables -P INPUT DROP
#iptables -P OUTPUT DROP
#iptables -P FORWARD DROP

# Allow Established and Related connetcions
# iptables -A INPUT -i eth0 -m state --state ESTABLISHED,RELATED -j ACCEPT
# iptables -A OUTPUT -o eth0 -m state --state ESTABLISHED,RELATED -j ACCEPT
# iptables -A INPUT -i tun0 -m state --state ESTABLISHED,RELATED -j ACCEPT
# iptables -A OUTPUT -o tun0 -m state --state ESTABLISHED,RELATED -j ACCEPT
# iptables -A FORWARD -i tun0 -o lo -m state --state ESTABLISHED,RELATED -j ACCEPT
# iptables -A FORWARD -i tun0 -o lo -j ACCEPT
# iptables -A FORWARD -i lo -o tun0 -m state --state ESTABLISHED,RELATED -j ACCEPT
# iptables -A FORWARD -i lo -o tun0 -j ACCEPT

# Allow localhostloop
# iptables -A INPUT -i lo -j ACCEPT
# iptables -A OUTPUT -o lo -j ACCEPT

# Allow connections for api
iptables -A INPUT -i eth0 -p tcp -m tcp --dport 8080 -j ACCEPT

iptables -A INPUT -i eth0 -p udp -m udp --dport 1194 -j ACCEPT
# Allow connections for the TOR PORTS
iptables -A INPUT -i eth0 -p tcp -m tcp -m multiport --dports 9001,9030 -j ACCEPT

# Allow connections for OPENVPN
# iptables -A INPUT -i eth0 -p tcp -m tcp --dport 443 -j ACCEPT
# iptables -A INPUT -i tun0 -s 10.8.0.0/24 -p udp -m udp --dport 123 -j ACCEPT
# iptables -A INPUT -i tun0 -s 10.8.0.0/24 -p udp -m udp --dport 53 -j ACCEPT
# iptables -A INPUT -i tun0 -s 10.8.0.0/24 -p tcp -m tcp -j ACCEPT

# # transparent Tor proxy
iptables -A INPUT -i tun0 -s 10.8.0.0/24 -m state --state NEW -j ACCEPT
# iptables -t nat -A PREROUTING -i tun0 -p udp --dport 53 -s 10.8.0.0/24 -j DNAT --to-destination 10.8.0.1:53530
iptables -t nat -A PREROUTING -i tun0 -p tcp -s 10.8.0.0/24 -j DNAT --to-destination 10.8.0.1:9040
# iptables -t nat -A PREROUTING -i tun0 -p udp -s 10.8.0.0/24 -j DNAT --to-destination 10.8.0.1:9040

iptables -A OUTPUT ! -o lo ! -d 127.0.0.1 ! -s 127.0.0.1 -p tcp -m tcp --tcp-flags ACK,FIN ACK,FIN -j DROP
iptables -A OUTPUT ! -o lo ! -d 127.0.0.1 ! -s 127.0.0.1 -p tcp -m tcp --tcp-flags ACK,RST ACK,RST -j DROP

#&& rm /tmp/iptables.sh && \\
mkdir -p /dev/net && mknod /dev/net/tun c 10 200
/etc/init.d/lighttpd start &
service atd start &
(sleep 5 && service tor restart) &
/usr/local/openvpn/sbin/openvpn --config /usr/local/openvpn/etc/server.ovpn


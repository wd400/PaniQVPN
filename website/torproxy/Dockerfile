FROM dperson/torproxy
RUN  mkdir -p /var/lib/tor/onion_auth && chmod 700 /var/lib/tor/onion_auth && \\
      echo ClientOnionAuthDir /var/lib/tor/onion_auth >> /etc/tor/torrc
CMD service tor restart
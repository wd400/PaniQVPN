# PaniQVPN

- "website" directory to launch the website (sudo docker-compose up and the site is available on Tor, regenerate a unique service key if you want to launch it).  
- "vpnnode" a VPN exit node (sudo docker-compose up), you can start as many as you want, normally everything syncs automatically (automatic management of the appearance and disappearance of nodes).   
  
Payment system via Monero, captcha integration and trial mode  

Bugs are to be expected, the service has never been put in production  

Based on https://github.com/microsoft/PQCrypto-VPN  


![Alt text](website/nginx/www/scheme.png?raw=true "Screen")

![Alt text](website.png?raw=true "Screen")

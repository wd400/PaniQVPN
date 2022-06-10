FROM nginx:1.19
RUN apt update && apt -y install nginx-extras libnginx-mod-http-headers-more-filter
COPY my_nginx.conf /etc/nginx/sites-available/
COPY nginx.conf /etc/nginx/nginx.conf
#COPY server.crt /etc/nginx/
#COPY server.key /etc/nginx/
COPY www /www/
RUN echo PrivateNetwork=yes >> /lib/systemd/system/nginx.service
# RUN mkdir -p /etc/nginx/sites-enabled/\
#     && ln -s /etc/nginx/sites-available/my_nginx.conf /etc/nginx/sites-enabled/\
#     && rm /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]

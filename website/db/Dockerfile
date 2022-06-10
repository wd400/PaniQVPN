FROM postgres:12
RUN apt-get update && apt-get -y install postgresql-12-cron
COPY postgresql.conf /etc/postgresql/postgresql.conf
EXPOSE 5432
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
FROM postgres:13.3-alpine

WORKDIR /usr/src

COPY . .

CMD ["psql", "-U postgres -f db_script.sql"]
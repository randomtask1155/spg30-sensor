


## crontab for pi user

```
@reboot python3 /home/pi/spg30-sensor/sense.py > /home/pi/sense.log 2>&1
0 * * * * /home/pi/spg30-sensor/clean-db.sh > /home/pi/clean-db.log 2>&1
```


## install graphana and import the dashboard `gas-sensor-dashboard.json`

## install postgresql

```
sudo apt install postgresql libpq-dev postgresql-client
```

### update /etc/postgresql/9.x/main/pg_hba.conf

```
# IPv4 local connections:
host    gas     all        127.0.0.1/32                 trust
host    all             all             127.0.0.1/32            md5
```

### create tables in postgres

```
/usr/bin/psql -U postgres -h 127.0.0.1 postgres -c "create database gas"
/usr/bin/psql -U postgres -h 127.0.0.1 postgres -c "create table readings ( time timestamp, co2 int, tvoc int);"
```

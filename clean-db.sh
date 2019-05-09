#!/bin/bash


/usr/bin/psql -U postgres -h 127.0.0.1 gas -c "delete from readings where time < now() - interval '24 hour'"
/usr/bin/psql -U postgres -h 127.0.0.1 gas -c "vacuum full readings"

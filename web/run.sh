#!/bin/sh

gunicorn \
	--bind 0.0.0.0:$WEB_PORT \
	--reload \
	--workers=$WORKERS_NUMBER \
	--access-logfile=- \
	--access-logformat='%(t)s %({X-Real-IP}i)s %(s)s %(m)s %(U)s %(q)s' \
	wsgi:app

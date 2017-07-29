#!/bin/sh

# Generate the basic auth user/password
echo "$AUTH_USERNAME:$AUTH_PASSWORD_HASHED" > .htpasswd

# Replace the env in the template
envsubst '$WEB_PORT' < default.template > default.conf

# Launch nginx
nginx -g 'daemon off;'

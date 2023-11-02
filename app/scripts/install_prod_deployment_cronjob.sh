#!/bin/sh

# Run this as the production user to install the cronjob which manages prod deployment.

job="*/2 * * * * /bin/sh ${HOME}/app/scripts/deploy.sh PROD >> ${HOME}/log/deployment.log 2>&1"

(crontab -l 2>/dev/null ; echo "$job") | sort -u | crontab -

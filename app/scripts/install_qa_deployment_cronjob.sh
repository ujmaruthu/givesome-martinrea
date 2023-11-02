#!/bin/sh

# Run this as the QA user to install the cronjob which manages QA deployment.

job="*/2 * * * * /bin/sh ${HOME}/app/scripts/deploy.sh QA >> ${HOME}/log/deployment.log 2>&1"

(crontab -l 2>/dev/null ; echo "$job") | sort -u | crontab -

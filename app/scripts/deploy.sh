#!/bin/sh

# shellcheck disable=SC2086  # It's fine that `$app_directories` is not quoted; we want it to expand.
# shellcheck disable=SC1091  # `../venv/bin/activate` should be there, no need to check it.

# This script is run by a cron job on the deployment server to update the project.
#
# One can also run this manually, then it's useful to pass the --always flag, so that the update gets run
# even if the app would already be up to date, e.g:
#
# $ ./deploy.sh PROD --always
#
# OR
#
# $ ./deploy.sh --always QA
#
# This relies on the following file structure on the server:
#
# . (user's home directory)
# ├── app/ (the project's repo)
# │  ├── app/ (the primary app and source code of the project)
# │  │  └── __init__.py
# │  ├── app_tests/ (optional: tests for the app)
# │  │  └── __init__.py
# │  ├── admin_app/ (optional: 2nd app for the project, e.g. an admin app)
# │  │  └── __init__.py
# │  └── admin_app_tests/ (optional: tests for the 2nd app)
# │     └── __init__.py
# ├── venv/ (the project's virtual environment)
# └── run/
#    └── uwsgi_reload (touching this file soft reloads the web server)

# The branch that this repo should be deployed from.
deployment_branch=master

# The top-level python packages of the project, these are removed on the server so that they
# won't clash with the installed versions in site-packages.
app_directories='givesome givesome_admin givesome_tests'

# The app name used to send Slack messages
app_name='Givesome'

error () {
    echo Error! "$@" 1>&2 && exit 1
}

starting_dir="$PWD"

cd ~/app/ || error 'Expecting app/ to be in the home directory.'
git fetch --quiet --tags origin "$deployment_branch" || error 'app/ was not a Git repository.'

if [ "$1" = 'PROD' ] || [ "$2" = 'PROD' ]; then
    latest_tag="$(git describe --abbrev=0 --match='v[0-9]*' --exclude='v[0-9]*-qa' "origin/${deployment_branch}")"
    deploy_env="PROD"
elif [ "$1" = 'QA' ] || [ "$2" = 'QA' ]; then
    latest_tag="$(git describe --abbrev=0 --match='v[0-9]*-qa' "origin/${deployment_branch}")"
    deploy_env="QA"
else
    error 'Expecting either QA or PROD as the argument.'
fi

commit_of_latest_tag="$(git rev-parse "${latest_tag}^{}")"
current_commit="$(git rev-parse HEAD)"

[ "$commit_of_latest_tag" = "$current_commit" ] && [ "$1" != '--always' ] && [ "$2" != '--always' ] && exit 0

changelog="$(git tag --list $latest_tag -n9999)"

git reset --hard "$latest_tag" \
&& git ls-files -z $app_directories | git update-index --skip-worktree -z --stdin \
&& rm -rf $app_directories \
&& . ../venv/bin/activate \
&& ~/.local/bin/poetry install --no-dev --no-root \
&& pip install --disable-pip-version-check wheels/*.whl \
&& python manage.py collectstatic --noinput \
&& python manage.py migrate \
&& python manage.py init_project \
&& python manage.py shell -c "from shuup.core import cache; cache.clear()" \
&& python manage.py crontab add \
&& touch ../run/uwsgi_reload \
&& deactivate \
&& curl -X POST -H 'Content-type: application/json' --data "{\"text\": \":rocket: $app_name $deploy_env has been updated to $latest_tag!\n\`\`\`$changelog\`\`\`\"}" https://hooks.slack.com/services/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

status="$?"
cd "$starting_dir" || exit 1
exit "$status"

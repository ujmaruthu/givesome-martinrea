# Givesome Marketplace

[![CI](https://github.com/shuup/givesome-marketplace/actions/workflows/ci.yml/badge.svg)](https://github.com/shuup/givesome-marketplace/actions)

### Clone the project

1. Make a directory for the project, e.g. `givesome-marketplace/`.

2. Clone the repo under that directory **to a directory called `app/`**:
```
$ git clone --recurse-submodules git@github.com:shuup/givesome-marketplace.git app
```

You will end up with about the following directory structure:
\
(The `shuup-packages/` directory location is not mandatory.)
```
.
├── givesome-marketplace/
│  ├── app/ (https://github.com/shuup/givesome-marketplace)
│  ├── var/ (will get autocreated when you save media files in the project)
│  └── venv/ (if you are not using pyenv or something else)
└── shuup-packages/ (optional packages that you install with `pip install -e` when needed)
   ├── shuup/ (https://github.com/shuup/shuup)
   └── shuup-multivendor/ (https://github.com/shuup/shuup-multivendor)
```

### Setting up a project for development

0. If you don't yet have Poetry and Make, see their respective instructions below.

1. Create a new virtual environment, you can also let Poetry create one for you if you prefer.

2. Create a (preferably PostgreSQL) database for the project.

3. `$ cp .env.template .env` and set your database credentials there.

4. Set up your development environment:
```
$ make
```

5. Start the app:
```
$ python manage.py runserver
```

#### Install Poetry to your system

You don't have to install Poetry inside the project's venv, this way you can use the same version
for all projects and Poetry's dependencies won't clash with the projects'.
\
Guide: https://github.com/python-poetry/poetry#installation

After installing Poetry you need to configure it to use your Shuup PyPI credentials:
```
$ poetry config http-basic.shuup <username>
```

#### Using Make

Make is used here as a convenient build tool.

If you are on Windows and don't have Make, you can get it from:
\
https://community.chocolatey.org/packages/make 
\
OR
\
http://gnuwin32.sourceforge.net/packages/make.htm

If you don't want to use Make, you can simply look up the commands from the `Makefile` and use those manually.

#### Cron jobs

This project uses [django-crontab](https://github.com/kraiz/django-crontab) to manage the cron jobs.
The cron jobs are defined in `settings.py` (`CRONJOBS`).
All the defined jobs are automatically applied when the application is updated.

## Copyright

Copyright (c) 2012-2021 by Shuup Commerce Inc. <support@shuup.com>

Shuup is International Registered Trademark & Property of Shuup Commerce Inc.,
Business ID: BC1126729,
Business Address: 1500 West Georgia Suite 1300, Vancouver, BC, V6G-2Z6, Canada.

## License

This source code is licensed under the Shuup Commerce Inc -
SELF HOSTED SOFTWARE LICENSE AGREEMENT executed by Shuup Commerce Inc, DBA as SHUUP®
and the Licensee.

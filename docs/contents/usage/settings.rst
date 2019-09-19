.. _settings:

Settings
========

All settings for the project can be found in ``src/drc/conf``.

The file ``local.py`` overwrites settings from the base configuration.

From environment variables
--------------------------

The settings listed below are pulled from environment variables.

* ``SITE_ID``: the ID of the site. Should be 1 unless you serve multiple
  domains with the same database/codebase.

* ``SECRET_KEY``: a strong secret key, used in various cryptographic process.
  We recommend generating one using the `secret key generator`_. Required.

* ``MIN_UPLOAD_SIZE``: the minimal request body that should be allowed,
  defaults to 4Gb. Note that this must also be set in the webserver config,
  at least for the ``/api/v1/enkelvoudinginformatieobjecten`` endpoints.

  This envvar is consumed by the Docker-compose nginx config, uwsgi server and
  Django itself.

**Database**

The database credentials on Docker have sane defaults.

* ``DB_NAME``: name of the database to connect with.
* ``DB_USER``: username to connect to the database as.
* ``DB_PASSWORD``: password to connect to the database with.
* ``DB_HOST``: hostname of the database.
* ``DB_PORT``: port number of the database, set if using a non-default.

**Misc**

* ``ADMINS``: a comma-separated list of e-mail addresses. They receive e-mails
  for crash reports.

* ``ALLOWED_HOSTS``: a comma-separated list of domain names and/or ip-addresses
  where the project is hosted. By default *anything* is allowed.

* ``IS_HTTPS``: used to build fully qualified URLs. Defaults to 'yes'.


* ``SENTRY_DSN``: Sentry project URL for error monitoring. If provided, crash
  reports are sent to Sentry.

.. _secret key generator: https://www.miniwebtool.com/django-secret-key-generator/

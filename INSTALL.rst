============
Installation
============

The project is developed in Python using the `Django framework`_. There are 3
sections below, focussing on developers, running the project using Docker and
hints for running the project in production.

.. _Django framework: https://www.djangoproject.com/


Development
===========


Prerequisites
-------------

You need the following libraries and/or programs:

* `Python`_ 3.4 or above
* Python `Virtualenv`_ and `Pip`_
* `PostgreSQL`_ 9.1 or above, with postgis extension
* `Node.js`_
* `npm`_

.. _Python: https://www.python.org/
.. _Virtualenv: https://virtualenv.pypa.io/en/stable/
.. _Pip: https://packaging.python.org/tutorials/installing-packages/#ensure-pip-setuptools-and-wheel-are-up-to-date
.. _PostgreSQL: https://www.postgresql.org
.. _Node.js: http://nodejs.org/
.. _npm: https://www.npmjs.com/


Getting started
---------------

Developers can follow the following steps to set up the project on their local
development machine.

Obtain source
^^^^^^^^^^^^^^

You can retrieve the source code using the following command:

   .. code-block:: bash

     $ git clone git@github.com:maykinmedia/gemma-documentregistratiecomponent.git

**Note:** You can also use the HTTPS syntax:

   .. code-block:: bash

     $ git clone https://github.com/maykinmedia/gemma-documentregistratiecomponent.git

Setting up virtualenv
^^^^^^^^^^^^^^^^^^^^^^

1. Go to the project directory:

   .. code-block:: bash

        $ cd gemma-documentregistratiecomponent

2. Create the virtual environment:

   .. code-block:: bash

       $ virtualenv -p /usr/bin/python3.x ./env

3. Source the activate script in your virtual environment to enable it:

   .. code-block:: bash

       $ source env/bin/activate

4. Install all the required libraries:

   .. code-block:: bash

       (env) $ pip install -r requirements/dev.txt

Installing the database
^^^^^^^^^^^^^^^^^^^^^^^^

1. Copy ``src/drc/conf/local_example.py`` to ``src/drc/conf/local.py``:

   .. code-block:: bash

       $ cp src/drc/conf/local_example.py src/drc/conf/local.py

2. Edit ``local.py`` and place correct values for the presented settings.

   .. code-block:: python

       DATABASES = {
           'default': {
               'ENGINE': 'django.contrib.gis.db.backends.postgis',
               'NAME': <name_of_your_pgSQL_db>,
               'USER': <user_that_can_access_db>,
               'PASSWORD': <password_of_this_user>,
               'HOST': '',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
               'PORT': '',  # Set to empty string for default.
           }
       }

3. Launch the migration process

   .. code-block:: bash

     (env) $ python src/manage.py migrate

**Note:** Make sure PostGIS is enabled in your database.
You can do it with a single SQL command:

   .. code-block:: bash

     CREATE EXTENSION postgis;

**Note:** If you are making any other local, machine specific, changes, add them to
``local.py``.


Running server
^^^^^^^^^^^^^^^^^^^^^^^^

1. Collect the static files:

   .. code-block:: bash

       (env) $ python src/manage.py collectstatic --link

2. Create a superuser to access the management interface:

   .. code-block:: bash

       (env) $ python src/manage.py createsuperuser

3. You can now run your installation and point your browser to the address
given by this command:

   .. code-block:: bash

       (env) $ python src/manage.py runserver


Generate the API schema
---------------------------

1. Install Javascript modules:

   .. code-block:: bash

       $ npm install

2. Launch the ``generate_schema`` script:

   .. code-block:: bash

        ./env/src/zds-schema/bin/generate_schema

3. The resulting ``openapi.yaml`` and ``swagger2.0.json`` files can be visualized with `Swagger`_

.. _Swagger: http://petstore.swagger.io/


Update installation
-------------------

When updating an existing installation:

1. Activate the virtual environment:

   .. code-block:: bash

       $ cd drc
       $ source env/bin/activate

2. Update the code and libraries:

   .. code-block:: bash

       $ git pull
       $ pip install -r requirements/dev.txt
       $ npm install
       $ gulp sass

3. Update the statics and database:

   .. code-block:: bash

       $ python src/manage.py collectstatic --link
       $ python src/manage.py migrate


Testsuite
---------

To run the test suite:

   .. code-block:: bash

       $ python src/manage.py test drc


Docker
======

The easiest way to get the project started is by using `Docker Compose`_.

1. Clone or download the code from `Github`_ in a folder like
   ``drc``:

   .. code-block:: bash

       $ git clone git@github.com:maykinmedia/gemma-mock-overigeregistratiecomponenten.git drc
       Cloning into 'drc'...
       ...

       $ cd drc

2. Start the database and web services:

   .. code-block:: bash

       $ docker-compose up -d
       Starting drc_db_1 ... done
       Starting drc_web_1 ... done

   It can take a while before everything is done. Even after starting the web
   container, the database might still be migrating. You can always check the
   status with:

   .. code-block:: bash

       $ docker logs -f drc_web_1

3. Create an admin user and load initial data. If different container names
   are shown above, use the container name ending with ``_web_1``:

   .. code-block:: bash

       $ docker exec -it drc_web_1 /app/src/manage.py createsuperuser
       Username: admin
       ...
       Superuser created successfully.

       $ docker exec -it drc_web_1 /app/src/manage.py loaddata admin_index groups
       Installed 5 object(s) from 2 fixture(s)

4. Point your browser to ``http://localhost:8000/`` to access the project's
   management interface with the credentials used in step 3.

   If you are using ``Docker Machine``, you need to point your browser to the
   Docker VM IP address. You can get the IP address by doing
   ``docker-machine ls`` and point your browser to
   ``http://<ip>:8000/`` instead (where the ``<ip>`` is shown below the URL
   column):

   .. code-block:: bash

       $ docker-machine ls
       NAME      ACTIVE   DRIVER       STATE     URL
       default   *        virtualbox   Running   tcp://<ip>:<port>

5. To shutdown the services, use ``docker-compose down`` and to clean up your
   system you can run ``docker system prune``.

.. _Docker Compose: https://docs.docker.com/compose/install/
.. _Github: https://github.com/maykinmedia/drc/


More Docker
-----------

If you just want to run the project as a Docker container and connect to an
external database, you can build and run the ``Dockerfile`` and pass several
environment variables. See ``src/drc/conf/docker.py`` for
all settings.

.. code-block:: bash

    $ docker build . && docker run \
        -p 8000:8000 \
        -e DJANGO_SETTINGS_MODULE=drc.conf.docker \
        -e DATABASE_USERNAME=... \
        -e DATABASE_PASSWORD=... \
        -e DATABASE_HOST=... \
        --name drc

    $ docker exec -it drc /app/src/manage.py createsuperuser


Staging and production
======================

Ansible is used to deploy test, staging and production servers. It is assumed
the target machine has a clean `Debian`_ installation.

1. Make sure you have `Ansible`_ installed (globally or in the virtual
   environment):

   .. code-block:: bash

       $ pip install ansible

2. Navigate to the project directory, and install the Maykin deployment
   submodule if you haven't already:

   .. code-block:: bash

       $ git submodule update --init

3. Run the Ansible playbook to provision a clean Debian machine:

   .. code-block:: bash

       $ cd deployment
       $ ansible-playbook <test/staging/production>.yml

For more information, see the ``README`` file in the deployment directory.

.. _Debian: https://www.debian.org/
.. _Ansible: https://pypi.org/project/ansible/


Settings
========

All settings for the project can be found in
``src/drc/conf``.
The file ``local.py`` overwrites settings from the base configuration.


Commands
========

Commands can be executed using:

.. code-block:: bash

    $ python src/manage.py <command>

There are no specific commands for the project. See
`Django framework commands`_ for all default commands, or type
``python src/manage.py --help``.

.. _Django framework commands: https://docs.djangoproject.com/en/dev/ref/django-admin/#available-commands

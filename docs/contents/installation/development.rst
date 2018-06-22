Development
===========

Prerequisites
-------------

You need the following libraries and/or programs:

* `Python`_ 3.4 or above
* Python `Virtualenv`_ and `Pip`_
* `PostgreSQL`_ 9.1 or above
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

        $ git clone git@github.com:maykinmedia/gemma-documentregistratiecomponent.git drc

**Note:** You can also use the HTTPS syntax:

   .. code-block:: bash

        $ git clone https://github.com/maykinmedia/gemma-documentregistratiecomponent.git drc

Setting up virtualenv
^^^^^^^^^^^^^^^^^^^^^^

1. Go to the project directory:

   .. code-block:: bash

        $ cd drc

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
               'ENGINE': 'django.db.backends.postgresql',
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

**Note:** If you are making any other local, machine specific, changes, add them to ``local.py``.


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

       (env) $ git pull
       (env) $ pip install -r requirements/dev.txt
       (env) $ npm install

3. Update the statics and database:

   .. code-block:: bash

       (env) $ python src/manage.py collectstatic --link
       (env) $ python src/manage.py migrate



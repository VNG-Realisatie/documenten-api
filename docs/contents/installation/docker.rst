Docker
======

Docker basics
-------------

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

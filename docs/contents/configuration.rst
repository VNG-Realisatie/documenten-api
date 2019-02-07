Configuration
=============

There is basic configuration required to get the project up-and-running in
a testing environment as part of a full-chain-test.

Settings from environment
-------------------------

Review the :ref:`settings` to see available settings.

.. note::

    The ``IS_HTTPS`` environment variable is a common pitfall. Set it to a
    falsy value in case you're not on HTTPS (yet). The default settings assume
    best practices, with HTTPS enabled.

Configuration in the admin
--------------------------

**Create superuser**

The admin is available on ``https://example.com/admin/``. Ensure you have a
superuser created before.

On the command line:

.. code-block:: bash

    python src/manage.py createsuperuser


**Sites**

Make sure to configure the 'Sites' and set up the correct domain. If you forget
this, internal URLs will be generated with the ``example.com`` domain, leading
to errors when integrating with other APIs.

**Credentials**

Configure 'Jwt secrets': these are the Client IDs and their shared secret that
you allow to access the API. The secret is used to protect against tampering
with authorisation tokens.


Configure 'API credentials': these are YOUR credentials to communicate with
external APIs.  If you're using ``https://api.example.com/zrc/api/v1/`` for
your ZRC, fill in that URL as 'Api root', and complete by filling in your
client ID and Secret as agreed with the external API.

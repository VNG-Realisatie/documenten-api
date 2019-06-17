=======
Plugins
=======

The DRC has a simple plugin architecture. Extra django apps can be installed
as a plugin and enabled, even in a pre-built docker-image context.

Configuration
=============

Two environment variables are relevant:

* ``PLUGINS``: a comma-separated list of app names. These are names that would
  typically go into an ``INSTALLED_APPS`` array. They must be valid python
  package/module names and be importable (see ``PLUGIN_DIRS``)

* ``PLUGIN_DIRS``: optionally specify directories to be added to the python
  path. A typical use case would be to run the DRC container with a volume
  mount containing the plugins. Comma-separated list of paths.


Plugin implementation considerations
====================================

Plugins are simply added to the list of ``INSTALLED_APPS``, at the end. Complex
configurations where the order matters are currently not supported.

No other settings are currently supported.

To initialize the plugin, you can use Django's ``django.apps.AppConfig.ready``
hook.

If you need configuration, consider using something like ``django-solo`` to
store the configuration in the database instead of custom settings.

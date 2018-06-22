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



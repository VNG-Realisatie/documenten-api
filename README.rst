============================
Documentregistratiecomponent
============================

:Version: 1.0.0-rc1
:Source: https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent
:Keywords: zaken, zaakgericht werken, GEMMA, RGBZ, DRC
:PythonVersion: 3.6

|build-status|

Referentieimplementatie van de documentregistratiecomponent (DRC).

Ontwikkeld door `Maykin Media B.V. <https://www.maykinmedia.nl>`_ in opdracht
van VNG.

Introduction
============

Binnen het Nederlandse gemeentelandschap wordt zaakgericht werken nagestreefd.
Om dit mogelijk te maken is er gegevensuitwisseling nodig. Er is een behoefte
om informatieobjecten (documenten) te relateren aan zaken.

Deze referentieimplementatie toont aan dat de API specificatie voor de
documentregistratiecomponent (hierna DRC) implementeerbaar is, en vormt een
voorbeeld voor andere implementaties indien ergens twijfel bestaat.

Deze component heeft ook een `testomgeving`_ waar leveranciers tegenaan kunnen
testen.

Documentation
=============

See ``docs/contents/installation.rst`` for installation instructions, available settings and
commands.

If you intend to develop on the component, we recommend the ``development.rst``
document, otherwise ``docker.rst`` is recommended.

See ``docs/contents/configuration.rst`` for runtime configuration.

References
==========

* `Issues <https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/issues>`_
* `Code <https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/>`_


.. |build-status| image:: http://jenkins.nlx.io/buildStatus/icon?job=gemma-documentregistratiecomponent-stable
    :alt: Build status
    :target: http://jenkins.nlx.io/job/gemma-documentregistratiecomponent-stable

.. |requirements| image:: https://requires.io/github/VNG-Realisatie/gemma-documentregistratiecomponent/requirements.svg?branch=master
     :target: https://requires.io/github/VNG-Realisatie/gemma-documentregistratiecomponent/requirements/?branch=master
     :alt: Requirements status

.. _testomgeving: https://ref.tst.vng.cloud/drc/

Licentie
========

Copyright © VNG Realisatie 2018

Licensed under the EUPL_

.. _EUPL: LICENCE.md

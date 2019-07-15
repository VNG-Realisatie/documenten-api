============================
Documentregistratiecomponent
============================

:Version: 0.1.5
:Source: https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent
:Keywords: zaken, zaakgericht werken, GEMMA, RGBZ, DRC
:PythonVersion: 3.6

|build-status|

Referentieimplementatie van de Documenten API als documentregistratiecomponent
(DRC).

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

Dit document bevat de technische documentatie voor deze component.


Contents
========

.. toctree::
    :maxdepth: 2

    contents/installation
    contents/configuration
    contents/usage
    contents/plugins
    source/drc
    contents/copyright
    contents/changelog


References
============

* `Issues <https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/issues>`_
* `Code <https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/>`_


.. |build-status| image:: http://jenkins.nlx.io/buildStatus/icon?job=gemma-documentregistratiecomponent-stable
    :alt: Build status
    :target: http://jenkins.nlx.io/job/gemma-documentregistratiecomponent-stable

.. |requirements| image:: https://requires.io/github/VNG-Realisatie/gemma-documentregistratiecomponent/requirements.svg?branch=master
     :target: https://requires.io/github/VNG-Realisatie/gemma-documentregistratiecomponent/requirements/?branch=master
     :alt: Requirements status

.. _testomgeving: https://documenten-api.vng.cloud/

==============
Documenten API
==============

:Version: 1.0.1
:Source: https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent
:Keywords: zaken, zaakgericht werken, GEMMA, RGBZ, DRC

Introductie
===========

Binnen het Nederlandse gemeentelandschap wordt zaakgericht werken nagestreefd.
Om dit mogelijk te maken is er gegevensuitwisseling nodig. Er is een behoefte
om informatieobjecten (documenten) te relateren aan bijvoorbeeld zaken.

API specificaties
=================

|lint-oas| |generate-sdks| |generate-postman-collection|

==========  ==============  ====================================================================================================================================================================================================  =======================================================================================================================  =================================================================================================================================
Versie      Release datum   API specificatie                                                                                                                                                                                      Autorisaties                                                                                                             Notificaties
==========  ==============  ====================================================================================================================================================================================================  =======================================================================================================================  =================================================================================================================================
1.0.x       n.v.t.          `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/VNG-Realisatie/gemma-documentregistratiecomponent/stable/1.0.x/src/openapi.yaml>`_,                                    `Scopes <https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/blob/stable/1.0.x/src/autorisaties.md>`_   `Berichtkenmerken <https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/blob/stable/1.0.x/src/notificaties.md>`_
                            `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/VNG-Realisatie/gemma-documentregistratiecomponent/stable/1.0.x/src/openapi.yaml>`_
                            (`verschillen <https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/compare/1.0.1..stable/1.0.x?diff=split#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.0.1       2019-12-16      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/VNG-Realisatie/gemma-documentregistratiecomponent/1.0.1/src/openapi.yaml>`_,                                           `Scopes <https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/blob/1.0.1/src/autorisaties.md>`_          `Berichtkenmerken <https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/blob/1.0.1/src/notificaties.md>`_
                            `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/VNG-Realisatie/gemma-documentregistratiecomponent/1.0.1/src/openapi.yaml>`_
                            (`verschillen <https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/compare/1.0.0...1.0.1?diff=split#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.0.0       2019-11-18      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/VNG-Realisatie/gemma-documentregistratiecomponent/1.0.0/src/openapi.yaml>`_,                                           `Scopes <https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/blob/1.0.0/src/autorisaties.md>`_          `Berichtkenmerken <https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/blob/1.0.0/src/notificaties.md>`_
                            `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/VNG-Realisatie/gemma-documentregistratiecomponent/1.0.0/src/openapi.yaml>`_
==========  ==============  ====================================================================================================================================================================================================  =======================================================================================================================  =================================================================================================================================

Zie ook: `Alle versies en wijzigingen <https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/blob/master/CHANGELOG.rst>`_

Ondersteuning
-------------

==========  ==============  ==========================  =================
Versie      Release datum   Einddatum ondersteuning     Documentatie
==========  ==============  ==========================  =================
1.x         2019-11-18      (nog niet bekend)           `Documentatie <https://vng-realisatie.github.io/gemma-zaken/standaard/documenten/index>`_
==========  ==============  ==========================  =================

Referentie implementatie
========================

|build-status| |coverage| |docker| |black| |python-versions|

Referentieimplementatie van de Documenten API. Ook wel
Documentregistratiecomponent (DRC) genoemd)

Ontwikkeld door `Maykin Media B.V. <https://www.maykinmedia.nl>`_ in opdracht
van VNG Realisatie.

Deze referentieimplementatie toont aan dat de API specificatie voor de
Documenten API implementeerbaar is, en vormt een voorbeeld voor andere
implementaties indien ergens twijfel bestaat.

Deze component heeft ook een `demo omgeving`_ waar leveranciers tegenaan kunnen
testen.

Links
=====

* Deze API is onderdeel van de `VNG standaard "API's voor Zaakgericht werken" <https://github.com/VNG-Realisatie/gemma-zaken>`_.
* Lees de `functionele specificatie <https://vng-realisatie.github.io/gemma-zaken/standaard/documenten/index>`_ bij de API specificatie.
* Bekijk de `demo omgeving`_ met de laatst gepubliceerde versie.
* Bekijk de `test omgeving <https://documenten-api.test.vng.cloud/>`_ met de laatste ontwikkel versie.
* Rapporteer `issues <https://github.com/VNG-Realisatie/gemma-zaken/issues>`_ bij vragen, fouten of wensen.
* Bekijk de `code <https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/>`_ van de referentie implementatie.

.. _`demo omgeving`: https://documenten-api.vng.cloud/

Licentie
========

Copyright © VNG Realisatie 2018 - 2020

Licensed under the EUPL_

.. _EUPL: LICENCE.md

.. |build-status| image:: https://travis-ci.org/VNG-Realisatie/gemma-documentregistratiecomponent.svg?branch=master
    :alt: Build status
    :target: https://travis-ci.org/VNG-Realisatie/gemma-documentregistratiecomponent

.. |requirements| image:: https://requires.io/github/VNG-Realisatie/gemma-documentregistratiecomponent/requirements.svg?branch=master
     :alt: Requirements status

.. |coverage| image:: https://codecov.io/github/VNG-Realisatie/gemma-documentregistratiecomponent/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage
    :target: https://codecov.io/gh/VNG-Realisatie/gemma-documentregistratiecomponent

.. |docker| image:: https://img.shields.io/badge/docker-latest-blue.svg
    :alt: Docker image
    :target: https://hub.docker.com/r/vngr/gemma-drc/

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code style
    :target: https://github.com/psf/black

.. |python-versions| image:: https://img.shields.io/badge/python-3.6%2B-blue.svg
    :alt: Supported Python version

.. |lint-oas| image:: https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/workflows/lint-oas/badge.svg
    :alt: Lint OAS
    :target: https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/actions?query=workflow%3Alint-oas

.. |generate-sdks| image:: https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/workflows/generate-sdks/badge.svg
    :alt: Generate SDKs
    :target: https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/actions?query=workflow%3Agenerate-sdks

.. |generate-postman-collection| image:: https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/workflows/generate-postman-collection/badge.svg
    :alt: Generate Postman collection
    :target: https://github.com/VNG-Realisatie/gemma-documentregistratiecomponent/actions?query=workflow%3Agenerate-postman-collection

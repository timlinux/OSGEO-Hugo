---
title: "OpenGIS Harmonization - OSGeo"
draft: false
aliases:
  - /opengis-harmonization/
harvested_from: "https://www.osgeo.org/opengis-harmonization/"
---

In an early experimented in cross-project collaboration GeoTools participated in the test-bed for the GeoAPI project responsible for **org.opengis****** interfaces. The OGC [GeoAPI Implementation Specification](<https://www.ogc.org/standard/geoapi/>) was eventually published, and now at version 3 has asked for exclusive use of the **org.opengis** Java package.

This activity requires your participation and support:

  * [Sponsor this initiative](<https://www.osgeo.org/about/how-to-become-a-sponsor/>) via Open Source Geospatial Foundation
  * This [activity](<https://git.osgeo.org/gitea/osgeo/todo/issues/142>) is already partially funded as a priority for [OSGeo 2023 Budget](<https://wiki.osgeo.org/wiki/OSGeo_Budget_2023>)

Initiative outcomes:

  1. Refactor the use of **org.opengis** interfaces in the GeoTools project
  2. Remove unused interfaces, such as Geometry, that have not attracted sufficient sustained investment.
  3. Rollback design changes made to GeoTools to facilitate adoption of GeoAPI interfaces.
  4. Provide downstream projects with a migration script to minimize disruption.

Timeline:

  * [2023 April](<https://www.osgeo.org/events/2023-open-standards-and-open-source-software-code-sprint/>): Open Standards and Open Source Software Code Sprint: initiatve promotion
  * [2023 June](<https://www.osgeo.org/events/foss4g-2023/>): FOSS4G Code Sprint: Design and Planning
  * [2023 August: Bolsena Code Sprint](<https://www.osgeo.org/events/bolsena-code-sprint-2023/>): GeoTools Refactor and API Change
  * [2023 September](<https://geotoolsnews.blogspot.com/2023/10/geotools-300-released.html>): GeoTools 30.0: Public release of API Change

Cross-project initiative with a range of projects affected:

  * [GeoServer](<https://www.osgeo.org/projects/geoserver/>)
  * [GeoMajas](<https://www.osgeo.org/projects/geomajas/>)
  * [GeoMesa](<https://www.osgeo.org/projects/geomesa/>)
  * [GeoWebCache](<https://www.osgeo.org/projects/geowebcache/>)
  * [GeoNetwork](<https://www.osgeo.org/projects/geonetwork/>)
  * [GeoWave](<https://www.osgeo.org/projects/geowave/>)
  * [GeoTrellis](<https://www.osgeo.org/projects/geotrellis/>)
  * And [many](<https://mvnrepository.com/artifact/org.geotools/gt-opengis/usages>), [many](<https://mvnrepository.com/artifact/org.geotools/gt-shapefile>), [more](<https://mvnrepository.com/artifact/org.geotools/gt-main/usages>) …

For background information:

  * [Remove OpenGIS](<https://github.com/geotools/geotools/wiki/Remove-OpenGIS>)
  * [GeoAPI History](<https://desruisseaux.github.io/history/GeoAPI.html>)

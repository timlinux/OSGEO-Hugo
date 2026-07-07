---
title: "Project Graduation Checklist - OSGeo"
draft: false
aliases:
  - /about/committees/incubation/graduation/
harvested_from: "https://www.osgeo.org/about/committees/incubation/graduation/"
---

### Document Status

**Version:** 2.0  
**Status:** approved  
**Last Edited:** June 16, 2014  
**Previous:** [ 1.0](<https://www.osgeo.org/incubator/process/project_graduation_checklist_v1.html>)

### Purpose

The purpose of this checklist is to determine whether an Incubator Project produces quality products, remains true to its stated licence and is sustainable. Satisfying this checklist is a prerequisite for graduation.

A project should have institutionalized the processes in this list or provide justification why the process is not used. See also the [Incubation Application Questionnaire](<https://www.osgeo.org/incubator/process/application.html>).

### Terms and Definitions

Mentor
    A member of the Incubation Committee chosen to assist a Project through the Incubation Process.
Institutionalized Process
    A documented process which which addresses a need and is actively in use. It typically takes months before a process becomes institutionalized.  
_A more detailed definition of institutionalization is found in the[ Capability Maturity Model (CMMI)](<http://www.sei.cmu.edu/library/abstracts/reports/02tr012.cfm>)_
Open Source License
    a license recognized by the [Open Source Initiative](<http://opensource.org/>)

## Incubation Checklist

### Open

The project has demonstrated that it has an open, active and healthy user and developer community:

  1. Open: projects are expected to function in an open and public manner and include: 
     * Open source license(s),
     * Open communication channels,
     * Open decision making process.
  2. Active and healthy community: 
     * The project should have a community of developers and users who actively collaborate and support each other in a healthy way.  
_Eg. collaboration on project activities such as testing, release and feature development._
     * Long term viability of the project is demonstrated by showing participation and direction from multiple developers, who come from multiple organisations.  
_Eg. The project is resilient enough to sustain loss of a developer or supporting organisation, often referred to as having a high[bus factor](<http://en.wikipedia.org/wiki/Bus_factor>). Decisions are made openly instead of behind closed doors, which empowers all developers to take ownership of the project and facilitates spreading of knowledge between current and future team members._

### Copyright and License

We need to ensure that the project owns or otherwise has obtained the ability to release the project code by completing the following steps:

  1. All project source code is available under an Open Source license.
  2. Project documentation is available under an open license.  
_Eg. Creative Commons_
  3. The project code, documentation and data has been adequately vetted to assure it is all properly licensed, and a copyright notice included.  
_As per a[Provenance Review](<https://www.osgeo.org/incubator/process/codereview.html>)_
  4. The project maintains a list of all copyright holders identified in the Provenance Review Document.
  5. All code contributors have agreed to abide by the project’s license policy, and this agreement has been documented and archived.

### Processes

  1. The project has code under configuration management.  
_Eg, subversion, git._
  2. The project uses an issue tracker and keeps the status of the issue tracker up to date.
  3. The project has documented its management processes.  
_This is typically done within a Developers Guide or Project Management Plan._
     * The project has a suitable open governance policy ensuring decisions are made, documented and adhered to in a public manner.  
_This typically means a Project Management Committee has been established with a process for adding new members. A robust Project Management Committee will typically draw upon developers, users and key stakeholders from multiple organisations as there will be a greater variety of technical visions and the project is more resilient to a sponsor leaving._
     * The project uses public communication channels for decision making to maintain transparency.  
_E.g. archived email list(s), archived IRC channel(s), public issue tracker._

### Documentation

  1. The project has user documentation: 
     * Including sufficient detail to guide a new user through performing the core functionality provided by the application.
  2. The project has developer documentation: 
     * Including checkout and build instructions.
     * Including commented code, ideally published for developer use.  
_Examples: javadocs for Java applications, or Sphinx documentation for Python applications._
     * Providing sufficient detail for an experienced programmer to contribute patches or a new module in accordance with the project’s programming conventions.

### Release Procedure

In order to maintain a consistent level of quality, the project should follow defined release and testing processes.

  1. The project follows a defined release process: 
     * Which includes execution of the testing process before releasing a stable release.
  2. The project follows a documented testing process.  
_Ideally, this includes both automated and manual testing_  
_Ideally this includes documented conformance to set quality goals, such as reporting Percentage Code Coverage of Unit Tests._
  3. Release and testing processes provide sufficient detail for an experienced programmer to follow.

## OSGeo Committees and Community

The OSGeo Foundation is made up of a number of [committees](<https://www.osgeo.org/content/foundation/committees.html>), projects and local chapters. This section gathers up information these groups have requested from OSGeo projects. These expectations are not mandatory requirements before graduation, but a project should be prepared to address them in order to be considered a good OSGeo citizen.

### Board

The [OSGeo Board](<https://wiki.osgeo.org/wiki/Board_of_Directors>) holds ultimate responsibility for all OSGeo activities. The Board requests:

  1. A project provide a Project Officer as primary contact point: 
     * The Project Officer should be listed at [Officers and Board of Directors](<https://www.osgeo.org/content/foundation/board_and_officers.html>) and [Contacts](<https://wiki.osgeo.org/wiki/Contacts#Software_Projects>)
     * This person is established when the incubation committee recommends the project for graduation
     * Your community can change the project officer as needed  
_Add an agenda item to the next board meeting so they can recognise the change of officer._

### Marketing

Access to OSGeo’s [Marketing_Committee](<https://wiki.osgeo.org/wiki/Marketing_Committee>) and associated [Marketing Pipeline](<https://wiki.osgeo.org/wiki/Marketing_Pipeline>) is one of the key benefits of joining the OSGeo foundation. The Marketing Committee requests:

  1. Marketing artefacts have been created about the project in line with the incubation criteria listed in the OSGeo Marketing Committee’s [Marketing Artefacts](<https://wiki.osgeo.org/wiki/Marketing_Artefacts>).  
This lists the documentation requirements for [OSGeo-Live](<http://live.osgeo.org/>). Marketing Artefacts include: 
     * Application Overview
     * Application Quick Start
     * Logo
     * Graphical Image
  2. Ideally, stable version(s) of executable applications are bundled with appropriate distributions.  
_In most cases, this will at least include[OSGeo-Live](<http://live.osgeo.org/>), but may also include [DebianGIS](<http://wiki.debian.org/DebianGis>), [UbuntuGIS](<https://wiki.ubuntu.com/UbuntuGIS>), and/or [osgeo4w](<https://trac.osgeo.org/osgeo4w/>), [ms4w](<http://ms4w.com/>), etc.)_

### Projects

Projects do not exist in isolation; and are expected to communicate and collaborate on key issues.

_As an example the PostGIS release procedure asks that the release be checked with MapServer, GeoServer and others._

### SAC

The [System Administration Committee](<https://wiki.osgeo.org/wiki/SAC>) is available to help with infrastructure and facilities. Information for this committee is collected as part of the [Project Graduation Checklist](<https://www.osgeo.org/incubator/process/project_graduation_checklist.html>).

  1. The following should be set up: 
     * A http://projectname.osgeo.org domain name
  2. A project may optionally request SAC help to make use of: 
     * OSGeo issue tracker
     * OSGeo mailing list
     * OSGeo svn
     * http://downloads.osgeo.org

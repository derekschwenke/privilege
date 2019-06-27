Overview
========

A role-based access control privilege reporting tool is required to help administrators define
permissions in a large organization. Permissions are defined as strings assigned to Roles that grant Users
privilege to perform a specific task on a resource. Some of the questions administrators need to answer are:

    "What are dave's permissions?"
    "Who can reboot this host?"
    "What can the admin group do?"
    "Can dave write to this directory?"

ASSUMPTIONS

Roles, Permissions and Users are assumed to be strings. Permission strings must be additive and positive. 

Privilege Command Line
======================

NAME

    privilege - generates a report of from three input csv files

SYNOPSIS

    python privilege [...] 

DESCRIPTION

    Three input files are read in CSV format in the working directory: users.txt, roles.txt and, permissions.txt.

        1. users.txt contains the User-ID, first_name, last_name
        2. roles.txt contains the Role, User-IDs,,,
        3. permissions.txt contains the Role, Permissions,,,

    The program will report consistency errors in the input files.
    Joining the input data produces six table reports that are printed.

        1. Users Permissions
        2. Permission Users
        3. User Roles
        4. Role Users
        5. Role Permissions
        6. Permission Roles
    
    These tables list all users. Other limited reports are possible.
    (In version 2 a report focused on a single user can also be printed)

Development plans
==============+==
A python 2.7 command line and a Django 1.11 implementation will explore alternate solutions. Django's support for interactive presentation will allow larger data sets to be reduced for display although the initial version will be static. Problems and solutions will be identified in each version and addressed in later releases. 

Command Line functions

These functions have been identified from feedback.
- Add output file and console log
- Add support for non csv input format
- Investigate using a database

Estimates: 4 hr ea.

Django functions

These features can chart the progress of the GUI.
- load static, dynamic data and display 
- Join data tables for display
- Join data in UI model and views
- Develop more views 
- Develop more GUI controls

Estimates: 2 days ea. 10 days total

Future Development 
==================
These features have been gathered from feedback from the inital version.
- Use data from genisys users and groups  Estimate: 1 day.
- Explore any structure to the roles and permission strings Estimate: 2 days.
  Roles and permissions have a useful structure for example: "HOST:SERVICE:API:permission" or "PARENT:CHILD" 
- Add a way to filter inputs. Estimate: 1 day.
- Add role/group descriptions. Estimate: 1 day.
  In a large set of Roles or Permissions, a description could help users understand the names.
- Have Django edit and save the data. Estimate: 2 days.
  
  
History
=======
In version 0:
- Individual permissions were supported, however, that was removed.
- ID's were required to be numbers, however that was removed.


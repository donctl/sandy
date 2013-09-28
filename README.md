sandy
=====
Copyright 2013 Sandy
Written by: Laszlo Toth, Ferenc Spala

Description
-----------

Sandy is an open-source Samsung phone encryption assessment framework. Sandy has different modules that allow you to carry out different attack scenarios against encrypted Samsung phones. For the details check our Derbycon 3.0 presentation (What’s common in Oracle and Samsung? They tried to think differently about crypto).

Requirements
------------
* It was developed with python 2.7. 
* Most of the modules works on OSX.
* Every modules should work on Kali Linux.
* You need pexpect, pbkdf2 and pyCrypto pyhton modules.
 
Usage
-----

main.py [-h] -p project_name

The project_name parameter is important. All files will be created in the following form:

[project_name]_filename

under the results folder. This is how the different modules can find each other results on the same project.


Disclaimer
----------

This is only for testing purposes and can only be used where strict consent has been given. Do not use this for illegal purposes.

Please read the license (LICENSE) for the licensing of Sandy. 


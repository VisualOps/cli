visualops
=========

``visualops`` is a command-line interface for VisualOps. It allows you to
deploy the same stack on your laptop, or in the cloud

note: output shown in this documentation is indicative only, please do not refer to it.

Requirements
------------

Before install, ensure Docker is installed (see http://docs.docker.com) in version >= 1.2.0 (1.3.1 is recommended).

Platform
--------

All Linux distributions supported by Docker should be compatible with VisualOps.
Ubuntu, Cent OS, Amazon Linux and Red Hat Linux (on their latest version) are officially suported.

On Mac OS X (not fully supported yet), boot2docker is required.

Install
-------

Preferred method of install is ``pip``:

::

    $ pip install visualops

Commands
--------

Check usage for detailed arguments:

::

    $ visualops --help

Use the help command to get help about one specific command:

::

    $ visualops help [command]

Notes
-----

When using `boot2docker` on OSX, ensure the latest version is installed (1.3.1 tested).
Not that only files/directories located under /Users will be mounted.

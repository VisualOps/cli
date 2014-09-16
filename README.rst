visualops
==

``visualops`` is a command-line interface for VisualOps. It allows you to
deploy the same stack on your laptop, or in the cloud

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

login
~~~~

Login in VisualOps. Once succeceed, the session will be persisted for the next 24 hours, or another login takes somewhere else.

::

    $ visualops login
    Enter username/email: jimmy
    Enter password:
    
    Succeeded!

logout
~~~~~~~~

Logout from VisualOps, and remove the persisted temporary session
::

    $ visualops logout
    Are you sure to logout? [Y/n]:
    
    Done!

list
~~~~

List your stacks and apps, locally or on AWS

::

    $ visualops list stack
    Stacks:
    	mysql   	us-east			stack-1kkd123b		https://ide.visualops.io/ops/stack-1kkd123b

pull
~~~~~

Pull a stack from VisualOps to local

::

    $ visualops pull stack-1kkd123b
    pulling stack-1kkd123b from remote ......
    
    Done!

push
~~~~~~

Push a stack to VisualOps

::

    $ visualops push ./stack-1kkd123b.yaml
    pushing stack-1kkd123b to remote ......

	Done!

run 
~~~~~~

Deploy the stack locally, or in the cloud

::

    $ visualops run ./stack-1kkd123b.yaml --local
    Deploying stack-1kkd123b.yaml ......
    
    Enter the app name: node-dev
    Enter the cpu share for my/node [1]: 1
    Enter the mem size for my/node [128]: 512
    Enter the mount point for my/node: /home/jimmy/www/:/var/www/html/

    pulling image my/node ...... 
    pulling image my/postgres ...... 
    rendering my/node:/etc/httpd.conf ...... 
    rendering my/postgres:/etc/postgres.conf .... 
    setup port mapping 80:my/node:8080 ...... 
    setup port mapping 45621:my/postgres:45621 ...... 
    creating container my/node ...... 
    creating container my/postgres ...... 

	Done! Successfully deploy node-dev locally.
	
	

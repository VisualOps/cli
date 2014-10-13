visualops
=========

``visualops`` is a command-line interface for VisualOps. It allows you to
deploy the same stack on your laptop, or in the cloud

note: output shown in this documentation is indicative only, please do not refer to it.

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

Login in VisualOps. Once succeceed, the session will be persisted for the next 24 hours, or until another login happens somewhere else.
::

    $ visualops login
    Enter username/email: jimmy
    Enter password: ******
    
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
    	mysql   	us-east			stack-1kkd123b		https://ide.visualops.io/ops/stack-1kkd123b    [local]
    	mysql   	us-east			stack-1abff654		https://ide.visualops.io/ops/stack-1abff654    [remote]

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
~~~~~

run [--local] [-lpq] [-r chroot] [-v [/host:/container]] [-b [hostname:container=source_port:dest_port]] [-m memory_size] [-p cpu-shares] [-n containers_number] [-c config_directory]


Deploy the stack locally, or in the cloud

::

    $ visualops run ./stack-1kkd123b.yaml --local
    Deploying stack-1kkd123b.yaml ......
    
    Enter the app name: node-dev
    Enter the cpu share for my/node: 1 [None]:
    Enter the mem size for my/node: 128m [None]: 512m
    Update mount point for my/node: /home/ec2-user/www=/var/www/html [None]: /home/jimmy/www=/var/www/html
    Update mount point for my/node: /data=/data [None]:
    Update port binding for my/node: 80=80 [None]: 80:80
    Update port binding for my/node: 6666=6666 [None]:
    Update number of containers for my/node: [2]: 1

    pulling image my/node ......
    pulling image my/postgres ......
    rendering my/node:/etc/httpd.conf ......
    rendering my/postgres:/etc/postgres.conf ....
    setup port mapping 80:my/node:8080 ......
    setup port mapping 45621:my/postgres:45621 ......
    creating container my/node ......
    creating container my/postgres ......

    Done! Successfully deploy node-dev locally.


Details:
`-q`: Quiet mode (detault: no)
      Bypass all interactivity (see parameters bellow to define the options)

`-v`: Volumes (default: none set)
      Override stack volumes mountpoints
Example: -v hostname:container:/host:/container -v ...
Note: By default, original path are mount. to ignore a volume, simply remove the host path (e.g. -v hostname:container::/container

`-r`: Volumes chroot (default: none set)
      All volumes host path will be preceed by "/chrootpath/appid/instanceid/containername/"
Example: -r /chrootpath
Note: Chroot will override the custom volumes host paths

`-b`: Bindings (default: none set)
      Override stack port bindings details
Example: -p hostname:container=0.0.0.0:80:80/tcp -p hostname:container=6666:6666/udp -p hostname:container=127.0.0.1:7777:7777 -p hostname:container=9999:9999/tcp -p hostname:container=23:23
Note: By detault, all port bindings are ignored.
      Please, note that these bindings are used to external bindings, and their usage is therefore limited in a local environment.
      Also, note that if you are using "boot2docker" or any remote (vitual)machine, you will need to bind the ports you want to access from your local machine.
      It is good practice to limit the ports bindings in a development environment, as multiple containers won't be able to be bind on the same port.

`-m`: Memory-size (default: none set)
      Override stack memory limit
Example: -m 512m
Note: Enter no value to lift the limit

`-p`: CPU shares (default: none set)
      Override stack CPU shares
Example: -p 1
Note: Enter no value to lift the limit

`-n`: Number of containers (default: 1)
      Override the number of containers to run (count option)
Exemple: -n 2

`-c`: Configuration path (default: ~/.visualops):
      The path to the configuration directory (where stacks details and containers configuration files are saved)
Example: -c ~/.visualops

`-k`: Keep (default: no)
      Keep the stack options (volumes, ports bindings, memory size, cpu shares)

`-l`: Load (default: no)
      Load config saved with `-k`
Note: If no config is available, this parameter won't take any action.

terminate
~~~~~~

Terminate a local app and associated resources

::

    $ visualops terminate app-1kkd123b --clean
    Terminating app-1kkd123b ......
    
    stopping container my/node ......
    stopping container my/postgres ......
    deleting image my/node ......
    deleting image my/postgres ......

    Done! Successfully terminate node-dev.

stop
~~~~~~

Stop a local app

::

    $ visualops stop app-1kkd123b
    Stopping app-1kkd123b ......
    
    stopping container my/node ......
    stopping container my/postgres ......

    Done! Successfully stop node-dev.

start
~~~~~~

Start a local app

::

    $ visualops start app-1kkd123b
    Starting app-1kkd123b ......
    
    creating container my/node ......
    creating container my/postgres ......

    Done! Successfully start node-dev.

reboot
~~~~~~

Reboot a local app or some containers

::

    $ visualops Reboot app-1kkd123b[:c1,c2,c3]
    Rebooting app-1kkd123b ......

    stopping container my/node ......
    stopping container my/postgres ......
    creating container my/node ......
    creating container my/postgres ......

    Done! Successfully reboot node-dev.

clone
~~~~~~

clone [-lpq] [-r chroot] [-v [/host:/container]] [-b [hostname:container=source_port:dest_port]] [-m memory_size] [-p cpu-shares] [-n containers_number] [-c config_directory]

Clone a remote app to local

::

    $ visualops clone app-1kkd123b
    Cloning app-1kkd123b ......

    pulling app-1kkd123b ......

    Enter the app name: node-dev
    Enter the cpu share for my/node: 1 [None]:
    Enter the mem size for my/node: 128m [None]: 512m
    Update mount point for my/node: /home/ec2-user/www=/var/www/html [None]: /home/jimmy/www=/var/www/html
    Update mount point for my/node: /data=/data [None]:
    Update port binding for my/node: 80=80 [None]: 80:80
    Update port binding for my/node: 6666=6666 [None]:
    Update number of containers for my/node: [2]: 1

    pulling image my/node ......
    pulling image my/postgres ......
    rendering my/node:/etc/httpd.conf ......
    rendering my/postgres:/etc/postgres.conf ....
    setup port mapping 80:my/node:8080 .......
    setup port mapping 45621:my/postgres:45621 ......
    creating container my/node ......
    creating container my/postgres ......

    Done! Successfully clone app-1kkd123b to local.

    Done! Successfully reboot node-dev.

Details:
Same as run

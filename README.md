cli
==================================================
CLI for VisualOps



==================================================
third-lib
==================================================
#virtual python environment
$ pip install virtualenv

#enter virtual python environment
$ virtualenv .venv
$ . .venv/bin/activate


#The flowlling lib should be installed under virtualenv

## command line interface formulation framework
$ pip install cliff

## formatting extensions for cliff(support html,json,yaml)
$ pip install cliff-tablib

## debugger
$ pip install pudb



==================================================
install
==================================================
$ python setup.py install



debug
===
#add the following line to first breakpoint
import pudb
pudb.set_trace()



==================================================
usage
==================================================
#enter virtual python environment
$ virtualenv .venv
$ . .venv/bin/activate

#enter interactive mode
(.venv)$ visualops

#show help
(.venv)$ visualops -h

#none-interactive mode
(.venv)$ visualops login
(.venv)$ visualops stack list us-east-1
(.venv)$ visualops -v stack list us-east-1
(.venv)$ visualops stack info ap-southeast-1 stack-993a496d

#demo
(.venv)$ visualops error --debug
(.venv)$ visualops listfile -f yaml # csv,table,html,json,yaml
(.venv)$ visualops showfile -f shell



==================================================
support auto-complete
==================================================
#generate bash_complete script
$ visualops complete

bash_complete script sample:
###################
_visualops()
{
...
}
complete -F _visualops visualops
###################

#create bash_complete script for visualops
put the bash_complete script to /etc/bash_completion.d/visualops

#use auto-complete
press tab twice

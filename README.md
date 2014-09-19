cli
===
CLI for VisualOps



[third-lib]
===
##1.install virtualenv (virtual python environment)
$ pip install virtualenv

##2.create virtual python environment
$ virtualenv .venv

##3.enter virtual python environment
$ . .venv/bin/activate


##4.The flowlling lib should be installed under virtualenv

###4.1 command line interface formulation framework
(.venv)$ pip install cliff

###4.2 formatting extensions for cliff(support html,json,yaml)
(.venv)$ pip install cliff-tablib

###4.3 debugger
(.venv)$ pip install pudb



[install]
===
(.venv)$ python setup.py install



[debug]
===
##add the following line to first breakpoint
<pre>
import pudb
pudb.set_trace()
</pre>



[usage]
==================================================
##1.enter virtual python environment
$ . .venv/bin/activate

##2.enter interactive mode
(.venv)$ visualops

##3.show help
(.venv)$ visualops -h

##4.none-interactive mode
(.venv)$ visualops login

(.venv)$ visualops stack list us-east-1

(.venv)$ visualops -v stack list us-east-1

(.venv)$ visualops stack info ap-southeast-1 stack-993a496d

##5.demo
(.venv)$ visualops error --debug

(.venv)$ visualops listfile -f yaml # csv,table,html,json,yaml

(.venv)$ visualops showfile -f shell



support auto-complete
===
##1.generate `bash_complete script`
(.venv)$ visualops complete

`bash_complete script` sample:
<pre>
_visualops()
{
...
}
complete -F _visualops visualops
</pre>

##create bash_complete script for visualops
put the `bash_complete script` to `/etc/bash_completion.d/visualops`

##use auto-complete
press `tab` twice when input command

import re
from setuptools import setup, find_packages

file_text = open('visualops/__init__.py').read()

def grep(attrname):
    pattern = r"{0}\W*=\W*'([^']+)'".format(attrname)
    strval, = re.findall(pattern, file_text)
    return strval

setup(
    name='visualops',
    version=grep('__version__'),
    author='Peng Zhao',
    author_email='peng@visuak.io',
    url='https://github.com/MadeiraCloud/cli',
    description='VisualOps CLI',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    scripts=['bin/visualops'],
    install_requires=['cliff','docker-py'],
    entry_points={
        'console_scripts': [
            'visualops = visualops.main:main'
        ],
        'visualops.cli': [
            'login      = visualops.cmd.session:Login',
            'logout     = visualops.cmd.session:Logout',

            'list stack = visualops.cmd.stack.list:List',
            'info stack = visualops.cmd.stack.info:Info',
            'pull       = visualops.cmd.stack.pull:Pull',
            'push       = visualops.cmd.stack.push:Push',
            'run        = visualops.cmd.stack.run:Run',
            'delete     = visualops.cmd.stack.delete:Delete',

            'list app  = visualops.cmd.app.list:List',
            'info app  = visualops.cmd.app.info:Info',
            'stop      = visualops.cmd.app.stop:Stop',
            'start     = visualops.cmd.app.start:Start',
            'reboot    = visualops.cmd.app.reboot:Reboot',
            'clone     = visualops.cmd.app.clone:Clone',
            'terminate = visualops.cmd.app.terminate:Terminate',

            'simple    = visualops.demo.simple:Simple',
            'listfile  = visualops.demo.list:Files',
            'showfile  = visualops.demo.show:File',
            'error     = visualops.demo.simple:Error',
        ],
    },
)

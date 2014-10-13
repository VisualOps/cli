# Copyright 2014 MadeiraCloud LTD.

import re
from setuptools import setup, find_packages

try:
    import multiprocessing  # noqa
except ImportError:
    pass

file_text = open('visualops/__init__.py').read()

def grep(attrname):
    pattern = r"{0}\W*=\W*'([^']+)'".format(attrname)
    strval, = re.findall(pattern, file_text)
    return strval

setup(
    name='visualops',
    version=grep('__version__'),
    author='Thibault Bronchain',
    author_email='thibault@visualops.io',
    license='LICENSE.txt',
    url='https://github.com/MadeiraCloud/cli',
    description='VisualOps CLI',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    scripts=[],
    install_requires=['cliff','requests','pyyaml','docker-py'],
    entry_points={
        'console_scripts': [
            'visualops = visualops.main:main'
        ],
        'visualops.cli': [
            'login      = visualops.cmd.session:Login',
            'logout     = visualops.cmd.session:Logout',

            'stack list   = visualops.cmd.stack.list:List',
            'stack info   = visualops.cmd.stack.info:Info',
            'stack pull   = visualops.cmd.stack.pull:Pull',
            'stack push   = visualops.cmd.stack.push:Push',
            'stack run    = visualops.cmd.stack.run:Run',
            'stack delete = visualops.cmd.stack.delete:Delete',

            'app list      = visualops.cmd.app.list:List',
            'app info      = visualops.cmd.app.info:Info',
            'app stop      = visualops.cmd.app.stop:Stop',
            'app start     = visualops.cmd.app.start:Start',
            'app reboot    = visualops.cmd.app.reboot:Reboot',
            'app clone     = visualops.cmd.app.clone:Clone',
            'app terminate = visualops.cmd.app.terminate:Terminate',

            'db reset      = visualops.cmd.db.reset:Reset',
        ],
    },
)

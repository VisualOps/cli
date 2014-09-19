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
            'login = visualops.cmd.session:Login',
            'stack list = visualops.cmd.stack:List',
            'stack info = visualops.cmd.stack:Info',
            'simple = visualops.demo.simple:Simple',
            'listfile = visualops.demo.list:Files',
            'showfile = visualops.demo.show:File',
            'error = visualops.demo.simple:Error',
        ],
    },
)

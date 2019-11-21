import os
from setuptools import setup
from setuptools import find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(name='refine-client',
    version='0.2.1',
    description=('The OpenRefine Python Client Library provides an '
                 'interface to communicating with an OpenRefine server.'),
    author='Paul Makepeace',
    author_email='paulm@paulm.com',
    url='https://github.com/PaulMakepeace/refine-client-py',
    packages=find_packages(exclude=['tests']),
    install_requires=['requests'],
    platforms=['Any'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
    ],
)

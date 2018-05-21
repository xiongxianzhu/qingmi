# coding: utf-8

import os
import re
# import sys

from codecs import open

from setuptools import setup, find_packages
# from setuptools.command.test import test as TestCommand


NAME = 'qingmi'
here = os.path.abspath(os.path.dirname(__file__))

# -*- Extras -*-
EXTENSIONS = {
    'bcrypt',
    'testing',
}

# -*- Classifiers -*-
classes = """
    Framework :: Flask
    Development Status :: 1 - Planning
    Environment :: Web Environment
    Intended Audience :: Developers
    License :: OSI Approved :: BSD License
    Operating System :: OS Independent
    Programming Language :: Python
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.6
    Topic :: Internet :: WWW/HTTP
    Topic :: Internet :: WWW/HTTP :: Dynamic Content
    Topic :: Software Development :: Libraries :: Application Frameworks
    Topic :: Software Development :: Libraries :: Python Modules
"""
classifiers = [s.strip() for s in classes.split('\n') if s]


about = {}
with open(os.path.join(here, NAME, '__about__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)


def read_file(filename):
    filepath = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', 'utf-8') as f:
            return f.read()
    else:
        return ''


readme = read_file('README.rst')
history = read_file('CHANGES.rst')


# -*- Distribution Meta -*-
re_meta = re.compile(r'__(\w+?)__\s*=\s*(.*)')
re_doc = re.compile(r'^"""(.+?)"""')


def _add_default(m):
    attr_name, attr_value = m.groups()
    return ((attr_name, attr_value.strip("\"'")),)


def _add_doc(m):
    return (('doc', m.groups()[0]),)


def parse_dist_meta():
    """Extract metadata information from ``$dist/__about__.py``."""
    pats = {re_meta: _add_default, re_doc: _add_doc}
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, NAME, '__about__.py')) as meta_fh:
        distmeta = {}
        for line in meta_fh:
            if line.strip() == '# -eof meta-':
                break
            for pattern, handler in pats.items():
                m = pattern.match(line.strip())
                if m:
                    distmeta.update(handler(m))
        return distmeta


# -*- Requirements -*-
def _strip_comments(l):
    return l.split('#', 1)[0].strip()


def _pip_requirement(req):
    if req.startswith('-r '):
        _, path = req.split()
        return reqs(*path.split('/'))
    return [req]


def _reqs(*f):
    return [
        _pip_requirement(r) for r in (
            _strip_comments(l) for l in open(
                os.path.join(os.getcwd(), 'requirements', *f)).readlines()
        ) if r]


def reqs(*f):
    """Parse requirement file.
    Example:
        reqs('default.txt')          # requirements/default.txt
        reqs('extras', 'redis.txt')  # requirements/extras/redis.txt
    Returns:
        List[str]: list of requirements specified in the file.
    """
    return [req for subreq in _reqs(*f) for req in subreq]


def extras(*p):
    """Parse requirement in the requirements/extras/ directory."""
    return reqs('extras', *p)


def install_requires():
    """Get list of requirements required for installation."""
    return reqs('default.txt')


def extras_require():
    """Get map of all extra requirements."""
    return {x: extras(x + '.txt') for x in EXTENSIONS}


# meta = parse_dist_meta()
# name=meta['name'],
# version=meta['version'],
# description=meta['description']
# 
# or
# 
# name=about['__name__'],
# version=about['__version__'],
# description=about['__description__']

setup(
    name=about['__name__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme + '\n\n' + history,
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=find_packages(),
    keywords=about['__keywords__'],
    license=about['__license__'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=install_requires(),
    classifiers=classifiers,
    extras_require=extras_require(),
    tests_require=reqs('test.txt'),
    entry_points={
        'console_scripts': [
            'qingmi = qingmi.cli:main',
        ],
    },
    project_urls={
        'Source': about['__source__'],
    },
)

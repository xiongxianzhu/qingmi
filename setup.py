# coding: utf-8

import os
from setuptools import setup, find_packages

about = {}
about_file = os.path.join(os.path.dirname(__file__), 'qingmi', '__about__.py')
with open(about_file, 'r') as f:
    exec(f.read(), about)

def read_file(filename):
    filepath = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), filename)
    if os.path.exists(filepath):
        return open(filepath).read()
    else:
        return ''

setup(
    name=about['__name__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=read_file('README.rst'),
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=find_packages(),
    keywords=['qingmi', 'flask'],
    license=about['__license__'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask==1.0.2',
        'click==6.7',
        'mongoengine==0.15.0',
        'flask-mongoengine==0.9.5',
        'Pillow==5.1.0',
        'wheezy.captcha==0.1.44',
    ],
    classifiers=[
        'Framework :: Flask',
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    extras_require={
        "bcrypt": ["bcrypt"],
        'testing': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'qingmi = qingmi.cli:main',
        ],
    },
    project_urls={
        'Source': about['__source__'],
    },
)

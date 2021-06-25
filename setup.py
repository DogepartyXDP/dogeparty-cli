#!/usr/bin/env python
from setuptools.command.install import install as _install
from setuptools import setup, find_packages, Command
import os, sys
import shutil
import ctypes.util
from dogepartycli import APP_VERSION

class generate_configuration_files(Command):
    description = "Generate configfiles from old files or dogecoind config file"
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def run(self):
        from dogepartycli.setup import generate_config_files
        generate_config_files()

class install(_install):
    description = "Install dogeparty-cli and dependencies"

    def run(self):
        caller = sys._getframe(2)
        caller_module = caller.f_globals.get('__name__','')
        caller_name = caller.f_code.co_name
        if caller_module == 'distutils.dist' or caller_name == 'run_commands':
            _install.run(self)
        else:
            self.do_egg_install()
        self.run_command('generate_configuration_files')

required_packages = [
    'appdirs==1.4.0',
    'setuptools-markdown==0.2',
    'prettytable==0.7.2',
    'colorlog==2.7.0',
    'python-dateutil==2.5.3',
    'requests>=2.20.0',
    'dogeparty-lib'
]

setup_options = {
    'name': 'dogeparty-cli',
    'version': APP_VERSION,
    'author': 'Dogeparty Developers',
    'author_email': 'dev@dogeparty.net',
    'maintainer': 'Dogeparty Developers',
    'maintainer_email': 'dev@dogeparty.net',
    'url': 'http://dogeparty.net',
    'license': 'MIT',
    'description': 'Dogeparty Protocol Command-Line Interface',
    'long_description': '',
    'keywords': 'dogeparty,dogecoin',
    'classifiers': [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Office/Business :: Financial",
        "Topic :: System :: Distributed Computing"
    ],
    'download_url': 'https://github.com/DogepartyXDP/dogeparty-cli/releases/tag/' + APP_VERSION,
    'provides': ['dogepartycli'],
    'packages': find_packages(),
    'zip_safe': False,
    'setup_requires': ['setuptools-markdown',],
    'install_requires': required_packages,
    'entry_points': {
        'console_scripts': [
            'dogeparty-client = dogepartycli:client_main',
            'dogeparty-server = dogepartycli:server_main',
        ]
    },
    'cmdclass': {
        'install': install,
        'generate_configuration_files': generate_configuration_files
    }
}
# prepare Windows binaries
if sys.argv[1] == 'py2exe':
    import py2exe
    from py2exe.distutils_buildexe import py2exe as _py2exe

    WIN_DIST_DIR = 'dogeparty-cli-win32-{}'.format(APP_VERSION)

    class py2exe(_py2exe):
        def run(self):
            from dogepartycli.setup import before_py2exe_build, after_py2exe_build
            # prepare build
            before_py2exe_build(WIN_DIST_DIR)
            # build exe's
            _py2exe.run(self)
            # tweak build
            after_py2exe_build(WIN_DIST_DIR)

    # Update setup_options with py2exe specifics options
    setup_options.update({
        'console': [
            'dogeparty-client.py',
            'dogeparty-server.py'
        ],
        'zipfile': 'library/site-packages.zip',
        'options': {
            'py2exe': {
                'dist_dir': WIN_DIST_DIR
            }
        },
        'cmdclass': {
            'py2exe': py2exe
        }
    })
# prepare PyPi package
elif sys.argv[1] == 'sdist':
    setup_options['long_description_markdown_filename'] = 'README.md'

setup(**setup_options)

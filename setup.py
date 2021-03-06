#!/usr/bin/env python

from distutils.core import setup
from distutils.errors import DistutilsArgError
from distutils.sysconfig import get_python_lib

from setuptools.command.install import install

import os
import subprocess
import sys
import time
import pip
import shutil

from pip.commands.show import search_packages_info

class MyInstall(install):
    def run(self):
        # Anything that can cause a failure must happen before install.run().
        # If install.run() completes successfully, pip will always return that
        # the installation succeeded.

        if "win32" != sys.platform:
            raise Exception("Windows is the only supported platform")

        rootdir = os.path.dirname(os.path.realpath(__file__))
        # install_requires/dependency_links doesn't work because the wheel
        # wouldn't be installed until install.run(self). This is a bad plan
        # because pywin32_postinstall can't run until the wheel is installed,
        # if this is after install.run(self) then we can't return failures
        # properly.
        pkgs = list(search_packages_info(["pywin32"]))
        if len(pkgs) > 1:
            raise Exception("error: multiple pywin32 detected")
        elif len(pkgs) == 1:
            pywin32 = pkgs[0]
            assert pywin32['name'] == 'pywin32'
            if pywin32['version'] != '220':
                raise Exception("error: incompatible version of pywin32 installed: {}".format(pywin32['version']))
        else:
            assert len(pkgs) == 0
            # wheel lifted from here http://www.lfd.uci.edu/~gohlke/pythonlibs/
            wheel = os.path.join(rootdir, "pyWin32Wrapper",
                "pywin32-220-cp27-none-win32.whl")
            pip.main(['install', wheel])

        postinstall = os.path.join(rootdir, "pyWin32Wrapper", "pywin32_postinstall.py")
        subprocess.check_call([sys.executable, postinstall, "-install"])

        # python27.dll must be available to Lib/site-packages/win32/PythonService.exe
        # This piece of code is only going to work if python27.dll is available
        # in the same directory as the python binary.  In the case of
        # virtualenv this condition is met if the python binary used to create
        # the venv has python27.dll in the same directory (virtualenv will copy
        # this python27.dll to the venv).  The python used to bootstrap
        # preveil daemon and updater meets this criteria.
        src  = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "python27.dll")
        dest = os.path.join(get_python_lib(), "win32", "python27.dll")
        shutil.copyfile(src, dest)

        install.run(self)

setup(name='pyWin32Wrapper',
      version='1.0',
      description='Handle installation intricacies for pywin32',
      author='Aaron Burrow',
      author_email='burrows@preveil.com',
      url='https://github.com/PreVeil/pyWin32Wrapper',
      packages=['pyWin32Wrapper'],
      package_data={'pyWin32Wrapper' :
          ["pywin32-220-cp27-none-win32.whl", "pywin32_postinstall.py"]},
      cmdclass={'install': MyInstall},
     )

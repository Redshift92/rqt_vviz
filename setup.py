# -*- coding: utf-8 -*-
# @Author: lorenzo
# @Date:   2017-05-28 16:26:03
# @Last Modified by:   lorenzo
# @Last Modified time: 2017-05-28 16:26:28

# ! DO NOT MANUALLY INVOKE THIS setup.py, USE CATKIN INSTEAD

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

# fetch values from package.xml
setup_args = generate_distutils_setup(
    packages=['rqt_vviz'],
    package_dir={'': 'src'},
    requires=['rospy']
)

setup(**setup_args)

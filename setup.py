import os
from setuptools import setup, find_packages

package_name = 'resource_publisher'

setup(
    name=package_name,
    version='0.5.3',
    # Packages to export
#    packages=[package_name],
    packages=[package_name],
    # Files we want to install, specifically launch files
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        # Include our package.xml file
        (os.path.join('share', package_name), ['package.xml'])
    ],
    # This is important as well
    install_requires=['setuptools'],
    zip_safe=True,
    author='Colin F. MacKenzie',
    author_email='nospam2@colinmackenzie.net',
    maintainer='Colin F. MacKenzie',
    maintainer_email='nospam2@colinmackenzie.net',
    keywords=['ros', 'ros2', 'urdf', 'xacro'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: Apache',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description='Publishes documents to a Ros2 topic including conversion of xacro files such as URDF',
    license='Apache',
    # Like the CMakeLists add_executable macro, you can add your python
    # scripts here.
    entry_points={
        'console_scripts': [
            'resource_publisher = resource_publisher:main'
        ],
    },
)


from setuptools import setup, find_packages
import pathlib, os, time



_name='onem2mlib-dev'
_version=time.strftime("%Y%m%d%H%M%S")

# _name='onem2mlib'
# _version='2026.06'



# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'tools/pypi/README.md').read_text()

# Find directories that are modules and have __init__.py
directories = [d for d,n,f in os.walk('onem2mlib') if '__init__.py' in f]
#print(directories)

setup(
	name=_name,
	version=_version,

	author='Andreas Kraft',
	author_email='an.kraft@gmail.com',

	classifiers=[
		'License :: OSI Approved :: BSD License',
		'Programming Language :: Python :: 3.11',
	],
	description='An open source implementation of a Python library for the oneM2M standard',
	include_package_data=True,
	install_requires=[
		'requests'
	],
	license='BSD',
	long_description=README,
	long_description_content_type='text/markdown',
	packages = directories,
	url='https://github.com/ankraft/onem2mlib',
)

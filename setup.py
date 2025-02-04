# -*- coding: utf-8 -*-
from setuptools import setup
import subprocess
from os import path

this_directory = path.abspath(path.dirname(__file__))

PACKAGE = "pytrendseries"

with open(path.join(this_directory, 'README_pypi.md'), encoding='utf-8') as f:
    long_description = f.read()

out = subprocess.Popen(['python', path.join(this_directory,'version.py')], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
stdout, _ = out.communicate()
version = stdout.decode("utf-8").strip()
print(version)

package_dir = \
{'': 'src'}

packages = \
[PACKAGE]

package_data = \
{'': ['*'],
 'detecttrend': ['.github/workflows/*']}

install_requires = \
[
 'tqdm>=4.60.0,<5.0.0']

extras_require = \
{':python_version <= "3.9"': ['matplotlib<=3.7.1', 'pandas<=1.5.3'],
 ':python_version >= "3.10"': ['matplotlib>=3.10.0', 'pandas>=2.2.3']}

setup_kwargs = {
    'name': PACKAGE,
    'version': version,
    'description': 'Detect trend in time series.',
    'long_description':long_description,
    'long_description_content_type':'text/markdown',
    'author': 'Rafael Rodrigues',
    'author_email': 'rafael.rafarod@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': f"https://github.com/rafa-rod/{PACKAGE}",
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

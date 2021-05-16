# -*- coding: utf-8 -*-
from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

packages = \
['detecttrend']

package_data = \
{'': ['*'],
 'detecttrend': ['.github/workflows/*',
                 '.pytest_cache/*',
                 '.pytest_cache/v/cache/*']}

install_requires = \
['matplotlib>=3.4.1,<4.0.0', 'pandas>=1.2.4,<2.0.0', 'tqdm>=4.60.0,<5.0.0']

setup_kwargs = {
    'name': 'detecttrend',
    'version': '0.1.0',
    'description': 'Detect trends on time series.',
    'long_description':long_description,
    'long_description_content_type':'text/markdown',
    'author': 'Rafael Rodrigues',
    'author_email': 'rafael.rafarod@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)


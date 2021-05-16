# -*- coding: utf-8 -*-
from setuptools import setup

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
    'long_description': None,
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


from setuptools import setup

setup(name='MitM',
      version='0.1',
      description='A reverse proxy MitM',
      packages=['mitm'],
      zip_safe=False,
      install_requires=[
          'kaitaistruct',
      ])
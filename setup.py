from setuptools import setup

import versioneer

setup(name='soaculib',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      )

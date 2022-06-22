from setuptools import setup

import versioneer

setup(name='soaculib',
      description='ACU Control Library for Simons Observatory',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      package_dir={'soaculib': 'python'},
      packages=['soaculib'],
      scripts=['scripts/acu-headsup', 'scripts/acu-special'],
      package_data={
          'soaculib': ['acu-configs.yaml']
      },
)

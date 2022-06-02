from setuptools import setup

setup(name='soaculib',
      description='ACU Control Library for Simons Observatory',
      package_dir={'soaculib': 'python'},
      packages=['soaculib'],
      scripts=['scripts/acu-headsup', 'scripts/acu-special'],
      install_requires=[
           'requests',
           'twisted',
      ],
      extras_require={
          'simulator': [
              'flask',
              'numpy',
              'scipy',
              'gunicorn',
          ],
      },
      )

from setuptools import setup


setup(name='ssh-switch',
      version='0.1',
      description='A command line tool to start and stop AWS EC2 instances using SSH aliases.',
      author='Thom Lane',
      packages=['ssh_switch'],
      entry_points={
          'console_scripts': ['ssh-switch=ssh_switch.script:main'],
      },
      install_requires=[
        'boto3'
      ]
)
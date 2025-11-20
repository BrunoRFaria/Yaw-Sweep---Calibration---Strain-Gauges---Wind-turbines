from setuptools import setup
# read the contents of your README file

from pathlib import Path
this_directory = Path(__file__).parent
# long_description = (this_directory / "yaw_sweep_sg_cali" / "README.md").read_text()
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(name='yaw_sweep_sg_cali',
version='4.0',
description='Package to generate the strain gauge calibration factors when those are placed on wind turbine towers. Based on idling operations, so called, yaw sweeps.', 
long_description = long_description,
long_description_content_type='text/markdown',
author='Bruno and Zahra',
author_email='brofa@dtu.dk',
packages=['yaw_sweep_sg_cali'],
install_requires = [
          'matplotlib',
          'numpy',
          'pandas',
          'pathlib',
          'scipy',
          'mysqlclient'
          ]

)
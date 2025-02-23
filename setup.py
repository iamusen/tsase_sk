#!/usr/bin/env python3

from skbuild import setup
import os

packages = []
for dirname, dirnames, filenames in os.walk('tsase'):
    if '__init__.py' in filenames:
        packages.append(dirname.replace('/', '.'))

scripts = [
    "bin/dump2xdat",
    "bin/kmc",
    "bin/lmp2con",
    "bin/lmp2pos",
    "bin/mobfil",
    "bin/neighbors",
    "bin/oldexpectra",
    "bin/pdf-make.py",
    "bin/soc2pos",
    "bin/splitxdat",
    "bin/temgui",
    "bin/tsase",
    "bin/water_solvate",
    "bin/water_solvate_z",
    "bin/xyz",
]

package_data = {
    'tsase': [
        'xyz/xyz.glade',
        'xyz/xyz.help',
        'xyz/*.png',
        'calculators/al/al_.so',
        'calculators/cuo/ffield.comb',
        'calculators/cuo/ffield.comb3',
        'calculators/cuo/in.lammps',
        'calculators/lepspho/lepspho_.so',
        'calculators/lisi/LiSi.meam',
        'calculators/lisi/in.lammps',
        'calculators/lisi/library.meam',
        'calculators/lj/lj_.so',
        'calculators/mo/Mo.set',
        'calculators/mo/in.lammps',
        'calculators/morse/morse_.so',
        'calculators/si/Si.meam',
        'calculators/si/library.meam',
        'calculators/w/W.set',
        'calculators/w/in.lammps'
    ]
}

setup(
    name='tsase',
    version='1.0',
    description='Library based upon ASE for transition state theory calculations.',
    author='Henkelman Research Group',
    author_email='henkelman@utexas.edu',
    url='http://www.henkelmanlab.org',
    packages=packages,
    scripts=scripts,
    package_data=package_data,
    include_package_data=True,
    zip_safe=False,
)

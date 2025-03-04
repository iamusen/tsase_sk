'''
The aluminum eam potential module.
'''

import numpy
from . import al_

from ase.calculators.calculator import Calculator


class al:

    def __init__(self):
        self.atoms = None
        self.u = None
        self.f = None
        al_.potinit()

    def get_potential_energy(self, atoms=None, force_consistent=False):
        if self.calculation_required(atoms, "energy"):
            self.atoms = atoms.copy()
            self.calculate()
        return self.u
        
    def get_forces(self, atoms):
        if self.calculation_required(atoms, "forces"):
            self.atoms = atoms.copy()
            self.calculate()
        return self.f.copy()
                        
    #def get_stress(self, atoms):
    #    raise NotImplementedError
        
    def calculation_required(self, atoms, quantities):
        if atoms != self.atoms or self.atoms == None:
            return True
        if numpy.any(self.f) == None or numpy.any(self.u) == None or numpy.any(atoms) == None:
            return True
        return False

    def set_atoms(self, atoms):
        pass

    def calculate(self):
        ra = self.atoms.positions.ravel()
        fa = ra * 0.0
        uRet = numpy.array([0], 'd')
        ax = self.atoms.cell[0][0]
        ay = self.atoms.cell[1][1]
        az = self.atoms.cell[2][2]
        al_.force(ra, fa, uRet, ax, ay, az)
        self.f = numpy.resize(fa, (len(self.atoms),3))
        self.u = uRet[0]



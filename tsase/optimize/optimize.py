"""Structure optimization. """

import sys
import pickle
import time
from math import sqrt
from os.path import isfile

import numpy as np

#from ase.parallel import rank, barrier #deprecated in ase 3.19.0
from ase.parallel import world, barrier
from ase.io.trajectory import PickleTrajectory


class Dynamics:
    """Base-class for all MD and structure optimization classes.

    Dynamics(atoms, logfile)

    atoms: Atoms object
        The Atoms object to operate on
    logfile: file object or str
        If *logfile* is a string, a file with that name will be opened.
        Use '-' for stdout.
    trajectory: Trajectory object or str
        Attach trajectory object.  If *trajectory* is a string a
        PickleTrajectory will be constructed.  Use *None* for no
        trajectory.
    """
    def __init__(self, atoms, logfile, trajectory):
        self.atoms = atoms

        if world.rank != 0:
            logfile = None
        elif isinstance(logfile, str):
            if logfile == '-':
                logfile = sys.stdout
            else:
                logfile = open(logfile, 'a')
        self.logfile = logfile
        
        self.observers = []
        self.nsteps = 0

        if trajectory is not None:
            if isinstance(trajectory, str):
                trajectory = PickleTrajectory(trajectory, 'w', atoms)
            self.attach(trajectory)

    def get_number_of_steps(self):
        return self.nsteps

    def insert_observer(self, function, position=0, interval=1, 
                        *args, **kwargs):
        """Insert an observer."""
        if not callable(function):
            function = function.write
        self.observers.insert(position, (function, interval, args, kwargs))

    def attach(self, function, interval=1, *args, **kwargs):
        """Attach callback function.

        At every *interval* steps, call *function* with arguments
        *args* and keyword arguments *kwargs*."""

        if not hasattr(function, '__call__'):
            function = function.write
        self.observers.append((function, interval, args, kwargs))

    def call_observers(self):
        for function, interval, args, kwargs in self.observers:
            if self.nsteps % interval == 0:
                function(*args, **kwargs)


class Optimizer(Dynamics):
    """Base-class for all structure optimization classes."""
    def __init__(self, atoms, restart, logfile, trajectory):
        """Structure optimizer object.

        atoms: Atoms object
            The Atoms object to relax.
        restart: str
            Filename for restart file.  Default value is *None*.
        logfile: file object or str
            If *logfile* is a string, a file with that name will be opened.
            Use '-' for stdout.
        trajectory: Trajectory object or str
            Attach trajectory object.  If *trajectory* is a string a
            PickleTrajectory will be constructed.  Use *None* for no
            trajectory.
        """
        Dynamics.__init__(self, atoms, logfile, trajectory)
        self.restart = restart

        if restart is None or not isfile(restart):
            self.initialize()
        else:
            self.read()
            barrier()
    def initialize(self):
        pass

###############################################################
    def run(self, fmax=0.05, emax= 0.001, steps=100000000,optimizer='L2',maximize=False):  
        """Run structure optimization algorithm.

        This method will return when the forces on all individual
        atoms are less than *fmax* or when the number of steps exceeds
        *steps*."""
        self.maximize = maximize
        self.fmax = fmax
        self.emax = emax
        step = 0
        while step < steps:
            if self.maximize == False:
             f = self.atoms.get_forces()
            else:
             f = - self.atoms.get_forces()
            self.log(f)
            self.call_observers()
            if optimizer == 'L2':
                if self.converged_L2(f):
                    return
            elif optimizer == 'maxatom':
                if self.converged(f):  
                    return
            elif optimizer == 'energy':
                if self.converged_PE(f):   
                    return
            elif optimizer == 'bgsd':
                if self.bgsd_check(f):
                    return
            self.step(f)
            self.nsteps += 1
            step += 1

    def converged(self, forces=None):
        """Did the optimization converge?"""
        if forces is None:
            forces = self.atoms.get_forces()
        if hasattr(self.atoms, 'get_curvature'):
            return (forces**2).sum(axis=1).max() < self.fmax**2 and \
                   self.atoms.get_curvature() < 0.0
        return (forces**2).sum(axis=1).max() < self.fmax**2

    def converged_L2(self, forces=None):
        """Did the optimization converge?"""
        if forces is None:
            forces = self.atoms.get_forces()
        if hasattr(self.atoms, 'get_curvature'):
            return np.sqrt(np.vdot(forces,forces)) < self.fmax and \
                   self.atoms.get_curvature() < 0.0
        return np.sqrt(np.vdot(forces,forces)) < self.fmax    

    def converged_PE(self, forces=None):
        """Did the optimization converge?"""
        return self.atoms.get_potential_energy() < self.emax

    def bgsd_check(self,  forces=None):
        if forces is None:
                    forces = self.atoms.get_forces()
        if self.atoms.get_potential_energy() < self.emax:
            return self.atoms.get_potential_energy() < self.emax
        else:
            return np.sqrt(np.vdot(forces,forces)) < self.fmax
            
    def log(self, forces):
        fmax = np.sqrt(np.vdot(forces,forces))
        e = self.atoms.get_potential_energy()
        T = time.localtime()
        if self.logfile is not None:
            name = self.__class__.__name__
            self.logfile.write('%s: %3d  %02d:%02d:%02d %15.10f %12.6f\n' %
                                           (name, self.nsteps, T[3], T[4], T[5], e, fmax))

            self.logfile.flush()
        
    def dump(self, data):
        if world.rank == 0 and self.restart is not None:
            pickle.dump(data, open(self.restart, 'wb'), protocol=2)

    def load(self):
        return pickle.load(open(self.restart))


class NDPoly:
    def __init__(self, ndims=1, order=3):
        """Multivariate polynomium.

        ndims: int
            Number of dimensions.
        order: int
            Order of polynomium."""
        
        if ndims == 0:
            exponents = [()]
        else:
            exponents = []
            for i in range(order + 1):
                E = NDPoly(ndims - 1, order - i).exponents
                exponents += [(i,) + tuple(e) for e in E]
        self.exponents = np.array(exponents)
        self.c = None
        
    def __call__(self, *x):
        """Evaluate polynomial at x."""
        return np.dot(self.c, (x**self.exponents).prod(1))

    def fit(self, x, y):
        """Fit polynomium at points in x to values in y."""
        A = (x**self.exponents[:, np.newaxis]).prod(2)
        self.c = np.linalg.solve(np.inner(A, A), np.dot(A, y))


def polyfit(x, y, order=3):
    """Fit polynomium at points in x to values in y.

    With D dimensions and N points, x must have shape (N, D) and y
    must have length N."""
    
    p = NDPoly(len(x[0]), order)
    p.fit(x, y)
    return p

import ase
import numpy

def read_xdatcar(filename, skip=0, every=1):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    lattice_constant = float(lines[1].strip())
    cell = numpy.array([[float(x) * lattice_constant for x in lines[2].split()], 
                        [float(x) * lattice_constant for x in lines[3].split()], 
                        [float(x) * lattice_constant for x in lines[4].split()]])
    elements = lines[5].split()
    natoms = [int(x) for x in lines[6].split()]
    nframes = (len(lines)-7)/(sum(natoms) + 1)
    trajectory = []
    for i in range(skip, int(nframes), every):
        a = ase.Atoms('H'*sum(natoms))
        a.masses = [1.0] * len(a)
        a.set_chemical_symbols(''.join([n*e for (n, e) in zip(natoms, elements)]))
        a.cell = cell.copy()
        a.set_pbc((True, True, True))
        j = 0
        for N, e in zip(natoms, elements):
            for k in range(N):
                split = lines[8 + i * (sum(natoms) + 1) + j].split()
                a[j].position = [float(l) for l in split[0:3]]
                j += 1
        a.positions = numpy.dot(a.positions, cell)
        trajectory.append(a)

    return trajectory



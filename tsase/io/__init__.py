import ase.io
from .con import read_con, write_con
from .feff import read_feff, write_feff
from .bopfox import read_bopfox, write_bopfox
from .vasp import read_xdatcar
from .lammps import read_lammps, read_dump
from .socorro import read_socorro, write_socorro
from .aims import read_aims, write_aims
from .colors import read_colors

def read_vasp_multiframe(filename, skip, every):
    try:
        xdat = read_xdatcar(filename, skip, every)
        if type(xdat) == list and len(xdat) > 1:
            return xdat
    except:
        pass
    f = open(filename, 'r')
    data = []
    while True:
        try:
            data.append(ase.io.read(f, format='vasp'))
        except:
            f.close()
            break
    if len(data) < 1:
        raise IOError("Could not read file %s as vasp file." % filename)
    if len(data) < 2:
        return data[0]
    return data
            

def read(filename, skip, every):

    try:
        return read_con(filename)
    except:
        pass
    try: 
        return read_bopfox(filename)
    except:
        pass
    try:
        return read_lammps(filename)
    except:
        pass
    try:
        return read_vasp_multiframe(filename, skip, every)
    except:
        pass
    try: 
        return read_dump(filename)
    except:
        pass
    try:
        return read_socorro(filename)
    except:
        pass
    try:
        return read_feff(filename)
    except:
        pass
    try:
        return ase.io.read(filename+"@:", format='xyz')
    except:
        pass
    try:
        return ase.io.read(filename+"@:", format='aims')
#        a = read_aims(filename)
#        if len(a.positions) < 1:
#            raise
#        return a
    except:
        pass
    try:
        return ase.io.read(filename+"@:")
    except:
        pass
    raise IOError("Could not read file %s." % filename)

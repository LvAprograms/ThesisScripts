from matplotlib import pyplot as plt
import numpy as np

class Material(object):
    """Holds material properties read from the database table with keyword word"""
    def __init__(self, line):
        d = line
        self.type        = d[0]             # material index              -
        self.eta_MIN     = d[1]             # Minimum viscosity        Pa.s
        self.eta_MAX     = d[2]             # Maximum viscosity        Pa.s
        self.sigma_MIN   = d[3]             #                          Pa
        self.sigma_MAX   = d[4]             #                          Pa
        self.inv_Ad      = d[5]             # 1/Ad                     Pa^n/s
        self.Ad          = 1/self.inv_Ad    # Pre-np.exponential factor   Pa^n-1/s
        self.Ea          = d[6]             # Activation energy E,     J/mol
        self.Va          = d[7]             # Activation volume
        self.sigma_trans = d[8]             # change disl to diffcreep Pa
        self.n           = d[9]             # Stress np.exponent,         -
        self.G           = d[10]            # elastic shear modulus,   Pa
        self.defLamb     = d[11]            # default lambda(1-Pf/Ps) when no fluids
        self.Cmin        = d[12]            # min. cohesion,           Pa
        self.Cmax        = d[13]            # max. cohesion            Pa
        self.mu_min      = d[14]            # min. friction coeff      -
        self.mu_max      = d[15]            # max. friction coeff      -
        self.eps_trans   = d[16]            # needed strain for weaken.-
        self.eps_max     = d[17]            # strain when max weakened.-
        self.rho_lim1    = d[18]            # something with dilatation-
        self.rho_lim2    = d[19]            # same                     -
        self.rho_0       = d[20]            # initial density          kg/m3
        self.alpha       = d[21]            # thermal np.expansivity      K-1
        self.beta        = d[22]            # compressibility          MPa-1
        self.Cp          = d[23]            # Volumetric heat capac.   J/kg/K
        self.k0          = d[24]            # thermal conductivity     W/m/K
        self.kz          = d[25]            # T dep. coeff for k       -
        self.kP          = d[26]            # P dep. coeff for k       -
        self.Hr          = d[27]            # internal heat production W/m3

nz = 251
z = np.arange(0, nz)
materials = np.zeros((nz, 1))
IDs = []
with open('rockprops.txt') as f:
    for line in f.readlines():
        line = line.split()
        IDs.append([float(v) for v in line])

def calc_visc(id, eii):
    m = Material(id)
    return m.Ad * eii * np.exp(m.Ea + m.)

eii = 1e-15
for i, z in enumerate(nz):
    if i < 21:
        sd = ID
from matplotlib import pyplot as plt
import numpy as np

class Znode(object):
    def __init__(self, i, z):
        self.index = i
        self.material = None    # assigned in strprofs.py
        self.z = z              # depth in meters
        self.T0 = 293           # surface temperature
        self.T = 0              # Temperature at this node
        self.eta_eff = 0        # effective viscosity read from hdf5 file
        self.P = 0              # Pressure read from hdf5 file
        self.k = 0

    def calc_T(self, Ta, L):
        """Calculates initial geotherm"""
        if self.z <= L:
            return self.z * (Ta - self.T0) / L + self.T0
        else:
            return (self.z - L) * 5E-4 + Ta

    def calc_rho(self):
        """
        Method to verify the formula used for the density calculation.
        It's rho_0 * (1 + beta(P - P0)) / (1 + alpha(T - T0)
        """
        x = self.material
        a = 1 + x.alpha * (self.T - self.T0)
        b = 1 + x.beta/100 * (self.P/1E6 - 0.1)
        return x.rho_0 * (b/a)

    def calc_k(self):
        x = self.material
        return (x.k0 + x.kz / (self.T + 77)) * (np.exp(x.kP * self.P/1E6))



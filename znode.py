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


class Material(object):
    """Holds material properties read from the database table with keyword word"""
    def __init__(self, word, table):
        self.data = table[word]
        d = self.data
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


class StrengthProfile(object):
    def __init__(self, Zdata:list, materials, strainratelists, log=False):
        self.materials = materials          # Layering used
        self.log = log
        self.nodes = Zdata                  # Nodes
        self.z = [n.z for n in self.nodes]  # depth vector in m
        self.sigma_britmax = []             # yield strength for mu_max
        self.sigma_britmin = []             # yield strength for mu_min
        self.sigma_visc = []                # Viscous strength (2 * eta_eff * strainrate)
        self.strengthmax = []               # Yield strength in the case of sigma_britmax
        self.strengthmin = []               # Yield strength in the case of sigma_britmin
        self.strainrates = strainratelists  # input the strainrates for which the viscous strength is calculated
        self.fig, self.ax = plt.subplots()  # Figure to hold the strength profile
        self.calc_rho()
        self.calc_k()
        self.calc_brittle()
        # self.ax.invert_yaxis()

    def calc_brittle(self):
        # mutot = 0
        for node in self.nodes:
            # mutot += node.material.mu_max
            self.sigma_britmax.append(node.material.Cmax + node.material.mu_max * node.P) # TODO: Where is Pf/Ps?
            # if node.P <= 200e6:
            #     self.sigma_britmax.append(node.material.Cmax + 0.85 * node.P)
            # else:
            #     self.sigma_britmax.append(node.material.Cmax + 0.60 * node.P)
            self.sigma_britmin.append(node.material.Cmax + node.material.mu_min * node.P)
        # print(mutot / len(self.nodes)) # Check average (maximum) friction in the model

    def calc_rho(self):
        rho = []
        for node in self.nodes:
            rho.append(node.calc_rho())
        # plt.plot(rho, [z/1000 for z in self.z])
        # plt.xlim([2700, 3500])
        # plt.ylim([20, 200])
        # plt.gca().invert_yaxis()
        # plt.xlabel("Density [kg/m3]")
        # plt.ylabel("Depth [km]")
        # plt.grid(b=True)
        # plt.show()

    def calc_k(self):
        k = []
        for node in self.nodes:
            k.append(node.calc_k())
        # plt.figure()
        # plt.plot(k, self.z)
        # plt.ylim([200e3, 20e3])
        # plt.xlim([0, 10])
        # plt.show()

    def calc_viscous(self, strainrate:float):
        for i, node in enumerate(self.nodes):
            self.sigma_visc.append(2 * node.eta_eff * strainrate)

    def draw_layering(self):
        """Draw the bottom boundaries of each rheological layer on the axis"""
        prev = None
        labels = {0.0:"Sticky air", 5.0:"Upper crust", 6.0:"Moho", 9.0:"Lithospheric Mantle"}
        for i, node in enumerate(self.nodes):
            if prev is not None:
                if prev.material != node.material:
                    self.ax.plot([0, 2000], [prev.z/1000, prev.z/1000],'--', linewidth=2, label=labels[prev.material.type])
                prev = node
            else:
                prev = node
        self.ax.set_xlabel("Differential stress [MPa]")
        self.ax.set_ylabel("Depth [km]")
        self.ax.grid(b=True)


    def draw(self, strainrate:float=1E-14, zmin=20, zmax=150):
        """Calculates strength and plots it against depth"""
        self.calc_viscous(strainrate)
        for i, sv in enumerate(self.sigma_visc):
            if sv <= self.sigma_britmin[i]:
                self.strengthmin.append(sv)
            else:
                self.strengthmin.append(self.sigma_britmin[i])
            if sv <= self.sigma_britmax[i]:
                self.strengthmax.append(sv)
            else:
                self.strengthmax.append(self.sigma_britmax[i])

        mpamax = [val/1E6 for val in self.strengthmax]
        mpamin = [val/1E6 for val in self.strengthmin]
        if self.log:
            self.ax.semilogx(mpamax, [z/1000 for z in self.z], label=r'$\mu_{max}, \dot{\epsilon}$' + "= {}".format(strainrate))
        else:
            self.ax.plot(mpamax, [z/1000 for z in self.z], label=r'$\mu_{max}, \dot{\epsilon}$' + "= {}".format(strainrate))

        # self.ax.plot(mpamin, [z/1000 for z in self.z], label=r'$\mu_{min}, \dot{\epsilon}$' + "= {}".format(strainrate))

        self.ax.set_ylim(zmax, zmin)
        if self.log:
            self.ax.set_xlim([1E0, 1E4])
        else:
            self.ax.set_xlim([0, 2000])

    def add_profile(self, strainrate:float):
        """Add the profile for another strainrate """
        self.sigma_visc = []
        self.strengthmin = []
        self.strengthmax = []
        self.draw(strainrate)
        # self.ax.invert_yaxis()

    def draw_all(self):
        for e in self.strainrates:
            self.add_profile(e)
        plt.legend(ncol=2, loc='upper right', fancybox=True)


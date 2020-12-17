from math import erf, sqrt
from matplotlib import pyplot as plt
from numpy import zeros


def halfspacetemp(T0, T1, diffusivity, ageseconds, depth):
    return T1 + (T0 - T1) * (1 - erf((depth-22e3) / (2*sqrt(diffusivity * ageseconds))))

T1 = 1617.6
T0 = 273.15
K = 1E-6

ageMy = [40, 70, 100]
depths = [range(20000, 200100, 100), range(20000, 120100, 100)]

plt.figure()

for age in ageMy:
    for depth in depths:
        agesec = age * 1E6 * 60 * 60 * 24 *365.25
        T = zeros((len(depth), 1))

        for i, d in enumerate(depth):
            T[i] = (halfspacetemp(T0, T1, agesec, K, d))

        plt.plot(T, [d/1000 for d in depth],'-', label=r'$LAB={}$km, $\tau$ = {}Myr'.format(depth[-1]/1e3, age))

plt.grid(b=True)
plt.xlim([T0, T1])
plt.ylim([200,0])
plt.xlabel("T [K]")
plt.ylabel("z [km]")
plt.legend()
plt.show()


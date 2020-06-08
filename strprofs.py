from znode import *
from find_x import *
import h5py as h5
import numpy as np

COL = 1200                # where on the x axis do we want a strength profile
Lz = 800e3              # Depth of model, m
nz = 508               # amount of nodes
L_sticky = 20e3         # Thickness of sticky air
L_uc = L_sticky + 20e3  # upper crustal bottom depth
L_lc = L_uc + 15e3      # lower crustal bottom depth
L_lm = 100e3            # lithosphere thickness
L_m = L_lc              # moho depth
nx = 1648
# Read the data
modelname = "CW"
f = h5.File('E:/ThesisData/{}/setup001.gzip.h5'.format(modelname), 'r')
dset = f['NodeGroup']
print(list(f['VisMarkerGroup'].keys()))
print(list(dset.keys()))
rho_tmp = dset['ro']
tk_tmp = dset['tk']
pr_tmp = dset['pr']
tk_tmp = np.reshape(tk_tmp, (nx, nz))
pr_tmp = np.reshape(pr_tmp, (nx, nz))
rho_tmp = np.reshape(rho_tmp, (nx, nz))
eta_tmp = np.reshape(dset['nu'], (nx, nz))

# Construct material database for this profile
database = {}
with open("CJ_rocprops.txt", 'r') as rheology:
    rock = "rockless"
    for i, line in enumerate(rheology.readlines()):
        if line.startswith("/"):
            rock = line.strip('/').strip('\n')
            if rock not in database.keys():
                database[rock] = []
            else:
                rock += "{}".format(i)
                database[rock] = []

        else:
            if rock != "rockless":
                for v in line.strip('\n').split():
                    database[rock].append(float(v))


materials = {"SA": Material("sticky_air_approximation", database),
             "UC": Material("upper_continental_crust_dalzilio2018_wet_quartzite", database),
             "LC": Material("lower_continental_crust_dalzilio2018_mafic_granulite", database),
             "UOC": Material("interface_basalt_wet_quartzite", database),
             "LOC": Material("lower_oceanic_crust_gabbro_anorthite_75%", database),
             "LM": Material("lithospheric_mantle_dry_olivin", database),
             "AM": Material("astenospheric_mantle_dry_olivin",database)}

# for k, v in database.items():
#     if k.startswith("dalzilio2018"):
#         print("{}: {}".format(k, v))
#
x_stag = []
x = []
x_size = f['ModelGroup']['Model'][1]
z_size = f['ModelGroup']['Model'][2]
x_nodes = int(f['ModelGroup']['Model'][3])
for i in range(1, x_nodes+1):
    x.append(find_x(i))
    if i > 1:
        x_stag.append((x[i - 2] + x[i-1])/2)
print(x_stag[0], x_stag[-1])


nodes = []
nodes.append(Znode(0, 0))
z = [0]
nodes[0].material = materials["SA"]
for i in range(1, nz):
    if i < 250:
        nodes.append(Znode(i, nodes[i - 1].z + 400))
        z.append(z[i-1] + 400)
        if nodes[i].z <= L_sticky:
            nodes[i].material = materials["SA"]
        elif L_sticky < nodes[i].z <= L_uc:
            nodes[i].material = materials["UC"]
        elif L_uc < nodes[i].z <= L_m:
            nodes[i].material = materials["LC"]
        elif L_m < nodes[i].z <= L_lm:
            nodes[i].material = materials["LM"]
    elif 250 <= i < 300:
        nodes.append(Znode(i, nodes[i - 1].z + 1000))
        z.append(z[i-1] + 1000)
        if L_m < nodes[i].z <= L_lm:
            nodes[i].material = materials["LM"]
        else:
            nodes[i].material = materials["AM"]
    elif 300 <= i < 350:
        nodes.append(Znode(i, nodes[i - 1].z + 2500))
        z.append(z[i-1] + 2500)
        nodes[i].material = materials["AM"]
    elif 350 <= i < nz:
        nodes.append(Znode(i, nodes[i - 1].z + 5000))
        z.append(z[i-1] + 5000)
        nodes[i].material = materials["AM"]


# Visualise variables in 1D
vars = [tk_tmp, pr_tmp, rho_tmp, np.log10(eta_tmp)]
xlabels = ["Temperature [K]", "Pressure [Pa]", "Density [kg/m3]", r'log$_{10}(\eta_{eff})$']
fig, axes = plt.subplots(2,2)
plt.suptitle("Visualisation parameters for model {} at x = {}km".format(modelname, find_x(COL)))
for i, var in enumerate(vars):
    var = var.transpose()
    axes.flatten()[i].plot(var[:, COL], [n.z/1000 for n in nodes])
    #fig.colorbar(axes.flatten()[i].pcolormesh(var), cmap='hot', ax=axes.flatten()[i])
    axes.flatten()[i].invert_yaxis()
    axes.flatten()[i].grid(b=True)
    axes.flatten()[i].set_xlabel(xlabels[i])
    axes.flatten()[i].set_ylabel("Depth [km]")
    axes.flatten()[i].set_ylim([250, 0])
    # axes.flatten()[i].colorbar()
# plt.show()
axes.flatten()[2].set_xlim([2700, 3550])
# dset = f['VisMarkerGroup']
# print(dset['Mtype'])

plt.figure()
plt.plot([node.material.type for node in nodes], [node.z/1000 for node in nodes],'-')
plt.ylim([0, 100])
plt.gca().invert_yaxis()


# for rock, data in database.items():
#     print(rock, data)
# print(len(database['sticky_air_approximation']))


# """
for node in nodes:
    node.rho = rho_tmp.transpose()[node.index, COL]
    node.eta_eff = eta_tmp.transpose()[node.index, COL]
    node.P = pr_tmp.transpose()[node.index, COL]
    node.T = tk_tmp.transpose()[node.index, COL]
# axes[1,1].plot(pr_tmp.transpose()[:, COL], [n.z for n in nodes])
strprof = StrengthProfile(nodes, materials, [1E-14, 1E-16], log=False)
strprof.draw_layering()
strprof.draw_all()
# strprof.add_profile(strainrate=1E-16)
# strprof.add_profile(strainrate=1E-15)
plt.title("vertical strength profile through x = {} km".format(find_x(COL)))
 # """
plt.show()


# fig, [ax1, ax2] = plt.subplots(1,2)
# y = [n.z for n in nodes]
# x = [n.material.type for n in nodes]
# ax1.plot(x,y)
# plt.grid(b=True)
# ax1.invert_yaxis()
# # plt.show()
#
# # Initial geotherm
# T = np.zeros(nz)
# T0 = 293    # K
# Tm = 1617.6 # K
# T[0] = 293
# c0 = T[0]
# for node in nodes:
#     node.T = node.calc_T(Tm, L_lm)
# xT = [n.T for n in nodes]
# ax2.plot(xT, y)
# ax2.invert_yaxis()
# plt.show()

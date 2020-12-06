from matplotlib import pyplot as plt
from numpy import array
from plot_slabpull import *
BASEPATH = "E:\ThesisData\\"
MODEL = "FJ"

def read_data(model, file):
    time = []
    data = []
    with open(BASEPATH + model + '\\{}_MDdata_{}.txt'.format(model, file)) as f:
        for line in f.readlines():
            line = line.split()
            time.append(float(line[0])/1e6)
            data.append([float(line[i]) for i in range(1,5)])
    return time, array(data)


def plot_drag(model, ax):
    files = ["mean"]
    labels = [" at z=158.25 km", " at z = 159.25 km", " at z = 160.25 km", " at z= 161.25 km", " z = 162.25 km"]
    for file in files:
        time, data = read_data(model, file)
        for i in range(4):
            ax.plot(time[2:], abs(data[2:, i]), label=model +": "+file+labels[i])
            # ax.semilogy(time, -data[:,i])
    plt.grid(b=True)
    # ax.set_xlim([0, max(time) + 5])
    ax.set_xlim([0, 45])
    ax.set_ylim([1e9, 4e15])


fig, ax = plt.subplots()
# plot_drag("ER", ax)
# for m in ["ER", "FQ", "FR", "FS", "FT"]:
#     plot_drag(m, ax)
#     t, SP, A = plot_SP_data(m, overlay=True)
#     ax.semilogy(t, abs(array(SP)),'m--', label="Slab Pull")
plot_drag(MODEL, ax)
t, SP, A = plot_SP_data(MODEL, overlay=True)
ax.semilogy(t, abs(array(SP)),'m--', label="Slab Pull")
ax.set_xlabel("Time [Myr]")
ax.set_ylabel("Mantle drag force magnitude[N/m]")
# ax.set_xlim([0, 10])
plt.legend(loc='lower right')
plt.show()

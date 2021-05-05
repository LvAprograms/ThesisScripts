from matplotlib import pyplot as plt
from numpy import array, zeros

def cm_to_inch(val:float):
    return val * 0.393700787

def plot_SP_data(model, overlay=False):
    t = []
    SP = []
    A = []
    with open("E:\ThesisData\{}\{}_SPdata.txt".format(model, model), 'r') as f:
        for line in f.readlines():
            if line.startswith('time'):
                pass
            else:
                data = line.split()
                if float(data[0]) / 1e6 < 0.01:
                    pass
                else:
                    t.append(float(data[0]) / 1e6)
                    SP.append(float(data[1]))
                    A.append(float(data[2]))
    if overlay:
        return t, SP, A
    else:
        fig, ax = plt.subplots(2, 1, figsize=(cm_to_inch(14.0), cm_to_inch(15.2)))
        ax[0].plot(t, SP, 'r*-', label=model)
        ax[1].plot(t, A, 'rx-', label=model)
        # ax[0].set_xlabel('Time [Myr]')
        ax[1].set_xlabel('Time [Myr]')
        ax[0].set_ylabel('Slab pull force [N/m]')
        ax[1].set_ylabel(r'Slab area [$m^2$]')
        ax[0].grid(b=True)
        ax[1].grid(b=True)
        return fig, ax


from matplotlib import pyplot as plt
from numpy import array, zeros

def cm_to_inch(val:float):
    return val * 0.393700787

def plot_SP_data(model, overlay=False):
    t = []
    SP = []
    A = []
    with open("E:\ThesisData\{}\{}_SPdata.txt".format(model, model), 'r') as f:
        for line in f.readlines():
            if line.startswith('time'):
                pass
            else:
                data = line.split()
                if float(data[0]) / 1e6 < 0.01:
                    pass
                else:
                    t.append(float(data[0]) / 1e6)
                    SP.append(float(data[1]))
                    A.append(float(data[2]))
    if overlay:
        return t, SP, A
    else:
        fig, ax = plt.subplots(2, 1, figsize=(cm_to_inch(14.0), cm_to_inch(15.2)))
        ax[0].plot(t, SP, 'r*-', label=model)
        ax[1].plot(t, A, 'rx-', label=model)
        # ax[0].set_xlabel('Time [Myr]')
        ax[1].set_xlabel('Time [Myr]')
        ax[0].set_ylabel('Slab pull force [N/m]')
        ax[1].set_ylabel(r'Slab area [$m^2$]')
        ax[0].grid(b=True)
        ax[1].grid(b=True)
        return fig, ax

if __name__ =="__main__":
    Models = ["ER", "FI", "FJ", "FK"]
    colours = ['r', 'b', 'k', 'g', 'c', 'y']
    labels = ["610 km ocean", "510 km ocean", "410 km ocean", "310 km ocean"]
    fig, ax = plot_SP_data("ER", overlay=False)
    # fig, ax = plt.subplots(2,1)
    for i, model in enumerate(Models):
        t, SP, A = plot_SP_data(model, overlay=True)
        if model != "ER":
            ax[0].plot(t, SP,'-', color=colours[i], label=model + ": " + labels[i])
            ax[1].plot(t, A, '-', color=colours[i], label=model + ": " + labels[i])
        else:
            ax[0].plot(t, SP, '-', color=colours[i], marker='*', label=model + ": " + labels[i])
            ax[1].plot(t, A, '-', color=colours[i], marker='x', label=model + ": " + labels[i])
    # fig, ax = plot_SP_data("FI", overlay=False)
    # t, SP, A = plot_SP_data("ER", overlay=True)
    # ax[0].plot(t, SP,'g--')
    # ax[1].plot(t, A, 'g--')
    # for a in ax:
        # a.set_xlim([0, 20])
    # ax[0].set_xlabel('Time [Myr]')
    ax[1].set_xlabel('Time [Myr]')
    ax[0].set_ylabel('Slab pull force [N/m]')
    ax[1].set_ylabel(r'Slab area [$m^2$]')
    [_.set_xlim([0,45]) for _ in ax]
    ax[0].set_ylim([-1.7e14, 0.5e14])
    ax[1].set_ylim([0, 4e11])
    ax[0].grid(b=True)
    ax[1].grid(b=True)
    # fig.legend(bbox_to_anchor=(0.5, 0.0), ncol=4, loc='lower center', borderaxespad=0.1, fancybox=True)
    # plt.subplots_adjust(bottom=0.15)  # place legend below figure
    # plt.show()
    # plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                        hspace=0.2, wspace=0)
    plt.margins(0, 0)
    plt.savefig('{}.png'.format(labels[0].split()[-1]), bbox_inches='tight', pad_inches=0)
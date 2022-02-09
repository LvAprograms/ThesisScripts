from matplotlib import pyplot as plt
from numpy import array, zeros, amax, amin
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

def cm_to_inch(val:float):
    return val * 0.393700787

def plot_SP_data(model, overlay=False):
    t = []
    SP = []
    A = []
    with open("C:\\Users\\luukv\\Documents\\Studie\\Masters\\Jaar2\\MSc_thesis\\PAPER\\forcedata\\{}_SPdata.txt".format(model), 'r') as f:
    # with open("C:\\Users\\luukv\\Documents\\ThesisData\\{}\\{}_SPdata.txt".format(model, model), 'r') as f:
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
        return array(t), array(SP), array(A)
    else:
        fig, ax = plt.subplots(2, figsize=(8, 4.0))
        #cm_to_inch(14.0), cm_to_inch(15.2))
        ax[0].plot(t, SP, 'r*-', label=model)
        ax[1].plot(t, A, 'r*-', label=model)
        for axis in ax:
            axis.xaxis.set_major_locator(MultipleLocator(10))
            axis.xaxis.set_major_formatter('{x:.0f}')
            axis.xaxis.set_minor_locator(MultipleLocator(5))
        # ax[0].set_xlabel('Time [Myr]')
        ax[1].set_xlabel('Time [Myr]')
        ax[0].set_ylabel('Slab pull force [N/m]')
        ax[1].set_ylabel(r'Slab area [$m^2$]')

        ax[0].grid(b=True)
        ax[1].grid(b=True)
        return fig, ax


if __name__ =="__main__":
    # dictionary to hold colours and labels for each model to prevent mistakes.
    idclrs = {"ER": ['r', 'ref'], "FI": ['b', 'oc510'], "FI_shortpush": [(0, 0, 0.67), 'oc510sp'], "FJ": ['k', 'oc410'], "FK": ['g', 'oc310'],
              "FP_rerun": [(1, 153 / 255, 153 / 255), 'peierls'], "FQ": ['c', 'LM25'], "FR": ['y', 'LM50'],
              "FS": ['m', 'LM75'], "FT": [(139 / 255, 69 / 255, 19 / 255), 'LMoc510'], "FX": [(0.8, 0.8, 0.8),
                                                                                              'slowref']}

    Models = ["ER", 'FI', 'FJ', 'FK', 'FP_rerun', 'FQ', 'FR', 'FS', 'FT', 'FX']
    # Models = ["ER", "FQ", "FR", "FS", "FT"]
    # Models = ["ER", "FI", "FJ", "FK"]
    # Models = ["FP"]
    # filename = "oceanlength_old"
    filename = "selection"
    # fig, ax = plot_SP_data("ER", overlay=False)
    fig, ax = plt.subplots(2, figsize=(8, 3.5))
    for axis in ax:
        axis.xaxis.set_major_locator(MultipleLocator(10))
        axis.xaxis.set_major_formatter('{x:.0f}')
        axis.xaxis.set_minor_locator(MultipleLocator(5))
    for i, model in enumerate(Models):
        t, SP, A = plot_SP_data(model, overlay=True)
        if model != "ER":
            ax[0].plot(t, SP, '-', color=idclrs[model][0], label= idclrs[model][1])
            ax[1].plot(t, A, '-', color=idclrs[model][0])
            print("Peak slab pull of {:.3e} N/m reaced at t = {} for model {}".format(min(SP), t[SP.argmin()], model))
        else:
            ax[0].plot(t, SP, '-', color=idclrs[model][0], marker='*', label=idclrs[model][1])
            ax[1].plot(t, A, '-', color=idclrs[model][0], marker='*')
            print("Peak slab pull of {:.3e} N/m reaced at t = {} for model {}".format(min(SP), t[SP.argmin()], model))
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
    [_.set_xlim([0, 115]) for _ in ax] if "FX" in Models else [_.set_xlim([0, 60]) for _ in ax]
    ax[0].set_ylim([-4.7e14, 0.8e14]) if "FX" in Models else ax[0].set_ylim([-1.7e14, 0.7e14])
    ax[0].plot([0, 120], [0, 0], 'k:', linewidth=2)
    ax[1].set_ylim([0, 8.1e11]) if "FX"in Models else ax[1].set_ylim([0, 5e11])
    ax[0].legend(bbox_to_anchor=(0.5, 1.25), ncol=5, loc='upper center', borderaxespad=0.1, fancybox=True)
    # plt.subplots_adjust(bottom=0.15)  # place legend below figure
    # plt.show()
    # plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                        hspace=0.2, wspace=0)
    plt.margins(0, 0)
    plt.savefig('C:/Users/luukv/Documents/Studie/Masters/Jaar2/MSc_thesis/PAPER/modelfigs/forces/{}.png'.format(filename), bbox_inches='tight', pad_inches=0, dpi=300)

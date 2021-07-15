import numpy as np
import matplotlib.pyplot as plt
import cProfile
import pstats

class PTtProf(object):
    """
    object able to parse the file PTt.log for time, coordinates, pressure and time data for a specific marker <ID>
    inputs:
    index: marker ID
    data: file with PTt data
    """
    def __init__(self, index, data):
        # print(index)
        self.i = int(index)
        self.d = data

    def process_data(self):
        """
        function that processes the input data to extract the necessary arrays for PTt path construction
        :return: time, x, y, P, T arrays
        """
        time = np.round(self.d[:, 1] / 1e6, 2)
        x = self.d[:, 2] / 1e3
        y = self.d[:, 3] / 1e3
        P = self.d[:, 4] / 1e9
        T = self.d[:, 5] - 273.15
        return time, x, y, P, T

    def plot(self, ax, timethreshold, MARKERS):
        """
        :param ax: axis to plot on
        :param timethreshold: determines how many steps should be plotted (and skips data with too small increments),
        e.g. 1 point per 0.5 MYr. Especially in the startup phase, time slowly progresses.
        :param MARKERS: markers for plotting. Default is given in the :class: PTtProfManager
        :return: labeltimes (times that were actually used for plotting) and scatter object (sco).
        """
        time, x, y, P, T = self.process_data()
        points = np.arange(0, np.round(max(time), 1), 0.5)
        plotpoints = []
        labeltimes = []
        loc = 0
        # search algorithm: iterate over idealised time series `points`, minimise difference with actual data points
        # and fill arrays to use for plotting. In this case a while loop is much more convenient than a for loop. 
        for i, point in enumerate(points):
            err = 100
            j = loc
            while err > timethreshold:
                tmp = abs(time[j] - point)
                if tmp < err:
                    err = tmp   # starting difference between idealised time vector point and actual time data
                    loc = j     # location of minimum difference
                    lab = point  # timestamp of this minimum difference point
                    if loc > 0:
                        plotpoints.append((T[loc], P[loc]))
                        labeltimes.append(lab)
                j += 1
        plotpoints = np.array(plotpoints)
        sco = ax.scatter(plotpoints[:, 0], plotpoints[:, 1], marker=MARKERS.pop(0), c=labeltimes, cmap='hot', vmin=0, vmax=55)

        return labeltimes, sco



class PTtProfManager(object):
    def __init__(self, file, timethreshold, BOTTLENECKING=False):
        """
        Management class capable of combining indidual marker PTt paths into one PTt figure
        :param file: file containing the PTt data
        :param timethreshold: ideal time interval between two plotted points
        """
        self.MARKERS = ['*', 'd', '^', 'o', 'v']
        self.thresh = timethreshold
        self.BOTTLENECKING = BOTTLENECKING
        self.f = file
        self.profiles = []
        self.assign_profiles()
        self.plot_ensemble()


    def assign_profiles(self):
        """
        Process data file into different PTtprof classes and combines them in the list self.profiles
        :return: nothing
        """
        markerdata = {}
        with open(self.f) as f:
            # 5 different markers
            for line in f.readlines():
                l = line.split()
                k = l[0]
                if k not in list(markerdata.keys()):
                    markerdata[k] = []
                markerdata[k].append(list([float(l[i]) for i in range(1, len(l))]))

        for marker, data in markerdata.items():
            self.profiles.append(PTtProf(marker, np.array(data)))
        print("Profiles assigned...")

    def plot_ensemble(self):
        """
        Iterates over child PTtProf objects and combines each plot into one ensemble PTt plot.
        :return: nothing
        """
        fig, ax = plt.subplots()
        plt.xlabel("T [Celsius]")
        plt.ylabel("P [GPa]")
        plt.grid(b=True)
        # plt.title("PTt path ")
        labels = {}
        if self.BOTTLENECKING:
            prof = cProfile.Profile()
            prof.enable()
        sco = None  # scatter object placeholder
        for i, profile in enumerate(self.profiles):
            print("Plotting profile {}...".format(i))
            labels[profile.i], sco = profile.plot(ax, self.thresh, self.MARKERS)
        if self.BOTTLENECKING:
            ps = pstats.Stats(prof)
            ps.sort_stats('calls', 'cumtime')
            ps.print_stats(5)

        plt.legend(labels, loc='upper left')
        plt.xlim([0, 850])
        plt.ylim([0, 4])
        cb = plt.colorbar(sco)
        cb.set_label("Time [Myr]")
        print("Done")


if __name__ == "__main__":
    models = ["ER", "FI", "FJ", "FK", "FQ", "FR", "FS", "FT", "FX"]
    for m in models:
        PM = PTtProfManager("C:\\Users\\luukv\\Documents\\Studie\\Masters\\Jaar2\\MSc_thesis\\PAPER\\" +
                                               "modelfigs\\PTt\\{}_PTt.log".format(m), timethreshold=0.001)
        plt.savefig("C:\\Users\\luukv\\Documents\\Studie\\Masters\\Jaar2\\MSc_thesis\\PAPER\\" +
                                                "modelfigs\\PTt\\{}_PTt.png".format(m))



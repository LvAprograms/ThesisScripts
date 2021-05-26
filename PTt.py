import numpy as np
import matplotlib.pyplot as plt
import cProfile
import pstats

MARKERS = ['*','d','^','o','v']
class PTtProf(object):
    def __init__(self, index, data):
        print(index)
        self.i = int(index)
        self.d = data

    def process_data(self):
        time = np.round(self.d[:,1]/(1e6), 2)
        x = self.d[:,2]/1e3
        y = self.d[:,3]/1e3
        P = self.d[:,4]/1e9
        T = self.d[:,5] - 273.15
        return time, x, y, P, T

    def plot(self, ax, timethreshold):
        time, x, y, P, T = self.process_data()
        points = np.arange(0, np.round(max(time), 1), 0.5)
        plotpoints = []
        labeltimes = []
        # TODO: Optimise this function. Takes up a lot of time. too many calls to abs().
        loc = 0
        for i, point in enumerate(points):
            err = 100
            j = loc
            while err > timethreshold:
                tmp = abs(time[j] - point)
                if tmp < err:
                    err = tmp # starting difference between idealised time vector point and actual time data
                    loc = j # location of minimum difference
                    lab = point # timestamp of this minimum difference point
                    if loc > 0:
                        plotpoints.append((T[loc], P[loc]))
                        # labeltimes.append(self.i) if self.i not in labeltimes else None
                        labeltimes.append(lab)
                j += 1
        plotpoints = np.array(plotpoints)
        C = ax.scatter(plotpoints[:,0], plotpoints[:,1], marker=MARKERS.pop(0), c=labeltimes, cmap='hot')

        return labeltimes, C



class PTtProfManager(object):
    def __init__(self, file, timethreshold):
        self.f = file
        self.profiles = []
        self.assign_profiles()
        self.plot_ensemble(timethreshold)


    def assign_profiles(self):
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

    def plot_ensemble(self, timethreshold):
        fig, ax = plt.subplots()
        plt.xlabel("T [Celsius]")
        plt.ylabel("P [GPa]")
        plt.grid(b=True)
        plt.title("PTt path ")
        labels = {}
        prof = cProfile.Profile()
        prof.enable()
        for profile in self.profiles:
            labels[profile.i], C = profile.plot(ax, timethreshold)
            # labels.append(profile.i)
        ps = pstats.Stats(prof)
        ps.sort_stats('calls', 'cumtime')
        ps.print_stats(5)
        plt.legend(labels)
        cb = plt.colorbar(C)
        cb.set_label("Time [Myr]")



if __name__=="__main__":
    PM = PTtProfManager("E:\ThesisData\PAPER\FI_rerun\FI_PTt.log", timethreshold=0.001)
    plt.show()



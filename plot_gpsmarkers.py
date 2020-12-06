from numpy import zeros, sqrt, nonzero
from math import floor
from matplotlib import pyplot as plt

MODELNAME = "CWs"
FILENAME = "eachdt_gpsmarker_{}.txt".format(MODELNAME)


markers = {}
marker_ids = []
n = 0
with open(FILENAME, 'r') as f:
    remove_lines = 0
    for i, line in enumerate(f.readlines()):
        line = line.split()
        if i == 0:
            # Marker ids
            for j, val in enumerate(line):
                n += 1
                if val in markers.keys():
                    markers[val + 'd']  = zeros((10000, 8))
                marker_ids.append((val))
                markers[val] = zeros((10000, len(line)))
        elif i > 1:
            # get dict key
            # print(i)
            row = int(floor((i-2) / n)) + (i-2) % n
            # print(col)
            item = marker_ids[(i-2)% n]
            for j, val in enumerate(line):
                markers[item][row][j] = float(val)
            remove_lines = row - n + 1
# print(markers)

fig, ax = plt.subplots(2,2)
for marker, data in markers.items():
    data = data[0:remove_lines, 0:8]
    # if 0.0 in data[0:remove_lines]:
    #     print("zero in time data for marker {}".format(marker))
    # else:
    ax[0][0].plot(data[0:remove_lines,0], data[0:remove_lines,1],'o--', label=marker)
    ax[0][0].legend()

    # ax[0][1].plot(data[0:remove_lines,0], sqrt(data[0:remove_lines,4] ** 2 + data[0:remove_lines,5] ** 2))
    # ax[1][0].plot(data[0:remove_lines,0], data[0:remove_lines, 2], '-')
    # plt.pause(0.01)
ax[0][0].set_xlabel("Time [s]")
ax[0][0].set_ylabel("Horizontal position [m]")
plt.show()
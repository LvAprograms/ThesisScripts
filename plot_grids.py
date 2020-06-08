from matplotlib import pyplot as plt


def get_steps_from_init_file(file):
    x_nodes = []
    y_nodes = []
    dx = []
    dy = []
    with open(file, 'r') as f:
        counter = 0
        for line in f.readlines():
            if line.startswith('X'):
                # print(line)
                line = line.split()
                node_start = int(line[1])
                node_end = int(line[2])
                if node_end - node_start == 0:
                    x_nodes.append(node_start)
                    dx.append(float(line[5]))
                elif node_end - node_start > 0:
                    for i in range(node_start, node_end+1):
                        x_nodes.append(i)
                        dx.append(float(line[5]))
            elif line.startswith('Y'):
                # print(line)
                line = line.split()
                node_start = int(line[3])
                node_end = int(line[4])
                if node_end - node_start == 0:
                    y_nodes.append(node_start)
                    dy.append(float(line[5]))
                elif node_end - node_start > 0:
                    for i in range(node_start, node_end+1):
                        y_nodes.append(i)
                        dy.append(float(line[5]))
    return x_nodes, y_nodes, dx,dy



if __name__ == "__main__":
    x = [0]
    y = [0]
    x_nodes, y_nodes, dx, dy = get_steps_from_init_file(file="../../initfiles/CI_init_ls.t3c")
    with open('x_grid.txt', 'w') as f:
        f.write("Node\tX\n1\t0\n")
        for i in range(1, len(dx)):
            x.append(x[i-1] + dx[i-1]/1000)
            f.write("{}\t{}\n".format(x_nodes[i], x[i]))

    for i in range(1, len(dy)):
        y.append(y[i-1] + dy[i-1]/1000)

    fig, axes = plt.subplots(4, 1)
    x_plottables = [x_nodes, x_nodes, y_nodes, y_nodes]
    plottables = [x, dx, y, dy]
    ylabels = ["X coordinate [km]", "X step [km]", "Y coordinate [km]", "Y step [km]"]
    for i in range(len(plottables)):
        axes[i].plot(x_plottables[i], plottables[i],'o-')
        axes[i].grid(b=True)
        axes[i].set_xlabel('Node number')
        axes[i].set_ylabel(ylabels[i])
        axes[i].set_xlim([max(x_plottables[i]) -5, max(x_plottables[i]) +5])
        # axes[i].set_xlim([0, max(x_plottables[i])])

    # axes[2].set_ylim([0, 800])
    # axes[0].set_ylim([700, 900])
    # axes[0].set_xlim([71, 100])

    plt.show()


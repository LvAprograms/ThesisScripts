from matplotlib import pyplot as plt


def get_steps_from_init_file(file):
    def parse_grid_line(line, Y=False):
        split = line.split()
        if Y:
            node_start = int(split[3])
            node_end = int(split[4])
        else:
            node_start = int(split[1])
            node_end = int(split[2])

        delta_node = node_end - node_start
        first = None
        if delta_node == 0:
            first = (node_start,)
        elif node_end - node_start > 0:
            first = range(node_start, node_end + 1)
        return first, float(split[5])

    x_nodes = []
    y_nodes = []
    dx = []
    dy = []
    with open(file, 'r') as f:
        counter = 0
        for line in f.readlines():
            if line.startswith('X'):
                r = parse_grid_line(line)
                x_nodes.extend(r[0])
                [dx.append(r[1]) for _ in r[0]]
            elif line.startswith('Y'):
                r = parse_grid_line(line, Y=True)
                y_nodes.extend(r[0])
                [dy.append(r[1]) for _ in r[0]]

    return x_nodes, y_nodes, dx,dy



if __name__ == "__main__":
    x = [0]
    y = [0]
    modelname = input("Enter model ID")
    x_nodes, y_nodes, dx, dy = get_steps_from_init_file(file="../../initfiles/{}_init_ls.t3c".format(modelname))
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
        # axes[i].plot(x_plottables[i], plottables[i])

        axes[i].grid(b=True)
        axes[i].set_xlabel('Node number')
        axes[i].set_ylabel(ylabels[i])
        # axes[i].set_xlim([max(x_plottables[i]) -5, max(x_plottables[i]) +5])
        axes[i].set_xlim([0, max(x_plottables[i])])

    # axes[2].set_ylim([0, 800])
    # axes[0].set_ylim([2300, 2350])
    # axes[0].set_xlim([71, 100])
    plt.suptitle("Grid plots for model {}".format(modelname))
    plt.show()


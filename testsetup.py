from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

x1 = [0, 0, 1130, 1100, 0]
y1 = [-20, -40, -40, -20, -20]

fig, ax = plt.subplots()
ax.plot(x1,y1,'o-',label='leftUC1')
x2 = [1100, 1130, 1148, 1148]
y2 = [-20, -40, -30.61, -30.6]
ax.plot(x2,y2,'x-',label='leftUC2')
x3 = [0, 0, 1200, 1200, 0]
y3 = [-26, -32, -32, -26, -26]
ax.plot(x3,y3,'^-',label='leftUC3')
path = 'C:\\Users\\Luuk van Agtmaal\\Documents\\Studie\\Masters\\Jaar2\\MSc_thesis\\'
fig.legend()
ax.grid(b=True)
ax.set_xlim([1100, 1200])
plt.savefig("{}leftUC.png".format(path))
xlc1 = [0, 0, 1200, 1200, 0]
ylc1 = [-40, -55, -55, -40, -40]
xlc2 = [0, 0, 1200, 1200, 0]
ylc2 = [-45, -50, -50, -45, -45]
ax.plot(xlc1, ylc1, 'v-',label='leftLC1')
ax.plot(xlc2, ylc2, '*-',label='leftLC2')
fig.legend()
plt.savefig('{}leftcrust.png'.format(path))

path2 = "C:\\Users\\Luuk van Agtmaal\\Desktop\\init_ls.t3c"
labels = []
data = {}
with open(path2) as f:
    for i,line in enumerate(f.readlines()):
        #print("{}: {}".format(i, line))
        if 127 <= i <157:
            line = line.split()
            if line[0].startswith('/'):
                label=line[0].strip('/')
                labels.append(label)
                data[label] = []
            else:
                print(line)
                for j in range(2,10,2):
                    x = line[j]
                    y = line[j+1]
                    if x.startswith('m'):
                        data[label].append((float(x.strip('m'))/1000, float(y.strip('m'))/1000))
                    else:
                        x = int(x) * 3000000
                        data[label].append((float(x)/1000, float(y.strip('m'))/1000))
                temp = data[label][-2]
                data[label][-2] = data[label][-1]
                data[label][-1] = temp
                data[label].append(data[label][0])
print(data['Left_Upper_Crust'])
symbols = ['x','o','^','v','<','>','*','d','p','P','8']
plt.figure()
for k,v in data.items():
    print(k)
    print(list(data.keys()).index(k))
    plt.plot(*zip(*v),marker=symbols[list(data.keys()).index(k)], linestyle='-',label=k)
plt.legend(ncol=2)
plt.xlim([0, 3000])
plt.ylim([0, 250])
plt.gca().invert_yaxis()
plt.pause(0.01)

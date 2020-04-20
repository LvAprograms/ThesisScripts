from matplotlib import pyplot as plt
from math import floor, sqrt
import logging as log


log.basicConfig(filename='logfile.log',filemode='w', level=log.INFO)

"""
GOAL: find the formula for the change in km/node as a function of node number.
first line:      x1(N) = a1 + b1N
transition line: x2(N) = a2 + b2N + cN**2
Third line:      x3(N) = a3 + b3N
That is: a1, a2, b2, c, a3 are unknowns.

we know a couple of things:
1) x1 at node n equals x2 at node n (= Xs)
2) x3 at node m equals x2 at node m (= Xe)
3) the derivative of x2 at node n equals that of x1 at node n
4) the derivative of x2 at node m equals that of x3 at node m

This translates to the following equations:
1) a1 + b1*n = a2 + b2*n + c*n**2
2) a3 + b3*m = a2 + b2*m + c*m**2
3) b2 + 2c*n = b1
4) b2 + 2c*m = b3
Interpretation
c : 0.5 * parabola y-intercept: d2X/dN2 = 2c
b2: y-intercept of tangent of parabola (variable. 0
a2: N = 0 -> x3 = a3. So parabola y-intercept. 
"""

class Parabola(object):
    def __init__(self, n:int, Xs:int, Xe:int, a1:int=0, b1:int=10, b3:int=5):
        self.n = n
        self.a1 = a1 # intercept of first line with y-axis, km
        self.b1 = b1 # slope of first line, km/node
        self.b3 = b3 # slope of line after transition, km/node
        self.a3 = 0  # intercept of lin after transition with y-axis, km
        self.Xs = Xs # y-coordinate where transition starts
        self.Xe = Xe # y-coordinate where transition should end
        self.c = 0   # 0.5 * curvature of transition zone (double derivative of X2 = a2 + b2*N + c * N**2)
        self.b2 = 0  # slope of the derivative of parabola
        self.a2 = 0  # y-intercept of the derivative of th parabola
        self.m = self.n
        self.fig, self.ax = plt.subplots()
        self.maxM = int(floor(self.Xe - self.Xs) / (self.b1 - self.b3)) # set a limit to the width of the transition zone
        log.info("Maximum m value allowed is {}".format(self.maxM))
        self.formula = ""

    def calc(self, N, dxdn=False):
        if dxdn:
            return 2*self.c * N + self.b2
        else:
            return self.a2 + self.b2 * N + self.c * N ** 2

    def discriminant(self):
        return self.b2 ** 2 - 4 * self.a2 * self.c

    def plot(self, where=range(100), dxdn=False):
        x = where
        y = []
        if dxdn:
            for i in where:
                y.append(self.calc(i, dxdn=True))
        else:
            for i in where:
                y.append(self.calc(i))
        self.ax.plot(x,y,'--', label=self.formula)

    def plot_constraints(self):
        x = []
        y = []
        for i in range(0, self.n+1, self.n):
            x.append(i)
            y.append(self.a1 + self.b1 * i)
        self.ax.plot(x,y,'r-',label="x1(N) = {} + {}N".format(self.a1, self.b1))
        self.ax.plot([self.n + self.maxM, self.n + self.maxM], [0, 3000],'m--', label='Maximum allowed m')
        max_a3 = self.Xe - self.b3 * (self.n + self.maxM)
        self.ax.plot([self.n, self.n + self.maxM], [max_a3  + self.b3 * self.n,
                                                    max_a3 + self.b3 * (self.n + self.maxM)],
                                                    label='a3 + b3m for max m')

        plt.pause(0.001)

    def parameters_from_m(self, m:float):
        self.c = (self.b1 - self.b3) / (2 * (self.n - m))
        self.b2 = self.b1 - 2 * self.c * self.n
        self.a2 = self.Xe - self.b2 * m - self.c * m ** 2
        self.formula = "best fit: {:.3f}N$^2$ + {:.3f}N + {:.3f}".format(self.c, self.b2, self.a2)
        log.info(self.formula)

    def fit(self):
        residuals = []
        for m in range(self.n+1, self.n + self.maxM):
            log.info("\nm = {}".format(m))
            self.parameters_from_m(m)
            D = self.discriminant()
            print("Discriminant D = {}".format(D))
            if self.calc(self.n) == self.Xs:
                log.info("X2(n) = Xs? True")
            if self.b1 == round(self.b2 + 2 * self.c * self.n):
                log.info("slope check at node n True")
            if D <= 0:
                log.warning("Discriminant not larger than zero")
                pass
            R = sqrt((self.calc(self.n) - self.Xs) ** 2 + (self.calc(m) - self.Xe) ** 2)
            residuals.append(R)
            log.info("Residual at node n: {}".format(R))
            if abs(self.calc(self.n) - self.Xs) > 50:
                pass
            else:
                # self.plot(where=range(1, 150))
                log.info("X3'(m) = {}, X2'(m) = {}".format(self.b3, 2 * self.c * m + self.b2))
                self.a3 = self.Xe - self.b3 * m
                # self.ax.plot([self.n, self.n + 50], [self.a3 + self.b3 * self.n, self.a3 + self.b3 * (self.n+50)], 'k--')
        best_m = self.n + residuals.index(min(residuals))
        self.parameters_from_m(best_m)
        self.plot(where=range(1,150))
        print("The minimum residual of {} is found for m = {}".format(min(residuals), best_m))

X2 = Parabola(n=90, Xs=900, Xe=1000)
X2.fit()
X2.plot_constraints()

plt.xlim([0, 200])
plt.ylim([0, 1200])
plt.plot([X2.n,X2.n],[0,3000],'--', label='N = n')
plt.plot([0, X2.n + 50], [X2.Xs, X2.Xs],'bd--', label='X = Xs')
plt.plot([0, X2.n + 50], [X2.Xe, X2.Xe],'rd--', label='X = Xe')
plt.xlabel("Node number")
plt.ylabel("X coordinate [km]")
plt.grid(b=True)
plt.legend()
plt.show()

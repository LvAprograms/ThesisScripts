from matplotlib import pyplot as plt

def rupture_width(a, b, Mw):
    return 10 ** ((Mw - a) / b)

mags = []
widthsNF = []
widthsRF = []
for mag in range(81):
    mag /= 10
    mags.append(mag)
    widthsNF.append(rupture_width(3.80, 0.41, mag))
    widthsRF.append(rupture_width(4.37, 1.95, mag))

plt.figure()
plt.plot(mags, widthsNF, 'rx-')
plt.plot(mags, widthsRF, 'b^')
plt.plot([0, 8], [1, 1],'g--')
plt.grid(b=True)
plt.xlabel("Moment magnitude")
plt.ylabel("Rupture width [km]")
plt.show()
                    
    

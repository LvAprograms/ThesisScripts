from matplotlib import pyplot as plt

secinyr = 60*60*24*365.25
secinMyr = secinyr * 1E6
vp0 = -0.1/secinyr    # km/Myr 
timebond = 5*secinMyr # Myr
x = 1 * secinMyr # Myr
time = range(0,10000000, 100000) # yr
v = []                # km/Myr
for t in time:
    if t*secinyr < timebond:
        v.append(vp0)
    elif timebond <= t*secinyr <= timebond + x:
        v.append((-(vp0 * t * secinyr) / x + (vp0 *timebond)/x + vp0))
    else:
        v.append(0)

plt.plot(time,v)
plt.xlabel('time[yr]')
plt.ylabel('v[m/s]')
plt.show()
        

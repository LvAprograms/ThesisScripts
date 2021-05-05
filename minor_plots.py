from matplotlib import pyplot as plt

labels = ["15 km", "20 km", "25 km"]
depths = [330, 150, 90]
x = [15, 20, 25]
t = [25, 9.9, 5.8]
fig, ax = plt.subplots(1, 2)
ax[0].plot(x, depths, 'bo--')
ax[0].set_xlabel("Lower crustal thickness [km]")
ax[0].set_ylabel("Detachment depth [km below surface]")
ax[0].grid(b=True)
ax[0].legend()
ax[0].invert_yaxis()
ax[1].plot(x, t, 'ko--')
ax[1].set_xlabel("Lower crustal thickness [km]")
ax[1].set_ylabel("Moment of detachment [Myr]")
ax[1].grid(b=True)
ax[1].legend()
plt.show()

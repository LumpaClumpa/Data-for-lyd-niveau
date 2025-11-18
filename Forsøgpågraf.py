import matplotlib.pyplot as plt
from matplotlib import animation
import requests
from matplotlib import style

style.use('fivethirtyeight')

fig, ax1 = plt.subplots()
TARGET_LOKALE = 2221  # adjust to the same room Arduino sends
SERVER = "http://192.168.1.100:5000"  # set to your Flask server IP

def animate(i):
    try:
        resp = requests.get(f"{SERVER}/maalinger/{TARGET_LOKALE}", timeout=2)
        resp.raise_for_status()
        data = resp.json()  # expect list of [ts, db]
        if not data:
            return
        xs = [d[0] / 1000.0 for d in data]  # seconds
        ys = [d[1] for d in data]
        ax1.clear()
        ax1.plot(xs, ys)
        ax1.set_xlabel('time (s)')
        ax1.set_ylabel('dB')
        ax1.set_title(f'Live plot lokale {TARGET_LOKALE}')
    except Exception as e:
        print("Fetch/plot error:", e)

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
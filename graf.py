import matplotlib.pyplot as plt
from matplotlib import animation  # keep the module accessible
from matplotlib import style

style.use('fivethirtyeight')

fig, ax1 = plt.subplots()

def animate(i):
    with open('file.txt', 'r') as f:
        lines = f.read().splitlines()

    xs, ys = [], []
    for line in lines:
        if line.strip():  # skip empty lines
            x_str, y_str = line.split(',')
            xs.append(float(x_str))
            ys.append(float(y_str))

    ax1.clear()
    ax1.plot(xs, ys)
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    ax1.set_title('Live plot from file.txt')

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()

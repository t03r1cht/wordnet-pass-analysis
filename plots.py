import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np


def bar_graph(opts):
    print("===", matplotlib.get_backend())
    t = np.arange(0.0, 2.0, 0.01)
    s = 1 + np.sin(2*np.pi*t)
    plt.plot(t, s)

    plt.title('About as simple as it gets, folks')
    plt.show()

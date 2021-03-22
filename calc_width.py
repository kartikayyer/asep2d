import numpy as np
import asep2d

dists = []
nreps = 10

for L in range(50, 501, 50):
    print('L =', L)
    n = L//2
    x, y = np.indices((n, L))
    intdist = (np.abs(L / n * x - y) / np.sqrt(1 + (L/n)**2)).astype('i4')

    dcount = np.zeros(intdist.max() + 1)
    davg = np.zeros(intdist.max() + 1)
    avg_davg = np.zeros(intdist.max() + 1) 

    for i in range(nreps):
        a = asep2d.ASEP2D(n, L)
        a.run(20000, np.ones(n), np.zeros(n))
        states = a.run(20000, np.ones(n), np.zeros(n), accumulate=True)

        mgrid = np.zeros((a.nrows, a.ncols))
        for s in states:
            grid = a.togrid(s, restrict=True)
            grid[grid<0] = 0
            mgrid += grid
        mgrid /= len(states)

        dcount[:] = 0
        davg[:] = 0
        np.add.at(dcount, intdist, 1)
        np.add.at(davg, intdist, mgrid)
        davg /= dcount
        avg_davg += davg
    avg_davg /= nreps

    dists.append(avg_davg[:20])

np.save('widths.npy', np.array(dists))

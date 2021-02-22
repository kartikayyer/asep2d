import numpy as np

class ASEP2D():
    def __init__(self, nrows, ncols):
        if not ncols > nrows:
            raise ValueError('Number of columns must be larger than number of rows')
        
        self.nrows = nrows
        self.ncols = ncols

        self.randomize()

    def randomize(self):
        '''Generate random state vector

        Numbers from 0 to (nrows-1) indicate type 1 particle
        Numbers from nrows to (2*nrows-1) indicate type 2 particle
        '''
        self.state = np.empty(self.ncols, dtype='i4')

        col1 = sorted(np.random.choice(range(self.ncols), self.nrows, replace=False))
        self.state[col1] = np.arange(self.nrows, dtype='i4')

        col2 = np.delete(range(self.ncols), col1)
        self.state[col2] = np.random.randint(0, self.nrows, self.ncols - self.nrows) + self.nrows
        self._init_state = self.state.copy()

    def reset(self):
        self.state = self._init_state.copy()

    def togrid(self, state=None):
        grid = np.zeros((self.nrows, self.ncols), dtype='i1')
        if state is None:
            state = self.state

        sel = state < self.nrows
        grid[state[sel], sel] = 1
        grid[state[~sel]-self.nrows, ~sel] = -1
        return grid

    def step_right(self, row):
        return self._step(row, 1)

    def step_left(self, row):
        return self._step(row, -1)

    def _step(self, row, sign):
        col = np.where(self.state == row)[0][0]
        ncol = self._cadd(col, sign)
        nrow = self.state[ncol]
        if nrow < self.nrows:
            return 0

        if nrow - self.nrows != row:
            self.state[[col, ncol]] = self.state[[ncol, col]]
            return 1

        back_row = self._radd(row, -sign)
        back_col = np.where(self.state == back_row)[0][0]
        if (col - back_col)*sign < 0:
            # Wrapping
            roll_num = (self.ncols-1)*(sign > 0) - back_col
        else:
            roll_num = -back_col - 1
        self.state = np.roll(self.state, roll_num)
        if sign > 0:
            #print(ncol, roll_num)
            self.state[1:ncol+1+roll_num] = self.state[:ncol+roll_num]
            self.state[0] = back_row + self.nrows
        else:
            self.state[ncol+roll_num:-1] = self.state[ncol+1+roll_num:]
            self.state[-1] = back_row + self.nrows
        self.state = np.roll(self.state, -roll_num)
        #else:
        #    dest = sorted([self._cadd(back_col, 2*(sign>0)), ncol+2*(sign>0)])
        #    src = sorted([self._cadd(back_col, (sign>0)), col+(sign>0)])
        #    self.state[dest[0]:dest[1]-1] = self.state[src[0]:src[1]]
        #    self.state[self._cadd(back_col, sign)] = back_row + self.nrows
        return 2

    def _cadd(self, val1, val2):
        return (val1 + val2 + self.ncols) % self.ncols

    def _radd(self, val1, val2):
        return (val1 + val2 + self.nrows) % self.nrows

def main():
    grids = np.load('asep_grids_0.6.npy')
    #grids = np.load('tasep_grids.npy')
    #grids = np.load('asep_grids_0.8.npy')
    
    import sys
    import pylab as P
    from matplotlib import animation

    W = animation.writers['ffmpeg']
    writer = W(fps=30, bitrate=1800)

    fig = P.figure(figsize=(7.5, 2))
    ax = fig.add_subplot(111)
    ax.imshow(grids[0], cmap='coolwarm')
    ax.set_axis_off()
    P.tight_layout()

    def update(i):
        sys.stderr.write('\r%d'%i)
        im = ax.imshow(grids[i], cmap='coolwarm')
        return im, 
        
    #anim = animation.FuncAnimation(P.gcf(), update, frames=np.arange(0,10000,100), interval=30, blit=True)
    #anim.save('asep2d_1.mp4', writer=writer)

    #anim = animation.FuncAnimation(P.gcf(), update, frames=np.arange(10000,20000,100), interval=30, blit=True)
    #anim.save('asep2d_2.mp4', writer=writer)

    anim = animation.FuncAnimation(P.gcf(), update, frames=np.arange(20000,30000,100), interval=30, blit=True)
    anim.save('asep2d_3.mp4', writer=writer)

if __name__ == '__main__':
    main()

import sys
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

    def togrid(self, state=None, restrict=False):
        grid = np.zeros((self.nrows, self.ncols), dtype='i1')
        if state is None:
            state = self.state
        if restrict:
            c0 = np.where(state == 0)[0][0]
            state = np.roll(state.copy(), -c0)

        sel = state < self.nrows
        grid[state[sel], sel] = 1
        grid[state[~sel]-self.nrows, ~sel] = -1

        return grid

    def run(self, num_steps, p_vals, q_vals, accumulate=False):
        assert len(p_vals) == self.nrows
        assert len(q_vals) == self.nrows

        total_rate = p_vals + q_vals
        prob_right = p_vals / total_rate
        prob_row = total_rate / total_rate.sum()

        if accumulate:
            states = []

        for i in range(num_steps):
            row = np.random.choice(np.arange(self.nrows), 1, p=prob_row)
            sign = int(np.random.rand() < prob_right[row]) * 2 - 1
            self._step(row, sign)
            if accumulate:
                states.append(self.state.copy())
            sys.stderr.write('\r%d/%d' % (i+1, num_steps))
        sys.stderr.write('\n')

        if accumulate:
            return states

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
            self.state[1:ncol+1+roll_num] = self.state[:ncol+roll_num]
            self.state[0] = back_row + self.nrows
        else:
            #print(ncol, roll_num)
            self.state[ncol+roll_num:-2] = self.state[ncol+roll_num+1:-1]
            self.state[-2] = back_row + self.nrows
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
    import sys
    import os.path as op
    import argparse
    import imageio

    parser = argparse.ArgumentParser(description='Save evolution of ASEP2D model')
    parser.add_argument('states_file', help='Path to states file (.npy format)')
    parser.add_argument('-m', '--max_step',
                        help='Highest step number to plot. Default: all',
                        type=int, default=-1)
    parser.add_argument('-s', '--step_skip',
                        help='Save every step_skip steps. Default: 100',
                        type=int, default=100)
    parser.add_argument('--oversampling',
                        help='Image pixels per data pixel. Default: 16',
                        type=int, default=16)
    parser.add_argument('-r', '--restrict',
                        help='Show restricted grids', action='store_true')
    args = parser.parse_args()

    states = np.load(args.states_file)
    a = ASEP2D((states[0].max() + 1) // 2, states.shape[1])

    max_frame = len(states) if args.max_step < 0 else args.max_step
    sel_states = states[0:max_frame:args.step_skip]

    grids = np.array([a.togrid(s, restrict=args.restrict)+1 for s in sel_states]).astype('u1')
    grids[grids==2] = 255
    grids[grids==1] = 128
    grids = np.repeat(grids, args.oversampling, axis=1)
    grids = np.repeat(grids, args.oversampling, axis=2)

    fname = '%s.mp4' % op.splitext(args.states_file)[0]
    print('Saving to', fname)
    imageio.mimwrite(fname, grids, fps=30, quality=10)

if __name__ == '__main__':
    main()

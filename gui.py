import sys

from PyQt5 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg
import numpy as np

import asep2d

class ASEPGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.states = []
        self.grids = []
        self._init_ui()

    def _init_ui(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle('2D ASEP GUI')
        self.resize(1000, 600)
        layout = QtWidgets.QVBoxLayout()
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        central.setLayout(layout)

        self.imview = pg.ImageView()
        self.imview.ui.roiBtn.hide()
        self.imview.ui.menuBtn.hide()
        self.imview.ui.histogram.hide()
        layout.addWidget(self.imview)

        line = QtWidgets.QHBoxLayout()
        layout.addLayout(line)
        label = QtWidgets.QLabel('n =')
        line.addWidget(label)
        self.n_val = QtWidgets.QLineEdit('20')
        line.addWidget(self.n_val)
        label = QtWidgets.QLabel('L =')
        line.addWidget(label)
        self.l_val = QtWidgets.QLineEdit('100')
        line.addWidget(self.l_val)
        button = QtWidgets.QPushButton('Reset')
        button.clicked.connect(self.reset)
        line.addWidget(button)
        line.addStretch(1)

        line = QtWidgets.QHBoxLayout()
        layout.addLayout(line)
        label = QtWidgets.QLabel('p =')
        line.addWidget(label)
        self.p_val = QtWidgets.QLineEdit('1.')
        line.addWidget(self.p_val)
        label = QtWidgets.QLabel('q =')
        line.addWidget(label)
        self.q_val = QtWidgets.QLineEdit('0.')
        line.addWidget(self.q_val)
        label = QtWidgets.QLabel('Num. steps:')
        line.addWidget(label)
        self.num_steps = QtWidgets.QLineEdit('10000')
        line.addWidget(self.num_steps)
        button = QtWidgets.QPushButton('Run')
        button.clicked.connect(self.run)
        line.addWidget(button)
        line.addStretch(1)
        self.curr_steps = QtWidgets.QLabel('')
        line.addWidget(self.curr_steps)

        line = QtWidgets.QHBoxLayout()
        layout.addLayout(line)
        line.addStretch(1)
        button = QtWidgets.QPushButton('Save')
        button.clicked.connect(self.save)
        line.addWidget(button)
        button = QtWidgets.QPushButton('Quit')
        button.clicked.connect(self.close)
        line.addWidget(button)

        self.reset()
        self.show()

    def reset(self):
        self.asep = asep2d.ASEP2D(nrows=int(self.n_val.text()), ncols=int(self.l_val.text()))
        del self.states
        del self.grids
        self.states = [self.asep.state.copy()]
        self.curr_steps.setText('1 step')
        self.update_view()

    def run(self):
        p_val = float(self.p_val.text())
        q_val = float(self.q_val.text())
        prob_right = p_val / (p_val + q_val)
        curr_steps = len(self.states)
        num_steps = int(self.num_steps.text())

        for i in range(num_steps):
            row = np.random.randint(self.asep.nrows)
            sign = int(np.random.rand() < prob_right) * 2 - 1
            self.asep._step(row, sign)
            self.states.append(self.asep.state.copy())
            sys.stderr.write('\r%d/%d' % (i+curr_steps+1, curr_steps + num_steps))
        sys.stderr.write('\n')

        self.curr_steps.setText(str(len(self.states)) + ' steps')
        self.update_view()

    def update_view(self):
        self.grids = np.array([self.asep.togrid(state) for state in self.states])
        self.imview.setImage(self.grids.transpose(0, 2, 1), levels=(-1,1))

    def save(self):
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save states', '', 'Numpy data (*.npy)')
        if fname:
            print('Saving to', fname)
            np.save(fname, np.array(self.states))

    def load(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Load states', '', 'Numpy data (*.npy)')
        if not fname:
            return

        print('Loading from', fname)
        self.states = list(np.load(fname))
        ncols = len(self.states[0])
        nrows = (self.states[0].meax() + 1) // 2
        self.asep = asep2d.ASEP2D(nrows, ncols)
        self.asep.state = self.states[-1].copy()
        self.n_val.setText(str(nrows))
        self.l_val.setText(str(ncols))
        self.curr_steps.setText(str(len(self.states)) + ' steps')
        self.update_view()

def main():
    app = QtWidgets.QApplication([])
    gui = ASEPGUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

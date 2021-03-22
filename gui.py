#!/usr/bin/env python

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
        self.restrict = QtWidgets.QCheckBox('Restrict')
        self.restrict.stateChanged.connect(self.update_view)
        line.addWidget(self.restrict)

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
        label = QtWidgets.QLabel('Statistics:')
        line.addWidget(label)
        button = QtWidgets.QPushButton('Type-1 average')
        button.clicked.connect(lambda _: self.calc_mean(1))
        line.addWidget(button)
        button = QtWidgets.QPushButton('Type-2 average')
        button.clicked.connect(lambda _: self.calc_mean(2))
        line.addWidget(button)
        label = QtWidgets.QLabel('Transient:')
        line.addWidget(label)
        self.transient_steps = QtWidgets.QLineEdit('5000')
        line.addWidget(self.transient_steps)
        line.addStretch(1)

        line = QtWidgets.QHBoxLayout()
        layout.addLayout(line)
        line.addStretch(1)
        button = QtWidgets.QPushButton('Refresh')
        button.clicked.connect(self.update_view)
        line.addWidget(button)
        button = QtWidgets.QPushButton('Load')
        button.clicked.connect(self.load)
        line.addWidget(button)
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
        try:
            pvals = np.ones(self.asep.nrows)*float(self.p_val.text())
        except ValueError:
            pvals = np.random.rand(self.asep.nrows)

        try:
            qvals = np.ones(self.asep.nrows)*float(self.q_val.text())
        except ValueError:
            qvals = np.random.rand(self.asep.nrows)

        num_steps = int(self.num_steps.text())
        self.states += self.asep.run(num_steps, pvals, qvals, accumulate=True)

        self.curr_steps.setText(str(len(self.states)) + ' steps')
        self.update_view()

    def update_view(self):
        do_restrict = self.restrict.isChecked()
        self.grids = np.array([self.asep.togrid(state, restrict=do_restrict) for state in self.states])
        self.imview.setImage(self.grids.transpose(0, 2, 1), levels=(-1,1))
        self.imview.ui.histogram.hide()

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
        nrows = (self.states[0].max() + 1) // 2
        self.asep = asep2d.ASEP2D(nrows, ncols)
        self.asep.state = self.states[-1].copy()
        self.n_val.setText(str(nrows))
        self.l_val.setText(str(ncols))
        self.curr_steps.setText(str(len(self.states)) + ' steps')
        self.update_view()

    def calc_mean(self, ptype=1):
        tsteps = int(self.transient_steps.text())
        if len(self.grids) <= tsteps:
            print('Less steps than in the transient')
            return
        mgrids = self.grids[tsteps:].copy()
        if ptype == 1:
            mgrids[mgrids < 0] = 0
            self.imview.setImage(mgrids.mean(0).T)
            self.imview.ui.histogram.show()
        elif ptype == 2:
            mgrids[mgrids > 0] = 0
            self.imview.setImage(-mgrids.mean(0).T)
            self.imview.ui.histogram.show()
        else:
            print('Unknown particle type', ptype)

def main():
    app = QtWidgets.QApplication([])
    gui = ASEPGUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

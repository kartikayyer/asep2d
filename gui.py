#!/usr/bin/env python

import sys

from PyQt5 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import h5py

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
        self.resize(1000, 800)
        layout = QtWidgets.QVBoxLayout()
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        central.setLayout(layout)

        self.imview = pg.ImageView()
        self.imview.ui.roiBtn.hide()
        self.imview.ui.menuBtn.hide()
        self.imview.ui.histogram.hide()
        layout.addWidget(self.imview, stretch=2)

        line = QtWidgets.QHBoxLayout()
        layout.addLayout(line, stretch=1)
        self.current_barwidget = pg.PlotWidget()
        line.addWidget(self.current_barwidget)
        self.current_timewidget = pg.PlotWidget()
        line.addWidget(self.current_timewidget)

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
        self.accumulate = QtWidgets.QCheckBox('Accumulate')
        self.accumulate.setChecked(False)
        line.addWidget(self.accumulate)
        self.acc_curr = QtWidgets.QCheckBox('Acc. currents')
        self.acc_curr.setChecked(True)
        line.addWidget(self.acc_curr)
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
        self.pvals = None
        self.qvals = None
        self.grids = []
        self.states = [self.asep.state.copy()]
        self.curr_steps.setText('1 step')
        self.update_view()

    def run(self):
        try:
            self.pvals = np.ones(self.asep.nrows)*float(self.p_val.text())
        except ValueError:
            if self.pvals is None:
                self.pvals = np.random.rand(self.asep.nrows)

        try:
            self.qvals = np.ones(self.asep.nrows)*float(self.q_val.text())
        except ValueError:
            if self.qvals is None:
                self.qvals = np.random.rand(self.asep.nrows)

        num_steps = int(self.num_steps.text())
        if self.accumulate.isChecked():
            self.states += self.asep.run(num_steps, self.pvals, self.qvals,
                                         accumulate_states=True,
                                         accumulate_curr=self.acc_curr.isChecked())
        else:
            self.asep.run(num_steps, self.pvals, self.qvals,
                          accumulate_states=False,
                          accumulate_curr=self.acc_curr.isChecked())
            self.states = [self.asep.state.copy()]
        self.curr_steps.setText(str(self.asep.total_num_steps) + ' steps')
        self.update_view()
        self.update_current_plots()

    def update_view(self):
        do_restrict = self.restrict.isChecked()
        self.grids = np.array([self.asep.togrid(state, restrict=do_restrict) for state in self.states])
        self.imview.setImage(self.grids.transpose(0, 2, 1), levels=(-1,1))
        self.imview.ui.histogram.hide()

    def update_current_plots(self):
        self.current_barwidget.getPlotItem().clear()
        barplot = pg.BarGraphItem(x=np.arange(self.asep.nrows)-0.2,
                                  height=self.asep.curr1,
                                  width=0.4,
                                  brush=(0,9))
        self.current_barwidget.addItem(barplot)
        barplot = pg.BarGraphItem(x=np.arange(self.asep.nrows)+0.2,
                                  height=self.asep.curr2,
                                  width=0.4,
                                  brush=(5,9))
        self.current_barwidget.addItem(barplot)

        self.current_timewidget.getPlotItem().clear()
        xvals = np.arange(1, len(self.asep.mean_curr1)+1)
        self.current_timewidget.plot(xvals, self.asep.mean_curr1, pen=(0,9))
        self.current_timewidget.plot(xvals, self.asep.mean_curr2, pen=(5,9))
        self.current_timewidget.plot(xvals, np.array(self.asep.mean_curr1)-np.array(self.asep.mean_curr2), pen=(3,9))

        n = self.asep.nrows
        L = self.asep.ncols
        p = self.pvals[0]
        q = self.qvals[0]
        theo_current = (p-q) * (L - n) / (L - 1) / n / (p + q)
        line = pg.InfiniteLine(theo_current, angle=0, pen='w')
        self.current_timewidget.addItem(line)

    def save(self):
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save states', '', 'HDF5 file (*.h5)')
        if not fname:
            return

        print('Saving to', fname)
        with h5py.File(fname, 'w') as f:
            f['params/n'] = self.asep.nrows
            f['params/L'] = self.asep.ncols
            f['params/p_values'] = self.pvals
            f['params/q_values'] = self.qvals
            f['data/initial_state'] = self.asep._init_state
            f['data/state'] = self.asep.state
            f['data/current_1'] = self.asep.curr1
            f['data/current_2'] = self.asep.curr2
            f['data/mean_curr1'] = self.asep.mean_curr1
            f['data/mean_curr2'] = self.asep.mean_curr2
            f['data/num_steps'] = self.asep.total_num_steps
            if len(self.states) > 1:
                f['data/all_states'] = self.states

    def load(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Load states', '', 'HDF5 file (*.h5)')
        if not fname:
            return

        print('Loading from', fname)
        with h5py.File(fname, 'r') as f:
            self.n_val.setText(str(f['params/n'][...]))
            self.l_val.setText(str(f['params/L'][...]))
            self.asep = asep2d.ASEP2D(nrows=int(self.n_val.text()), ncols=int(self.l_val.text()))

            self.pvals = f['params/p_values'][:]
            self.qvals = f['params/q_values'][:]
            self.p_val.setText(str(self.pvals[0]))
            self.q_val.setText(str(self.qvals[0]))

            self.asep.state = f['data/state'][:]
            self.asep._init_state = f['data/initial_state'][:]
            self.asep.total_num_steps = f['data/num_steps'][...]
            self.asep.curr1 = f['data/current_1'][:]
            self.asep.curr2 = f['data/current_2'][:]
            self.asep.mean_curr1 = list(f['data/mean_curr1'][:])
            self.asep.mean_curr2 = list(f['data/mean_curr2'][:])

            if 'data/all_states' in f:
                self.states = list(f['data/all_states'][:])
            else:
                self.states = [self.asep.state.copy()]
            self.grids = np.array([self.asep.togrid(state, restrict=self.restrict.isChecked()) for state in self.states])
            self.curr_steps.setText(str(self.asep.total_num_steps) + ' steps')

        self.update_view()
        self.update_current_plots()

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

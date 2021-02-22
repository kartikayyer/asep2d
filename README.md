# 2D ASEP GUI

GUI to explore dynamics of 2D ASEP model

### Prerequisites
 * PyQt5
 * pyqtgraph
 * numpy
 
### Usage
Run GUI with the command
```
$ python gui.py
```

An initial state is randomly generated. Class-1 particles are white while class-2 ones are black.

The system can be evolved with given `p` and `q` values for the given number of steps. This then updates the viewer with a scrollable bar which can be used to scroll through the evolution.

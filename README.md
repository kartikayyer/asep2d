# 2D ASEP GUI

GUI to explore dynamics of 2D ASEP model

### Prerequisites
 * numpy [For model]
 * PyQt5 [For GUI]
 * pyqtgraph [For GUI]
 * imageio [For saving video]
 * imageio-ffmpeg [For saving video]
 
### Usage
Run GUI with the command
```
$ python gui.py
```

An initial state is randomly generated. Class-1 particles are white while class-2 ones are black.

The system can be evolved with given `p` and `q` values for the given number of steps. This then updates the viewer with a scrollable bar which can be used to scroll through the evolution.

The time-evolution can be saved using the 'Save' button. To convert the time evolution to a movie, use the `asep2d.py` script from the command line.
```
$ python asep2d.py <saved_states.npy>
```
You can use the `-h` flag to look at customizing the video.

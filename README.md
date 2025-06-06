# PathFinder
A program to create, edit and solve graphs using the A* (A-star) algorithm and different heuristic functions.

The created graphs can be saved to .graph files and opened later.

## Python library requierements
- Tkinter: Standard GUI (Graphical User Interface) library for Python
- canvasvg: Helper library to export TKinter canvas to .svg files (Source: [canvasvg - PyPI](https://pypi.org/project/canvasvg/)). _This library is embeded for compatibility and don't requiere installation_.

## GUI mode
This mode is opened simple opening the .bat or .sh file (with python3 and the requiered libraries installed)

In this modes the controls are:
- **Left Click:** Creates or moves nodes
- **Left Click over Nodes:** Select/Deselect node
  - With a node selected, click another to connect them
- **Right Click over Nodes:** Delete node
- **Center Click:** Cicle between types Normal, Start and End

## Console mode
This is an optimized mode for opening and solving .graph files. This mode is accesed by using a terminal/console to open the .bat or .sh file and adding the `--ng` or `--no-gui`.
```
usage: PathFinder [-h] [--hf {e,m,c,1m5,3m}] [-s] [--ng] [filename]

Developed by NodeFinders (Matías Balbuena, Oscar Wohlfarhrt)

positional arguments:
  filename

options:
  -h, --help            show this help message and exit
  --hf, --h-func {e,m,c,1m5,3m}
                        selects an heuristic function to be used. Euclidian, Manhattan, Chebyshev, Minkowski 1.5, Minkowski 3 respectively
  -s, --solve           automatically solves the graph with the heuristic function specified on --h-func argument. This option has no effect when used with --no-gui.
  --ng, --no-gui        only outputs on the console and shows no window. Always resolves the graph and requieres a filename.
```

- [Versión en Español](#pathfinder-español)
- [English version](#pathfinder-english)

# PathFinder (Español)

Un programa que permite crear, editar y resolver grafos usando el algorítmo A* (A-estrella) y diferentes funciones de heurística

Los gráficos creados pueden ser guardados a un archivo .graph para poder ser abiertos en otro momento.

_Se requiere tener Python 3 instalado para ejecutar el programa._

## Librerías de Python requeridas
- Tkinter: Librería de Intefaz Gráfica de Usaurio estandar de Python
- canvasvg: Librería auxiliar para exportar los canvas de Tkinter a archivos .svg (Fuente: [canvasvg - PyPI](https://pypi.org/project/canvasvg/)). _Esta librería esta embebida junto con los archivos fuente por compatibilidad y no requiere instalación_.

## Instalación
Extraer todos los archivos fuentes en una misma carpeta.

Si los archivos .bat o .sh no funcionan correctamente, se puede ejecutar el programa con el comando: `python3 "PathFinder.py"`

## Modo Gráfico
Este modo se abre simplemente ejecutando el archivo .bat o .sh (teniendo python3 y las librerías requeridas instaladas)

En este modo los controles son:
- **Click Izquierdo:** Crea o mueve nodos seleccionados
- **Click Izquierdo sobre Nodos:** Selecciona/Deselecciona al nodo
  - Con un nodo seleccionado, hacer click sobre otro nodo para conectarlos entre sí
- **Click Derecho sobre Nodos:** Elimina el nodo
- **Click Central sobre Nodos:** Cambia el tipo de nodo entre Normal, Inicio y Final

## Modo de consola
Este es un modo optimizado para abrir y resolver archivos .graph. Se accede a este modo usando una terminal/consola para abrir el archivo .bat o .sh y añadiendo el argumento `--ng` o `--no-gui`.

Con el argumento `--help` se muestra el siguiente mensaje:
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

# PathFinder (English)

A program to create, edit and solve graphs using the A* (A-star) algorithm and different heuristic functions.

The created graphs can be saved to .graph files and opened later.

_Python 3 is requiered to execute the program._

## Python library requierements
- Tkinter: Standard GUI (Graphical User Interface) library for Python
- canvasvg: Helper library to export TKinter canvas to .svg files (Source: [canvasvg - PyPI](https://pypi.org/project/canvasvg/)). _This library is embeded with the source code for compatibility and don't requiere installation_.

## Instalation
Extract all source files inside a folder.

If the .bat or .sh files doesn't work correctly, the program can be executed with the command: `python3 "PathFinder.py"`

## GUI mode
This mode is opened simple opening the .bat or .sh file (with python3 and the requiered libraries installed)

In this modes the controls are:
- **Left Click:** Creates or moves selected nodes
- **Left Click over Nodes:** Select/Deselect node
  - With a node selected, click another to connect them
- **Right Click over Nodes:** Delete node
- **Center Click:** Cicle between types Normal, Start and End

## Console mode
This is an optimized mode for opening and solving .graph files. This mode is accesed by using a terminal/console to open the .bat or .sh file and adding the `--ng` or `--no-gui`.

With the `--help` argument this message is showed:
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
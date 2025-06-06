## Autores: Matías Balbuena y Oscar Wohlfarhrt

from __future__ import annotations
import math
from typing import Callable

## Funcion de distancia Euclidiana
def distanceBetween(x1,y1,x2,y2):
    return math.hypot(x2 - x1, y2 - y1)

## Funcion de distancia de Manhattan
def manhattanDistanceBetween(x1,y1,x2,y2):
    return abs(x1 - x2) + abs(y1 - y2)

## Funcion de distancia de Chebyshev
def chebyshevDistanceBetween(x1,y1,x2,y2):
    return max(abs(x1 - x2), abs(y1 - y2))

## Funcion de distancia de Minkowski
## Caso general. p = 1: distancia de Manhattan; p = 2: distancia Euclidiana; p = infinito: distancia de Chebyshev
def minkowskiDistanceBetween(x1,y1,x2,y2,p:float = 1.5):
    p = p if p > 0 else 0
    base = abs(x1 - x2)**p + abs(y1 - y2)**p
    if p < 1:
        return base
    else:
        return base**(1/p)

## Interfaz para la abstración de la implementación de los nodos
class INode:
    def __init__(self):
        self.coords:tuple[int, int] = (0,0) # coordenadas del nodo
        self.edges:list[int] = [] # lista de id's de nodos vecinos

    ## Función para determinar el costo entre dos nodos
    ## La implementación por defecto es con la distacia Euclidiana
    def distanceTo(self, other: INode):
        return distanceBetween(*self.coords, *other.coords)
    
    ## Función para obtener los vecinos de un nodo
    def getNeighbors(self) -> list[int]:
        return self.edges

## Estructura de datos para registrar el costo y heurística de los nodos
class NodeData:
    def __init__(self, g: float=0, h: float=0, parent: int=None):
        self.g = g # costo
        self.h = h # heurística
        self.f = g + h # función de evaluación (costo + heurística)
        self.parent = parent

    def __gt__(self, other: NodeData):
        return self.f > other.f
    def __lt__(self, other: NodeData):
        return self.f < other.f
    def __eq__(self, other: NodeData):
        return self.f == other.f

## Clase que implementa el algorímo A*
class AStar:
    # Funciones de heurística predeterminadas
    hFunctions={
        "Euclidian": distanceBetween,
        "Manhattan": manhattanDistanceBetween,
        "Chebyshev": chebyshevDistanceBetween,
        "Minkowski 1.5": lambda x1,y1,x2,y2: minkowskiDistanceBetween(x1,y1,x2,y2,1.5),
        "Minkowski 3": lambda x1,y1,x2,y2: minkowskiDistanceBetween(x1,y1,x2,y2,3),
    }

    ## Constructor de la clase
    def __init__(self, nodes: dict[int,INode], hFunction: Callable[[int,int,int,int],float] = None):
        self.nodes: dict[int,INode] = nodes
        self.hFunc: Callable[[int,int,int,int],float] = hFunction if hFunction != None else distanceBetween
        self.nodesData: dict[int,NodeData] = {}

    ## función auxiliar para reconstruir el camino hasta el nodo inicial
    def buildPath(self, nodeId) -> list[int]:
        path = []
        # Se recorren los nodos hasta que no exista un parent
        while nodeId != None and nodeId in self.nodesData:
            path.append(nodeId)
            nodeId = self.nodesData[nodeId].parent
        # Dado que se reconstruye el camino inverso, se debe invertir la lista
        path.reverse()
        return path

    ## Función principal que resuleve el grafo aplicando el algorímo de A*
    def solve(self, startId: int, endId: int, updateCallback: Callable[[dict[int,NodeData], int]] = None) -> list[int]:
        # variables de acceso rapido
        nodes: dict[int,INode] = self.nodes
        nodesData: dict[int,NodeData] = self.nodesData
        # se calcula el costo y heurística para el nodo inicial
        nodesData[startId] = NodeData(0,self.hFunc(*nodes[startId].coords, *nodes[endId].coords))
        self.reopened = 0

        open: list[int] = [startId] # Se crea la lista de nodos abiertos con el nodo inicial
        closed: set[int] = set() # Se crea la lista de nodos cerrados

        while open: # Mientras existan nodos en la lista de abiertos
            current = open.pop(0) # se extrae el nodo con menor valor en f

            if current == endId: # Se verifíca que se haya encontrado el nodo final
                return self.buildPath(current) # Se reconstruye el camino al nodo final
            
            closed.add(current) # Se cierra el nodo actual

            # Se obtienen y recorren los nodos vecinos del nodo actual
            for id in nodes[current].getNeighbors():
                # Se calcula el costo y heurística del nodo vecino
                nodeData = NodeData(nodesData[current].g + nodes[current].distanceTo(nodes[id]),
                                    self.hFunc(*nodes[id].coords, *nodes[endId].coords),
                                    current)
                
                # Se verifica que el nodo exista en la lista de abiertos
                # y que tenga un valor de evaluación menor
                if id in open and nodesData[id].f > nodeData.f:
                    nodesData[id] = nodeData # Se actualizan los datos

                # Se verifica que el nodo esté cerrado 
                # y que tenga un valor de evaluación menor
                elif id in closed and nodesData[id].f > nodeData.f:
                    nodesData[id] = nodeData
                    # Se elimina el nodo de la lista de cerrados y se lo añade a la lista de abiertos
                    print(f"overestimation in {id}")
                    self.reopened += 1
                    closed.remove(id)
                    open.append(id)

                # Si el nodo no está cerrado ni abierto se añade a la lista de abiertos
                elif (id not in open) and (id not in closed):
                    nodesData[id] = nodeData
                    open.append(id)
                
                # Se invola la función de actualización si esta existiera
                if updateCallback != None:
                    updateCallback(nodesData, current, id, self.buildPath(current))

            # Se ordenan los nodos de la lista de abieros basado en su función de evaluación
            open.sort(key = lambda id: nodesData[id].f)

        # Si se recorren todos los nodos sin encontrar el nodo final, se debuelve un camino nulo
        return None
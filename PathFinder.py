## Autores: Matías Balbuena y Oscar Wohlfarhrt

from __future__ import annotations

# Librerias estandar de python
import tkinter as tk
from tkinter import ttk
import re
import json
import math
import time
import random
from random import Random
import tkinter.simpledialog as sdialg
import tkinter.filedialog as fdialg
import tkinter.messagebox as msgbox
import sys
import argparse
from xml.dom import minidom

# Libreria para exportar el canvas a svg (https://pypi.org/project/canvasvg/)
import canvasvg

# Libreria creada por el grupo
from aStar import *

# Funciones auxiliares
def getDirection(x1,y1,x2,y2):
    dist = distanceBetween(x1,y1,x2,y2)
    return ((x2-x1)/dist, (y2-y1)/dist)
def getDirectionDistance(x1,y1,x2,y2):
    dist = distanceBetween(x1,y1,x2,y2)
    return ((x2-x1)/dist, (y2-y1)/dist, dist)

def getNodeTags(nodeId):
    base = f"node_{nodeId}"
    return f"{base}n", f"{base}c", f"{base}h", f"{base}b"
def getEdgeTag(startId,endId):
    base = f"edge_{startId}_{endId}"
    if startId > endId:
        base = f"edge_{endId}_{startId}"
    return f"{base}l", f"{base}c", f"{base}b"

def getRandVec2Simple(rand : Random,minVal:int,maxVal:int):
    return getRandVec2(rand,minVal,maxVal,minVal,maxVal)
def getRandVec2(rand : Random,minX:int,maxX:int,minY:int,maxY:int):
    return rand.randint(minX,maxX),rand.randint(minY,maxY)

# Implementación de los nodos usando la interfaz INode
class Node(INode):
    Finded = -4
    Current = -3
    Search = -2
    Path = -1
    Normal = 0
    Start = 1
    End = 2
    
    Types={
        -4:"Finded",
        -3:"Current",
        -2:"Search",
        -1:"Path",
        0:"Normal",
        1:"Start",
        2:"End",
    }

    Colors={
        -4: ("white", "black"),
        -3: ("gold3", "black"),
        -2: ("greenyellow", "black"),
        -1: ("khaki", "black"),
        0: ("lightblue", "black"),
        1: ("forestgreen", "black"),
        2: ("orangered", "black"),
    }
    SelectedColor = ("coral", "black")

    def __init__(self,name: str,coords: tuple[int, int], edges: list[int], type:int = Normal):
        self.name:str = name
        self.coords:tuple[int, int] = coords
        self.edges:list[int] = edges
        self.type:int = type

    def isInside(self,x:int,y:int,radius: int):
        return distanceBetween(*self.coords,x,y) < radius

    def addEdge(self, nodeId: int):
        if nodeId not in self.edges:
            self.edges.append(nodeId)
            return True
        return False

    def delEdge(self, nodeId: int):
        if nodeId in self.edges:
            self.edges.remove(nodeId)
            return True
        return False
    
    def setType(self,t : int):
        self.type = t % 3

    def toString(self):
        typestr = f"[{Node.Types[self.type][0]}]" if self.type > 0 else ""
        return f"{self.name} (x: {int(self.coords[0])}; y: {int(self.coords[1])}) {typestr}"
    
    def toJSON(self):
        return self.__dict__

class ListCanvasApp:
    def __init__(self, master, filePath:str = None, console:bool = False):
        self.console = console
        self.master = master

        self.rf = tk.Frame(master)
        self.rf.pack(fill="both",expand=True)

        self.statusLabel = tk.Label(self.rf)
        self.statusLabel.pack(side="top",fill="x",expand=False)
        self.statusLabel.config(text="Status")

        self.leftFrame = tk.Frame(self.rf)
        self.leftFrame.pack(side="left",fill="both")
        self.listFrame = tk.Frame(self.leftFrame)
        self.listFrame.pack(side="top",fill="both",expand=True)
        self.adminFrame = tk.Frame(self.leftFrame)
        self.adminFrame.pack(side="bottom",fill="x")

        self.nodeList = tk.Listbox(self.listFrame,width=25,selectmode=tk.SINGLE)
        self.nodeList.pack(side="left",fill="both")
        self.scrollbar = tk.Scrollbar(self.listFrame, orient="vertical", command=self.nodeList.yview)
        self.scrollbar.pack(side="left", fill="y")
        self.nodeList.config(yscrollcommand=self.scrollbar.set)

        self.controlFrame = tk.Frame(self.rf,width=130)
        self.controlFrame.pack(side="left",fill="both")
        self.addButton = tk.Button(self.controlFrame,text="Add Node", command=self.addButton_Click)
        self.addButton.pack(side="top",fill="x",expand=False)
        self.nodeNameLabel = tk.Label(self.controlFrame,text="Node Name")
        self.nodeNameLabel.pack(side="top",fill="x",expand=False)
        self.nodeName = tk.Entry(self.controlFrame)
        self.nodeName.pack(side="top",fill="x",expand=False)
        self.nodeCordLabel = tk.Label(self.controlFrame,text="Node Coordinates")
        self.nodeCordLabel.pack(side="top",fill="x",expand=False)
        self.nodeCord = tk.Entry(self.controlFrame)
        self.nodeCord.pack(side="top",fill="x",expand=False)
        self.nodeTypeLabel = tk.Label(self.controlFrame,text="Node Type")
        self.nodeTypeLabel.pack(side="top",fill="x",expand=False)
        self.nodeTypeVar = tk.StringVar(value=Node.Types[0])
        self.nodeType = tk.OptionMenu(self.controlFrame,self.nodeTypeVar,*Node.Types.values())
        self.nodeType.pack(side="top",fill="x",expand=False)
        self.updButton = tk.Button(self.controlFrame,text="Update Node", command=self.updButton_Click)
        self.updButton.pack(side="top",fill="x",expand=False)
        paddingTop = tk.Label(self.controlFrame,text="")
        paddingTop.pack(side="top",fill="x",expand=False)
        self.delButton = tk.Button(self.controlFrame,text="Delete Node", command=self.delButton_Click)
        self.delButton.pack(side="top",fill="x",expand=False)

        self.saveButton = tk.Button(self.adminFrame,text="Save Graph", command=self.saveButton_Click)
        self.saveButton.pack(side="bottom",fill="x",expand=False)
        self.saveSvgButton = tk.Button(self.adminFrame,text="Save SVG", command=self.saveSvgButton_Click)
        self.saveSvgButton.pack(side="bottom",fill="x",expand=False)
        self.loadButton = tk.Button(self.adminFrame,text="Load Graph", command=self.loadButton_Click)
        self.loadButton.pack(side="bottom",fill="x",expand=False)
        self.randomButton = tk.Button(self.adminFrame,text="Random Graph", command=self.randomButton_Click)
        self.randomButton.pack(side="bottom",fill="x",expand=False)
        self.clearButton = tk.Button(self.adminFrame,text="Clear Graph", command=self.clearGraph)
        self.clearButton.pack(side="bottom",fill="x",expand=False)
        self.helpButton = tk.Button(self.adminFrame,text="Help", command=self.showHelp)
        self.helpButton.pack(side="bottom",fill="x",expand=False)
        #paddingBottom = tk.Label(self.controlFrame,text="")
        #paddingBottom.pack(side="bottom",fill="x",expand=False)
        self.resetButton = tk.Button(self.controlFrame,text="Reset", command=self.resetButton_Click)
        self.resetButton.pack(side="bottom",fill="x",expand=False)
        self.solveButton = tk.Button(self.controlFrame,text="Solve", command=self.solveButton_Click)
        self.solveButton.pack(side="bottom",fill="x",expand=False)
        self.stepVar = tk.BooleanVar(value=False)
        self.stepCheckbox = tk.Checkbutton(self.controlFrame, text="Step by Step", variable=self.stepVar)
        self.stepCheckbox.pack(side="bottom",fill="x",expand=False)
        self.funcTypeVar = tk.StringVar(value=list(AStar.hFunctions.keys())[0])
        self.funcType = tk.OptionMenu(self.controlFrame,self.funcTypeVar,*AStar.hFunctions.keys())
        self.funcType.pack(side="bottom",fill="x",expand=False)

        self.scrollDimension = 2000
        self.canvasFrame = tk.Frame(self.rf)
        self.canvasFrame.pack(side="right",fill="both",expand=True)
        self.nodeCanvas = tk.Canvas(self.canvasFrame,bg="white",border=1,highlightbackground="lightgrey",scrollregion=(0,0,self.scrollDimension,self.scrollDimension))
        self.yCanvasScroll = tk.Scrollbar(self.canvasFrame, orient="vertical", command=self.nodeCanvas.yview)
        self.yCanvasScroll.pack(side="right", fill="y")
        self.xCanvasScroll = tk.Scrollbar(self.canvasFrame, orient="horizontal", command=self.nodeCanvas.xview)
        self.xCanvasScroll.pack(side="bottom", fill="x")
        self.nodeCanvas.config(xscrollcommand=self.xCanvasScroll.set,yscrollcommand=self.yCanvasScroll.set)
        self.nodeCanvas.pack(side="left",fill="both",expand=True)

        self.nodeCanvas.bind('<MouseWheel>', lambda event: self.nodeCanvas.yview_scroll(int(-event.delta/120), 'units'))
        self.nodeCanvas.bind('<Shift-MouseWheel>', lambda event: self.nodeCanvas.xview_scroll(int(-event.delta/120), 'units'))
        
        self.nodes : dict[int,Node] = {}
        self.selectedNode : int = -1
        self.nodeRadius = 15

        self.nodeCanvas.bind("<Button-1>", self.handleCanvasClick) #Click Izquierdo
        self.nodeCanvas.bind("<Button-2>", self.handleCanvasClick) #Click Central
        self.nodeCanvas.bind("<Button-3>", self.handleCanvasClick) #Click Derecho

        self.nodeList.bind("<<ListboxSelect>>", self.handleListClick)
        
        if filePath:
            self.loadGraphFromFile(filePath)

    def showHelp(self):
        helpStr = """Controls:
- Left Click: Creates or moves nodes
- Left Click over Nodes: Select/Deselect node
- With a node selected, click another to connect them
- Right Click over Nodes: Delete node
- Center Click: Cicle between types Normal, Start and End"""
        msgbox.showinfo("Help and Controls",helpStr)

    def clearGraph(self):
        self.selectedNode = -1
        self.clearNodes()
        self.updateCanvas()

    def handleCanvasClick(self, event):
        x, y = self.nodeCanvas.canvasx(event.x), self.nodeCanvas.canvasy(event.y)
        nodeId = self.getCanvasNode(x,y)

        if event.num == 1: # Left Click
            if nodeId != -1 and self.selectedNode == nodeId:
                self.setStatus(f"Node {self.selectedNode} deselected")
                self.selectedNode = -1
            elif self.selectedNode != -1 and nodeId!=-1 and self.selectedNode != nodeId:
                if nodeId in self.nodes[self.selectedNode].edges:
                    self.delEdge(self.selectedNode,nodeId)
                else:
                    self.addEdge(self.selectedNode,nodeId)
                self.selectedNode = -1
            elif self.selectedNode != -1 and nodeId == -1:
                self.nodes[self.selectedNode].coords = (x,y)
                self.selectedNode = -1
                
            elif nodeId >= 0:
                self.selectedNode = nodeId
                self.setStatus(f"Node {nodeId} selected")
            else:
                self.selectedNode = -1
                self.addNode(x,y)
                
        elif event.num == 2: # Center Click
            if nodeId >= 0:
                self.nodes[nodeId].type = (self.nodes[nodeId].type + 1) % 3
        elif event.num == 3: # Right Click
            if nodeId >= 0:
                self.delNode(nodeId)
            self.selectedNode = -1
        self.updateCanvas()

    def handleListClick(self, event):
        nodeId = sorted(self.nodes.items())[self.nodeList.curselection()[0]][0]
        if self.selectedNode == nodeId:
            self.setStatus(f"Node {self.selectedNode} deselected")
            self.selectedNode = -1
            self.nodeList.selection_clear(0,tk.END)
        else:
            self.selectedNode = nodeId
            self.setStatus(f"Node {nodeId} selected")
            
        self.updateCanvas(False)

    def addButton_Click(self):
        if self.selectedNode < 0:
            nodeInfo = self.getNodeFromFields()
            if nodeInfo != None:
                self.addNode(*nodeInfo.coords,nodeInfo.name, nodeInfo.type)
                self.updateList()
                self.updateUI()

    def updButton_Click(self):
        if self.selectedNode >= 0:
            nodeInfo = self.getNodeFromFields()
            if nodeInfo != None:
                if nodeInfo.name != None:
                    self.nodes[self.selectedNode].name = nodeInfo.name
                self.nodes[self.selectedNode].coords = nodeInfo.coords
                self.nodes[self.selectedNode].type = nodeInfo.type
                self.setStatus(f"Node {self.selectedNode} updated")
                self.updateCanvas()

    def delButton_Click(self):
        if self.selectedNode >= 0:
            self.delNode(self.selectedNode)
            self.selectedNode = -1
            self.updateList()
            self.updateUI()

    def randomButton_Click(self):
        print("random")
        nodeCount = sdialg.askinteger("Random Graph","How many nodes will be generated?",initialvalue=20,minvalue=5,maxvalue=500)
        rand = Random()
        
        if nodeCount != None:
            nodeSpacing = self.nodeRadius * 4
            self.selectedNode = -1
            # Se eliminan todos los nodos
            self.clearNodes()

            # Se crean nodos de forma aleatoria en el grafo
            for i in range(0,nodeCount):
                trys = 100
                x,y = getRandVec2Simple(rand,self.nodeRadius+5,int(self.scrollDimension)-self.nodeRadius-5)
                while trys>0 and any(n.isInside(x,y,nodeSpacing) for n in self.nodes.values()):
                    x,y = getRandVec2Simple(rand,self.nodeRadius+5,int(self.scrollDimension)-self.nodeRadius-5)
                    trys-=1
                if trys<=0:
                    break

                self.addNode(x,y)
            
            # Por cada nodo, se buscan los dos nodos mas cercanos y se los conecta
            for id, node in self.nodes.items():
                minDist = [-1, -1]
                distances = {eId:node.distanceTo(eNode) for eId,eNode in self.nodes.items()}
                distances.pop(id)
                for run in range(2):
                    for eId, dist in distances.items():
                        if id == eId:
                            continue
                        for i in range(len(minDist)):
                            if (eId not in minDist) and (minDist[i] == -1 or (dist < distances[minDist[i]])):
                                minDist[i] = eId
                for eId in minDist:
                    self.addEdge(id,eId)
            
            # Se verifica que todos los nodos esten conectados
            # De no ser así, se buscan los dos nodos mas cercanos que se encuentren en dos grupos separados
            connectedNodes = set()
            while not all(id in connectedNodes for id in self.nodes.keys()):
                connectedNodes = set()
                curNodes = [list(self.nodes.keys())[0]]
                while len(curNodes)>0:
                    id = curNodes.pop(0)
                    node = self.nodes[id]
                    connectedNodes.add(id)
                    for eId in node.edges:
                        if eId not in connectedNodes:
                            curNodes.append(eId)
                
                minDistCon = -1
                minDistNoCon = -1
                minDistNum = float('inf')
                for id, node in self.nodes.items():
                    if id not in connectedNodes:
                        for eId, eNode in self.nodes.items():
                            if id == eId:
                                continue
                            distNum = node.distanceTo(eNode)
                            if (minDistCon == -1 or (distNum < minDistNum and eId in connectedNodes)):
                                minDistNoCon = id
                                minDistCon = eId
                                minDistNum = distNum
                if minDistCon >= 0 and minDistNoCon >= 0:
                    self.addEdge(minDistCon,minDistNoCon)

            self.updateCanvas()

    def saveButton_Click(self):
        print("save")
        file = fdialg.asksaveasfile(initialdir="./",initialfile="My Graph",filetypes=[("Graph File",".graph"),("Json File",".json")],defaultextension=".graph")
        if file != None:
            json.dump({id:node.toJSON() for id,node in self.nodes.items()},file)
            file.close()
    
    def saveSvgButton_Click(self):
        print("save svg")
            
        doc: minidom.Document = canvasvg.SVGdocument()
        elements: list[minidom.Element] = canvasvg.convert(doc, self.nodeCanvas)
        x1, y1, x2, y2 = self.nodeCanvas.bbox("all")
        dx = x2-x1
        dy = y2-y1
        doc.documentElement.setAttribute("width",f"{dx:0.3f}")
        doc.documentElement.setAttribute("height",f"{dy:0.3f}")
        doc.documentElement.setAttribute('viewBox', "%0.3f %0.3f %0.3f %0.3f" % (x1, y1, dx, dy))

        for e in elements:
            if e.nodeName == "text":
                text = e.firstChild.nodeValue
                lines = text.split("\n")
                e.removeChild(e.firstChild)
                for l in lines:
                    line = doc.createElement("tspan")
                    line.setAttribute("x",e.getAttribute("x"))
                    line.setAttribute("dy","1.2em")
                    line.appendChild(doc.createTextNode(l))
                    e.appendChild(line)
                e.firstChild.removeAttribute("dy")
                e.firstChild.setAttribute("y",e.getAttribute("y"))
            doc.documentElement.appendChild(e)

        file = fdialg.asksaveasfile(initialdir="./",initialfile="My Graph",filetypes=[("Scalable Vector Graphics",".svg")],defaultextension=".svg")
        if file != None:
            file.write(doc.toxml())
            file.close()
        

    def loadButton_Click(self):
        print("load")
        file = fdialg.askopenfilename(initialdir="./",filetypes=[("Graph File",".graph"),("Json File",".json")],defaultextension=".graph")
        self.loadGraphFromFile(file)

    def loadGraphFromFile(self, path):
        file = open(path,"r")
        if file != None:
            lNodes = json.load(file)
            file.close()
            self.selectedNode = -1
            self.clearNodes()
            for id,n in lNodes.items():
                self.addNode(*n["coords"], n["name"],n["type"], int(id))
            for id,n in lNodes.items():
                for eId in n["edges"]:
                    self.addEdge(int(id),int(eId))
            self.updateList()

    def resetButton_Click(self):
        self.resetNodeTypes()
        self.resetNodesValue()
        self.updateCanvas()

    def solveButton_Click(self):
        if not self.console:
            print("solve")
        
        self.resetButton_Click()
        errMsg = None

        # Se verifica que solo exista un nodo de inicio y de final
        sNodes = sum(n.type == Node.Start for n in self.nodes.values())
        eNodes = sum(n.type == Node.End for n in self.nodes.values())
        errMsg = "Cannot resolve, there can only be 1 start node" if sNodes > 1 else errMsg
        errMsg = "Cannot resolve, there has to be at least 1 start node" if sNodes < 1 else errMsg
        errMsg = "Cannot resolve, there can only be 1 end node" if eNodes > 1 else errMsg
        errMsg = "Cannot resolve, there has to be at least 1 end node" if eNodes < 1 else errMsg

        if errMsg != None:
            if not self.console:
                self.setStatus(f"!! {errMsg} !!")
                msgbox.showerror("Solving Error",errMsg)
            else:
                print(f"Invalid graph: {errMsg}")
            return

        # Se invoca a la función de resolución proporcionandole los datos necesarios
        self.solveGraph(next(id for id,n in self.nodes.items() if n.type == Node.Start),
                        next(id for id,n in self.nodes.items() if n.type == Node.End),
                        self.stepVar.get(), AStar.hFunctions[self.funcTypeVar.get()])

        self.updateCanvas()

    # función auxiliar para obtener los datos del nodo a partir de los campos de la interfaz
    def getNodeFromFields(self) -> Node | None: 
        coordMatch = re.search(r"^\s*(\d+)\s*;\s*(\d+)\s*$", self.nodeCord.get())
        if coordMatch != None:
            coords = coordMatch.groups()
            coords : tuple[int,int]= (int(coords[0]),int(coords[1]))

            nName = self.nodeName.get()
            if nName == "":
                nName = None
            #nType = list(Node.Types.keys())[list(Node.Types.values()).index(self.nodeTypeVar.get())]
            nType = next((id for id,type in Node.Types.items() if type == self.nodeTypeVar.get()),0)

            return Node(nName,coords,[],nType)

        return None

    def getCanvasNode(self, x, y):
        nodeId = -1
        for id,node in self.nodes.items():
            if node.isInside(x,y,self.nodeRadius):
                nodeId = id
        return nodeId

    def getNewNodeId(self):
        i=0
        curIds=self.nodes.keys()
        while i in curIds:
            i+=1
        return i

    def addNode(self, x, y, name:str = None, type: int = Node.Normal, id: int = None):
        nodeId = self.getNewNodeId() if id == None else id
        type = Node.Normal if type == None else type % 3 if type >= 0 else 0
        if nodeId in self.nodes.keys():
            return

        self.nodes[nodeId] = Node(nodeId if name == None else name, (x, y), [], type)
        self.setStatus(f"Node {nodeId} added")
        self.drawNode(nodeId, x, y)

    def delNode(self,nodeId):
        for id,node in self.nodes.items():
            if nodeId in node.edges:
                self.delEdge(id,nodeId)
                #node.delEdge(nodeId)
                #eTag, ecTag, ebTag = getEdgeTag(nodeId,id)
                #self.nodeCanvas.delete(eTag)
        for t in getNodeTags(nodeId):
            self.nodeCanvas.delete(t)
        self.nodes.pop(nodeId)
        self.setStatus(f"Node {nodeId} deleted")

    def clearNodes(self):
        for id in [*self.nodes.keys()]:
            self.delNode(id)

    def drawNode(self, nodeId, x, y):
        canvas = self.nodeCanvas
        nTag, cTag, hTag, bTag = getNodeTags(nodeId)
        radius = self.nodeRadius
        fColor, lColor = Node.Colors[self.nodes[nodeId].type]
        canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fColor, outline=lColor, tags=cTag)
        canvas.create_text(x, y, text=str(nodeId), tags=nTag)
        canvas.create_text(x + 1.5*radius, y, text=f"g=?\nh=?", fill="olivedrab", anchor="w", tags=hTag)
        canvas.create_rectangle(canvas.bbox(hTag), fill="white", outline="white", tags=bTag)
        canvas.tag_raise(hTag,bTag)

    def delEdge(self, startId, endId):
        self.nodes[startId].delEdge(endId)
        self.nodes[endId].delEdge(startId)
        
        for t in getEdgeTag(startId,endId):
            self.nodeCanvas.delete(t)

    def addEdge(self, startId, endId):
        if (endId not in self.nodes[startId].edges) or (startId not in self.nodes[endId].edges):
            self.nodes[startId].addEdge(endId)
            self.nodes[endId].addEdge(startId)
            self.drawEdge(startId,endId)

    def drawEdge(self, startId, endId):
        canvas = self.nodeCanvas
        radius = self.nodeRadius
        eTag, ecTag, ebTag = getEdgeTag(startId,endId)

        sx,sy = self.nodes[startId].coords
        ex,ey = self.nodes[endId].coords
        dx,dy,dist = getDirectionDistance(sx,sy,ex,ey)
        cx = sx+dx * dist/2
        cy = sy+dy * dist/2
        sx += dx * radius
        sy += dy * radius
        ex -= dx * radius
        ey -= dy * radius

        canvas.create_line(sx,sy,ex,ey,fill="black",width=3,tags=eTag)
        canvas.create_text(cx,cy,text=f"{dist:.2f}",tags=ecTag)
        canvas.create_rectangle(canvas.bbox(ecTag), fill="white", outline="white", tags=ebTag)
        canvas.tag_raise(ecTag,ebTag)

    def updateList(self):
        nList = self.nodeList

        nList.delete(0, tk.END)
        nList.insert(tk.END, *[f"[{id}] {n.toString()}" for id,n in sorted(self.nodes.items())])

    def updateCanvas(self,upList : bool = True, onlyTypes : bool = False):
        radius = self.nodeRadius
        canvas = self.nodeCanvas

        for id, node in self.nodes.items():
            nTag, cTag, hTag, bTag = getNodeTags(id)

            fColor, lColor = Node.SelectedColor if id == self.selectedNode else Node.Colors[node.type]
            canvas.itemconfig(cTag,fill = fColor, outline=lColor)
            
            if not onlyTypes:
                x, y = node.coords
                canvas.coords(cTag,x - radius, y - radius, x + radius, y + radius)
                canvas.coords(nTag, x, y)
                canvas.coords(hTag, x + 1.5*radius, y)
                canvas.coords(bTag, canvas.bbox(hTag))

                for eId in node.edges:
                    eTag, ecTag, ebTag = getEdgeTag(id,eId)
                    ex,ey = self.nodes[eId].coords
                    dx,dy,dist = getDirectionDistance(x,y,ex,ey)
                    cx = x+dx * dist/2
                    cy = y+dy * dist/2
                    sx = x + dx * radius
                    sy = y + dy * radius
                    ex -= dx * radius
                    ey -= dy * radius

                    canvas.coords(eTag,sx,sy,ex,ey)
                    canvas.itemconfig(ecTag, text=f"{dist:.2f}")
                    canvas.coords(ecTag,cx,cy)
                    canvas.coords(ebTag, canvas.bbox(ecTag))
                    canvas.tag_raise(ecTag,ebTag)
                
                canvas.tag_raise(bTag)
                canvas.tag_raise(hTag)

        self.updateUI()
        if upList:
            self.updateList()

    def setStatus(self, text):
        self.statusLabel.config(text=text)

    def updateUI(self):
        self.nodeName.delete(0,tk.END)
        self.nodeCord.delete(0,tk.END)
        self.nodeTypeVar.set(Node.Types[0])

        if self.selectedNode >= 0:
            node = self.nodes[self.selectedNode]
            self.nodeName.insert(0,node.name)
            self.nodeCord.insert(0,f"{int(node.coords[0])}; {int(node.coords[1])}")
            self.nodeTypeVar.set(Node.Types[node.type])

    def resetNodeTypes(self):
        for id,node in self.nodes.items():
            node.type = 0 if node.type < 0 else node.type

    # función que crea la clase A* y resuelve el grafo actualizando la interfaz
    def solveGraph(self,startId: int, endId: int, step: bool, hFunc: Callable):
        solver = AStar(self.nodes, hFunc)
        startTime = time.perf_counter()
        path = solver.solve(startId, endId, self.updateSolver if step else None)
        endTime = time.perf_counter()
        elapsedTime = (endTime - startTime)*1000
        self.resetNodeTypes()
        self.updateNodesValue(solver.nodesData)
        for id in solver.nodesData.keys():
            if self.nodes[id].type == Node.Normal:
                self.nodes[id].type = Node.Finded
        
        if path != None:
            for id in path:
                if id != startId and id != endId:
                    self.nodes[id].type = Node.Path
        elif not self.console:
            msgbox.showerror("Solving error","Cannot found a path to the end node")
        costMsg = f"{solver.nodesData[endId].g:.2f}" if endId in solver.nodesData else "inf"
        sumMsg = f"{len(solver.nodesData.keys())} nodes has been explored\n{solver.reopened} nodes has been reopened\nFinal cost {costMsg}\n\nElapsed Time: {elapsedTime:.3f} ms"
        print(f"{sumMsg}\nPath: {path}")
        if not self.console:
            self.updateCanvas()
            self.nodeCanvas.update()
            pathStr = str.join(" -> ",[str(p) for p in path]) if path else "None"
            msgbox.showinfo("Solution Resume", f"{sumMsg}\nPath: {pathStr}")

    def resetNodesValue(self):
        canvas = self.nodeCanvas

        for id in self.nodes.keys():
            nTag, cTag, hTag, bTag = getNodeTags(id)
            canvas.itemconfig(hTag, text=f"g=?\nh=?")
            canvas.coords(bTag, canvas.bbox(hTag))

    def updateNodesValue(self,nodesData: list[int,NodeData]):
        canvas = self.nodeCanvas

        for id,data in nodesData.items():
            nTag, cTag, hTag, bTag = getNodeTags(id)
            canvas.itemconfig(hTag, text=f"g={data.g:.2f}\nh={data.h:.2f}")
            canvas.coords(bTag, canvas.bbox(hTag))

    def updateSolver(self, nodesData: dict[int,NodeData], curId: int, searchId: int, path: list[int]):
        self.updateNodesValue(nodesData)
        self.resetNodeTypes()
        for id in path:
            if self.nodes[id].type <= Node.Normal:
                self.nodes[id].type = Node.Path
        if self.nodes[curId].type <= Node.Normal:
            self.nodes[curId].type = Node.Current
        if self.nodes[searchId].type <= Node.Normal:
            self.nodes[searchId].type = Node.Search
        self.updateCanvas(False,True)
        self.nodeCanvas.update()
        time.sleep(.1)


# Definición de argumentos para la linea de comandos
parser = argparse.ArgumentParser("PathFinder",description="Developed by NodeFinders (Matías Balbuena, Oscar Wohlfarhrt)")
parser.add_argument("filename",default=None,nargs="?")
hChoises = ", ".join(AStar.hFunctions.keys())
hfuncs = ["e", "m", "c", "1m5", "3m"]
parser.add_argument("--hf", "--h-func", choices=hfuncs, dest="hfunc",help=f"selects an heuristic function to be used. {hChoises} respectively")
parser.add_argument("-s", "--solve", action='store_true', dest="solve", help="automatically solves the graph with the heuristic function specified on --h-func argument. This option has no effect when used with --no-gui.")
parser.add_argument("--ng", "--no-gui", action='store_true', dest="nogui",help="only outputs on the console and shows no window. Always resolves the graph and requieres a filename.")

args = parser.parse_args()

root = tk.Tk(className="PathFinderApp")
root.title("PathFinder - Developed by NodeFinders (Matías Balbuena, Oscar Wohlfarhrt)")
root.minsize(600,420)
try:
    icon = tk.PhotoImage(file="./PFIcon.png")
    root.iconphoto(True, icon)
except tk.TclError:
    print("Warning: Could not load icon.png. Make sure it's in the correct path and a supported format (PNG, GIF).")

if args.nogui:
    # Solo linea de comandos (diseñado apra benchmark)
    if args.filename:
        app = ListCanvasApp(root,args.filename,True)
        if args.hfunc:
            app.funcTypeVar.set(list(AStar.hFunctions.keys())[hfuncs.index(args.hfunc)])
            print(f"Using {app.funcTypeVar.get()} distance as heuristic")
        app.solveButton_Click()
else:
    # Crea la interfaz inicial e inicia la aplicación
    app = ListCanvasApp(root,args.filename)
    if args.filename:
        if args.hfunc:
            app.funcTypeVar.set(list(AStar.hFunctions.keys())[hfuncs.index(args.hfunc)])
            #print(f"Using {app.funcTypeVar.get()} distance as heuristic")
        if args.solve:
            app.solveButton_Click()
    root.mainloop()

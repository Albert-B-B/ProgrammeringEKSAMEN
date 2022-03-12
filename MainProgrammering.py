# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 11:01:25 2022

@author: Albert
"""

import tkinter as tk
import tkinter.filedialog as tkd
import numpy as np
class PCBClass(object):
    def __init__(self,name):
        self.name = name
        self.nets = []
        self.components = []
        self.traces = []
        self.pads = []
        self.via = []
    def __str__(self):
        string = "nets:\n"
        for i in self.nets:
            string += "{} {}\n".format(i.number,i.name)
        string += "Pads:\n"
        for pad in self.pads:
            string += "{} {} {} {} {} {} {} {}\n".format(pad.width,pad.height,pad.drill,pad.net,pad.x,pad.y,pad.ang,pad.shape)
        return(string)
class NetClass(object):
    def __init__(self,name,number):
        self.name = name
        self.number = number
    
class TraceClass(object):
    def __init__(self,width,net):
        self.width = width
        self.net = net
    
class ComponentClass(object):
    def __init__(self,x,y,ang):
        self.x = x
        self.y = y
        self.ang = ang

class PadClass(object):
    def __init__(self,width,height,drill,net,x,y,ang,shape,component):
        self.shape = shape
        self.x = x
        self.y = y
        self.ang = ang
        self.width = width
        self.height = height
        self.drill = drill
        self.net = net
        self.component = component
        
    
class ViaClass(object):
    def __init__(self,width,drill,net):
        self.width = width
        self.drill = drill
        self.net = net

class GUIClass(tk.Frame):
    def __init__(self):
        tk.Frame.__init__(self)
        
        self.PCBs = [] #List containing PCBS
        
        #Options for UI
        self.cWidth = 500 #Width of canvas
        self.cHeight = 500 #Height of canvas
        
        self.backgroundColor = "#000000" #Black
        
        #Drawing UI
        self.master.title("PCB Autorouter") #For title on tkinter window
        self.build_gui() #Function that defines GUI made in tkinter
    
    def getFile(self):
        file = tkd.askopenfile(mode='r')
        if file == None:
            return
        fileEnding = file.name[len(file.name)-9:len(file.name)] 
        
        if fileEnding != "kicad_pcb" or file == None:
            self.selectFileResult.config(text="Invalid file type \n must be kicad_pcb",fg='#ff0000')
        else:
            self.selectFileResult.config(text="Found kicad_pcb file",fg='#00ff00')
            count = 1
            while file.name[len(file.name)-count] != "/":
                count += 1
            fileName = file.name[len(file.name)-count+1:len(file.name)-10]
            self.PCBs.append(self.parseFile(file,fileName))
            self.drawPCB(self.PCBs[0])
    def parseFile(self,fileRaw,name):
        nPCB = PCBClass(name)
        fileOpen = open(fileRaw.name,"r")
        fileD = fileOpen.readlines()
        
        currComponentIndex = -1 #Current component
        for index,val in enumerate(fileD):
            #For evaluating all pads and nets
            if "(module" in val:
                placementString = fileD[index+1]
                tempSplit = placementString.split(" ")
                if len(tempSplit) >= 7: #Makes sure we get no option string
                    x = float(tempSplit[5])
                    if len(tempSplit) == 8: #Check if angle is stored
                        y = float(tempSplit[6])
                        angle = float(tempSplit[7][0:len(tempSplit[3])-2])
                    else:
                        y = float(tempSplit[6][0:len(tempSplit[2])-2])
                        angle = 0
                    currComponentIndex += 1
                    nPCB.components.append(ComponentClass(x,y,angle))
            if "(pad " in val:
                split = val.split("(")
                #print(split)
                #Finds the shape
                tempSplit = split[1].split(" ")
                shape = tempSplit[3]
                #Finds the position and angle
                tempSplit = split[2].split(" ")
                x = float(tempSplit[1])
                if len(tempSplit) == 5: #Check if angle is stored
                    y = float(tempSplit[2])
                    angle = float(tempSplit[3][0:len(tempSplit[3])-1])
                else:
                    y = float(tempSplit[2][0:len(tempSplit[2])-1])
                    angle = 0
                #Finds width and height
                tempSplit = split[3].split(" ")
                width = float(tempSplit[1])
                height = float(tempSplit[2][0:len(tempSplit[2])-1])
                #Finds drill
                tempSplit = split[4].split(" ")
                drill = float(tempSplit[1][0:len(tempSplit[1])-1])
                #Finds net
                netString = fileD[index+1]
                netStringSplit = netString.split(" ")
                netAlreadyExsists = False
                netNumb = int(netStringSplit[7])
                netName = netStringSplit[8][0:len(netStringSplit[8])-3]
                #Check if net already exsists
                for net in nPCB.nets:
                    if netNumb == net.number:
                        netAlreadyExsists = True
                        break
                if netAlreadyExsists == False:
                    nPCB.nets.append(NetClass(netName,netNumb))
                nPCB.pads.append(PadClass(width,height,drill,netNumb,x,y,angle,shape,currComponentIndex))
        fileOpen.close()
        return nPCB
    
    def build_gui(self):
        #Frame med canvas
        self.canvasFrame = tk.Frame(self)
        #Frame hvorfra man vælger
        self.settingsFrame = tk.Frame(self)
        
        #Frames bliver placeret til venstre og højre
        self.canvasFrame.pack(side=tk.RIGHT)
        self.settingsFrame.pack(side=tk.LEFT)
        self.pack()

        #Canvas hvor at PCB bliver tegnet
        self.canvas = tk.Canvas(self.canvasFrame,bg="white",width=self.cWidth,height=self.cHeight)
        self.canvas.create_rectangle(0,0,self.cWidth,self.cHeight, fill=self.backgroundColor)
        self.canvas.pack(side=tk.TOP)
        
        #Indtillinger
        self.selectFileButton = tk.Button(self.settingsFrame,text ="Select PCB file",command=self.getFile)
        self.selectFileButton.pack()
        self.selectFileResult = tk.Label(self.settingsFrame,text="")
        self.selectFileResult.pack()
        
    def drawPCB(self,pcb):
        border = 50 #Border area not used for drawing
        
        #This part is for figuring out how to scale between screen and real measurements takes rotation into account
        minx = 0
        maxx = 0
        miny = 0
        maxy = 0
        for index,pad in enumerate(pcb.pads):
            if pad.x*np.cos(np.pi*pad.ang/180)-pad.y*np.cos(np.pi*pad.ang/180)+pcb.components[pad.component].x < minx or index == 0:
                minx = pad.x*np.cos(np.pi*pad.ang/180)-pad.y*np.cos(np.pi*pad.ang/180)+pcb.components[pad.component].x
            elif pad.x*np.cos(np.pi*pad.ang/180)-pad.y*np.cos(np.pi*pad.ang/180)+pcb.components[pad.component].x > maxx or index == 0:
                maxx = pad.y+pcb.components[pad.component].x
            if pad.x*np.sin(np.pi*pad.ang/180)+pad.y*np.cos(np.pi*pad.ang/180)+pcb.components[pad.component].y < miny or index == 0:
                miny = pad.x*np.sin(np.pi*pad.ang/180)+pad.y*np.cos(np.pi*pad.ang/180)+pcb.components[pad.component].y
            elif pad.x*np.sin(np.pi*pad.ang/180)+pad.y*np.cos(np.pi*pad.ang/180)+pcb.components[pad.component].y > maxy or index == 0:
                maxy = pad.x*np.sin(np.pi*pad.ang/180)+pad.y*np.cos(np.pi*pad.ang/180)+pcb.components[pad.component].y
        #Which side is the largest relative to screen side. We scale with regards to largest.
        if (self.cWidth-2*border)/abs(maxx-minx) < (self.cHeight-2*border)/abs(maxy-miny):
            scale = (self.cWidth-2*border)/abs(maxx-minx)
        else:
            scale = (self.cHeight-2*border)/abs(maxy-miny)
        #Loop that draws each pad to screen
        for pad in pcb.pads:
            #We use a rotation matrix to rotate pads
            cx = border + (pad.x*np.cos(-np.pi*pad.ang/180)-pad.y*np.sin(-np.pi*pad.ang/180)+pcb.components[pad.component].x-minx)*scale #Canvas x center
            cy = border + (pad.x*np.sin(-np.pi*pad.ang/180)+pad.y*np.cos(-np.pi*pad.ang/180)+pcb.components[pad.component].y-miny)*scale #Canvas y center
            if pad.shape == "rect":
                pass
            elif pad.shape == "oval":
                pass
            elif pad.shape == "circle":
                pass
            else:
                print("Error unrecognized pad shape:",pad.shape)
            #Draws the drill hole
            drillDraw = pad.drill*scale*0.5 #Converts to radius
            
            self.canvas.create_oval(cx-drillDraw,cy-drillDraw,cx+drillDraw,cy+drillDraw,fill="#ff0000") #Tegner drill hole

def main():
    GUI = GUIClass()    
    GUI.mainloop()

if __name__ == "__main__":
    main()
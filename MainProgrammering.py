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
        self.vias = []
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
        self.dWidth = 0
class TraceClass(object):
    def __init__(self,net,x0,y0,x1,y1,width=0):
        self.width = width
        self.net = net
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        
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
    def __init__(self,x,y,width,drill,net):
        self.x = x
        self.y = y
        self.width = width
        self.drill = drill
        self.net = net

class GUIClass(tk.Frame):
    def __init__(self):
        tk.Frame.__init__(self)
        
        self.PCBs = [] #List containing PCBS
        
        #Options for UI
        self.cWidth = 800 #Width of canvas
        self.cHeight = 800 #Height of canvas
        
        self.backgroundColor = "#000000" #Black
        
        #Drawing constants will be set once PCB is drawn
        self.minx = 0
        self.maxx = 0
        self.miny = 0
        self.maxy = 0
        self.scale = 1
        
        self.border = 50
        
        #Drawing UI
        self.master.title("PCB Autorouter") #For title on tkinter window
        self.build_gui() #Function that defines GUI made in tkinter
    
    def getFile(self):
        file = tkd.askopenfile(mode='r')
        #If no file was selected do not continue
        if file == None:
            return
        fileEnding = file.name[len(file.name)-9:len(file.name)]  
        #Check if it is valid filetype
        if fileEnding != "kicad_pcb":
            self.selectFileResult.config(text="Invalid file type \n must be kicad_pcb",fg='#ff0000')
        else:
            self.selectFileResult.config(text="Found kicad_pcb file",fg='#00ff00')
            count = 1
            while file.name[len(file.name)-count] != "/":
                count += 1
            fileName = file.name[len(file.name)-count+1:len(file.name)-10]
            self.PCBs.append(self.parseFile(file,fileName))
            self.drawPCB(self.PCBs[len(self.PCBs)-1])
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
            if "(segment" in val:
                tempSplit = fileD[index].split(" ")
                if len(tempSplit) < 15:
                    continue
                x0 = float(tempSplit[4])
                y0 = float(tempSplit[5][0:len(tempSplit[5])-1])
                x1 = float(tempSplit[7])
                y1 = float(tempSplit[8][0:len(tempSplit[8])-1])
                width = float(tempSplit[10][0:len(tempSplit[10])-1])
                if len(tempSplit) == 15:
                    netNumb = int(tempSplit[14][0:len(tempSplit[14])-3])
                else:
                    netNumb = int(tempSplit[14][0:len(tempSplit[14])-1])
                
                netAlreadyExsists = False
                for net in nPCB.nets:
                    if netNumb == net.number:
                        netAlreadyExsists = True
                        break
                if netAlreadyExsists == False:
                    nPCB.nets.append(NetClass("net {}".format(netNumb),netNumb))
                nPCB.traces.append(TraceClass(netNumb,x0,y0,x1,y1,width))
                
            elif "(via" in val:
                tempSplit = fileD[index].split(" ")
                if len(tempSplit) < 13:
                    continue
                x = float(tempSplit[4])
                y = float(tempSplit[5][0:len(tempSplit[5])-1])
                width = float(tempSplit[7][0:len(tempSplit[7])-1])
                drill = float(tempSplit[9][0:len(tempSplit[9])-1])
                
                netAlreadyExsists = False
                netNumb = int(tempSplit[14][0:len(tempSplit[14])-3])
                
                for net in nPCB.nets:
                    if netNumb == net.number:
                        netAlreadyExsists = True
                        break
                if netAlreadyExsists == False:
                    nPCB.nets.append(NetClass("net {}".format(netNumb),netNumb))
                nPCB.vias.append(ViaClass(x,y,width,drill,net))
                
        fileOpen.close()
        #For faster indexing later
        nPCB.nets.sort(key=lambda x: x.number,reverse=True)
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
    
    def rotatePoint(self,x,y,a):
        return [x*np.cos(a)-y*np.sin(a),x*np.sin(a)+y*np.cos(a)]
    
    def rotatedRectCorners(self,w,h,a):
        w1,h1 = self.rotatePoint(w,h,a)
        w2,h2 = self.rotatePoint(w,-h,a)
        w3,h3 = self.rotatePoint(-w,-h,a)
        w4,h4 = self.rotatePoint(-w,h,a)
        return [w1,h1,w2,h2,w3,h3,w4,h4]
    def drawPad(self,pcb,pad,padColor,holeColor):
        #We use a rotation matrix to rotate pads
        cx = self.border + (pad.x*np.cos(-np.pi*pad.ang/180)-pad.y*np.sin(-np.pi*pad.ang/180)+pcb.components[pad.component].x-self.minx)*self.scale #Canvas x center
        cy = self.border + (pad.x*np.sin(-np.pi*pad.ang/180)+pad.y*np.cos(-np.pi*pad.ang/180)+pcb.components[pad.component].y-self.miny)*self.scale #Canvas y center
        #Draws pad depending on shape
        if pad.shape == "rect":
            w = pad.width*0.5*self.scale
            h = pad.height*0.5*self.scale
            w1,h1,w2,h2,w3,h3,w4,h4 = self.rotatedRectCorners(w, h, -np.pi*pad.ang/180)
            self.canvas.create_polygon([cx+w1,cy+h1,cx+w2,cy+h2,cx+w3,cy+h3,cx+w4,cy+h4],fill=padColor,outline=padColor) #Tegner rektangel
        elif pad.shape == "oval":
            if pad.width == pad.height:
                r = pad.width*self.scale*0.5 #Convert to radius from diameter
                self.canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill=padColor,outline=padColor) #Tegner drill hole
            elif pad.width > pad.height:
                #Draw middle rectangle
                adjWidth = (pad.width-pad.height)*0.5*self.scale
                w = pad.width*0.5*self.scale
                h = pad.height*0.5*self.scale
                w1,h1,w2,h2,w3,h3,w4,h4 = self.rotatedRectCorners(adjWidth, h, -np.pi*pad.ang/180)
                self.canvas.create_polygon([cx+w1,cy+h1,cx+w2,cy+h2,cx+w3,cy+h3,cx+w4,cy+h4],fill=padColor,outline=padColor) #Tegner midter rektangel
                #Draw halfcircle
                lcx,lcy = [-h-adjWidth*np.cos(-np.pi*pad.ang/180), -h-adjWidth*np.sin(-np.pi*pad.ang/180)]
                rcx,rcy = [h-adjWidth*np.cos(-np.pi*pad.ang/180), h-adjWidth*np.sin(-np.pi*pad.ang/180)]
                self.canvas.create_arc(cx+lcx,cy+lcy,cx+rcx,cy+rcy,start=pad.ang+90,extent=180,fill=padColor,outline=padColor)
                #Draw other half circle
                lcx,lcy = [-h+adjWidth*np.cos(-np.pi*pad.ang/180), -h+adjWidth*np.sin(-np.pi*pad.ang/180)]
                rcx,rcy = [h+adjWidth*np.cos(-np.pi*pad.ang/180), h+adjWidth*np.sin(-np.pi*pad.ang/180)]
                self.canvas.create_arc(cx+lcx,cy+lcy,cx+rcx,cy+rcy,start=pad.ang+270,extent=180,fill=padColor,outline=padColor)
                
                #self.canvas.create_arc(cx+w*3,cy-h,cx-w*1,cy+h,start=pad.ang+270,extent=180,fill=padColor,outline=padColor)
            elif pad.width < pad.height:
                #Add the reverse for when height is larger than pad
                adjHeight = (pad.height-pad.width)*0.5*self.scale
                w = pad.width*0.5*self.scale
                h = pad.height*0.5*self.scale
                w1,h1,w2,h2,w3,h3,w4,h4 = self.rotatedRectCorners(w, adjHeight, -np.pi*pad.ang/180)
                self.canvas.create_polygon([cx+w1,cy+h1,cx+w2,cy+h2,cx+w3,cy+h3,cx+w4,cy+h4],fill=padColor,outline=padColor) #Tegner midter rektangel
                #Draw halfcircle
                lcx,lcy = [-w-adjHeight*np.sin(-np.pi*pad.ang/180), -w+adjHeight*np.cos(-np.pi*pad.ang/180)]
                rcx,rcy = [w-adjHeight*np.sin(-np.pi*pad.ang/180), w+adjHeight*np.cos(-np.pi*pad.ang/180)]
                self.canvas.create_arc(cx+lcx,cy+lcy,cx+rcx,cy+rcy,start=pad.ang+180,extent=180,fill=padColor,outline=padColor)
                #Draw other half circle
                lcx,lcy = [-w+adjHeight*np.sin(-np.pi*pad.ang/180), -w-adjHeight*np.cos(-np.pi*pad.ang/180)]
                rcx,rcy = [w+adjHeight*np.sin(-np.pi*pad.ang/180), w-adjHeight*np.cos(-np.pi*pad.ang/180)]
                self.canvas.create_arc(cx+lcx,cy+lcy,cx+rcx,cy+rcy,start=pad.ang,extent=180,fill=padColor,outline=padColor)
        elif pad.shape == "circle":
            r = pad.width*self.scale*0.5 #Convert to radius from diameter
            self.canvas.create_oval(cx-r,cy-r,cx+r,cy+r,fill=padColor,outline=padColor) #Tegner drill hole
        else:
            print("Error unrecognized pad shape:",pad.shape)
        #Draws the drill hole
        drillDraw = pad.drill*self.scale*0.5 #Converts to radius
        
        self.canvas.create_oval(cx-drillDraw,cy-drillDraw,cx+drillDraw,cy+drillDraw,fill=holeColor) #Tegner drill hole
    def drawTrace(self,trace,traceColor):
        cx0 = self.border + (trace.x0-self.minx)*self.scale
        cy0 = self.border + (trace.y0-self.miny)*self.scale
        cx1 = self.border + (trace.x1-self.minx)*self.scale
        cy1 = self.border + (trace.y1-self.miny)*self.scale
        swidth = trace.width*self.scale
        angle = np.arctan2(cx0-cx1,cy0-cy1)
        
        self.canvas.create_line(cx0,cy0,cx1,cy1,fill=traceColor,width=swidth)
        swidth*=0.5 #Change to radius
        self.canvas.create_arc(cx0-swidth,cy0-swidth,cx0+swidth,cy0+swidth,start=180*angle/np.pi+180,extent=180,fill=traceColor,outline=traceColor)
        self.canvas.create_arc(cx1-swidth,cy1-swidth,cx1+swidth,cy1+swidth,start=180*angle/np.pi+180,extent=-180,fill=traceColor,outline=traceColor)
    def drawVia(self,via,padColor,holeColor):
        cx = self.border + (via.x-self.minx)*self.scale #Canvas x center
        cy = self.border + (via.y-self.miny)*self.scale #Canvas y center
        viaDraw = via.width*self.scale*0.5
        self.canvas.create_oval(cx-viaDraw,cy-viaDraw,cx+viaDraw,cy+viaDraw,fill=padColor,outline=padColor) #Tegner drill hole
        drillDraw = via.drill*self.scale*0.5 #Converts to radius
        self.canvas.create_oval(cx-drillDraw,cy-drillDraw,cx+drillDraw,cy+drillDraw,fill=holeColor,outline=holeColor) #Tegner drill hole
    def drawPCB(self,pcb):
        #Colors used
        padColor = "#00ff00"
        holeColor = "#ff0000"
        #holeColor = "#000000"
        traceColor = "#00ff00"
        bgColor = self.backgroundColor #Black
        #Clear screen
        self.canvas.delete("all")
        self.canvas.create_rectangle(0,0,self.cWidth,self.cHeight,fill=bgColor)
        
        #This part is for figuring out how to scale between screen and real measurements takes rotation into account
        self.minx = 0
        self.maxx = 0
        self.miny = 0
        self.maxy = 0
        for index,pad in enumerate(pcb.pads):
            if pad.x*np.cos(np.pi*pad.ang/180)-pad.y*np.cos(np.pi*pad.ang/180)+pcb.components[pad.component].x < self.minx or index == 0:
                self.minx = pad.x*np.cos(np.pi*pad.ang/180)-pad.y*np.cos(np.pi*pad.ang/180)+pcb.components[pad.component].x
            elif pad.x*np.cos(np.pi*pad.ang/180)-pad.y*np.cos(np.pi*pad.ang/180)+pcb.components[pad.component].x > self.maxx or index == 0:
                self.maxx = pad.y+pcb.components[pad.component].x
            if pad.x*np.sin(np.pi*pad.ang/180)+pad.y*np.cos(np.pi*pad.ang/180)+pcb.components[pad.component].y < self.miny or index == 0:
                self.miny = pad.x*np.sin(np.pi*pad.ang/180)+pad.y*np.cos(np.pi*pad.ang/180)+pcb.components[pad.component].y
            elif pad.x*np.sin(np.pi*pad.ang/180)+pad.y*np.cos(np.pi*pad.ang/180)+pcb.components[pad.component].y > self.maxy or index == 0:
                self.maxy = pad.x*np.sin(np.pi*pad.ang/180)+pad.y*np.cos(np.pi*pad.ang/180)+pcb.components[pad.component].y
        
        #Which side is the largest relative to screen side. We scale with regards to largest.
        if (self.cWidth-2*self.border)/abs(self.maxx-self.minx) < (self.cHeight-2*self.border)/abs(self.maxy-self.miny):
            self.scale = (self.cWidth-2*self.border)/abs(self.maxx-self.minx)
        else:
            self.scale = (self.cHeight-2*self.border)/abs(self.maxy-self.miny)
        
        #Draws all objects
        for trace in pcb.traces:
            pass
            #self.drawTrace(trace,traceColor)
        for pad in pcb.pads:
            self.drawPad(pcb,pad,padColor,holeColor)
        
        for via in pcb.vias:
            self.drawVia(via,padColor,holeColor)
        
        
def main():
    GUI = GUIClass()    
    GUI.mainloop()

if __name__ == "__main__":
    main()
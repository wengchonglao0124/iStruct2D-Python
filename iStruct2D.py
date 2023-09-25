"""
Developer: Weng Chong LAO
Start date: 03/03/2021

Project name: iStruct2D
Programming Language: Python
Description: This project is my individual project, the purpose of the project is to
            develop a prototype of the structural analysis software by using Python,
            this software is using Direct Stiffness Method to solve the bending moment diagram,
            shear force diagram, deflection and reaction force for an input structure,
            then representing the result in a comprehensive user interface.
"""

import math
import tkinter as tk
from directStiffnessMethod.structure import Structure
from directStiffnessMethod.matrixCalculation import MatrixCalculation
from tkinter import *
from PIL import ImageTk, Image
from tkinter import simpledialog
from tkinter import filedialog
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table
from reportlab.platypus import TableStyle


class DataInput(object):
    """
    A pop-up window for the data input
    """

    def __init__(self, master, app, title, inputs, id=None, pictures=None, windowSize=None, tips=None):
        """
        Initiating a pop-up window for the data input

        :param master: tk.Tk()
        :param app: iStruct2D window
        :param title: title for the pop-up window
        :param inputs: list of required input parameter strings
        :param id: id of the input data
        :param pictures: list of picture name
        :param windowSize: size of the original window
        :param tips: tip string
        """
        self._master = master
        self._master.title(title)
        self._title = title
        self._master.protocol("WM_DELETE_WINDOW", self.cancel)
        size = len(inputs)*65
        if title == "Add Member Uniformly Distributed Load":
            size = len(inputs)*80
        self._master.geometry("400x" + str(size) + "+" + str(round(windowSize[0]*0.4)) + "+" + str(round(windowSize[1]*0.25)))
        self._app = app
        self._unit = self._app._unit

        self._inputs = []

        if app._moving == True:
            app._moving = False
            app._origin = [100, 800]
            app.updateOrigin()
            app._canvas.unbind("<Motion>")

        for index in range(0, len(inputs)):

            tk.Label(self._master, text=inputs[index]+" = ").pack()
            text = tk.Text(self._master, height = 1, width = 15, bd=2, bg="grey")

            if self._title == "Add Member":
                text.config(width = 20)

            if id != None and index == id[0]:
                text.insert(tk.INSERT, str(id[1]))

            if self._title == "Add Node" and index == 3:
                text.bind("<Button-1>", self.clear)

            text.pack()
            self._inputs.append(text)

        if pictures != None:
            self._master.geometry("300x400")
            self._inputs.append(tk.Text(self._master, height = 1, width = 15))

            self.names =[]
            for item in pictures:
                self.names.extend(pictures[item])

            for support in pictures:
                self._supportFrame = tk.Frame(self._master)
                self._supportFrame.pack(pady=5)
                for fileName in pictures[support]:
                    img = Image.open('supportType/'+fileName)
                    image = img.resize((40, 40))
                    picture = ImageTk.PhotoImage(image)
                    supportButton = tk.Button(self._supportFrame, image=picture, command = lambda x=fileName: self.supportButton(x))
                    supportButton.image = picture
                    supportButton.pack(side=tk.LEFT, padx=5)

        self._buttonFrame = tk.Frame(self._master)
        self._buttonFrame.pack(pady=10)

        self._addButton = tk.Button(self._buttonFrame, text="Add", command = self.add)
        self._addButton.pack(side = tk.LEFT, padx = 10)

        self._cancelButton = tk.Button(self._buttonFrame, text="Cancel", command = self.cancel)
        self._cancelButton.pack(side = tk.RIGHT, padx = 10)

        if tips != None:
            if pictures != None:
                self._master.geometry("300x450")
            tk.Label(self._master, text=tips, fg="#D0701A").pack()


    def clear(self, event):
        """
        Clear the input box
        """
        self._inputs[4].delete("0.0", tk.END)


    def supportButton(self, type):
        """
        Input the required support type string to the input box

        :param type: support type string
        """
        self._inputs[3].delete("0.0", tk.END)
        type = type.split(".")
        typeName = type[0][0:3]
        self._inputs[3].insert(tk.INSERT, typeName)

        self._inputs[4].delete("0.0", tk.END)
        self._inputs[4].insert(tk.INSERT, type[0])


    def close(self):
        """
        Close the pop-up window
        """
        self._master.destroy()


    def cancel(self):
        """
        Cancel the input process and close the pop-up window
        """
        if self._title == "Add Member Uniformly Distributed Load":
            self._app.displayData("Fail to add " + self._title.split(" ",2)[2] + "\n")
        else:
            self._app.displayData("Fail to add " + self._title.split(" ",1)[1] + "\n")
        self._master.destroy()


    def add(self):
        """
        Add the relevant data from user's input to iStruct2D
        """
        result = []

        for x in self._inputs:
            result.append(x.get("0.0", tk.END).strip())

        # Generate the Node
        if self._title == "Add Node":
            x = float(result[1])
            y = float(result[2])
            if self._unit[1] == "m":
                x = x*1000
                y = y*1000
            self._app.createNode(result[0], x, y, result[3], result[4], True)

        # Generate the Member
        if self._title == "Add Member":
            self._app.createMember(result[0], result[1], result[2], result[3], result[4], result[5], result[6], True)

        # Generate the Node Loading
        if self._title == "Add Nodal Load":
            Fx = float(result[1])
            Fy = float(result[2])
            M = float(result[3])
            if self._unit[0] == "kN":
                Fx = Fx*1000
                Fy = Fy*1000
                M = M*1000
            if self._unit[1] == "m":
                M = M*1000
            self._app.createNodalLoad(result[0], Fx, Fy, M, True)

        # Generate the Member Point Loading
        if self._title == "Add Member Point Load":
            x = float(result[1])
            Fx = float(result[2])
            Fy = float(result[3])
            if self._unit[1] == "m":
                x = x*1000
            if self._unit[0] == "kN":
                Fx = Fx*1000
                Fy = Fy*1000
            self._app.createMemberPointLoad(result[0], x, Fx, Fy)

        # Generate the Member UDL
        if self._title == "Add Member Uniformly Distributed Load":
            w = float(result[1])
            if self._unit[1] == "m":
                w = w/1000
            if self._unit[0] == "kN":
                w = w*1000
            self._app.createMemberUniformlyDistributedLoad(result[0], w)

        # Close the pop-up window at the end
        self.close()


class App(object):
    """
    Main window of iStruct2D
    """

    def __init__(self, master):
        """
        Initiating the main window of iStruct2D
        Basic UI setup

        :param master: tk.Tk()
        """
        self._master = master
        self._master.title("iStruct2D")

        self._filename = None

        self._windowWidth = self._master.winfo_screenwidth()
        self._windowHeight = self._master.winfo_screenheight()
        self._windowSize = (self._windowWidth, self._windowHeight)

        #self._master.geometry("1250x950")
        self._master.geometry(str(round(self._windowWidth*0.86))+"x"+str(round(self._windowHeight*0.82))+"+"
                              +str(round(self._windowWidth*0.07))+"+"+str(round(self._windowHeight*0.05)))

        self._canvasFrame = tk.Frame(self._master)
        self._canvasFrame.pack(fill=tk.X)

        self._canvas = tk.Canvas(self._canvasFrame, bg="#DEE7EF", height=round(self._windowHeight*0.82), width=round(self._windowWidth*0.65))
        self._canvas.pack(side=tk.LEFT)

        self._canvasDeflectedShape = tk.Canvas(self._canvasFrame, bg="#DEE7EF", height=round(self._windowHeight*0.82), width=round(self._windowWidth*0.65))
        self._canvasReactionForce = tk.Canvas(self._canvasFrame, bg="#DEE7EF", height=round(self._windowHeight*0.82), width=round(self._windowWidth*0.65))
        self._canvasAxialLoad = tk.Canvas(self._canvasFrame, bg="#DEE7EF", height=round(self._windowHeight*0.82), width=round(self._windowWidth*0.65))
        self._canvasShearForce = tk.Canvas(self._canvasFrame, bg="#DEE7EF", height=round(self._windowHeight*0.82), width=round(self._windowWidth*0.65))
        self._canvasBendingMoment = tk.Canvas(self._canvasFrame, bg="#DEE7EF", height=round(self._windowHeight*0.82), width=round(self._windowWidth*0.65))

        self._canvasDisplay = tk.Text(self._canvasFrame, bg="#2B2B2B", fg="#BBBBBB", pady=5, padx=5, font=("Arial", 15),
                                      spacing3=10)

        scrollbar = tk.Scrollbar(self._canvasFrame, orient='vertical', command=self._canvasDisplay.yview)
        self._canvasDisplay['yscrollcommand'] = scrollbar.set

        self._canvasDisplay.pack(side=tk.LEFT, fill=tk.BOTH)

        self._addNodeButton = tk.Label(self._master, text="Add Node",fg="#BBBBBB", bg="#2B2B2B")
        self._addNodeButton.bind("<Button-1>", lambda event:self.addNode())
        self._addNodeButton.place(anchor="sw", x=5, rely=0.99)

        self._addMemberButton = tk.Label(self._master, text="Add Member",fg="#BBBBBB", bg="#2B2B2B")
        self._addMemberButton.bind("<Button-1>", lambda event:self.addMember())
        self._addMemberButton.place(anchor="sw", x=80, rely=0.99)

        self._analyseButton = tk.Label(self._master, text="Analyse", fg="#BBBBBB", bg="#2B2B2B", font=("Arial", 18))
        self._analyseButton.bind("<Button-1>", lambda event:self.analyseStructure())
        self._analyseButton.place(anchor="sw", x=round(self._windowWidth*0.65)-78, rely=0.99)

        self._addPointLoadButton = tk.Label(self._master, text="Add Nodal Load",fg="#BBBBBB", bg="#2B2B2B")
        self._addPointLoadButton.bind("<Button-1>", lambda event:self.addNodalLoad())
        self._addPointLoadButton.place(anchor="sw", x=173, rely=0.99)

        self._addMemberPointLoadButton = tk.Label(self._master, text="Add Member Point Load",fg="#BBBBBB", bg="#2B2B2B")
        self._addMemberPointLoadButton.bind("<Button-1>", lambda event:self.addMemberPointLoad())
        self._addMemberPointLoadButton.place(anchor="sw", x=284, rely=0.99)

        self._addMemberUniformlyDistributedLoadButton = tk.Label(self._master, text="Add Uniformly Distributed Load", fg="#BBBBBB", bg="#2B2B2B")
        self._addMemberUniformlyDistributedLoadButton.bind("<Button-1>", lambda event:self.addMemberUniformlyDistributedLoad())
        self._addMemberUniformlyDistributedLoadButton.place(anchor="sw", x=445, rely=0.99)

        menubar = tk.Menu(self._master)
        self._master.config(menu=menubar)
        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=self.new)
        filemenu.add_command(label="Open", command=self.open)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_command(label="Save As", command=self.saveAs)
        filemenu.add_command(label="Quit", command= lambda : self._master.destroy())

        filemenu2 = tk.Menu(menubar)
        menubar.add_cascade(label="Structure", menu=filemenu2)
        filemenu2.add_command(label="Add Node", command= self.addNode)
        filemenu2.add_command(label="Add Member", command=self.addMember)

        filemenu3 = tk.Menu(menubar)
        menubar.add_cascade(label="Load", menu=filemenu3)
        filemenu3.add_command(label="Add Nodal Load", command=self.addNodalLoad)
        filemenu3.add_command(label="Add Member Point Load", command=self.addMemberPointLoad)
        filemenu3.add_command(label="Add Uniformly Distributed Load", command=self.addMemberUniformlyDistributedLoad)

        filemenu4 = tk.Menu(menubar)
        menubar.add_cascade(label="Analysis", menu=filemenu4)
        filemenu4.add_command(label="Linear Analysis", command=self.analyseStructure)
        filemenu4.add_command(label="Generate Results", command=self.generatePdfResult)

        filemenu5 = tk.Menu(menubar)
        menubar.add_cascade(label="Settings", menu=filemenu5)
        filemenu5.add_command(label="Unit")
        filemenu5.add_command(label="Decimal Place")
        filemenu5.add_command(label="Diagram Step")

        self._matrixCalculator = MatrixCalculation()

        self._deflectedShapeLabel = tk.Label(self._canvasFrame, text="Deflected Shape", fg="#BBBBBB", bg="#2B2B2B", width=12)
        self._deflectedShapeLabel.bind("<Button-1>", lambda event:self.clickResultLabel(event, 1))
        self._reactionForceLabel = tk.Label(self._canvasFrame, text="Reaction Force", fg="#BBBBBB", bg="#2B2B2B", width=11)
        self._reactionForceLabel.bind("<Button-1>", lambda event:self.clickResultLabel(event, 2))
        self._axialLoadLabel = tk.Label(self._canvasFrame, text="Axial Load", fg="#BBBBBB", bg="#2B2B2B", width=8)
        self._axialLoadLabel.bind("<Button-1>", lambda event:self.clickResultLabel(event, 3))
        self._shearForceLabel = tk.Label(self._canvasFrame, text="Shear Force", fg="#BBBBBB", bg="#2B2B2B", width=9)
        self._shearForceLabel.bind("<Button-1>", lambda event:self.clickResultLabel(event, 4))
        self._bendingMomentLabel = tk.Label(self._canvasFrame, text="Bending Moment", fg="#BBBBBB", bg="#2B2B2B", width=12)
        self._bendingMomentLabel.bind("<Button-1>", lambda event:self.clickResultLabel(event, 5))
        self._selectedLabel = 0

        self.new()
        self.showResultLabel()


    def singularityFunction(self, x, a):
        """
        Determination of the singularity for the point load diagram
        """
        if a > x:
            return 0
        else:
            return 1

    def singularityFunctionForBending(self, x, a):
        """
        Determination of the singularity for the bending diagram
        """
        if a >= x:
            return 0
        else:
            return x-a


    def createGraph(self, canvas, originalStructure, deflectedStructure=None, reactionForce=None, axialLoad=None,
                    shearForce=None, bendingMoment=None):
        """
        Generating the result diagram

        :param canvas: canvas instance
        :param originalStructure: the structure instance that user created
        :param deflectedStructure: the deflected structure which was affected by the applied loading
        :param reactionForce: reactional force of the support
        :param axialLoad: axial force in the member
        :param shearForce: shear force in the member
        :param bendingMoment: bending moment in the member
        """
        self.drawGridLine(canvas)

        # Draw the axial direction for x-axis and y-axis
        canvas.create_line([(30, 860), (100, 860)], width=2, fill="#716FB0")
        canvas.create_line([(100, 860), (95, 855)], width=2, fill="#716FB0")
        canvas.create_line([(100, 860), (95, 865)], width=2, fill="#716FB0")
        canvas.create_line([(30, 860), (30, 790)], width=2, fill="#716FB0")
        canvas.create_line([(30, 790), (35, 795)], width=2, fill="#716FB0")
        canvas.create_line([(30, 790), (25, 795)], width=2, fill="#716FB0")

        # Draw the axial label for x-axis and y-axis
        canvas.create_text(105, 860, text="x", fill="#716FB0", width=2)
        canvas.create_text(30, 780, text="y", fill="#716FB0", width=2)

        # Draw the nodes
        nodes = originalStructure["node"].copy()
        for data in nodes:
            self.createNode(data[0], data[1],data[2], data[3], data[4], False, canvas)

        # Draw the members
        members = originalStructure["member"].copy()
        for data in members:
            self.createMember(data[0], data[1],data[2], data[3], data[4], data[5], data[6], False, canvas)

        # Draw the deflected structure if there is one
        if deflectedStructure != None:
            for node in deflectedStructure["node"].copy():
                self.createSimpleNode(node[1], node[2], canvas)
                if len(node) > 3:
                    deltaY = 15
                    for labelIndex in range(3,len(node)):
                        deltaY = deltaY + 15
                        canvas.create_text((node[1]/self._scaling + self._origin[0]), (self._origin[1] - node[2]/self._scaling) - deltaY, text=node[labelIndex], fill="#953BCB", font=("Arial", 10))

            for member in deflectedStructure["member"].copy():
                for node in deflectedStructure["node"].copy():
                    if node[0] == member[0]:
                        xi = node[1]
                        yi = node[2]
                    if node[0] == member[1]:
                        xj = node[1]
                        yj = node[2]
                self.createSimpleMember(xi,yi,xj,yj, canvas)

        # Draw the reaction forces
        if reactionForce != None:
            for data in reactionForce:
                self.createNodalLoad(data[0], data[1],data[2], data[3], False, canvas)

        # Draw the axial forces
        if axialLoad != None:
            for data in axialLoad:
                midX, midY = self.calculatePosition((data[0], data[1]), (data[2],data[3]), data[5]/2)
                vector = [[data[2]-midX,],
                          [data[3]-midY,]]
                rotation = [[math.cos(math.pi/2), math.sin(math.pi/2)],
                            [-math.sin(math.pi/2), math.cos(math.pi/2)]]
                vector = self._matrixCalculator.matrixMultiplication(rotation, vector)
                magnitude = math.sqrt(vector[0][0]**2 + vector[1][0]**2)
                vector = self._matrixCalculator.matrixScale(vector, 1/magnitude)
                vector = self._matrixCalculator.matrixScale(vector, 360)
                positionX = vector[0][0] + midX
                positionY =vector[1][0] + midY
                axialForce = data[4]
                if self._unit[0] == "kN":
                    axialForce = axialForce/1000

                axialForce = round(axialForce, self._unit[2])

                axialForceType = ""
                if axialForce < 0:
                    axialForceType = " (C)"
                elif axialForce > 0:
                    axialForceType = " (T)"

                canvas.create_text((positionX/self._scaling + self._origin[0]), (self._origin[1] - positionY/self._scaling), text=str(axialForce)+" "+self._unit[0]+axialForceType,
                                   fill="#953BCB", font=("Arial", 13))

        # Draw the shear forces
        if shearForce != None:
            shearMax = 0
            for memberShearData in shearForce:
                for member in self._structure.getMembers():
                    if member.getId() == memberShearData["id"]:
                        drawingMember = member

                for x in range(0, round(drawingMember.getL())+1, 10):
                    shear = 0
                    if len(memberShearData["pointLoad"]) != 0:
                        for pointData in memberShearData["pointLoad"].copy():
                            shear = shear + self.singularityFunction(x,pointData[0])*pointData[1]
                    if len(memberShearData["uniformlyDistributedLoad"]) != 0:
                        for w in memberShearData["uniformlyDistributedLoad"].copy():
                            shear = shear + w*x
                    if abs(shear) > shearMax:
                        shearMax = abs(shear)

            lastPoint = None
            shearNum = 0
            for memberShearData in shearForce:
                for member in self._structure.getMembers():
                    if member.getId() == memberShearData["id"]:
                        drawingMember = member
                if drawingMember.getType() == "frame":
                    lastPoint = None

                x_axis = drawingMember.get_x_Axis()
                y_axis = drawingMember.get_y_Axis()

                x_axis = self._matrixCalculator.matrixScale(x_axis, 1/math.sqrt(x_axis[0][0]**2+x_axis[1][0]**2))
                y_axis = self._matrixCalculator.matrixScale(y_axis, 1/math.sqrt(y_axis[0][0]**2+y_axis[1][0]**2))

                for nodeData in self._structure.getNodes():
                    if nodeData.getID() == drawingMember.geti():
                        xi = nodeData.getx()
                        yi = nodeData.gety()
                    if nodeData.getID() == drawingMember.getj():
                        xj = nodeData.getx()
                        yj = nodeData.gety()

                if self._structure.vectorsBeamCheckSign(x_axis, [[1,],[0,]]) == False and drawingMember.getType() == "beam":
                    x_axis = self._matrixCalculator.matrixScale(x_axis, 1)
                    y_axis = self._matrixCalculator.matrixScale(y_axis, -1)
                    lastPoint = None

                if lastPoint == None:
                    lastPoint = (xi, yi)

                for x in range(0, round(drawingMember.getL())+1, 10):
                    shearNum = shearNum + 1
                    tag = "shear" + str(shearNum)
                    shear = 0
                    if len(memberShearData["pointLoad"]) != 0:
                        for pointData in memberShearData["pointLoad"].copy():
                            shear = shear + self.singularityFunction(x,pointData[0])*pointData[1]
                    if len(memberShearData["uniformlyDistributedLoad"]) != 0:
                        for w in memberShearData["uniformlyDistributedLoad"].copy():
                            shear = shear + w*x

                    x_axis_Vector = self._matrixCalculator.matrixScale(x_axis, x)
                    y_axis_Vector = self._matrixCalculator.matrixScale(y_axis, 85*self._scaling*shear/shearMax)

                    axis_Vector = self._matrixCalculator.matrixAddition(x_axis_Vector, "+", y_axis_Vector)

                    shearX = xi + axis_Vector[0][0]
                    shearY = yi + axis_Vector[1][0]

                    shearX = shearX/self._scaling+ self._origin[0]
                    shearY = self._origin[1] - shearY/self._scaling

                    canvas.create_oval([(shearX-1, shearY-1), (shearX +1, shearY +1)], outline="blue", tag=tag)
                    canvas.tag_bind(tag, "<Enter>", lambda e, x_value=x, shearValue=shear: self.updateMagnitude(canvas, x_value, shearValue, "Shear Force"))
                    canvas.tag_bind(tag, "<Leave>", lambda e: self.deleteMagnitude(canvas))

                    shearLastX = lastPoint[0]/self._scaling+ self._origin[0]
                    shearLastY = self._origin[1] - lastPoint[1]/self._scaling

                    shearMemberX = (shearX-self._origin[0])*self._scaling
                    shearMemberY = (self._origin[1] - shearY)*self._scaling

                    canvas.create_line([(shearX,shearY), (shearLastX, shearLastY)], fill='blue', width=2)

                    if self._unit[0] == "kN":
                        shear = shear/1000

                    shear = round(shear, self._unit[2])

                    if x == round(drawingMember.getL()):
                        jPointX = xj/self._scaling + self._origin[0]
                        jPointY = self._origin[1] - yj/self._scaling
                        canvas.create_line([(shearX,shearY), (jPointX, jPointY)], fill='blue', width=2)

                    if x == 0 or x == round(drawingMember.getL()):
                        shearMagnitudeVector = [[shearMemberX-y_axis_Vector[0][0]],
                                                [shearMemberY-y_axis_Vector[1][0]]]
                        yshearMagnitudeVector = self._matrixCalculator.matrixScale(y_axis_Vector, 1.2)
                        shearMagnitudeX1, shearMagnitudeY1 = (shearMagnitudeVector[0][0]+yshearMagnitudeVector[0][0], shearMagnitudeVector[1][0]+yshearMagnitudeVector[1][0])
                        canvas.create_text(shearMagnitudeX1/self._scaling+self._origin[0], self._origin[1]-shearMagnitudeY1/self._scaling, text=str(shear) + " " + self._unit[0], fill="blue")

                    lastPoint = (shearMemberX, shearMemberY, shear)

        # Draw the bending moments
        if bendingMoment != None:

            bendingMax = 0
            for memberBendingData in bendingMoment:
                for member in self._structure.getMembers():
                    if member.getId() == memberBendingData["id"]:
                        drawingMember = member

                for x in range(0, round(drawingMember.getL())+1, 10):
                    bending = 0
                    if len(memberBendingData["pointLoad"]) != 0:
                        for pointData in memberBendingData["pointLoad"].copy():
                            if x <= pointData[0]:
                                bending = bending + (-pointData[1])*x*(drawingMember.getL()-pointData[0])/drawingMember.getL()
                            elif x > pointData[0]:
                                bending = bending + (-pointData[1])*(drawingMember.getL()-x)*pointData[0]/drawingMember.getL()
                    if len(memberBendingData["uniformlyDistributedLoad"]) != 0:
                        for w in memberBendingData["uniformlyDistributedLoad"].copy():
                            bending = bending + (-w/2)*(x**2) + ((w*drawingMember.getL())/2)*x
                    if len(memberBendingData["pointMoment"]) != 0:
                        for pointData in memberBendingData["pointMoment"].copy():
                            if pointData[0] == 0:
                                bending = bending + (pointData[1]/drawingMember.getL())*(drawingMember.getL()-x)
                            elif pointData[0] == round(drawingMember.getL()):
                                bending = bending + (pointData[1]*x)/drawingMember.getL()
                    if abs(bending) > bendingMax:
                        bendingMax = abs(bending)

            lastPoint = None
            bendingNum = 0
            for memberBendingData in bendingMoment:
                for member in self._structure.getMembers():
                    if member.getId() == memberBendingData["id"]:
                        drawingMember = member
                if drawingMember.getType() == "frame":
                    lastPoint = None

                x_axis = drawingMember.get_x_Axis()
                y_axis = drawingMember.get_y_Axis()

                x_axis = self._matrixCalculator.matrixScale(x_axis, 1/math.sqrt(x_axis[0][0]**2+x_axis[1][0]**2))
                y_axis = self._matrixCalculator.matrixScale(y_axis, 1/math.sqrt(y_axis[0][0]**2+y_axis[1][0]**2))

                for nodeData in self._structure.getNodes():
                    if nodeData.getID() == drawingMember.geti():
                        xi = nodeData.getx()
                        yi = nodeData.gety()
                    if nodeData.getID() == drawingMember.getj():
                        xj = nodeData.getx()
                        yj = nodeData.gety()

                if self._structure.vectorsBeamCheckSign(x_axis, [[1,],[0,]]) == False and drawingMember.getType() == "beam":
                    x_axis = self._matrixCalculator.matrixScale(x_axis, -1)
                    y_axis = self._matrixCalculator.matrixScale(y_axis, -1)
                    xi = xj
                    yi = yj

                    momentList = memberBendingData["pointMoment"].copy()
                    for momentMagnitude in momentList:
                        if momentMagnitude[0] == 0:
                            momentMagnitude[0] =round(drawingMember.getL())
                        if momentMagnitude[0] == round(drawingMember.getL()):
                            momentMagnitude[0] = 0
                        momentMagnitude[1] = momentMagnitude[1]*(-1)
                    memberBendingData["pointMoment"] = momentList

                if lastPoint == None:
                    lastPoint = (xi, yi)

                for x in range(0, round(drawingMember.getL())+1, 10):
                    bendingNum = bendingNum + 1
                    tag = "bending" + str(bendingNum)
                    bending = 0
                    if len(memberBendingData["pointLoad"]) != 0:
                        for pointData in memberBendingData["pointLoad"].copy():
                            if x <= pointData[0]:
                                bending = bending + (pointData[1])*x*(drawingMember.getL()-pointData[0])/drawingMember.getL()
                            elif x > pointData[0]:
                                bending = bending + (pointData[1])*(drawingMember.getL()-x)*pointData[0]/drawingMember.getL()

                    if len(memberBendingData["uniformlyDistributedLoad"]) != 0:
                        for w in memberBendingData["uniformlyDistributedLoad"].copy():
                            bending = bending + (-w/2)*(x**2) + ((w*drawingMember.getL())/2)*x
                    if len(memberBendingData["pointMoment"]) != 0:
                        for pointData in memberBendingData["pointMoment"].copy():
                            if pointData[0] == 0:
                                bending = bending + (-pointData[1]/drawingMember.getL())*(drawingMember.getL()-x)
                            elif pointData[0] == round(drawingMember.getL()):
                                bending = bending + (-pointData[1]*x)/drawingMember.getL()

                    x_axis_Vector = self._matrixCalculator.matrixScale(x_axis, x)
                    y_axis_Vector = self._matrixCalculator.matrixScale(y_axis, 85*self._scaling*bending/bendingMax)

                    axis_Vector = self._matrixCalculator.matrixAddition(x_axis_Vector, "+", y_axis_Vector)

                    bendingX = xi + axis_Vector[0][0]
                    bendingY = yi + axis_Vector[1][0]

                    bendingX = bendingX/self._scaling+ self._origin[0]
                    bendingY = self._origin[1] - bendingY/self._scaling

                    canvas.create_oval([(bendingX-1, bendingY-1), (bendingX +1, bendingY +1)], outline="red", tag=tag)
                    canvas.tag_bind(tag, "<Enter>", lambda e, x_value=x, bendingValue=bending: self.updateMagnitude(canvas, x_value, -bendingValue, "Bending Moment"))
                    canvas.tag_bind(tag, "<Leave>", lambda e: self.deleteMagnitude(canvas))

                    bendingLastX = lastPoint[0]/self._scaling+ self._origin[0]
                    bendingLastY = self._origin[1] - lastPoint[1]/self._scaling

                    bendingMemberX = (bendingX-self._origin[0])*self._scaling
                    bendingMemberY = (self._origin[1] - bendingY)*self._scaling

                    canvas.create_line([(bendingX,bendingY), (bendingLastX, bendingLastY)], fill='red', width=2)

                    if self._unit[0] == "kN":
                        bending = bending/1000
                    if self._unit[1] == "m":
                        bending = bending/1000

                    bending = round(bending, self._unit[2])

                    if x == round(drawingMember.getL()):
                        jPointX = xj/self._scaling + self._origin[0]
                        jPointY = self._origin[1] - yj/self._scaling
                        canvas.create_line([(bendingX,bendingY), (jPointX, jPointY)], fill='red', width=2)

                    if x == 0 or x == round(drawingMember.getL()):
                        bendingMagnitudeVector = [[bendingMemberX-y_axis_Vector[0][0]],
                                                [bendingMemberY-y_axis_Vector[1][0]]]
                        yBendingMagnitudeVector = self._matrixCalculator.matrixScale(y_axis_Vector, 1.2)
                        bendingMagnitudeX1, bendingMagnitudeY1 = (yBendingMagnitudeVector[0][0]+bendingMagnitudeVector[0][0]
                                                                  , yBendingMagnitudeVector[1][0]+bendingMagnitudeVector[1][0])
                        canvas.create_text(bendingMagnitudeX1/self._scaling+self._origin[0], self._origin[1]-bendingMagnitudeY1/self._scaling, text=str(-bending) + " " + self._unit[0]+self._unit[1], fill="red")

                    lastPoint = (bendingMemberX, bendingMemberY, bending)


    def createSimpleNode(self, nodeX, nodeY, canvas):
        """
        Generate the node in the canvas

        :param nodeX: x coordinate
        :param nodeY: y coordinate
        :param canvas: canvas of iStruct2D
        """
        x = nodeX/self._scaling+ self._origin[0]
        y = self._origin[1] - nodeY/self._scaling
        canvas.create_oval([(x-2.5, y-2.5), (x +2.5, y +2.5)], fill='red')


    def createSimpleMember(self, nodeiX, nodeiY, nodejX, nodejY,canvas):
        """
        Generate the member in the canvas

        :param nodeiX: x coordinate of starting node
        :param nodeiY: y coordinate of starting node
        :param nodejX: x coordinate of ending node
        :param nodejY: y coordinate of ending node
        :param canvas: canvas of iStruct2D
        """
        xi = nodeiX/self._scaling+ self._origin[0]
        yi = self._origin[1] - nodeiY/self._scaling

        xj = nodejX/self._scaling+ self._origin[0]
        yj = self._origin[1] - nodejY/self._scaling
        canvas.create_line([(xi, yi), (xj, yj)], fill='red')


    def showResultLabel(self):
        """
        Draw the result label in the canvas
        """
        self._deflectedShapeLabel.place(anchor="nw", x=3, rely=0.002)
        self._reactionForceLabel.place(anchor="nw", x=120, rely=0.002)
        self._axialLoadLabel.place(anchor="nw", x=228, rely=0.002)
        self._shearForceLabel.place(anchor="nw", x=309, rely=0.002)
        self._bendingMomentLabel.place(anchor="nw", x=399, rely=0.002)


    def clickResultLabel(self, e, id):
        """
        Handle the event when the specific result is clicked

        :param e: event
        :param id: id of the label
        """
        self.hideAllCanvas()

        if self._selectedLabel == id or id == -1:
            self._selectedLabel = 0
            self._deflectedShapeLabel.config(bg="#2B2B2B")
            self._reactionForceLabel.config(bg="#2B2B2B")
            self._axialLoadLabel.config(bg="#2B2B2B")
            self._shearForceLabel.config(bg="#2B2B2B")
            self._bendingMomentLabel.config(bg="#2B2B2B")
            self._deflectedShapeLabel.config(bd=2)
            self._reactionForceLabel.config(bd=2)
            self._axialLoadLabel.config(bd=2)
            self._shearForceLabel.config(bd=2)
            self._bendingMomentLabel.config(bd=2)
            self.showCanvas(self._canvas)

        else:
            self._selectedLabel = id
            self._deflectedShapeLabel.config(bg="#2B2B2B")
            self._reactionForceLabel.config(bg="#2B2B2B")
            self._axialLoadLabel.config(bg="#2B2B2B")
            self._shearForceLabel.config(bg="#2B2B2B")
            self._bendingMomentLabel.config(bg="#2B2B2B")
            self._deflectedShapeLabel.config(bd=2)
            self._reactionForceLabel.config(bd=2)
            self._axialLoadLabel.config(bd=2)
            self._shearForceLabel.config(bd=2)
            self._bendingMomentLabel.config(bd=2)
            self.hideResultLabel()

            if id == 1:
                self.showCanvas(self._canvasDeflectedShape)
                self._deflectedShapeLabel.config(bg="#4D5254")
                self._deflectedShapeLabel.config(bd=3)
            elif id == 2:
                self.showCanvas(self._canvasReactionForce)
                self._reactionForceLabel.config(bg="#4D5254")
                self._reactionForceLabel.config(bd=3)
            elif id == 3:
                self.showCanvas(self._canvasAxialLoad)
                self._axialLoadLabel.config(bg="#4D5254")
                self._axialLoadLabel.config(bd=3)
            elif id == 4:
                self.showCanvas(self._canvasShearForce)
                self._shearForceLabel.config(bg="#4D5254")
                self._shearForceLabel.config(bd=3)
                self._labelMessage = self._canvasShearForce.create_text(round(self._windowWidth*0.65)-150, 15, text="", fill="#8A2F19")
            elif id == 5:
                self.showCanvas(self._canvasBendingMoment)
                self._bendingMomentLabel.config(bg="#4D5254")
                self._bendingMomentLabel.config(bd=3)
                self._labelMessage = self._canvasBendingMoment.create_text(round(self._windowWidth*0.65)-150, 15, text="", fill="#8A2F19")
            self.showResultLabel()


    def new(self):
        """
        Reset the environment of iStruct2D
        """
        self._moving = False
        self._unit = ["N","mm",2]
        self._filename = None
        self._analysisTime = 0
        self._structure = Structure()
        self._structureData = {"node":[], "member":[], "nodalLoad":[], "memberPointLoad":[], "uniformlyDistributedLoad":[]}
        self._structureDrawingData = {"node":[], "member":[]}
        self._canvas.delete("all")
        self.clearAllCanvas()
        self._master.title("iStruct2D")
        self.clearAllData()
        self.drawGridLine(self._canvas)
        self.drawGridLine(self._canvasDeflectedShape)
        self.drawGridLine(self._canvasReactionForce)
        self.drawGridLine(self._canvasAxialLoad)
        self.drawGridLine(self._canvasShearForce)
        self.drawGridLine(self._canvasBendingMoment)
        self.displayData("iStruct2D is ready\n")
        self.displayData("Tips:\n" + " Change the unit before adding any element\n" +
                         " Change the scaling before adding any element\n" +
                         " Hold and drag to change the Origin position\n")
        self._canvas.create_line([(30, 860), (100, 860)], width=2, fill="#716FB0")
        self._canvas.create_line([(100, 860), (95, 855)], width=2, fill="#716FB0")
        self._canvas.create_line([(100, 860), (95, 865)], width=2, fill="#716FB0")
        self._canvas.create_line([(30, 860), (30, 790)], width=2, fill="#716FB0")
        self._canvas.create_line([(30, 790), (35, 795)], width=2, fill="#716FB0")
        self._canvas.create_line([(30, 790), (25, 795)], width=2, fill="#716FB0")

        self._canvas.create_text(105, 860, text="x", fill="#716FB0", width=2)
        self._canvas.create_text(30, 780, text="y", fill="#716FB0", width=2)

        self._label = self._canvas.create_text(round(self._windowWidth*0.65)-150, 15, text="number of Node: 0      number of Member: 0", fill="#8A2F19")

        # show origin (0,0) --> (100, 800)
        self._origin = [100, 800]
        self._originLine1 = self._canvas.create_line([(self._origin[0]+5, self._origin[1]-5), (self._origin[0]-5, self._origin[1]+5)], width=1, fill="#8A2F19", tag="originLine1")
        self._originLine2 = self._canvas.create_line([(self._origin[0]-5, self._origin[1]-5), (self._origin[0]+5, self._origin[1]+5)], width=1, fill="#8A2F19", tag="originLine2")
        self._originPoint = self._canvas.create_oval([(self._origin[0]-2, self._origin[1]-2), (self._origin[0]+2, self._origin[1]+2)], width=1, fill="#8A2F19", tag="originPoint")

        self._originText = self._canvas.create_text(self._origin[0]-25, self._origin[1]+20, text="Origin", fill="#8A2F19", tag="originText")

        self._canvas.tag_bind("originLine1", "<Button-1>", self.moveOrigin1)
        self._canvas.tag_bind("originLine2", "<Button-1>", self.moveOrigin1)
        self._canvas.tag_bind("originPoint", "<Button-1>", self.moveOrigin1)

        self.hideAllCanvas()
        self.clickResultLabel(None, -1)

        self._unitButtonFBG = self._canvas.create_rectangle(round(self._windowWidth*0.65)-243, round(self._windowHeight*0.82)*0.959,
                                                            round(self._windowWidth*0.65)-243+70, round(self._windowHeight*0.82)*0.959+28, fill="#2B2B2B", tag="unitF")

        self._unitButtonFText = self._canvas.create_text(round(self._windowWidth*0.65)-208, round(self._windowHeight*0.82)*0.975,
                                                     text="N    kN", fill="#BBBBBB", font=("Arial", 18), tag="unitF")

        self._unitButtonMBG = self._canvas.create_rectangle(round(self._windowWidth*0.65)-165, round(self._windowHeight*0.82)*0.959,
                                                            round(self._windowWidth*0.65)-165+75, round(self._windowHeight*0.82)*0.959+28, fill="#2B2B2B", tag="unitM")

        self._unitButtonFText = self._canvas.create_text(round(self._windowWidth*0.65)-128, round(self._windowHeight*0.82)*0.975,
                                                         text="mm   m", fill="#BBBBBB", font=("Arial", 18), tag="unitM")

        self._unitButtonCover1 = self._canvas.create_rectangle(round(self._windowWidth*0.65)-209, round(self._windowHeight*0.82)*0.96455,
                                                               round(self._windowWidth*0.65)-209+35, round(self._windowHeight*0.82)*0.96455+18, fill="#5E6468", width=0, tag="unitF")
        self._unitButtonCover2 = self._canvas.create_rectangle(round(self._windowWidth*0.65)-125, round(self._windowHeight*0.82)*0.96455,
                                                               round(self._windowWidth*0.65)-125+35, round(self._windowHeight*0.82)*0.96455+18, fill="#5E6468", width=0, tag="unitM")
        self._canvas.tag_bind("unitF", "<Button-1>", lambda e: self.unitChange("forceUnit"))
        self._canvas.tag_bind("unitM", "<Button-1>", lambda e: self.unitChange("distanceUnit"))
        self.updateUnit()

        self._movingScalingBar = False
        self._scalingLine = self._canvas.create_line([(680, round(self._windowHeight*0.82)*0.985), (880, round(self._windowHeight*0.82)*0.985)], width=2, fill="#2B2B2B", tag="scalingLineButtonLine")
        self._scalingLineButton = self._canvas.create_rectangle(680, round(self._windowHeight*0.82)*0.985-5,
                                                                680+5, round(self._windowHeight*0.82)*0.985+5, fill="#2B2B2B", tag="scalingLineButton")
        self._canvas.tag_bind("scalingLineButton", "<Button-1>", lambda e: self.moveScalingBar())
        self._canvas.tag_bind("scalingLineButtonLine", "<Button-1>", lambda e: self.moveScalingBar())

        self._scalingSizeLine1 = self._canvas.create_line([(770, round(self._windowHeight*0.82)*0.97), (770 + 100, round(self._windowHeight*0.82)*0.97)], width=2, fill="#5D6468")
        self._scalingSizeLine2 = self._canvas.create_line([(770, round(self._windowHeight*0.82)*0.97), (770, round(self._windowHeight*0.82)*0.97 -8)], width=2, fill="#5D6468")
        self._scalingSizeLine3 = self._canvas.create_line([(770 + 100, round(self._windowHeight*0.82)*0.97), (770 + 100, round(self._windowHeight*0.82)*0.97 -8)], width=2, fill="#5D6468")
        self._scaling = 30
        self._scalingText = self._canvas.create_text(717, round(self._windowHeight*0.82)*0.965,
                                                         text="1000 [mm] / 1 [m]", fill="#5D6468", font=("Arial", 12))
        self.scalingBarUpdate2()
        self._master.update()


    def scalingBarUpdate(self, e):
        """
        Update the value of the scaling bar
        :param e: event
        """
        x = e.x
        if e.x < 680:
            x = 680
        if e.x > 875:
            x = 874
        scalingLength = x*(85/194) + (15-680*85/194)
        self._scaling = 1000/scalingLength
        self.scalingBarUpdate2(x=x)


    def scalingBarUpdate2(self, x=None):
        """
        Draw the scaling bar

        :param x: position of the pin on the scaling bar
        """
        self._canvas.delete(self._scalingLineButton)
        self._canvas.delete(self._scalingSizeLine1)
        self._canvas.delete(self._scalingSizeLine2)
        self._canvas.delete(self._scalingSizeLine3)

        if x == None:
            x = (1000/self._scaling - (15-680*85/194))*(194/85)

        self._scalingLineButton = self._canvas.create_rectangle(x, round(self._windowHeight*0.82)*0.985-5,
                                                                x+5, round(self._windowHeight*0.82)*0.985+5, fill="#2B2B2B", tag="scalingLineButton")

        self._scalingSizeLine1 = self._canvas.create_line([(770, round(self._windowHeight*0.82)*0.97), (770 + 1000/self._scaling, round(self._windowHeight*0.82)*0.97)], width=2, fill="#5D6468")
        self._scalingSizeLine2 = self._canvas.create_line([(770, round(self._windowHeight*0.82)*0.97), (770, round(self._windowHeight*0.82)*0.97 -8)], width=2, fill="#5D6468")
        self._scalingSizeLine3 = self._canvas.create_line([(770 + 1000/self._scaling, round(self._windowHeight*0.82)*0.97), (770 + 1000/self._scaling, round(self._windowHeight*0.82)*0.97 -8)], width=2, fill="#5D6468")


    def moveScalingBar(self):
        """
        Update the scaling bar status for moving
        """
        if self._structure.getNodeNum() == 0:
            if self._movingScalingBar:
                self._movingScalingBar = False
            elif self._movingScalingBar == False:
                self._movingScalingBar = True

            if self._movingScalingBar:
                self._canvas.bind("<Motion>", self.scalingBarUpdate)
                #self._canvas.bind("<Button-1>", lambda e: self.moveScalingBar())
            else:
                self._canvas.unbind("<Motion>")
                #self._canvas.unbind("<Button-1>")
        else:
            self.displayData("Error Message:\n" + "Scaling cannot be changed after added any element\n")


    def unitChange(self, type):
        """
        Set the unit of the measurement

        :param type: type of the unit that want to change
        """
        if self._structure.getNodeNum() == 0:
            if type == "forceUnit":
                if self._unit[0] == "kN":
                    self._unit[0] = "N"
                elif self._unit[0] == "N":
                    self._unit[0] = "kN"

            elif type == "distanceUnit":
                if self._unit[1] == "m":
                    self._unit[1] = "mm"
                elif self._unit[1] == "mm":
                    self._unit[1] = "m"

            self.updateUnit()

        else:
            self.displayData("Error Message:\n" + "Unit cannot be changed after added any element\n")


    def updateUnit(self):
        """
        Update the value of the unit
        """
        self._canvas.delete(self._unitButtonCover1)
        self._canvas.delete(self._unitButtonCover2)

        if self._unit[0] == "kN":
            distance1 = 237
        elif self._unit[0] == "N":
            distance1 = 209

        if self._unit[1] == "m":
            distance2 = 159
        elif self._unit[1] == "mm":
            distance2 = 125

        self._unitButtonCover1 = self._canvas.create_rectangle(round(self._windowWidth*0.65)-distance1, round(self._windowHeight*0.82)*0.96455,
                                                                round(self._windowWidth*0.65)-distance1+30, round(self._windowHeight*0.82)*0.96455+18, fill="#5E6468", width=0, tag="unitF")
        self._unitButtonCover2 = self._canvas.create_rectangle(round(self._windowWidth*0.65)-distance2, round(self._windowHeight*0.82)*0.96455,
                                                               round(self._windowWidth*0.65)-distance2+30, round(self._windowHeight*0.82)*0.96455+18, fill="#5E6468", width=0, tag="unitM")


    def moveOrigin1(self, e):
        """
        Update the status of the origin for moving

        :param e: event of the action
        """
        if self._structure.getNodeNum() == 0:
            if self._moving:
                self._moving = False
            elif self._moving == False:
                self._moving = True

            if self._moving:
                self._canvas.bind("<Motion>", self.moveOrigin2)
            else:
                self._canvas.unbind("<Motion>")
        else:
            self.displayData("Error Message:\n" + "Origin cannot be changed after added any element\n")


    def moveOrigin2(self, e):
        """
        Update the origin coordinate

        :param e: event of the action
        """
        self._origin = [e.x, e.y]
        self.updateOrigin()


    def updateOrigin(self):
        """
        Draw the origin point
        """
        self._canvas.delete(self._originLine1)
        self._canvas.delete(self._originLine2)
        self._canvas.delete(self._originPoint)
        self._canvas.delete(self._originText)

        self._originLine1 = self._canvas.create_line([(self._origin[0]+5, self._origin[1]-5), (self._origin[0]-5, self._origin[1]+5)], width=1, fill="#8A2F19", tag="originLine1")
        self._originLine2 = self._canvas.create_line([(self._origin[0]-5, self._origin[1]-5), (self._origin[0]+5, self._origin[1]+5)], width=1, fill="#8A2F19", tag="originLine2")
        self._originPoint = self._canvas.create_oval([(self._origin[0]-2, self._origin[1]-2), (self._origin[0]+2, self._origin[1]+2)], width=1, fill="#8A2F19", tag="originPoint")

        self._originText = self._canvas.create_text(self._origin[0]-25, self._origin[1]+20, text="Origin", fill="#8A2F19", tag="originText")


    def drawGridLine(self, canvas):
        """
        Draw the gridline of the canvas

        :param canvas: canvas of iStruct2D
        """
        for x in range(0, round(self._windowWidth*0.65), 30):
            canvas.create_line([(x, 0), (x, self._windowHeight*0.82)], width=1, fill="#CBD1D9")
        for y in range(0, round(self._windowHeight*0.82), 30):
            canvas.create_line([(0, y), (self._windowWidth*0.65, y)], width=1, fill="#CBD1D9")


    def hideResultLabel(self):
        """
        Hide the result label
        """
        self._deflectedShapeLabel.place_forget()
        self._reactionForceLabel.place_forget()
        self._axialLoadLabel.place_forget()
        self._shearForceLabel.place_forget()
        self._bendingMomentLabel.place_forget()


    def hideAllCanvas(self):
        """
        Hide all the canvas from iStruct2D
        """
        self._canvas.pack_forget()
        self._canvasDeflectedShape.pack_forget()
        self._canvasReactionForce.pack_forget()
        self._canvasAxialLoad.pack_forget()
        self._canvasShearForce.pack_forget()
        self._canvasBendingMoment.pack_forget()


    def showCanvas(self, canvas):
        """
        Display the specific canvas

        :param canvas: canvas that want to be displayed
        """
        self._canvasDisplay.pack_forget()
        canvas.pack(side=tk.LEFT)
        self._canvasDisplay.pack(side=tk.LEFT, fill=tk.BOTH)


    def open(self):
        """
        Open and read the structure from .txt file
        """
        filename = filedialog.askopenfilename(title="Choosing File", initialdir=("exampleStructures/"))
        if filename:
            self.new()
            self._filename = filename.split("/")[-1].split(".")[0]
            self._master.title("iStruct2D: "+ self._filename)
            fd = open("exampleStructures/" + self._filename + ".txt", "r")

            line = fd.readline().strip("\n")
            origin = line.split(";")
            self._origin = [float(origin[0]), float(origin[1])]
            self.updateOrigin()

            line = fd.readline().strip("\n")
            unit = line.split(";")
            self._unit = [unit[0], unit[1], int(unit[2])]
            self.updateUnit()

            line = fd.readline().strip("\n")
            self._scaling = float(line)
            self.scalingBarUpdate2()

            line = fd.readline().strip("\n")

            type = None

            while line != "":
                if "#" in line:
                    type = line.strip("#")

                else:
                    if type == "node":
                        data = line.split(";")
                        self.createNode(data[0], data[1],data[2], data[3], data[4], True)
                    elif type == "member":
                        data = line.split(";")
                        self.createMember(data[0], data[1],data[2], data[3], data[4], data[5], data[6], True)
                    elif type == "nodalLoad":
                        data = line.split(";")
                        self.createNodalLoad(data[0], data[1],data[2], data[3], True)
                    elif type == "memberPointLoad":
                        data = line.split(";")
                        self.createMemberPointLoad(data[0], data[1],data[2], data[3])
                    elif type == "uniformlyDistributedLoad":
                        data = line.split(";")
                        self.createMemberUniformlyDistributedLoad(data[0], data[1])

                line = fd.readline().strip("\n")
            fd.close()
            self.displayData("Successfully open the structure\n" +
                             "    Filename: " + self._filename + ".txt\n")


    def save(self):
        """
        Save the structure into .txt file
        """
        if self._filename is None:
            filename = simpledialog.askstring("Saving the structure", "Structure name:")
            if filename:
                self._filename = filename

        if self._filename:
            self._master.title("iStruct2D: "+ self._filename)
            fd = open("exampleStructures/" + self._filename + ".txt", "w")

            result = "" + str(self._origin[0]) + ";" + str(self._origin[1]) + "\n"
            result = result + self._unit[0] + ";" + self._unit[1] + ";" + str(self._unit[2]) + "\n"
            result = result + str(self._scaling) + "\n"

            for key in self._structureData:
                result = result + "#"+key+"\n"
                for data in self._structureData[key]:
                    for info in data:
                        if info == None:
                            info = ""
                        result = result + str(info) + ";"
                    result = result[:-1]
                    result = result + "\n"

            fd.write(result)
            fd.close()
            self.displayData("Successfully saved the structure\n" +
                             "    Filename: " + self._filename + ".txt\n" +
                             "    Location: " + "exampleStructures/" + self._filename + ".txt\n")


    def saveAs(self):
        """
        Save the structure into .txt file at the selected location
        """
        filename = simpledialog.askstring("Saving the structure", "Structure name:")
        if filename:
            self._filename = filename

        if self._filename:
            self._master.title("iStruct2D: "+ self._filename)
            fd = open("exampleStructures/" + self._filename + ".txt", "w")

            result = "" + str(self._origin[0]) + ";" + str(self._origin[1]) + "\n"
            result = result + self._unit[0] + ";" + self._unit[1] + ";" + str(self._unit[2]) + "\n"
            result = result + str(self._scaling) + "\n"

            for key in self._structureData:
                result = result + "#"+key+"\n"
                for data in self._structureData[key]:
                    for info in data:
                        if info == None:
                            info = ""
                        result = result + str(info) + ";"
                    result = result[:-1]
                    result = result + "\n"

            fd.write(result)
            fd.close()
            self.displayData("Successfully saved the structure\n" +
                             "    Filename: " + self._filename + ".txt\n" +
                             "    Location: " + "exampleStructures/" + self._filename + ".txt\n")


    def clearAllData(self):
        """
        Clear the string data from the result center
        """
        self._canvasDisplay.config(state=NORMAL)
        self._canvasDisplay.delete("0.0", tk.END)
        self._canvasDisplay.config(state=DISABLED)


    def displayData(self, data):
        """
        Display the string data into the result center

        :param data: data string
        """
        self._canvasDisplay.config(state=NORMAL)
        self._canvasDisplay.insert(tk.END, "-> " + data + "\n")
        self._canvasDisplay.see(tk.END)
        self._canvasDisplay.config(state=DISABLED)


    def clearAllCanvas(self):
        """
        Delete all contents from all canvas
        """
        self._canvasDeflectedShape.delete("all")
        self._canvasReactionForce.delete("all")
        self._canvasAxialLoad.delete("all")
        self._canvasShearForce.delete("all")
        self._canvasBendingMoment.delete("all")


    def analyseStructure(self):
        """
        Analyse and get the results of the structure
        """
        self._structure.changeUnit(self._unit)

        deflectedShapeData = {"node":[], "member":[]}
        for node in self._structure.getNodes():
            deflectedShapeData['node'].append([node.getID(), node.getx(), node.gety()])
        for member in self._structure.getMembers():
            deflectedShapeData['member'].append([member.geti(), member.getj()])

        allResult = self._structure.packAllResult()
        result = allResult["nodalDisplacement"].copy()

        for data in result:
            if "u" in data[0]:
                nodeNum = int(data[0].strip("u"))
                for nodeDataIndex in range(len(deflectedShapeData["node"])):
                    nodeData = deflectedShapeData["node"][nodeDataIndex]
                    if nodeData[0] == nodeNum:
                        deflectedShapeData['node'][nodeDataIndex][1] = data[1]+nodeData[1]
                        displacement = data[1]
                        if self._unit[1] == "m":
                            displacement = displacement/1000
                        deflectedShapeData['node'][nodeDataIndex].append("Δx: "+ format(displacement, "5.2e")+data[2])

            elif "v" in data[0]:
                nodeNum = int(data[0].strip("v"))
                for nodeDataIndex in range(len(deflectedShapeData["node"])):
                    nodeData = deflectedShapeData["node"][nodeDataIndex]
                    if nodeData[0] == nodeNum:
                        deflectedShapeData['node'][nodeDataIndex][2] = data[1]+nodeData[2]
                        displacement = data[1]
                        if self._unit[1] == "m":
                            displacement = displacement/1000
                        deflectedShapeData['node'][nodeDataIndex].append("Δy: " + format(displacement, "5.2e")+data[2])

            elif "θ" in data[0]:
                nodeNum = int(data[0].strip("θ"))
                for nodeDataIndex in range(len(deflectedShapeData["node"])):
                    nodeData = deflectedShapeData["node"][nodeDataIndex]
                    if nodeData[0] == nodeNum:
                        displacement = data[1]
                        deflectedShapeData['node'][nodeDataIndex].append("θ: " + format(displacement, "5.2e")+data[2])

        result = allResult["reactionForce"].copy()
        reactionForceData = []
        for forceData in result:
            force = [forceData[0][-1], 0, 0, 0]
            if forceData[0][0] == "F":
                if forceData[0][1] == "x":
                    force[1] = forceData[1]
                elif forceData[0][1] == "y":
                    force[2] = forceData[1]
            elif forceData[0][0] == "M":
                force[3] = forceData[1]
            reactionForceData.append(force)

        result = allResult["axialLoad"].copy()
        axialLoadData = []
        for axialForceData in result:
            for nodeItem in self._structure.getNodes():
                if nodeItem.getID() == axialForceData[1]:
                    xi = nodeItem.getx()
                    yi = nodeItem.gety()
                elif nodeItem.getID() == axialForceData[2]:
                    xj = nodeItem.getx()
                    yj = nodeItem.gety()
            axialLoadData.append([xi,yi,xj,yj, axialForceData[3], axialForceData[4]])

        shearForceData = allResult["shearForce"]
        bendingMomentData = allResult["bendingMoment"]


        self._analysisTime = self._analysisTime + 1
        result = "Linear Analysis Result#" +str(self._analysisTime)+ ":\n" + self._structure.getAllResult()
        self.displayData(result)
        self._canvasDisplay.config(state=NORMAL)
        pos = self._canvasDisplay.search("Linear Analysis Result#"+str(self._analysisTime),"1.0")
        self._canvasDisplay.see(pos)
        self._canvasDisplay.config(state=DISABLED)

        self.clearAllCanvas()
        self.createGraph(self._canvasDeflectedShape, self._structureDrawingData, deflectedStructure=deflectedShapeData)
        self.createGraph(self._canvasReactionForce, self._structureDrawingData, reactionForce=reactionForceData)
        self.createGraph(self._canvasAxialLoad, self._structureDrawingData, axialLoad=axialLoadData)
        self.createGraph(self._canvasShearForce, self._structureDrawingData, shearForce=shearForceData)
        self.createGraph(self._canvasBendingMoment, self._structureDrawingData, bendingMoment=bendingMomentData)


    def addNodalLoad(self):
        """
        Open a window for adding the nodal force
        """
        root = tk.Tk()
        addNodalLoad = DataInput(root, self, "Add Nodal Load", ["node number", "Fx [" + self._unit[0] + "]", "Fy ["+ self._unit[0] + "]",
                                                                "M [" + self._unit[0] + self._unit[1] + "]"], windowSize=self._windowSize,
                                 tips="It can be 0 if having no value")
        self.displayData("Adding the Nodal Load")
        root.mainloop()


    def addMemberPointLoad(self):
        """
        Open a window for adding the member force
        """
        root = tk.Tk()
        addMemberPointLoad = DataInput(root, self, "Add Member Point Load", ["member number", "position (from node i) [" + self._unit[1]+ "]",
                                                                             "Fx [" + self._unit[0] + "]", "Fy ["+ self._unit[0] + "]"], windowSize=self._windowSize,
                                       tips="It can be 0 if having no value")
        self.displayData("Adding the Member Point Load")
        root.mainloop()


    def addMemberUniformlyDistributedLoad(self):
        """
        Open a window for adding the UDL force
        """
        root = tk.Tk()
        addMemberUniformlyDistributedLoad = DataInput(root, self, "Add Member Uniformly Distributed Load",
                                                      ["member number", "w [" + self._unit[0] + "/" + self._unit[1] + "]"],windowSize=self._windowSize,
                                                      tips="It can be 0 if having no value")
        self.displayData("Adding the Uniformly Distributed Load")
        root.mainloop()


    def addNode(self):
        """
        Open a window for adding the node
        """
        nodeNum = self._structure.getNodeNum() + 1
        supportType = {"Roller":["FRR2.png","RFR1.png","FRR1.png","RFR2.png"],
                       "Pin": ["FFR4.png","FFR1.png","FFR2.png","FFR3.png"],
                       "Fixed":["FFF4.png","FFF1.png", "FFF2.png","FFF3.png"]}

        root = tk.Toplevel()
        addNode = DataInput(root, self, "Add Node", ["node number", "x [" + self._unit[1] + "]", "y ["+ self._unit[1] + "]",
                                                     "restraint (support type)"], (0,nodeNum),pictures=supportType, windowSize=self._windowSize,
                            tips= "If the node has no restraint(support)\nLeave it blank")
        self.displayData("Adding a Node")
        root.mainloop()


    def addMember(self):
        """
        Open a window for adding the member
        """
        memberNum = self._structure.getMemberNum() + 1

        root = tk.Tk()
        addMember = DataInput(root, self, "Add Member", ["member number", "node i", "node j",
                                                         "(Cross Section Area) A [mm^2]", "(Area Moment of Inertia) I [mm^4]", "E [MPa]", "type (truss/beam/frame)"], (0,memberNum),
                              windowSize=self._windowSize, tips="Truss: I can be blank\nBeam: A can be blank\nPower of 10 example:\n1.5x10^5 --> 1.5e5")
        self.displayData("Adding a Member")
        root.mainloop()


    def drawArrow(self, A, B, color, canvas=None):
        """
        Draw the arrow for 2 points

        :param A: coordinate of starting point
        :param B: coordinate of ending point
        :param color: arrow colour
        :param canvas: canvas for arrow
        """
        if canvas == None:
            canvas = self._canvas
        Ax = A[0]
        Ay = A[1]
        Bx = B[0]
        By = B[1]

        vector = [[Ax-Bx,],
                  [Ay-By,]]
        magnitude = math.sqrt(vector[0][0]**2 + vector[1][0]**2)
        vector = self._matrixCalculator.matrixScale(vector, 1/magnitude)
        rotation1 = [[math.cos(math.pi/6), math.sin(math.pi/6)],
                     [-math.sin(math.pi/6), math.cos(math.pi/6)]]
        rotation2 = [[math.cos(-math.pi/6), math.sin(-math.pi/6)],
                     [-math.sin(-math.pi/6), math.cos(-math.pi/6)]]
        vector1 = self._matrixCalculator.matrixMultiplication(rotation1, vector)
        vector2 = self._matrixCalculator.matrixMultiplication(rotation2, vector)

        vector1 = self._matrixCalculator.matrixScale(vector1, 15)
        vector2 = self._matrixCalculator.matrixScale(vector2, 15)

        position1 = [vector1[0][0]+Bx, vector1[1][0]+By]
        position2 = [vector2[0][0]+Bx, vector2[1][0]+By]

        canvas.create_line([(Bx, By), (position1[0], position1[1])], fill=color)
        canvas.create_line([(Bx, By), (position2[0], position2[1])], fill=color)
        canvas.create_line([(position1[0], position1[1]), (position2[0], position2[1])], fill=color)


    def createMember(self, data0, data1, data2, data3, data4, data5, data6, detail, canvas=None):
        """
        Generate the member from the user's input

        :param data0: member ID
        :param data1: starting node ID
        :param data2: ending node ID
        :param data3: Area value
        :param data4: Area Moment of Inertia value
        :param data5: Elasticity value
        :param data6: type string
        :param detail: detail of member
        :param canvas: canvas to be added into
        """
        if canvas == None:
            canvas = self._canvas

        memberID = int(data0)
        nodeI = int(data1)
        nodeJ = int(data2)
        A = None
        if data3 != "":
            A = float(data3)
        I = None
        if data4 != "":
            I = float(data4)

        E = float(data5)

        type = data6

        if detail:
            self._structure.addMember(memberID,nodeI, nodeJ, A, I, E, type)
            memberData = [memberID,nodeI,nodeJ,A,I,E,type]
            self._structureData["member"].append(memberData)

        for member in self._structure.getMembers():
            if member.getId() == memberID:
                L = member.getL()

        for node in self._structure.getNodes():
            if node.getID() == nodeI:
                nodeIx = node.getx()/self._scaling+ self._origin[0]
                nodeIy = self._origin[1] - node.gety()/self._scaling
            if node.getID() == nodeJ:
                nodeJx = node.getx()/self._scaling+ self._origin[0]
                nodeJy = self._origin[1] - node.gety()/self._scaling

        canvas.create_line([(nodeIx, nodeIy), (nodeJx, nodeJy)], fill='black')

        if detail:
            canvas.create_text((nodeIx+nodeJx)/2-10, (nodeIy+nodeJy)/2-12, text=str(memberID), fill="#21D789")

            # draw arrow
            self.drawArrow((nodeIx,nodeIy), ((nodeIx+nodeJx)/2, (nodeIy+nodeJy)/2), "black")

        if A != None:
            dataA = " A: " + format(A, "5.2e") + " [mm^2]\n   "
        else:
            dataA = " A: None\n   "

        if I != None:
            dataI = " I: " + format(I, "5.2e") + " [mm^4]\n   "
        else:
            dataI = " I: None\n   "

        if detail:
            length = L
            if self._unit[1] == "m":
                length = length/1000

            self.displayData("Successfully created Member "+str(memberID)+" : \n   "+
                             " type: " + type + "\n   "
                             " i: Node " + str(nodeI) +" ; j: Node "+ str(nodeJ)+ "\n   "+
                             " E: " + format(E, "5.2e") + " [MPa]\n   " +
                             dataI + dataA +
                             " L: " + format(length, "5.2e")+ " [" + self._unit[1] +"]\n   ")
            self._structureDrawingData["member"].append([data0, data1, data2, data3, data4, data5, data6])
        self.update()


    def pointRotation(self, point, radian, center):
        """
        Rotation of a point
        """
        rotation = [[math.cos(radian), math.sin(radian)],
                     [-math.sin(radian), math.cos(radian)]]

        center = center[0], center[1]*(-1)

        point[1][0] = point[1][0]*(-1)

        point[0][0] = point[0][0] - 0
        point[1][0] = point[1][0] - (-self._origin[1])

        point[0][0] = point[0][0]-(center[0]-0)
        point[1][0] = point[1][0]-(center[1]-(-self._origin[1]))

        result = self._matrixCalculator.matrixMultiplication(rotation, point)

        result[0][0] = result[0][0] + (center[0]-0)
        result[1][0] = result[1][0] + (center[1]-(-self._origin[1]))

        result[0][0] = result[0][0] + 0
        result[1][0] = result[1][0] + (-self._origin[1])

        result[1][0] = result[1][0]*(-1)

        return result


    def createNode(self, data0, data1, data2, data3, data4, detail, canvas=None):
        """
        Generate the node from the user's input

        :param data0: node ID
        :param data1: x coordinate of the node
        :param data2: y coordinate of the node
        :param data3: restraint string of the node
        :param data4: restraint shape string of the node
        :param detail: detail of the node
        :param canvas: canvas to be added into
        """
        if canvas == None:
            canvas = self._canvas
        nodeID = int(data0)
        nodeX = int(data1)
        nodeY = int(data2)
        restraint = data3
        restraintShape = data4

        if restraint == "":
            restraint = "RRR"

        if detail:
            self._structure.addNode(nodeID, nodeX, nodeY, restraint)

            nodeData = [nodeID,nodeX,nodeY,restraint,restraintShape]
            self._structureData["node"].append(nodeData)

        x = nodeX/self._scaling+ self._origin[0]
        y = self._origin[1] - nodeY/self._scaling
        canvas.create_oval([(x-2.5, y-2.5), (x +2.5, y +2.5)], fill='black')

        if restraint == "RRR":
            type = "Free to move"
            if detail:
                canvas.create_text(x-10, y-5, text=str(nodeID), fill="#5897BE")

        if restraint == "FFF":
            type = "Fixed end support"

            centerPoint = [[x,],
                           [y+2]]
            linePoint1 = [[x-10,],
                          [y+2]]
            linePoint2 = [[x+10,],
                          [y+2]]
            additionPoint1 = [[x-9,],
                              [y+2]]
            additionPoint2 = [[x-7,],
                              [y+7]]
            additionPoint3 = [[x-5,],
                              [y+2]]
            additionPoint4 = [[x-3,],
                              [y+7]]

            additionPoint5 = [[x-1,],
                              [y+2]]
            additionPoint6 = [[x+1,],
                              [y+7]]

            additionPoint7 = [[x+3,],
                              [y+2]]
            additionPoint8 = [[x+5,],
                              [y+7]]
            additionPoint9 = [[x+7,],
                              [y+2]]
            additionPoint10 = [[x+9,],
                              [y+7]]

            if restraintShape == "FFF1" or restraintShape == "":
                if detail:
                    canvas.create_text(x-10, y-5, text=str(nodeID), fill="#5897BE")
                radian = 0

            if restraintShape == "FFF2":
                if detail:
                    canvas.create_text(x+15, y-5, text=str(nodeID), fill="#5897BE")
                radian = 3*math.pi/2

            if restraintShape == "FFF3":
                if detail:
                    canvas.create_text(x-14, y-4, text=str(nodeID), fill="#5897BE")
                radian = math.pi

            if restraintShape == "FFF4":
                if detail:
                    canvas.create_text(x+10, y-5, text=str(nodeID), fill="#5897BE")
                radian = math.pi/2

            center = (x,y)

            centerPoint = self.pointRotation(centerPoint, radian, center)
            linePoint1 = self.pointRotation(linePoint1, radian, center)
            linePoint2 = self.pointRotation(linePoint2, radian, center)

            additionPoint1 = self.pointRotation(additionPoint1, radian, center)
            additionPoint2 = self.pointRotation(additionPoint2, radian, center)
            additionPoint3 = self.pointRotation(additionPoint3, radian, center)
            additionPoint4 = self.pointRotation(additionPoint4, radian, center)
            additionPoint5 = self.pointRotation(additionPoint5, radian, center)

            additionPoint6 = self.pointRotation(additionPoint6, radian, center)
            additionPoint7 = self.pointRotation(additionPoint7, radian, center)
            additionPoint8 = self.pointRotation(additionPoint8, radian, center)
            additionPoint9 = self.pointRotation(additionPoint9, radian, center)
            additionPoint10 = self.pointRotation(additionPoint10, radian, center)

            canvas.create_line([(centerPoint[0][0], centerPoint[1][0]), (linePoint1[0][0], linePoint1[1][0])], fill='black')
            canvas.create_line([(centerPoint[0][0], centerPoint[1][0]), (linePoint2[0][0], linePoint2[1][0])], fill='black')

            canvas.create_line([(additionPoint1[0][0], additionPoint1[1][0]), (additionPoint2[0][0], additionPoint2[1][0])], fill='black')
            canvas.create_line([(additionPoint3[0][0], additionPoint3[1][0]), (additionPoint4[0][0], additionPoint4[1][0])], fill='black')
            canvas.create_line([(additionPoint5[0][0], additionPoint5[1][0]), (additionPoint6[0][0], additionPoint6[1][0])], fill='black')
            canvas.create_line([(additionPoint7[0][0], additionPoint7[1][0]), (additionPoint8[0][0], additionPoint8[1][0])], fill='black')
            canvas.create_line([(additionPoint9[0][0], additionPoint9[1][0]), (additionPoint10[0][0], additionPoint10[1][0])], fill='black')

        if restraint == "FFR":
            type = "Pined support"

            nodePoint = [[x,],
                         [y,]]

            centerPoint = [[x,],
                           [y+15]]
            linePoint1 = [[x-15,],
                          [y+15]]
            linePoint2 = [[x+15,],
                          [y+15]]

            linePoint3 = [[x-10,],
                          [y+15]]
            linePoint4 = [[x+10,],
                          [y+15]]

            additionPoint1 = [[x-9,],
                              [y+15]]
            additionPoint2 = [[x-7,],
                              [y+20]]
            additionPoint3 = [[x-5,],
                              [y+15]]
            additionPoint4 = [[x-3,],
                              [y+20]]

            additionPoint5 = [[x-1,],
                              [y+15]]
            additionPoint6 = [[x+1,],
                              [y+20]]

            additionPoint7 = [[x+3,],
                              [y+15]]
            additionPoint8 = [[x+5,],
                              [y+20]]
            additionPoint9 = [[x+7,],
                              [y+15]]
            additionPoint10 = [[x+9,],
                               [y+20]]

            if restraintShape == "FFR1" or restraintShape == "":
                if detail:
                    canvas.create_text(x-10, y-2, text=str(nodeID), fill="#5897BE")
                radian = 0

            if restraintShape == "FFR2":
                if detail:
                    canvas.create_text(x-10, y-5, text=str(nodeID), fill="#5897BE")
                radian = 3*math.pi/2

            if restraintShape == "FFR3":
                if detail:
                    canvas.create_text(x-10, y-5, text=str(nodeID), fill="#5897BE")
                radian = math.pi

            if restraintShape == "FFR4":
                if detail:
                    canvas.create_text(x+10, y-5, text=str(nodeID), fill="#5897BE")
                radian = math.pi/2

            center = (x,y)

            centerPoint = self.pointRotation(centerPoint, radian, center)
            linePoint1 = self.pointRotation(linePoint1, radian, center)
            linePoint2 = self.pointRotation(linePoint2, radian, center)
            nodePoint = self.pointRotation(nodePoint, radian, center)
            linePoint3 = self.pointRotation(linePoint3, radian, center)
            linePoint4 = self.pointRotation(linePoint4, radian, center)

            additionPoint1 = self.pointRotation(additionPoint1, radian, center)
            additionPoint2 = self.pointRotation(additionPoint2, radian, center)
            additionPoint3 = self.pointRotation(additionPoint3, radian, center)
            additionPoint4 = self.pointRotation(additionPoint4, radian, center)
            additionPoint5 = self.pointRotation(additionPoint5, radian, center)

            additionPoint6 = self.pointRotation(additionPoint6, radian, center)
            additionPoint7 = self.pointRotation(additionPoint7, radian, center)
            additionPoint8 = self.pointRotation(additionPoint8, radian, center)
            additionPoint9 = self.pointRotation(additionPoint9, radian, center)
            additionPoint10 = self.pointRotation(additionPoint10, radian, center)

            canvas.create_line([(nodePoint[0][0], nodePoint[1][0]), (linePoint3[0][0], linePoint3[1][0])], fill='black')
            canvas.create_line([(nodePoint[0][0], nodePoint[1][0]), (linePoint4[0][0], linePoint4[1][0])], fill='black')
            canvas.create_line([(linePoint3[0][0], linePoint3[1][0]), (linePoint4[0][0], linePoint4[1][0])], fill='black', width=2)

            canvas.create_line([(centerPoint[0][0], centerPoint[1][0]), (linePoint1[0][0], linePoint1[1][0])], fill='black')
            canvas.create_line([(centerPoint[0][0], centerPoint[1][0]), (linePoint2[0][0], linePoint2[1][0])], fill='black')

            canvas.create_line([(additionPoint1[0][0], additionPoint1[1][0]), (additionPoint2[0][0], additionPoint2[1][0])], fill='black')
            canvas.create_line([(additionPoint3[0][0], additionPoint3[1][0]), (additionPoint4[0][0], additionPoint4[1][0])], fill='black')
            canvas.create_line([(additionPoint5[0][0], additionPoint5[1][0]), (additionPoint6[0][0], additionPoint6[1][0])], fill='black')
            canvas.create_line([(additionPoint7[0][0], additionPoint7[1][0]), (additionPoint8[0][0], additionPoint8[1][0])], fill='black')
            canvas.create_line([(additionPoint9[0][0], additionPoint9[1][0]), (additionPoint10[0][0], additionPoint10[1][0])], fill='black')

        if restraint == "FRR" or restraint == "RFR":
            type = "Roller support"

            nodePoint = [[x,],
                         [y,]]

            linePoint3 = [[x-10,],
                          [y+15]]
            linePoint4 = [[x+10,],
                          [y+15]]

            circlePoint1 = [[x-3,],
                           [y+22]]
            circlePoint2 = [[x+3,],
                           [y+22]]

            centerPoint = [[x,],
                           [y+22]]
            linePoint1 = [[x-15,],
                          [y+22]]
            linePoint2 = [[x+15,],
                          [y+22]]

            additionPoint1 = [[x-9,],
                              [y+22]]
            additionPoint2 = [[x-7,],
                              [y+27]]
            additionPoint3 = [[x-5,],
                              [y+22]]
            additionPoint4 = [[x-3,],
                              [y+27]]

            additionPoint5 = [[x-1,],
                              [y+22]]
            additionPoint6 = [[x+1,],
                              [y+27]]

            additionPoint7 = [[x+3,],
                              [y+22]]
            additionPoint8 = [[x+5,],
                              [y+27]]
            additionPoint9 = [[x+7,],
                              [y+22]]
            additionPoint10 = [[x+9,],
                               [y+27]]

            if restraintShape == "" and restraint == "FRR":
                if detail:
                    canvas.create_text(x-10, y-7, text=str(nodeID), fill="#5897BE")
                radian = 3*math.pi/2

            if restraintShape == "" and restraint == "RFR":
                if detail:
                    canvas.create_text(x-10, y-5, text=str(nodeID), fill="#5897BE")
                radian = 0

            if restraintShape == "RFR1":
                if detail:
                    canvas.create_text(x-10, y-5, text=str(nodeID), fill="#5897BE")
                radian = 0

            if restraintShape == "FRR1":
                if detail:
                    canvas.create_text(x-10, y-7, text=str(nodeID), fill="#5897BE")
                radian = 3*math.pi/2

            if restraintShape == "RFR2":
                if detail:
                    canvas.create_text(x-10, y-5, text=str(nodeID), fill="#5897BE")
                radian = math.pi

            if restraintShape == "FRR2":
                if detail:
                    canvas.create_text(x+10, y-7, text=str(nodeID), fill="#5897BE")
                radian = math.pi/2

            center = (x,y)

            nodePoint = self.pointRotation(nodePoint, radian, center)
            linePoint3 = self.pointRotation(linePoint3, radian, center)
            linePoint4 = self.pointRotation(linePoint4, radian, center)

            centerPoint = self.pointRotation(centerPoint, radian, center)
            linePoint1 = self.pointRotation(linePoint1, radian, center)
            linePoint2 = self.pointRotation(linePoint2, radian, center)

            circlePoint1 = self.pointRotation(circlePoint1, radian, center)
            circlePoint2 = self.pointRotation(circlePoint2, radian, center)

            additionPoint1 = self.pointRotation(additionPoint1, radian, center)
            additionPoint2 = self.pointRotation(additionPoint2, radian, center)
            additionPoint3 = self.pointRotation(additionPoint3, radian, center)
            additionPoint4 = self.pointRotation(additionPoint4, radian, center)
            additionPoint5 = self.pointRotation(additionPoint5, radian, center)

            additionPoint6 = self.pointRotation(additionPoint6, radian, center)
            additionPoint7 = self.pointRotation(additionPoint7, radian, center)
            additionPoint8 = self.pointRotation(additionPoint8, radian, center)
            additionPoint9 = self.pointRotation(additionPoint9, radian, center)
            additionPoint10 = self.pointRotation(additionPoint10, radian, center)

            canvas.create_line([(nodePoint[0][0], nodePoint[1][0]), (linePoint3[0][0], linePoint3[1][0])], fill='black')
            canvas.create_line([(nodePoint[0][0], nodePoint[1][0]), (linePoint4[0][0], linePoint4[1][0])], fill='black')
            canvas.create_line([(linePoint3[0][0], linePoint3[1][0]), (linePoint4[0][0], linePoint4[1][0])], fill='black', width=2)

            canvas.create_oval([(linePoint3[0][0], linePoint3[1][0]), (circlePoint1[0][0], circlePoint1[1][0])])
            canvas.create_oval([(linePoint4[0][0], linePoint4[1][0]), (circlePoint2[0][0], circlePoint2[1][0])])

            canvas.create_line([(centerPoint[0][0], centerPoint[1][0]), (linePoint1[0][0], linePoint1[1][0])], fill='black')
            canvas.create_line([(centerPoint[0][0], centerPoint[1][0]), (linePoint2[0][0], linePoint2[1][0])], fill='black')

            canvas.create_line([(additionPoint1[0][0], additionPoint1[1][0]), (additionPoint2[0][0], additionPoint2[1][0])], fill='black')
            canvas.create_line([(additionPoint3[0][0], additionPoint3[1][0]), (additionPoint4[0][0], additionPoint4[1][0])], fill='black')
            canvas.create_line([(additionPoint5[0][0], additionPoint5[1][0]), (additionPoint6[0][0], additionPoint6[1][0])], fill='black')
            canvas.create_line([(additionPoint7[0][0], additionPoint7[1][0]), (additionPoint8[0][0], additionPoint8[1][0])], fill='black')
            canvas.create_line([(additionPoint9[0][0], additionPoint9[1][0]), (additionPoint10[0][0], additionPoint10[1][0])], fill='black')

        self.update()
        if detail:
            x_coordinate = nodeX
            y_coordinate = nodeY

            if self._unit[1] == "m":
                x_coordinate = x_coordinate/1000
                y_coordinate = y_coordinate/1000

            self.displayData("Successfully created Node "+str(nodeID)+" : \n   "+
                             " coordinate: (" + str(x_coordinate) +","+ str(y_coordinate)+ ") [" + self._unit[1] + "]\n   "+
                             " type: " + type + "\n   "
                             " restraint: " + restraint+ "\n   ")
            self._structureDrawingData["node"].append([data0, data1, data2, data3, data4])


    def createNodalLoad(self, data0, data1, data2, data3, detail, canvas=None):
        """
        Generate the nodal force from the user's input

        :param data0: node ID
        :param data1: x value of the force
        :param data2: y value of the force
        :param data3: moment value of the force
        :param detail: detail of the nodal load
        :param canvas: canvas to be added into
        """
        if canvas == None:
            canvas = self._canvas
        nodeID = int(data0)
        Fx = float(data1)
        Fy = float(data2)
        M = float(data3)

        if detail:
            self._structure.addNodalLoad(nodeID,Fx, Fy, M)
            nodalLoadData = [nodeID,Fx,Fy,M]
            self._structureData["nodalLoad"].append(nodalLoadData)

        if self._unit[0] == "kN":
            Fx = Fx/1000
            Fy = Fy/1000
            M = M/1000
        if self._unit[1] == "m":
            M = M/1000

        Fx = round(Fx,self._unit[2])
        Fy = round(Fy,self._unit[2])
        M = round(M,self._unit[2])

        for node in self._structure.getNodes():
            if node.getID() == nodeID:
                x = node.getx()/self._scaling + self._origin[0]
                y = self._origin[1] - node.gety()/self._scaling

        if Fx > 0 or Fx < 0:
            if Fx > 0:
                canvas.create_line([(x, y), (x + 60, y)], fill='red')
                self.drawArrow((x,y), (x + 60, y), "red", canvas)
                canvas.create_text(x+70, y-15, text=str(Fx) + " " + self._unit[0], fill="red")
            elif Fx < 0:
                canvas.create_line([(x, y), (x - 60, y)], fill='red')
                self.drawArrow((x,y), (x - 60, y), "red", canvas)
                canvas.create_text(x-70, y-15, text=str(-Fx) + " " + self._unit[0], fill="red")

        if Fy > 0 or Fy < 0:
            if Fy > 0:
                canvas.create_line([(x, y), (x, y-60)], fill='red')
                self.drawArrow((x,y), (x, y-60), "red", canvas)
                canvas.create_text(x, y-70, text=str(Fy) + " " + self._unit[0], fill="red")
            elif Fy < 0:
                canvas.create_line([(x, y), (x, y+60)], fill='red')
                self.drawArrow((x,y), (x, y+60), "red", canvas)
                canvas.create_text(x, y+70, text=str(-Fy) + " " + self._unit[0], fill="red")

        coord = x-20,y-20,x+20,y+20
        if M > 0 or M < 0:
            if M > 0:
                canvas.create_arc(coord, start=30, extent=270, style=tk.ARC, width=1, outline="red")
                self.drawArrow((x+5,y+19), (x+10, y+18), "red", canvas)
                canvas.create_text(x+10, y+36, text=str(M) + " " + self._unit[0]+self._unit[1], fill="red")
            elif M < 0:
                canvas.create_arc(coord, start=-120, extent=270, style=tk.ARC, width=1, outline="red")
                self.drawArrow((x-5,y+19), (x-10, y+18), "red", canvas)
                canvas.create_text(x-10, y+36, text=str(-M) + " " + self._unit[0]+self._unit[1], fill="red")
        if detail:
            self.displayData("Successfully added Nodal Load"+ "\n   ")


    def calculatePosition(self, i, j, x):
        """
        Calculate the position of the required point on the member

        :param i: starting point coordinate
        :param j: ending point coordinate
        :param x: distance from starting point
        :return: the calculated position of the required point
        """
        ix = i[0]
        iy = i[1]
        jx = j[0]
        jy = j[1]
        vector = [[jx-ix,],
                  [jy-iy,]]
        magnitude = math.sqrt(vector[0][0]**2 + vector[1][0]**2)
        vector = self._matrixCalculator.matrixScale(vector, 1/magnitude)
        vector = self._matrixCalculator.matrixScale(vector, x)
        return (vector[0][0]+ix, vector[1][0]+iy)


    def createMemberPointLoad(self, data0, data1, data2, data3):
        """
        Generate the member point load from the user's input

        :param data0: member ID
        :param data1: distance from starting point
        :param data2: x value of the force
        :param data3: y value of the force
        """
        memberID = int(data0)
        x = float(data1)
        Fx = float(data2)
        Fy = float(data3)

        for member in self._structure.getMembers():
            if member.getId() == memberID:
                type = member.getType()
                nodes = member.get_ij()
                L = member.getL()

        if x > L:
            return None

        for node in self._structure.getNodes():
            if node.getID() == nodes[0]:
                ix = node.getx()
                iy = node.gety()
            elif node.getID() == nodes[1]:
                jx = node.getx()
                jy = node.gety()

        memberPointLoadData = [memberID,x,Fx,Fy]
        self._structureData["memberPointLoad"].append(memberPointLoadData)

        if type == "beam":
            self._structure.addMemberPointLoad(memberID,x,Fy)
            pointX, pointY = self.calculatePosition((ix,iy), (jx,jy), x)
            pointX = pointX/self._scaling + self._origin[0]
            pointY = self._origin[1] - pointY/self._scaling

            if self._unit[0] == "kN":
                Fy = Fy/1000

            Fy = round(Fy,self._unit[2])

            if Fy < 0:
                self._canvas.create_line([(pointX, pointY), (pointX, pointY-60)], fill='red')
                self.drawArrow((pointX, pointY-60), (pointX, pointY), "red")
                self._canvas.create_text(pointX, pointY-70, text=str(-Fy) + " " + self._unit[0], fill="red")
            elif Fy > 0:
                self._canvas.create_line([(pointX, pointY), (pointX, pointY+60)], fill='red')
                self.drawArrow((pointX, pointY+60), (pointX, pointY), "red")
                self._canvas.create_text(pointX, pointY+70, text=str(Fy) + " " + self._unit[0], fill="red")

        elif type == "frame":
            self._structure.addGlobalMemberPointLoad(memberID,x,Fx,Fy)
            pointX, pointY = self.calculatePosition((ix,iy), (jx,jy), x)
            pointX = pointX/self._scaling + self._origin[0]
            pointY = self._origin[1] - pointY/self._scaling

            if self._unit[0] == "kN":
                Fx = Fx/1000
                Fy = Fy/1000

            Fx = round(Fx,self._unit[2])
            Fy = round(Fy,self._unit[2])

            if Fy < 0:
                self._canvas.create_line([(pointX, pointY), (pointX, pointY-60)], fill='red')
                self.drawArrow((pointX, pointY-60), (pointX, pointY), "red")
                self._canvas.create_text(pointX, pointY-70, text=str(-Fy) + " " + self._unit[0], fill="red")
            elif Fy > 0:
                self._canvas.create_line([(pointX, pointY), (pointX, pointY+60)], fill='red')
                self.drawArrow((pointX, pointY+60), (pointX, pointY), "red")
                self._canvas.create_text(pointX, pointY+70, text=str(Fy) + " " + self._unit[0], fill="red")

            if Fx < 0:
                self._canvas.create_line([(pointX, pointY), (pointX+60, pointY)], fill='red')
                self.drawArrow((pointX+60, pointY), (pointX, pointY), "red")
                self._canvas.create_text(pointX+70, pointY-15, text=str(-Fx) + " " + self._unit[0], fill="red")
            elif Fx > 0:
                self._canvas.create_line([(pointX, pointY), (pointX-60, pointY)], fill='red')
                self.drawArrow((pointX-60, pointY), (pointX, pointY), "red")
                self._canvas.create_text(pointX-70, pointY-15, text=str(Fx) + " " + self._unit[0], fill="red")

        distance = x
        if self._unit[1] == "m":
            distance = distance/1000
        self.displayData("Successfully added Member Point Load:\n   " +
                         " Distance from node " + str(nodes[0]) + " : " + str(distance)+ " " + self._unit[1] + "\n   ")


    def createMemberUniformlyDistributedLoad(self, data0, data1):
        """
        Generate the member UDL from the user's input
        UDL not included in frame member

        :param data0: member ID
        :param data1: value of the UDL
        """
        memberID = int(data0)
        w = float(data1)

        self._structure.addMemberUniformlyDistributedLoad(memberID, w)
        uniformlyDistributedLoadData = [memberID,w]
        self._structureData["uniformlyDistributedLoad"].append(uniformlyDistributedLoadData)

        if self._unit[0] == "kN":
            w = w/1000

        if self._unit[1] == "m":
            w = w*1000

        w = round(w,self._unit[2])


        for member in self._structure.getMembers():
            if member.getId() == memberID:
                nodes = member.get_ij()
                L = member.getL()

        for node in self._structure.getNodes():
            if node.getID() == nodes[0]:
                ix = node.getx()
                iy = node.gety()
            elif node.getID() == nodes[1]:
                jx = node.getx()
                jy = node.gety()

        numOfLine = math.floor((L/self._scaling)/20)

        distance = (L/self._scaling)/(numOfLine-1)

        for index in range(numOfLine):
            pointX, pointY = self.calculatePosition((ix,iy), (jx,jy), index*distance*self._scaling)
            pointX = pointX/self._scaling + self._origin[0]
            pointY = self._origin[1] - pointY/self._scaling

            if w < 0:
                if index == 0:
                    point1 = (pointX, pointY-65)

                self._canvas.create_line([(pointX, pointY-5), (pointX, pointY-65)], fill='red')
                self.drawArrow((pointX, pointY-65), (pointX, pointY-5), "red")

                if index == numOfLine-1:
                    self._canvas.create_line([point1, (pointX, pointY-65)], fill='red')

                if index == numOfLine//2:
                    self._canvas.create_text(pointX, pointY-75, text=str(-w) + " "+self._unit[0]+"/"+self._unit[1], fill="red")

            elif w > 0:
                if index == 0:
                    point1 = (pointX, pointY+65)

                self._canvas.create_line([(pointX, pointY+5), (pointX, pointY+65)], fill='red')
                self.drawArrow((pointX, pointY+65), (pointX, pointY+5), "red")

                if index == numOfLine-1:
                    self._canvas.create_line([point1, (pointX, pointY+65)], fill='red')

                if index == numOfLine//2:
                    self._canvas.create_text(pointX, pointY+75, text=str(w) + " "+self._unit[0]+"/"+self._unit[1], fill="red")

        self.displayData("Successfully added Distributed Load"+ "\n   ")


    def update(self):
        """
        Update the node and member information for the label
        """
        nodeNum = self._structure.getNodeNum()
        memberNum = self._structure.getMemberNum()
        text = "number of Node: " + str(nodeNum) + "      number of Member: " + str(memberNum)
        self._canvas.delete(self._label)
        self._label = self._canvas.create_text(round(self._windowWidth*0.65)-150, 15, text=text, fill="#8A2F19")


    def deleteMagnitude(self, canvas):
        """
        Delete the magnitude label from the canvas

        :param canvas: canvas to be removed
        """
        canvas.delete(self._labelMessage)


    def updateMagnitude(self, canvas, x, magnitude, type):
        """
        Update the magnitude label from the canvas

        :param canvas: canvas to be updated
        :param x: distance value
        :param magnitude: magnitude value
        :param type: type string of the force
        """
        if self._unit[1] == "m":
            x = x/1000

        if type == "Shear Force":
            if self._unit[0] == "kN":
                magnitude = magnitude/1000
            unit = self._unit[0]

        elif type == "Bending Moment":
            if self._unit[0] == "kN":
                magnitude = magnitude/1000
            if self._unit[1] == "m":
                magnitude = magnitude/1000

            unit = self._unit[0] + self._unit[1]

        magnitude = round(magnitude, self._unit[2])

        text = "x :  " + str(x) + " " + self._unit[1] +"      " + \
               type + ": " + str(magnitude) + " " + unit
        self.deleteMagnitude(canvas)
        self._labelMessage = canvas.create_text(round(self._windowWidth*0.65)-165, 20, text=text, fill="#8A2F19")


    def generatePdfResult(self):
        """
        Generate the result of the analysis and save it into PDF
        """
        filename = "results/" + self._filename + ".pdf"

        pdf = SimpleDocTemplate(filename, pagesize=letter)

        style1 = TableStyle([("ALIGN", (0,0), (-1,-1),"CENTER"),
                             ("BOX", (0,0), (-1,-1), 2, "black"),
                             ("LINEBEFORE", (0,0), (-1,-1), 1, "black"),
                             ("LINEABOVE", (0,0), (-1,-1), 1, "black")])

        memberTable1 = Table(self._structure.getMemberInformationTable1())
        memberTable2 = Table(self._structure.getMemberInformationTable2())

        memberTable1.setStyle(style1)
        memberTable2.setStyle(style1)

        elements = []
        elements.append(Table([["Linear Analysis Result: " + self._filename,],]))
        elements.append(Table([["unit: [N], [mm]",],]))
        elements.append(Table([["",],]))
        elements.append(Table([["Member Information: ",],]))
        elements.append(Table([["",],]))
        elements.append(memberTable1)
        elements.append(Table([["",],])) # blank line
        elements.append(memberTable2)
        elements.append(Table([["",],]))

        style2 = TableStyle([("ALIGN", (0,0), (-1,-1),"CENTER"),])

        elements.append(Table([["",],]))
        elements.append(Table([["Member Local Stiffness: ",],]))
        elements.append(Table([["",],]))
        for stiffness in self._structure.getLocalStiffness():
            table = Table(stiffness)
            table.setStyle(style2)
            elements.append(table)
            elements.append(Table([["",],]))

        style3 = TableStyle([("ALIGN", (0,0), (-1,-1),"CENTER"),
                             ("FONTSIZE", (0,0), (-1,-1), 7)])

        elements.append(Table([["",],]))
        elements.append(Table([["Structure Global Stiffness: ",],]))
        elements.append(Table([["",],]))
        globalStiffness = Table(self._structure.getGlobalStiffnessString())
        globalStiffness.setStyle(style3)
        elements.append(globalStiffness)
        elements.append(Table([["",],]))

        elements.append(Table([["",],]))
        elements.append(Table([["Nodal Displacement & Nodal Load: ",],]))
        elements.append(Table([["",],]))
        r_R = Table(self._structure.getNodalDisplacementAndLoad())
        r_R.setStyle(style2)
        elements.append(r_R)
        elements.append(Table([["",],]))

        elements.append(Table([["",],]))
        elements.append(Table([["Member Local P: ",],]))
        elements.append(Table([["",],]))
        for P in self._structure.getAllLocalP():
            eachP = Table(P)
            eachP.setStyle(style2)
            elements.append(eachP)
            elements.append(Table([["",],]))
        elements.append(Table([["",],]))

        elements.append(Table([["",],]))
        elements.append(Table([["Structure Global P: ",],]))
        elements.append(Table([["",],]))
        globalP = Table(self._structure.getGlobalPString())
        globalP.setStyle(style2)
        elements.append(globalP)
        elements.append(Table([["",],]))

        elements.append(Table([["",],]))
        elements.append(Table([["Nodal Displacement {rf}: ",],]))
        elements.append(Table([["{Rf} = [Kff]{rf} + {Pf}",],]))
        elements.append(Table([["{rf} = [Kff]^(-1) x ({Rf} - {Pf})",],]))
        elements.append(Table([["",],]))
        Kff = Table(self._structure.getKffString())
        Kff.setStyle(style2)
        elements.append(Kff)
        elements.append(Table([["",],]))
        Rf = Table(self._structure.getRfString())
        Rf.setStyle(style2)
        elements.append(Rf)
        elements.append(Table([["",],]))
        Pf = Table(self._structure.getPfString())
        Pf.setStyle(style2)
        elements.append(Pf)
        elements.append(Table([["",],]))
        rf = Table(self._structure.get_rfString())
        rf.setStyle(style2)
        elements.append(rf)
        elements.append(Table([["",],]))

        elements.append(Table([["",],]))
        elements.append(Table([["Reaction Force {Rs}: ",],]))
        elements.append(Table([["{Rs} = [Ksf]{rf} + {Ps}",],]))
        elements.append(Table([["",],]))
        Ksf = Table(self._structure.getKsfString())
        Ksf.setStyle(style2)
        elements.append(Ksf)
        elements.append(Table([["",],]))
        Ps = Table(self._structure.getPsString())
        Ps.setStyle(style2)
        elements.append(Ps)
        elements.append(Table([["",],]))
        Rs = Table(self._structure.getRsString())
        Rs.setStyle(style2)
        elements.append(Rs)
        elements.append(Table([["",],]))

        elements.append(Table([["",],]))
        elements.append(Table([["Member Force: ",],]))
        elements.append(Table([["",],]))
        for F in self._structure.getLocalMemberForce():
            eachF = Table(F)
            eachF.setStyle(style2)
            elements.append(eachF)
            elements.append(Table([["",],]))

        pdf.build(elements)


root = tk.Tk()
app = App(root)
root.mainloop()
from directStiffnessMethod.trussElement import TrussElement
import math
from directStiffnessMethod import matrixCalculation
from directStiffnessMethod.beamElement import BeamElement
from directStiffnessMethod.frameElement import FrameElement
from fpdf import FPDF
from directStiffnessMethod.node import Node


class Structure(object):
    """
    Structure for analysis
    """

    def __init__(self):
        """
        Initiating the structure
        """
        self._nodes = []
        self._nodeNum = len(self._nodes)
        self._members = []
        self._memberNum = len(self._members)
        self._nodalDisplacement = []
        self._nodalLoad = []
        self._unit = ["N","mm",2]

        self._matrixCalculator = matrixCalculation.MatrixCalculation()


    def changeUnit(self, unit):
        """
        Set up the unit

        :param unit: required unit
        """
        self._unit = unit


    def addNode(self, id, x, y, restraint):
        """
        Add node into the structure

        :param id: nodal ID
        :param x: x coordinate
        :param y: y coordinate
        :param restraint: nodal restraint string
        """
        node = Node(id, x, y, restraint)
        self._nodes.append(node)
        self._nodeNum = len(self._nodes)


    def getNodeNum(self):
        """
        Return the number of nodes in the structure

        :return: the number of nodes in the structure
        """
        return self._nodeNum


    def getMemberNum(self):
        """
        Return the number of members in the structure

        :return: the number of members in the structure
        """
        return self._memberNum


    def addMember(self, id, i, j, A, I, E, type):
        """
        Add member into the structure

        :param id: member ID
        :param i: starting node
        :param j: ending node
        :param A: area value for the member
        :param I: area Moment of Inertia
        :param E: elasticity
        :param type: member type string
        """
        # need to check if two nodes exist
        # and make sure two nodes are different

        for node in self.getNodes():
            if node.getID() == i:
                node_i = node
            if node.getID() == j:
                node_j = node
        x = node_j.getx() - node_i.getx()
        y = node_j.gety() - node_i.gety()

        L = math.sqrt((x**2) + (y**2))

        if x > 0 and y >= 0:
            angle = math.atan(y/x)
        elif x <= 0 and y > 0:
            if x == 0:
                angle = math.pi/2
            else:
                angle = math.pi + math.atan(y/x)
        elif x < 0 and y <= 0:
            angle = math.pi - math.atan(y/x)
        elif x >= 0 and y < 0:
            if x == 0:
                angle = -math.pi/2
            else:
                angle = math.atan(y/x)

        member = None
        if type == "truss":
            member = TrussElement(id,i,j,A,E,L,angle)
        elif type == "beam":
            member = BeamElement(id,i,j,I,E,L)
        elif type == "frame":
            member = FrameElement(id,i,j,A,I,E,L,angle)

        x_axis = [[x,],
                  [y,]]
        y_axis = self._matrixCalculator.matrixMultiplication([[0,-1],[1,0]], x_axis)

        member.add_xy_Axis(x_axis, y_axis)

        self._members.append(member)
        self._memberNum = len(self._members)


    def addNodalLoad(self, nodeNum, fx, fy, moment):
        """
        Add the nodal loading into the node

        :param nodeNum: node ID
        :param fx: x value of the force
        :param fy: y value of the force
        :param moment: bending moment value of the force
        """
        for node in self.getNodes():
            if node.getID() == nodeNum:
                node.addNodalLoad(fx, fy, moment)


    def addMemberPointLoad(self, memberNum, x, P):
        """
        Add the point loading into the member

        :param memberNum: member ID
        :param x: distance from the starting node
        :param P: value of the point load
        """
        for member in self.getMembers():
            if member.getId() == memberNum:
                member.addPointLoad(x, P)


    def vectorProjection(self, vector, directedVector):
        """
        Calculation of the vector projection

        :param vector: input vector
        :param directedVector: required direction
        :return: result of the projection
        """
        dotProduct = vector[0][0]*directedVector[0][0] + vector[1][0]*directedVector[1][0]
        dotProduct = dotProduct/((directedVector[0][0]**2) + (directedVector[1][0]**2))
        result = [[directedVector[0][0]*dotProduct,],
                  [directedVector[1][0]*dotProduct,]]
        return result


    def vectorsCheckSign(self, vector1, vector2):
        """
        Check if the two input vectors are in the same direction

        :param vector1: first vector
        :param vector2: second vector
        :return: true or false
        """
        x = False
        y = False

        if vector1[0][0] > 0 and vector2[0][0] > 0:
            x = True
        elif vector1[0][0] < 0 and vector2[0][0] < 0:
            x = True

        if vector1[1][0] > 0 and vector2[1][0] > 0:
            y = True
        elif vector1[1][0] < 0 and vector2[1][0] < 0:
            y = True

        if x == True and y == True:
            return True
        else:
            return False


    def vectorsBeamCheckSign(self, vector1, vector2):
        """
        Check if the two input vectors for beam are in the same direction

        :param vector1: first vector
        :param vector2: second vector
        :return: true or false
        """
        x = False
        y = False

        if vector1[0][0] > 0 and vector2[0][0] > 0:
            x = True
        elif vector1[0][0] < 0 and vector2[0][0] < 0:
            x = True

        if vector1[1][0] > 0 and vector2[1][0] > 0:
            y = True
        elif vector1[1][0] < 0 and vector2[1][0] < 0:
            y = True

        if vector1[1][0] == 0 and vector2[1][0] == 0:
            y = True
        elif vector1[1][0] == 0 and vector2[1][0] == 0:
            y = True

        if x == True and y == True:
            return True
        else:
            return False


    def addGlobalMemberPointLoad(self, memberNum, x, fx, fy):
        """
        Add the global point loading into a member

        :param memberNum: member ID
        :param x: distance from the starting node
        :param fx: x value of the force
        :param fy: y value of the force
        """
        for member in self.getMembers():
            if member.getId() == memberNum:
                x_axis = member.get_x_Axis()
                y_axis = member.get_y_Axis()

                if fy != 0:
                    Fy = [[0,], [fy,]]
                    Xcomponent = self.vectorProjection(Fy, x_axis)
                    Ycomponent = self.vectorProjection(Fy, y_axis)
                    if self.vectorsCheckSign(Xcomponent, x_axis):
                        f_x = math.sqrt((Xcomponent[0][0]**2) + (Xcomponent[1][0]**2))
                    else:
                        f_x = -math.sqrt((Xcomponent[0][0]**2) + (Xcomponent[1][0]**2))

                    if self.vectorsCheckSign(Ycomponent, y_axis):
                        f_y = math.sqrt((Ycomponent[0][0]**2) + (Ycomponent[1][0]**2))
                    else:
                        f_y = -math.sqrt((Ycomponent[0][0]**2) + (Ycomponent[1][0]**2))

                    member.addGlobalPointLoad(x, f_x, f_y)

                if fx != 0:
                    Fx = [[fx,], [0,]]
                    Xcomponent = self.vectorProjection(Fx, x_axis)
                    Ycomponent = self.vectorProjection(Fx, y_axis)
                    if self.vectorsCheckSign(Xcomponent, x_axis):
                        f_x = math.sqrt((Xcomponent[0][0]**2) + (Xcomponent[1][0]**2))
                    else:
                        f_x = -math.sqrt((Xcomponent[0][0]**2) + (Xcomponent[1][0]**2))

                    if self.vectorsCheckSign(Ycomponent, y_axis):
                        f_y = math.sqrt((Ycomponent[0][0]**2) + (Ycomponent[1][0]**2))
                    else:
                        f_y = -math.sqrt((Ycomponent[0][0]**2) + (Ycomponent[1][0]**2))

                    member.addGlobalPointLoad(x, f_x, f_y)


    def addMemberUniformlyDistributedLoad(self, memberNum, w):
        """
        Add the UDL into the member

        :param memberNum: member ID
        :param w: UDL value
        """
        for member in self.getMembers():
            if member.getId() == memberNum:
                member.addUniformlyDistributedLoad(w)


    def getGlobalStiffnessMatrixSize(self):
        """
        Return the size of the global matrix stiffness

        :return: the size of the global matrix stiffness
        """
        return self.getNodeNum()*2


    def getMembers(self):
        """
        Get all the members in the structure

        :return: all the members in the structure
        """
        return self._members


    def getNodes(self):
        """
        Get all the nodes in the structure

        :return: all the nodes in the structure
        """
        return self._nodes


    def getNodalDisplacement(self):
        """
        Return the nodal displacement of the structure

        :return: the nodal displacement of the structure
        """
        result = []

        for num in range(1, self.getNodeNum()+1):
            for node in self.getNodes():
                if node.getID() == num:
                    r = node.getNodalDisplacement().copy()
                    type = []
                    for member in self.getMembers():
                        if num in member.get_ij():
                            type.append(member.getType())
                    typeIndex = []
                    if "truss" in type:
                        typeIndex.append(0)
                        typeIndex.append(1)
                    if "beam" in type:
                        typeIndex.append(1)
                        typeIndex.append(2)
                    if "frame" in type:
                        typeIndex.append(0)
                        typeIndex.append(1)
                        typeIndex.append(2)
                    if 0 not in typeIndex:
                        r.pop(0)
                    if 2 not in typeIndex:
                        r.pop(2)

                    result.extend(r)
        return result


    def getNodalLoad(self):
        """
        Return the nodal load of the structure

        :return: the nodal load of the structure
        """
        result = []
        for num in range(1, self.getNodeNum()+1):
            for node in self.getNodes():
                if node.getID() == num:
                    R = node.getNodalLoad().copy()
                    type = []
                    for member in self.getMembers():
                        if num in member.get_ij():
                            type.append(member.getType())
                    typeIndex = []
                    if "truss" in type:
                        typeIndex.append(0)
                        typeIndex.append(1)
                    if "beam" in type:
                        typeIndex.append(1)
                        typeIndex.append(2)
                    if "frame" in type:
                        typeIndex.append(0)
                        typeIndex.append(1)
                        typeIndex.append(2)
                    if 0 not in typeIndex:
                        R.pop(0)
                    if 2 not in typeIndex:
                        R.pop(2)

                    result.extend(R)
        return result


    def getNodalDisplacementNum(self, nodeNum):
        """
        Count the number of displacement for a node

        :param nodeNum: nodal ID
        :return: the number of displacement for the node
        """
        for node in self.getNodes():
            if node.getID() == nodeNum:
                r = node.getNodalDisplacement().copy()
                type = []
                for member in self.getMembers():
                    if nodeNum in member.get_ij():
                        type.append(member.getType())
                typeIndex = []
                if "truss" in type:
                    typeIndex.append(0)
                    typeIndex.append(1)
                if "beam" in type:
                    typeIndex.append(1)
                    typeIndex.append(2)
                if "frame" in type:
                    typeIndex.append(0)
                    typeIndex.append(1)
                    typeIndex.append(2)
                if 0 not in typeIndex:
                    return 2
                elif 2 not in typeIndex:
                    return 2
                else:
                    return 3


    def getGlobalP(self):
        """
        Return the global loading matrix

        :return: the global loading matrix
        """
        result = []
        for pointNum in range(1, self.getNodeNum()+1):
            resultRow1 = []
            resultRow2 = []
            resultRow3 = []
            resultRow1Num = 0
            resultRow2Num = 0
            resultRow3Num = 0

            nodeDisplacementNum = self.getNodalDisplacementNum(pointNum)
            for member in self.getMembers():

                P = member.getP()
                if nodeDisplacementNum == 3 and member.getType() == "truss":
                    P.append([0,])
                    P.append([0,])

                if nodeDisplacementNum == 3 and member.getType() == "beam":
                    P.insert(0, [0,])
                    P.insert(3, [0,])

                if pointNum == member.geti():
                    if nodeDisplacementNum == 2:
                        resultRow1Num = resultRow1Num + P[0][0]
                        resultRow2Num = resultRow2Num + P[1][0]
                    elif nodeDisplacementNum == 3:
                        resultRow1Num = resultRow1Num + P[0][0]
                        resultRow2Num = resultRow2Num + P[1][0]
                        resultRow3Num = resultRow3Num + P[2][0]

                elif pointNum == member.getj():
                    if nodeDisplacementNum == 2:
                        resultRow1Num = resultRow1Num + P[2][0]
                        resultRow2Num = resultRow2Num + P[3][0]
                    elif nodeDisplacementNum == 3:
                        resultRow1Num = resultRow1Num + P[3][0]
                        resultRow2Num = resultRow2Num + member.getP()[4][0]
                        resultRow3Num = resultRow3Num + member.getP()[5][0]

            resultRow1.append(resultRow1Num)
            resultRow2.append(resultRow2Num)
            result.append(resultRow1)
            result.append(resultRow2)

            if nodeDisplacementNum == 3:
                resultRow3.append(resultRow3Num)
                result.append(resultRow3)

        return result


    def getPf(self):
        """
        Return the free loading matrix

        :return: the free loading matrix
        """
        Pf = []
        for index in self.getFreeNodalIndex():
            Pf.append(self.getGlobalP()[index])
        return Pf


    def getPs(self):
        """
        Return the support loading matrix

        :return: the support loading matrix
        """
        Ps = []
        for index in self.getSupportNodalIndex():
            Ps.append(self.getGlobalP()[index])
        return Ps


    def getAllStiffness(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        allStiffness = []
        for member in self.getMembers():
            allStiffness.append(member.getStiffness())
        return allStiffness


    def getGlobalStiffness(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        allStiffness = self.getAllStiffness()
        globalStiffness = []

        for i in range(1, self.getNodeNum()+1):

            globalStiffnessRow = []
            for j in range(1, self.getNodeNum()+1):

                # testing
                iNum = self.getNodalDisplacementNum(i)
                jNum = self.getNodalDisplacementNum(j)

                stiffnessResult = []
                for rowNum in range(iNum):
                    row = []
                    for colNum in range(jNum):
                        row.append(0)
                    stiffnessResult.append(row)
                stiffnessResultSize = self._matrixCalculator.checkMatrixSize(stiffnessResult)
                for stiffness in allStiffness:
                    if i in stiffness.getij() and j in stiffness.getij():
                        stiffnessK = stiffness.getCertainK(i, j)

                        if stiffnessResultSize == (3,3) and self._matrixCalculator.checkMatrixSize(stiffnessK) == (2,2):
                            for row in stiffnessK:
                                row.append(0)
                            stiffnessK.append([0,0,0])

                        if stiffnessResultSize == (3,2):
                            if stiffness.getType() == "truss":
                                stiffnessK.append([0,0])
                            elif stiffness.getType() == "frame":
                                for row in stiffnessK:
                                    row.pop(2)
                        elif stiffnessResultSize == (2,3):
                            if stiffness.getType() == "truss":
                                for row in stiffnessK:
                                    row.append(0)
                            elif stiffness.getType() == "frame":
                                stiffnessK.pop(2)

                        stiffnessResult = self._matrixCalculator.matrixAddition(stiffnessResult, "+", stiffnessK)


                globalStiffnessRow.append(stiffnessResult)
            globalStiffness.append(globalStiffnessRow)

        result = []
        for i in range(self.getNodeNum()):
            row1 = []
            row2 = []
            # testing
            row3 = []

            for j in range(self.getNodeNum()):
                row1.extend(globalStiffness[i][j][0])
                row2.extend(globalStiffness[i][j][1])

                if len(globalStiffness[i][j]) == 3:
                    row3.extend(globalStiffness[i][j][2])

            result.append(row1)
            result.append(row2)

            if len(row3) != 0:
                result.append(row3)

        return result


    def getFreeNodalIndex(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        nodalDisplacementList = self.getNodalDisplacement()
        resultList = []
        for index in range(len(nodalDisplacementList)):
            if isinstance(nodalDisplacementList[index], str):
                resultList.append(index)
        return resultList


    def getNodeCoordinate(self, nodeNum):
        """
        Return the coordinate of a node

        :param nodeNum: nodal ID
        :return: the coordinate of the node
        """
        for node in self.getNodes():
            if node.getID() == nodeNum:
                return node.get_xy()


    def getSupportNodalIndex(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        nodalDisplacementList = self.getNodalDisplacement()
        resultList = []
        for index in range(len(nodalDisplacementList)):
            if not isinstance(nodalDisplacementList[index], str):
                resultList.append(index)
        return resultList


    def convertListToMatrixForm(self, itemList):
        """
        Convert one-way array to two-way array

        :param itemList: one-way array
        :return: two-way array
        """
        resultMatrix = []
        for item in itemList:
            resultMatrix.append([item,])
        return resultMatrix


    def getKff(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        index = self.getFreeNodalIndex()
        K = self.getGlobalStiffness()
        Kff = []
        for indexRow in index:
            KffRow = []
            for indexCol in index:
                KffRow.append(K[indexRow][indexCol])
            Kff.append(KffRow)
        return Kff


    def getRf(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        Rf = []
        for index in self.getFreeNodalIndex():
            Rf.append(self.getNodalLoad()[index])
        return Rf


    def getrfUnknown(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        rf = []
        for index in self.getFreeNodalIndex():
            rf.append(self.getNodalDisplacement()[index])
        return rf


    """
    def getrf(self):
        KffInverse = self._matrixCalculator.matrixInversion(self.getKff(), None)
        Rf = self.convertListToMatrixForm(self.getRf())
        Pf = self.getPf()
        Rf_Pf = self._matrixCalculator.matrixAddition(Rf, "-", Pf)

        return self._matrixCalculator.matrixMultiplication(KffInverse, Rf_Pf)
    """


    def getrf(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        Kff = self.getKff()
        Rf = self.convertListToMatrixForm(self.getRf())
        Pf = self.getPf()
        Rf_Pf = self._matrixCalculator.matrixAddition(Rf, "-", Pf)

        result = self._matrixCalculator.gaussElimination(Kff, Rf_Pf)
        return self.convertListToMatrixForm(result)


    def getKsf(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        K = self.getGlobalStiffness()
        Ksf = []
        for i in self.getSupportNodalIndex():
            KsfRow = []
            for j in self.getFreeNodalIndex():
                KsfRow.append(K[i][j])
            Ksf.append(KsfRow)
        return Ksf


    def getRsUnknown(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        Rs = []
        for index in self.getSupportNodalIndex():
            Rs.append(self.getNodalLoad()[index])
        return Rs


    def getRs(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        Rs = self._matrixCalculator.matrixMultiplication(self.getKsf(), self.getrf())
        Rs = self._matrixCalculator.matrixAddition(Rs, "+", self.getPs())
        return Rs


    def getNodalDisplacementResult(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        freeNodalIndex = self.getFreeNodalIndex()
        nodalDisplacement = self.getNodalDisplacement()
        rf = self.getrf()
        for index in range(len(freeNodalIndex)):
            nodalDisplacement[freeNodalIndex[index]] = rf[index][0]
        return nodalDisplacement


    def getMemberForce(self, member):
        """
        Calculate the function title value

        :param member: required member
        :return: the function title value
        """
        r = self.getNodalDisplacementResult()
        r_e = []
        type = member.getType()
        i = member.geti()
        j = member.getj()

        if i == 1:
            iStartPosition = 0
            iEndPosition = self.getNodalDisplacementNum(i)
        else:
            iStartPosition = 0
            for pointNum in range(1, i):
                iStartPosition = iStartPosition + self.getNodalDisplacementNum(pointNum)
            iEndPosition = iStartPosition + self.getNodalDisplacementNum(i)

        r_i = []
        for index in range(iStartPosition, iEndPosition):
            r_i.append(r[index])
        if type == "truss" and self.getNodalDisplacementNum(i) == 3:
            r_i.pop(2)
        elif type == "beam" and self.getNodalDisplacementNum(i) == 3:
            r_i.pop(0)
        r_e.extend(r_i)

        if j == 1:
            jStartPosition = 0
            jEndPosition = self.getNodalDisplacementNum(j)
        else:
            jStartPosition = 0
            for pointNum in range(1, j):
                jStartPosition = jStartPosition + self.getNodalDisplacementNum(pointNum)
            jEndPosition = jStartPosition + self.getNodalDisplacementNum(j)

        r_j = []
        for index in range(jStartPosition, jEndPosition):
            r_j.append(r[index])
        if type == "truss" and self.getNodalDisplacementNum(j) == 3:
            r_j.pop(2)
        elif type == "beam" and self.getNodalDisplacementNum(j) == 3:
            r_j.pop(0)
        r_e.extend(r_j)

        r_e = self.convertListToMatrixForm(r_e)
        return member.calculateMemberForce(r_e)


    def printReadableRs(self):
        """
        Display the function title value for read
        """
        matrixInformation = self._matrixCalculator.autoCommonFactorSimplify(self.getRs())
        Rs = matrixInformation[1]
        Rs = self._matrixCalculator.matrixRoundDecimal(Rs, 2)

        print("Rs = " + matrixInformation[2] + " x ")
        for row in Rs:
            print(row)


    def printReadable_rf(self, decimalPlace):
        """
        Display the function title value for read
        """
        print("rf = ")
        for item in self._matrixCalculator.matrixRoundDecimal(self.getrf(), decimalPlace):
            print(item)


    def printReadableRf(self):
        """
        Display the function title value for read
        """
        print("Rf = ")
        for item in self.getRf():
            print(item)


    def printReadableKff(self):
        """
        Display the function title value for read
        """
        matrixInformation = self._matrixCalculator.autoCommonFactorSimplify(self.getKff())
        Kff = matrixInformation[1]
        Kff = self._matrixCalculator.matrixRoundDecimal(Kff, 2)

        print("Kff = " + matrixInformation[2] + " x ")
        for row in Kff:
            print(row)


    def printReadableKsf(self):
        """
        Display the function title value for read
        """
        matrixInformation = self._matrixCalculator.autoCommonFactorSimplify(self.getKsf())
        Ksf = matrixInformation[1]
        Ksf = self._matrixCalculator.matrixRoundDecimal(Ksf, 2)

        print("Ksf = " + matrixInformation[2] + " x ")
        for row in Ksf:
            print(row)


    def printReadableGlobalStiffness(self):
        """
        Display the function title value for read
        """
        matrixInformation = self._matrixCalculator.autoCommonFactorSimplify(self.getGlobalStiffness())
        globalStiffness = matrixInformation[1]
        globalStiffness = self._matrixCalculator.matrixRoundDecimal(globalStiffness, 2)

        print("K = " + matrixInformation[2] + " x ")
        for row in globalStiffness:
            newRow = []
            for num in row:
                newRow.append(format(num, "5.2e"))
            print(newRow)


    def printReadableP(self):
        """
        Display the function title value for read
        """
        print("P = ")
        for item in self.getGlobalP():
            print(item)


    def autoScaleMemberForceResult(self, matrix, type):
        """
        Scale the result value for the member force

        :param matrix: input matrix
        :param type: member type string
        :return: scaled result
        """
        result = []
        unit = []
        if type == "beam":

            value1 = matrix[0][0]
            unit1 = " " + self._unit[0]
            if self._unit[0] == "kN":
                value1 = value1/1000
            result.append([value1,])
            unit.append(unit1)

            value2 = matrix[1][0]
            unit2 = " " + self._unit[0] + self._unit[1]
            if self._unit[0] == "kN":
                value2 = value2/1000
            if self._unit[1] == "m":
                value2 = value2/1000
            result.append([value2,])
            unit.append(unit2)

            value3 = matrix[2][0]
            unit3 = " " + self._unit[0]
            if self._unit[0] == "kN":
                value3 = value3/1000
            result.append([value3,])
            unit.append(unit3)

            value4 = matrix[3][0]
            unit4 = " " + self._unit[0] + self._unit[1]
            if self._unit[0] == "kN":
                value4 = value4/1000
            if self._unit[1] == "m":
                value4 = value4/1000
            result.append([value4,])
            unit.append(unit4)

        if type == "frame":

            value1 = matrix[0][0]
            unit1 = " " + self._unit[0]
            if self._unit[0] == "kN":
                value1 = value1/1000
            result.append([value1,])
            unit.append(unit1)

            value2 = matrix[1][0]
            unit2 = " " + self._unit[0]
            if self._unit[0] == "kN":
                value2 = value2/1000
            result.append([value2,])
            unit.append(unit2)

            value3 = matrix[2][0]
            unit3 = " " + self._unit[0] + self._unit[1]
            if self._unit[0] == "kN":
                value3 = value3/1000
            if self._unit[1] == "m":
                value3 = value3/1000
            result.append([value3,])
            unit.append(unit3)

            value4 = matrix[3][0]
            unit4 = " " + self._unit[0]
            if self._unit[0] == "kN":
                value4 = value4/1000
            result.append([value4,])
            unit.append(unit4)

            value5 = matrix[4][0]
            unit5 = " " + self._unit[0]
            if self._unit[0] == "kN":
                value5 = value5/1000
            result.append([value5,])
            unit.append(unit5)

            value6 = matrix[5][0]
            unit6 = " " + self._unit[0] + self._unit[1]
            if self._unit[0] == "kN":
                value6 = value6/1000
            if self._unit[1] == "m":
                value6 = value6/1000
            result.append([value6,])
            unit.append(unit6)

        return [result, unit]


    def printAllResult(self):
        """
        Display all the analysis result for read
        """
        freeNodalIndex = self.getFreeNodalIndex()
        supportNodalIndex = self.getSupportNodalIndex()
        nodalDisplacement = self.getNodalDisplacement()
        nodalLoad = self.getNodalLoad()

        rf = self.getrf()
        rf = self._matrixCalculator.matrixRoundDecimal(rf, None)

        print("")
        print("Nodal Displacement:")
        for index in range(len(freeNodalIndex)):
            name = nodalDisplacement[freeNodalIndex[index]]
            if "u" in name or "v" in name:
                unit = " mm"
            else:
                unit = ""
            print(name + " = " + str(rf[index][0]) + unit)

        Rs = self.getRs()
        print("")
        print("Nodal Reaction Force:")
        for index in range(len(supportNodalIndex)):
            resultNum = Rs[index][0]
            if "M" in nodalLoad[supportNodalIndex[index]]:
                if abs(resultNum) < 10000:
                    unit = " Nmm"
                    resultNum = round(resultNum, 2)
                else:
                    unit = " kNm"
                    resultNum = round(resultNum/1000000, 2)
            else:
                if abs(resultNum) < 100:
                    unit = " N"
                    resultNum = round(resultNum, 2)
                else:
                    unit = " kN"
                    resultNum = round(resultNum/1000, 2)
            print(nodalLoad[supportNodalIndex[index]] + " = " + str(resultNum) + unit)

        print("")
        print("Member Force:")
        for member in self.getMembers():
            memberData = ""
            if member.getType() == "truss":
                memberData = " {S" + str(member.getId()) + "} = " + str(round(self.getMemberForce(member)/1000, 2)) + " kN"

            elif member.getType() == "beam":
                memberForces = self.getMemberForce(member)
                info = self.autoScaleMemberForceResult(memberForces, "beam")
                memberForces = info[0]
                unit = info[1]
                id = str(member.getId())
                i = str(member.geti())
                j = str(member.getj())
                memberData = " {F'" + id + "} : " + "Fy," + i + " = " + str(round(memberForces[0][0],2)) + unit[0] + \
                             "\n                         M" + i + " = " + str(round(-memberForces[1][0],2)) + unit[1] + \
                             "\n                       Fy," + j + " = " + str(round(-memberForces[2][0],2)) + unit[2] + \
                             "\n                         M" + j + " = " + str(round(memberForces[3][0],2)) + unit[3]

            elif member.getType() == "frame":
                memberForces = self.getMemberForce(member)
                info = self.autoScaleMemberForceResult(memberForces, "frame")
                memberForces = info[0]
                unit = info[1]
                id = str(member.getId())
                i = str(member.geti())
                j = str(member.getj())
                memberData = " {F'" + id + "} : " + "Fx," + i + " = " + str(round(-memberForces[0][0],2)) + unit[0] + \
                             "\n                       Fy," + i + " = " + str(round(memberForces[1][0],2)) + unit[1] + \
                             "\n                         M" + i + " = " + str(round(-memberForces[2][0],2)) + unit[2] + \
                             "\n                       Fx," + j + " = " + str(round(memberForces[3][0],2)) + unit[3] + \
                             "\n                       Fy," + j + " = " + str(round(-memberForces[4][0],2)) + unit[4] + \
                             "\n                         M" + j + " = " + str(round(memberForces[5][0],2)) + unit[5]

            print("Member" + str(member.getId()) + " : " + member.getType() + memberData)
            print("")


    def packAllResult(self):
        """
        Pack all the analysis result for display
        """
        result = {"nodalDisplacement": [], "reactionForce":[], "axialLoad":[], "shearForce":[], "bendingMoment":[]}

        # nodal displacement
        freeNodalIndex = self.getFreeNodalIndex()
        nodalDisplacement = self.getNodalDisplacement()
        rf = self.getrf()

        for index in range(len(freeNodalIndex)):
            name = nodalDisplacement[freeNodalIndex[index]]
            displacement = rf[index][0]
            if "u" in name or "v" in name:
                unit = " " + self._unit[1]

            else:
                unit = ""

            result["nodalDisplacement"].append([name, displacement, unit])

        # reaction force
        supportNodalIndex = self.getSupportNodalIndex()
        nodalLoad = self.getNodalLoad()
        Rs = self.getRs()

        for index in range(len(supportNodalIndex)):
            resultNum = Rs[index][0]
            result["reactionForce"].append([nodalLoad[supportNodalIndex[index]], str(resultNum)])

        # axial load + shear force + bending moment
        for member in self.getMembers():

            if member.getType() == "truss":
                axialLoad = self.getMemberForce(member)
                if axialLoad == 0:
                    axialLoad = 0
                result["axialLoad"].append([member.getId(), member.geti(), member.getj(), axialLoad, member.getL()])

            elif member.getType() == "frame":
                memberForces = self.getMemberForce(member)
                axialLoad = -memberForces[0][0]
                if axialLoad == 0:
                    axialLoad = 0
                result["axialLoad"].append([member.getId(), member.geti(), member.getj(), axialLoad, member.getL()])

                memberLoads = member.getMemberLoads().copy()

                list = memberLoads["pointMoment"].copy()
                list.append([0, -memberForces[2][0]])
                list.append([round(member.getL()), memberForces[5][0]])
                memberLoads["pointMoment"] = list

                result["bendingMoment"].append(memberLoads)

                memberLoads = member.getMemberLoads().copy()

                list = memberLoads["pointLoad"].copy()
                list.append([0, memberForces[1][0]])
                list.append([round(member.getL()), memberForces[4][0]])
                memberLoads["pointLoad"] = list

                result["shearForce"].append(memberLoads)


            elif member.getType() == "beam":
                axialLoad = 0
                result["axialLoad"].append([member.getId(), member.geti(), member.getj(), axialLoad, member.getL()])

                memberForces = self.getMemberForce(member)
                memberLoads = member.getMemberLoads().copy()

                list = memberLoads["pointMoment"].copy()
                list.append([0, -memberForces[1][0]])
                list.append([round(member.getL()), memberForces[3][0]])
                memberLoads["pointMoment"] = list

                result["bendingMoment"].append(memberLoads)

                memberLoads = member.getMemberLoads().copy()

                list = memberLoads["pointLoad"].copy()
                list.append([0, memberForces[0][0]])
                list.append([round(member.getL()), memberForces[2][0]])
                memberLoads["pointLoad"] = list

                result["shearForce"].append(memberLoads)
        return result


    def getAllResult(self):
        """
        Analyse the structure and save the result
        """
        result = ""
        freeNodalIndex = self.getFreeNodalIndex()
        supportNodalIndex = self.getSupportNodalIndex()
        nodalDisplacement = self.getNodalDisplacement()
        nodalLoad = self.getNodalLoad()
        rf = self._matrixCalculator.matrixRoundDecimal(self.getrf(), None)

        result = result + "    ----------------------------------\n"
        result = result + "    Nodal Displacement:\n"

        for index in range(len(freeNodalIndex)):
            name = nodalDisplacement[freeNodalIndex[index]]
            displacement = rf[index][0]
            if "u" in name or "v" in name:
                unit = " " + self._unit[1]
                if self._unit[1] == "m":
                    displacement = displacement/1000
            else:
                unit = ""
            result = result + "    "+name + " = " + format(displacement, "5.2e") + unit +"\n"

        Rs = self.getRs()
        result = result + "\n"
        result = result + "    Nodal Reaction Force:\n"

        for index in range(len(supportNodalIndex)):
            resultNum = Rs[index][0]
            if "M" in nodalLoad[supportNodalIndex[index]]:
                unit = " " + self._unit[0] + self._unit[1]
                if self._unit[0] == "kN":
                    resultNum = resultNum/1000
                if self._unit[1] == "m":
                    resultNum = resultNum/1000

                resultNum = round(resultNum, self._unit[2])
            else:
                unit = " " + self._unit[0]
                if self._unit[0] == "kN":
                    resultNum = resultNum/1000

                resultNum = round(resultNum, self._unit[2])
            result = result + "    "+ nodalLoad[supportNodalIndex[index]] + " = " + str(resultNum) + unit + "\n"

        result = result + "    \n"
        result = result + "    Member Force:\n"

        for member in self.getMembers():
            memberData = ""
            if member.getType() == "truss":
                trussMemberForce = self.getMemberForce(member)
                if self._unit[0] == "kN":
                    trussMemberForce = trussMemberForce/1000
                memberData = " {S" + str(member.getId()) + "} = " + str(round(trussMemberForce, self._unit[2])) + " " + self._unit[0]


            elif member.getType() == "beam":
                memberForces = self.getMemberForce(member)
                info = self.autoScaleMemberForceResult(memberForces, "beam")
                memberForces = info[0]
                unit = info[1]
                id = str(member.getId())
                i = str(member.geti())
                j = str(member.getj())
                memberData = " {F'" + id + "} : " + \
                             "\n                             Fy," + i + " = " + str(round(memberForces[0][0],self._unit[2])) + unit[0] + \
                             "\n                             M" + i + " = " + str(round(-memberForces[1][0],self._unit[2])) + unit[1] + \
                             "\n                           Fy," + j + " = " + str(round(-memberForces[2][0],self._unit[2])) + unit[2] + \
                             "\n                             M" + j + " = " + str(round(memberForces[3][0],self._unit[2])) + unit[3]

            elif member.getType() == "frame":
                memberForces = self.getMemberForce(member)
                info = self.autoScaleMemberForceResult(memberForces, "frame")
                memberForces = info[0]
                unit = info[1]
                id = str(member.getId())
                i = str(member.geti())
                j = str(member.getj())
                memberData = " {F'" + id + "} : " + \
                             "\n                           Fx," + i + " = " + str(round(-memberForces[0][0],self._unit[2])) + unit[0] + \
                             "\n                           Fy," + i + " = " + str(round(memberForces[1][0],self._unit[2])) + unit[1] + \
                             "\n                             M" + i + " = " + str(round(-memberForces[2][0],self._unit[2])) + unit[2] + \
                             "\n                           Fx," + j + " = " + str(round(memberForces[3][0],self._unit[2])) + unit[3] + \
                             "\n                           Fy," + j + " = " + str(round(-memberForces[4][0],self._unit[2])) + unit[4] + \
                             "\n                             M" + j + " = " + str(round(memberForces[5][0],self._unit[2])) + unit[5]

            result = result + "    "+ "Member" + str(member.getId()) + " : " + member.getType() + memberData + "\n"

        return result


    def printableMatrixString(self, matrix, variable):
        """
        Display the function title value for read
        """
        size = len(matrix)
        pos = math.floor(size/2)
        result = "             \n"
        for index in range(size):
            row = matrix[index]
            if index == pos:
                rowString = variable + "   =  |   "
            else:
                rowString = "           |   "
            for col in row:
                if isinstance(col, str):
                    rowString = rowString + col + "         "
                else:
                    rowString = rowString + format(col, "5.2e")+ "    "
            result = result + rowString + "|\n"

        result = result + "             "
        return result


    def createAllResultPDF(self):
        """
        Generate the PDF for the analysis result
        """
        fd = open("../results/result.txt", "w")
        # truss only
        fd.write("Truss\n")
        title = "EID      i      j            E                   A              L           Theta             AE/L           c           s          cs\n"
        fd.write(title)
        for member in self.getMembers():
            data = ""
            data = data + str(member.getId()) + "         " + str(member.geti()) + "     " + str(member.getj()) + "      "
            data = data + format(member.getE(), "5.2e") + "      " + format(member.getA(), "5.2e") +  "      " + str(member.getL()) + "      "
            data = data + format(member.getAngle(), "5.2e") + "    " + format(member.getAEL(), "5.2e") + "    "
            data = data + format(member.getc(), ".2f") + "       " + format(member.gets(), ".2f") + "     " + format(member.getcs(), ".2f") + "      \n"
            fd.write(data)

        for member in self.getMembers():
            K = member.getStiffness().getK()
            name = "K" + str(member.getId())
            fd.write(self.printableMatrixString(K, name))
            # delete
            if member.getId() == 1 or member.getId() == 6 or member.getId() == 11 or member.getId() == 16:
                fd.write("\n")


        fd.write("\n")
        Ks = self.getGlobalStiffness()
        fd.write(self.printableMatrixString(Ks, "Ks"))
        fd.write("-----------------------------------------------")

        r = self.getNodalDisplacement()
        r = self.convertListToMatrixForm(r)
        fd.write(self.printableMatrixString(r, "r   "))
        fd.write("-----------------------------------------------")
        # delete
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")

        R = self.getNodalLoad()
        R = self.convertListToMatrixForm(R)
        fd.write(self.printableMatrixString(R, "R "))
        # delete
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        """
        for member in self.getMembers():
            nameId = "P" + str(member.getId())
            fd.write(self.printableMatrixString(member.getP(), nameId))
        """
        #P = self.getGlobalP()
        #fd.write(self.printableMatrixString(P, "P "))

        fd.write("\n")
        fd.write("{Rf} = [Kff]{rf} + {Pf}\n")
        fd.write("{rf} = [Kff]^-1 * ( {Rf} - {Pf} )\n")

        fd.write(self.printableMatrixString(self.convertListToMatrixForm(self.getrfUnknown()), "rf "))
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")

        fd.write(self.printableMatrixString(self.getKff(), "Kff"))
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("\n")

        fd.write(self.printableMatrixString(self.convertListToMatrixForm(self.getRf()), "Rf"))
        #fd.write(self.printableMatrixString(self.getPf(), "Pf"))

        fd.write("\n====>")
        fd.write(self.printableMatrixString(self.getrf(), "rf"))
        fd.write("\n")
        fd.write("\n")
        rfUnknown = self.getrfUnknown()
        rf = self.getrf()
        for i in range(len(rfUnknown)):
            fd.write(rfUnknown[i] + " = " + format(rf[i][0], "5.2e") + "\n")

        fd.write("\n")
        fd.write("\n")
        fd.write("\n")
        fd.write("{Rs} = [Ksf]{rf} + {Ps}\n")

        fd.write(self.printableMatrixString(self.convertListToMatrixForm(self.getRsUnknown()), "Rs"))
        fd.write(self.printableMatrixString(self.getKsf(), "Ksf"))
        fd.write(self.printableMatrixString(self.getrf(), "rf"))
        #fd.write(self.printableMatrixString(self.getPs(), "Ps"))

        fd.write("\n====>")
        fd.write(self.printableMatrixString(self.getRs(), "Rs"))
        fd.write("\n")
        RsUnknown = self.getRsUnknown()
        Rs = self.getRs()
        for i in range(len(RsUnknown)):
            fd.write(RsUnknown[i] + " = " + format(Rs[i][0]/1000, ".2f") + " kN\n")

        fd.write("\n")
        fd.write("\n")
        fd.write("Se = AE/L * <-c,-s,c,s>{re}\n")
        fd.write("------------------------------------\n")

        r = self.getNodalDisplacementResult()
        for member2 in self.getMembers():
            #fd.write("S" + str(member2.getId()) + ":\n")
            #fd.write("AE/L = " + format(member2.getAEL(), "5.2e") + "\n")
            #fd.write("<-c,-s,c,s> = <"+str(-member2.getc())+ ", " + str(-member2.gets()) +", "+ str(member2.getc())+", "+ str(member2.gets())+">\n")
            #fd.write(self.printableMatrixString(member2.getre(r), "re"))
            fd.write("S" + str(member2.getId()) + " = " + str(round(member2.calculateTrussBasicMemberForce(r)/1000 ,2)) + " kN")
            fd.write("\n")
        fd.write("############################################")
        fd.close()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=5)
        f = open("../results/result.txt", "r")
        for x in f:
            pdf.cell(200, 10, txt=x, ln=1, align="L")
        pdf.output("result.pdf")


    def checkPowerOf10(self, num):
        """
        Format the number for the function title

        :param num: input number
        :return: formatted number
        """
        if abs(num) > 10000:
            return format(num, "5.2e")
        else:
            return round(num, self._unit[2])


    def checkPowerOf10_2(self, num):
        """
        Format the number for the function title

        :param num: input number
        :return: formatted number
        """
        return format(num, "5.2e")


    def checkAngle(self, angle):
        """
        Format the number for the function title

        :param angle: input number
        :return: formatted number
        """
        if angle == 0:
            return 0
        return str(round(1/(math.pi/angle), 2)) + "π"


    def getMemberInformationTable1(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        result = [["EID", "i", "j", "E [MPa]", "I [mm^4]", "A [mm^2]", "L [mm]", "θ"],]

        for member in self.getMembers():
            memberList = []

            memberList.append(member.getId())
            memberList.append(member.geti())
            memberList.append(member.getj())
            memberList.append(self.checkPowerOf10(member.getE()))
            try:
                memberList.append(self.checkPowerOf10(member.getI()))
            except:
                memberList.append("None")
            try:
                memberList.append(self.checkPowerOf10(member.getA()))
            except:
                memberList.append("None")
            memberList.append(self.checkPowerOf10(member.getL()))
            try:
                memberList.append(self.checkAngle(member.getAngle()))
            except:
                memberList.append(0)
            result.append(memberList)

        return result


    def getMemberInformationTable2(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        result = [["EID", "c", "s", "cs", "c^2", "s^2", "AE/L", "12EI/L^3", "6EI/L^2", "4EI/L", "2EI/L"],]

        for member in self.getMembers():
            memberList = []

            memberList.append(member.getId())

            try:
                memberList.append(self.checkPowerOf10(member.getc()))
            except:
                memberList.append("None")
            try:
                memberList.append(self.checkPowerOf10(member.gets()))
            except:
                memberList.append("None")
            try:
                memberList.append(self.checkPowerOf10(member.getcs()))
            except:
                memberList.append("None")
            try:
                memberList.append(self.checkPowerOf10(member.getc2()))
            except:
                memberList.append("None")
            try:
                memberList.append(self.checkPowerOf10(member.gets2()))
            except:
                memberList.append("None")

            try:
                memberList.append(self.checkPowerOf10(member.getAEL()))
            except:
                memberList.append("None")
            try:
                memberList.append(self.checkPowerOf10(member.get12EIL()))
            except:
                memberList.append("None")
            try:
                memberList.append(self.checkPowerOf10(member.get6EIL()))
            except:
                memberList.append("None")
            try:
                memberList.append(self.checkPowerOf10(member.get4EIL()))
            except:
                memberList.append("None")
            try:
                memberList.append(self.checkPowerOf10(member.get2EIL()))
            except:
                memberList.append("None")

            result.append(memberList)

        return result


    def getLocalStiffness(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        results = []

        for member in self.getMembers():
            result = []
            stiffness = member.getStiffness().getK()
            size = len(stiffness)
            position = size//2
            for index in range(size):
                row = stiffness[index]
                rowList = []
                if index == position:
                    rowList.append("[K" + str(member.getId()) + "] = ")
                else:
                    rowList.append(" ")
                rowList.append("|")
                for col in row:
                    rowList.append(self.checkPowerOf10_2(col))
                rowList.append("|")
                result.append(rowList)

            results.append(result)

        return results


    def getGlobalStiffnessString(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        result = []
        stiffness = self.getGlobalStiffness()
        size = len(stiffness)
        position = size//2

        for index in range(size):
            row = stiffness[index]
            rowList = []
            if index == position:
                rowList.append("[K] = ")
            else:
                rowList.append(" ")
            rowList.append("|")
            for col in row:
                rowList.append(self.checkPowerOf10_2(col))
            rowList.append("|")
            result.append(rowList)

        return result


    def getNodalDisplacementAndLoad(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        result = []
        nodalDisplacement = self.getNodalDisplacement()
        nodalLoad = self.getNodalLoad()

        size = len(nodalDisplacement)
        position = size//2

        for index in range(size):
            rowList = []
            if index == position:
                rowList.append("{r} = ")
            else:
                rowList.append(" ")
            rowList.append("|")
            rowList.append(nodalDisplacement[index])
            rowList.append("|")

            rowList.append(" ")

            if index == position:
                rowList.append("{R} = ")
            else:
                rowList.append(" ")
            rowList.append("|")
            rowList.append(nodalLoad[index])
            rowList.append("|")

            result.append(rowList)
        return result


    def getAllLocalP(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        results = []
        numberOfP = self.getMemberNum()

        num = 2
        if numberOfP%2 == 1:
            num = 1

        loop = math.ceil(numberOfP/2)

        for memberIndex in range(loop):
            members = self.getMembers()

            member1 = members[2*memberIndex]
            P1 = member1.getP()

            if num == 1 and memberIndex == loop-1:
                pass
            else:
                member2 = members[2*memberIndex+1]
                P2 = member2.getP()

            size = len(P1)
            position = size//2
            result = []

            for index in range(size):

                rowList = []
                if index == position:
                    rowList.append("{P" + str(member1.getId()) + "} = ")
                else:
                    rowList.append(" ")
                rowList.append("|")
                rowList.append(self.checkPowerOf10_2(P1[index][0]))
                rowList.append("|")

                if num == 1 and memberIndex == loop-1:
                    pass
                else:
                    rowList.append(" ")
                    if index == position:
                        rowList.append("{P" + str(member2.getId()) + "} = ")
                    else:
                        rowList.append(" ")
                    rowList.append("|")
                    rowList.append(self.checkPowerOf10_2(P2[index][0]))
                    rowList.append("|")

                result.append(rowList)
            results.append(result)
        return results


    def getGlobalPString(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        result = []
        P = self.getGlobalP()
        size = len(P)
        position = size//2

        for index in range(size):
            row = P[index]
            rowList = []
            if index == position:
                rowList.append("{P} = ")
            else:
                rowList.append(" ")
            rowList.append("|")
            for col in row:
                rowList.append(self.checkPowerOf10_2(col))
            rowList.append("|")
            result.append(rowList)

        return result


    def getKffString(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        result = []
        Kff = self.getKff()
        size = len(Kff)
        position = size//2

        for index in range(size):
            row = Kff[index]
            rowList = []
            if index == position:
                rowList.append("[Kff] = ")
            else:
                rowList.append(" ")
            rowList.append("|")
            for col in row:
                rowList.append(self.checkPowerOf10_2(col))
            rowList.append("|")
            result.append(rowList)

        return result


    def getRfString(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        result = []
        Rf = self.getRf()
        size = len(Rf)
        position = size//2

        for index in range(size):
            row = Rf[index]
            rowList = []
            if index == position:
                rowList.append("{Rf} = ")
            else:
                rowList.append(" ")
            rowList.append("|")
            rowList.append(self.checkPowerOf10_2(row))
            rowList.append("|")
            result.append(rowList)

        return result


    def getPfString(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        result = []
        Pf = self.getPf()
        size = len(Pf)
        position = size//2

        for index in range(size):
            row = Pf[index]
            rowList = []
            if index == position:
                rowList.append("{Pf} = ")
            else:
                rowList.append(" ")
            rowList.append("|")
            for col in row:
                rowList.append(self.checkPowerOf10_2(col))
            rowList.append("|")
            result.append(rowList)

        return result


    def get_rfString(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        result = []
        rfUnknown = self.getrfUnknown()
        rf = self.getrf()

        size = len(rf)
        position = size//2
        for index in range(size):
            row = rf[index]
            rowList = []
            if index == position:
                rowList.append("==>  {rf} = ")
            else:
                rowList.append(" ")
            rowList.append(" ")
            rowList.append("|")
            rowList.append(rfUnknown[index])
            rowList.append("|")
            rowList.append(" ")
            if index == position:
                rowList.append(" = ")
            else:
                rowList.append(" ")
            rowList.append(" ")
            rowList.append("|")
            for col in row:
                rowList.append(self.checkPowerOf10_2(col))
            rowList.append("|")
            result.append(rowList)

        return result


    def getKsfString(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        result = []
        Ksf = self.getKsf()
        size = len(Ksf)
        position = size//2

        for index in range(size):
            row = Ksf[index]
            rowList = []
            if index == position:
                rowList.append("[Ksf] = ")
            else:
                rowList.append(" ")
            rowList.append("|")
            for col in row:
                rowList.append(self.checkPowerOf10_2(col))
            rowList.append("|")
            result.append(rowList)

        return result


    def getPsString(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        result = []
        Ps = self.getPs()
        size = len(Ps)
        position = size//2

        for index in range(size):
            row = Ps[index]
            rowList = []
            if index == position:
                rowList.append("{Ps} = ")
            else:
                rowList.append(" ")
            rowList.append("|")
            for col in row:
                rowList.append(self.checkPowerOf10_2(col))
            rowList.append("|")
            result.append(rowList)

        return result


    def getRsString(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        result = []
        RsUnknown = self.getRsUnknown()
        Rs = self.getRs()

        size = len(Rs)
        position = size//2
        for index in range(size):
            row = Rs[index]
            rowList = []
            if index == position:
                rowList.append("==>  {Rs} = ")
            else:
                rowList.append(" ")
            rowList.append(" ")
            rowList.append("|")
            rowList.append(RsUnknown[index])
            rowList.append("|")
            rowList.append(" ")
            if index == position:
                rowList.append(" = ")
            else:
                rowList.append(" ")
            rowList.append(" ")
            rowList.append("|")
            for col in row:
                rowList.append(self.checkPowerOf10_2(col))
            rowList.append("|")
            result.append(rowList)

        return result


    def getLocalMemberForce(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        results = []

        for member in self.getMembers():
            result = []

            if member.getType() == "truss":
                result.append(["Truss: member"+ str(member.getId())])
                result.append(["S"+ str(member.getId())+ " = (AE/L) x <-c,-s,c,s>{r" + str(member.getId()) + "} = "
                               + format(self.getMemberForce(member), "5.2e"),])

            elif member.getType() == "beam":
                memberForces = self.getMemberForce(member)

                size = len(memberForces)
                position = size//2
                result.append(["Beam: member"+ str(member.getId())])
                for index in range(size):
                    row = memberForces[index]
                    rowList = []
                    if index == position:
                        rowList.append("{F'"+ str(member.getId()) +"} = [K" +str(member.getId())
                                       + "]{r"+str(member.getId())+"} + {P"+str(member.getId())+"} = ")
                    else:
                        rowList.append(" ")
                    rowList.append("|")
                    for col in row:
                        rowList.append(self.checkPowerOf10_2(col))
                    rowList.append("|")
                    result.append(rowList)

            elif member.getType() == "frame":
                memberForces = self.getMemberForce(member)

                size = len(memberForces)
                position = size//2
                result.append(["Frame: member"+ str(member.getId())])
                for index in range(size):
                    row = memberForces[index]
                    rowList = []
                    if index == position:
                        rowList.append("{F'"+ str(member.getId()) +"} = ([K" +str(member.getId())
                                       + "]{r"+str(member.getId())+"} + {P"+str(member.getId())+"}) x [LD] = ")
                    else:
                        rowList.append(" ")
                    rowList.append("|")
                    for col in row:
                        rowList.append(self.checkPowerOf10_2(col))
                    rowList.append("|")
                    result.append(rowList)

            results.append(result)
        return results


# testing only

"""
# truss testing CIVL3340 L6 Example 6.1
structure = Structure()
structure.addNode(1,0,0,"FFR")
structure.addNode(2,5000,0,"RFR")
structure.addNode(3,5000,8660,"RRR")
structure.addNode(4,10000,8660,"RRR")

structure.addNodalLoad(4, 2.82*(10**5), -2.82*(10**5), 0)

structure.addMember(1,1,2,10**4,None,2*(10**5), "truss")
structure.addMember(2,3,4,10**4,None,2*(10**5), "truss")
structure.addMember(3,1,3,1.5*(10**4),None,2*(10**5), "truss")
structure.addMember(4,2,4,1.5*(10**4),None,2*(10**5), "truss")
structure.addMember(5,2,3,1.5*(10**4),None,2*(10**5), "truss")

structure.printAllResult()
"""


"""
# beam testing CIVL3340 L7 Example 7.1
structure = Structure()
structure.addNode(1,0,0,"FFF")
structure.addNode(2,4000,0,"RFR")
structure.addNode(3,8000,0,"RFR")

structure.addNodalLoad(2, 0, 0, 12000000)

structure.addMember(1,1,2,None,2.5*(10**8),2.1*(10**5),"beam")
structure.addMember(2,2,3,None,2.5*(10**8),2.1*(10**5),"beam")
structure.addMemberPointLoad(1,2000,-6000)
structure.addMemberPointLoad(2,2000,-3000)

structure.printAllResult()
"""


"""
# frame testing CIVL3340 L8 Example 8.1
structure = Structure()
structure.addNode(1,0,0,"RRR")
structure.addNode(2,-100,0,"FFF")
structure.addNode(3,100,-75,"FFF")

structure.addNodalLoad(1, 0, -10, -1000)

structure.addMember(1,2,1,10,10**3,10**4,"frame")
structure.addMember(2,1,3,10,10**3,10**4,"frame")

structure.addGlobalMemberPointLoad(2,62.5,0,-20)
structure.addMemberUniformlyDistributedLoad(1, -0.24)

structure.printAllResult()
"""


"""
# frame + truss element testing CIVL3340 Tutorial 9 half structure
structure = Structure()
structure.addNode(1,0,0,"RFR")
structure.addNode(2,-3000,-2000,"FFR")
structure.addNode(3,-3000,-4000,"FFF")

structure.addMember(1,2,1,50,None,10**5,"truss")
structure.addMember(2,3,1,25,10**7,10**5,"frame")

structure.addGlobalMemberPointLoad(2,2500,25000,0)

structure.printAllResult()
"""


"""
# frame + truss element testing CIVL3340 Tutorial 9 whole structure
structure = Structure()
structure.addNode(1,0,0,"RRR")
structure.addNode(2,-3000,-2000,"FFR")
structure.addNode(3,-3000,-4000,"FFF")
structure.addNode(4,3000,-2000,"FFR")
structure.addNode(5,3000,-4000,"FFF")

structure.addMember(1,2,1,50,None,10**5,"truss")
structure.addMember(2,3,1,25,10**7,10**5,"frame")
structure.addMember(3,4,1,50,None,10**5,"truss")
structure.addMember(4,5,1,25,10**7,10**5,"frame")

structure.addGlobalMemberPointLoad(2,2500,25000,0)
structure.addGlobalMemberPointLoad(4,2500,25000,0)

structure.printAllResult()
"""


"""
# CIVL3340 Assignment 2 Q5 testing PASS!
structure = Structure()
structure.addNode(1,0,0,"FFR")
structure.addNode(2,0,9000,"RRR")
structure.addNode(3,8000,0,"RRR")
structure.addNode(4,8000,9000,"RRR")
structure.addNode(5,16000,0,"RFR")
structure.addNode(6,16000,9000,"RRR")
structure.addNode(7,24000,0,"RRR")
structure.addNode(8,24000,9000,"RRR")
structure.addNode(9,32000,0,"FFR")
structure.addNode(10,32000,9000,"RRR")

structure.addMember(1,1,2,6660,None,2*(10**5),"truss")
structure.addMember(2,3,2,6660,None,2*(10**5),"truss")
structure.addMember(3,3,4,6660,None,2*(10**5),"truss")
structure.addMember(4,2,4,5210,None,2*(10**5),"truss")
structure.addMember(5,1,3,5210,None,2*(10**5),"truss")
structure.addMember(6,3,6,6660,None,2*(10**5),"truss")
structure.addMember(7,4,6,5210,None,2*(10**5),"truss")
structure.addMember(8,5,6,6660,None,2*(10**5),"truss")
structure.addMember(9,3,5,5210,None,2*(10**5),"truss")
structure.addMember(10,7,6,6660,None,2*(10**5),"truss")
structure.addMember(11,5,7,5210,None,2*(10**5),"truss")
structure.addMember(12,6,8,5210,None,2*(10**5),"truss")
structure.addMember(13,7,8,6660,None,2*(10**5),"truss")
structure.addMember(14,7,10,6660,None,2*(10**5),"truss")
structure.addMember(15,8,10,5210,None,2*(10**5),"truss")
structure.addMember(16,9,10,6660,None,2*(10**5),"truss")
structure.addMember(17,7,9,5210,None,2*(10**5),"truss")

structure.addNodalLoad(2,0,-50000,0)
structure.addNodalLoad(4,0,-100000,0)
structure.addNodalLoad(6,0,-100000,0)
structure.addNodalLoad(8,0,-100000,0)
structure.addNodalLoad(10,0,-50000,0)

structure.printAllResult()
"""


"""
# frame testing CIVL3340 Assignment 3 Q2 (Anti-Symmetric System)
structure = Structure()
structure.addNode(1,0,0,"RRR")
structure.addNode(2,0,-6000,"FFF")
structure.addNode(3,750,0,"RFR")

structure.addMember(1,2,1,1.14*(10**4),48.4*(10**6),2*(10**5),"frame")
structure.addMember(2,1,3,1.6*(10**4),986*(10**6),2*(10**5),"frame")

structure.addGlobalMemberPointLoad(1,5250,25*(10**3),0)

structure.printAllResult()
"""


"""
# truss testing
structure = Structure()
structure.addNode(1,0,0,"FFR")
structure.addNode(2,5000,0,"RRR")
structure.addNode(3,11000,0,"FFR")
structure.addNode(4,11000,-8000,"FFR")

structure.addNodalLoad(2, -10*math.cos(math.pi/4)*(10**3), -10*math.sin(math.pi/4)*(10**3), 0)

structure.addMember(1,1,2,10000,None,2*(10**5), "truss")
structure.addMember(2,2,3,20000,None,2*(10**5), "truss")
structure.addMember(3,2,4,10000,None,2*(10**5), "truss")

structure.printAllResult()
"""


"""
I = (10**8)
E = 200*(10**3)

structure = Structure()
structure.addNode(1,0,0,"FFF")
structure.addNode(2,2000,0,"RFR")
structure.addNode(3,5000,0,"RFR")
structure.addNode(4,9000,0,"FFF")

structure.addMember(1,1,2,None,I,E,"beam")
structure.addMember(2,2,3,None,I,E,"beam")
structure.addMember(3,3,4,None,I,E,"beam")

structure.addMemberUniformlyDistributedLoad(2, -4)
structure.addMemberPointLoad(3, 2000, -10000)

delta = 2 # [mm]


for m in structure.getMembers():
    if m.getId() == 2:
        m.addP([[12*E*I*delta/(3000**3),],
                [6*E*I*delta/(3000**2),],
                [-12*E*I*delta/(3000**3),],
                [6*E*I*delta/(3000**2),]])
    if m.getId() == 3:
        m.addP([[-12*E*I*delta/(4000**3),],
                [-6*E*I*delta/(4000**2),],
                [12*E*I*delta/(4000**3),],
                [-6*E*I*delta/(4000**2),]])

structure.printAllResult()
"""


"""
structure = Structure()
structure.addNode(1,0,0,"FFF")
structure.addNode(2,3000,6000,"RRR")
structure.addNode(3,8000,6000,"FFF")

structure.addMember(1,1,2,(10**4),(10**7),2*(10**5),"frame")
structure.addMember(2,2,3,(10**4),(10**7),2*(10**5),"frame")

structure.addGlobalMemberPointLoad(2,2500,0,-10000)

structure.printAllResult()
"""
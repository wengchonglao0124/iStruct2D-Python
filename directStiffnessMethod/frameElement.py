from directStiffnessMethod.member import Member
import math
from directStiffnessMethod.frameStiffness import FrameStiffness
from directStiffnessMethod.matrixCalculation import MatrixCalculation

class FrameElement(Member):
    """
    Frame element member
    """

    def __init__(self, id, i, j, A, I, E, L, angle):
        """
        Initiating the frame element

        :param id: member ID
        :param i: starting node
        :param j: ending node
        :param A: area value of this member
        :param I: area Moment of Inertia
        :param E: elasticity
        :param L: length of the member
        :param angle: rotational angle of the member
        """
        super().__init__(id, i, j, E, L)
        self._I = I
        self._A = A
        self._angle = angle
        self._c = math.cos(angle)
        self._s = math.sin(angle)

        self._allP = [[[0,],
                       [0,],
                       [0,],
                       [0,],
                       [0,],
                       [0,]] ,]

        self._stiffness = FrameStiffness(id, i, j, A, I, E, L, self._c, self._s)
        self._matrixCalculator = MatrixCalculation()

        self._memberLoads = {"pointLoad": [], "uniformlyDistributedLoad":[], "id":self.getId(), "pointMoment":[]}


    def getType(self):
        """
        Return the type string of this member

        :return: type string of this member
        """
        return "frame"


    def getMemberLoads(self):
        """
        Return all the loading on this member

        :return: loading on this member
        """
        return self._memberLoads


    def getLD(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return self.getStiffness().get_LD()


    def addP(self, P):
        """
        Add the loading matrix into this member

        :param P: loading  matrix
        """
        self._allP.append(P)


    def addUniformlyDistributedLoad(self, w):
        """
        Add the UDL into this member

        :param w: UDL
        """
        Pw = [[0,],
              [-w*self._L/2,],
              [-w*(self._L**2)/12,],
              [0,],
              [-w*self._L/2,],
              [w*(self._L**2)/12,]]
        self.addP(Pw)
        self._memberLoads["uniformlyDistributedLoad"].append(w)


    def addPointLoad(self, x, P):
        """
        Add the point load into this member

        :param x: distance for the point load on the member from starting node
        :param P: point load magnitude
        """
        a = x
        b = self._L - x
        L = self._L
        Pp = [[0,],
              [-P+(P*a/L)*(1-(b**2-a*b)/(L**2))],
              [-P*a*(b**2)/(L**2)],
              [0,],
              [-(P*a/L)*(1-(b**2-a*b)/(L**2))],
              [P*(a**2)*b/(L**2)]]
        self.addP(Pp)
        self._memberLoads["pointLoad"].append([x,P])


    def addGlobalPointLoad(self, x, Px, Py):
        """
        Add the global point load into this member

        :param x: distance for the point load on the member from starting node
        :param Px: point load magnitude for x direction
        :param Py: point load magnitude for y direction
        """
        a = x
        b = self._L - x
        L = self._L
        Pp = [[-Px*(a/L),],
              [-Py+(Py*a/L)*(1-(b**2-a*b)/(L**2))],
              [-Py*a*(b**2)/(L**2)],
              [-Px*(b/L),],
              [-(Py*a/L)*(1-(b**2-a*b)/(L**2))],
              [Py*(a**2)*b/(L**2)]]
        self.addP(Pp)
        self._memberLoads["pointLoad"].append([x,Py])


    def getI(self):
        """
        Get the Area Moment of Inertia

        :return: Area Moment of Inertia
        """
        return self._I


    def getEI(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return self._E*self._I


    def getA(self):
        """
        Get the area value of this member

        :return: area value of this member
        """
        return self._A


    def getStiffness(self):
        """
        Return the stiffness matrix of this member

        :return: stiffness matrix of this member
        """
        return self._stiffness


    def getAEL(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return (self._A*self._E)/self._L


    def getc(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return self._c


    def getc2(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return self._c**2


    def gets(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return self._s


    def gets2(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return self._s**2


    def getcs(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return self._c*self._s


    def getAngle(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return self._angle


    def getP(self):
        """
        Return the loading matrix of this member

        :return: the loading matrix of this member
        """
        result = self._allP[0]
        for item in self._allP:
            result = self._matrixCalculator.matrixAddition(result, "+", item)

        if self.getAngle() != 0 and self.getAngle() != math.pi:
            result = self._matrixCalculator.matrixMultiplication(self.getStiffness().get_LD_transpose(), result)

        return result


    def getCertainP(self, pointNum):
        """
        Return the specific loading matrix of this member

        :param pointNum: loading ID
        :return: the specific loading matrix of this member by ID
        """
        P = self.getP()
        if pointNum == self.geti():
            return [P[0],
                    P[1],
                    P[2]]
        elif pointNum == self.getj():
            return [P[3],
                    P[4],
                    P[5]]


    def calculateMemberForce(self, r_e):
        """
        Calculate the member force of this member

        :param r_e: nodal displacement
        :return: member force of this member
        """
        Ke = self.getStiffness().getK()
        Pe = self.getP()
        LDe = self.getLD()

        result = self._matrixCalculator.matrixMultiplication(Ke, r_e)
        result = self._matrixCalculator.matrixAddition(result, "+", Pe)
        result = self._matrixCalculator.matrixMultiplication(LDe, result)
        return result


    def printReadableEIL(self):
        """
        Display the details of the member matrix
        """
        print("----------------------------")
        print("Member " + str(self.getId()) + " : ")
        print("EA/L =", format(self._E*self._A/(self._L), "5.2e"))
        print("")
        print("12EI/L^3 =", format(12*self.getEI()/(self._L**3), "5.2e"))
        print("")
        print("6EI/L^2 =", format(6*self.getEI()/(self._L**2), "5.2e"))
        print("")
        print("4EI/L =", format(4*self.getEI()/(self._L**1), "5.2e"))
        print("")
        print("2EI/L =", format(2*self.getEI()/(self._L**1), "5.2e"))


    def printReadableLD(self):
        """
        Display the LD value for read
        """
        print("----------------------------")
        print("Member " + str(self.getId()) + " : ")
        print("LD = ")
        for row in self.getLD():
            print(row)


    def get12EIL(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return 12*self.getEI()/(self._L**3)


    def get6EIL(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return 6*self.getEI()/(self._L**2)


    def get4EIL(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return 4*self.getEI()/(self._L**1)


    def get2EIL(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return 2*self.getEI()/(self._L**1)
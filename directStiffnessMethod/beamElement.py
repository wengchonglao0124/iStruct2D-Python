from directStiffnessMethod.member import Member
from directStiffnessMethod.beamStiffness import BeamStiffness
from directStiffnessMethod.matrixCalculation import MatrixCalculation

class BeamElement(Member):
    """
    Beam element member
    """

    def __init__(self, id, i, j, I, E, L):
        """
        Initiating the beam element

        :param id: member ID
        :param i: starting node
        :param j: ending node
        :param I: area Moment of Inertia
        :param E: elasticity
        :param L: length of the member
        """
        super().__init__(id,i,j,E,L)
        self._I = I

        self._stiffness = BeamStiffness(id, i, j, I, E, L)
        self._matrixCalculator = MatrixCalculation()

        self._memberLoads = {"pointLoad": [], "uniformlyDistributedLoad":[], "id":self.getId(), "pointMoment":[]}


    def getType(self):
        """
        Return the type string of this member

        :return: type string of this member
        """
        return "beam"


    def getMemberLoads(self):
        """
        Return all the loading on this member

        :return: loading on this member
        """
        return self._memberLoads


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
        Pw = [[-w*self._L/2,],
              [-w*(self._L**2)/12,],
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
        Pp = [[-P+(P*a/L)*(1-(b**2-a*b)/(L**2))],
              [-P*a*(b**2)/(L**2)],
              [-(P*a/L)*(1-(b**2-a*b)/(L**2))],
              [P*(a**2)*b/(L**2)]]
        self.addP(Pp)
        self._memberLoads["pointLoad"].append([x,P])


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


    def getStiffness(self):
        """
        Return the stiffness matrix of this member

        :return: stiffness matrix of this member
        """
        return self._stiffness


    def getP(self):
        """
        Return the loading matrix of this member

        :return: the loading matrix of this member
        """
        result = self._allP[0]
        for item in self._allP:
            result = self._matrixCalculator.matrixAddition(result, "+", item)
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
                    P[1]]
        elif pointNum == self.getj():
            return [P[2],
                    P[3]]


    def calculateMemberForce(self, r_e):
        """
        Calculate the member force of this member

        :param r_e: nodal displacement
        :return: member force of this member
        """
        Ke = self.getStiffness().getK()
        Pe = self.getP()

        result = self._matrixCalculator.matrixMultiplication(Ke, r_e)
        result = self._matrixCalculator.matrixAddition(result, "+", Pe)
        return result


    def printReadable_re(self, r):
        """
        Print the nodal displacement for read

        :param r: nodal displacement
        """
        r_e = []
        r_e.append([r[2*(self.geti()-1)],])
        r_e.append([r[2*(self.geti()-1)+1],])
        r_e.append([r[2*(self.getj()-1)],])
        r_e.append([r[2*(self.getj()-1)+1],])
        print("r" + str(self.getId()) + " = ")
        for item in r_e:
            print(item)
        print("")


    def printReadableP(self):
        """
        Print the loading matrix for read
        """
        P = self.getP()
        print("----------------------")
        print("P" + str(self.getId()) + " = ")
        for item in P:
            print(item)


    def printReadableMemberForce(self, r):
        """
        Print the member forces for read

        :param r: nodal displacement
        """
        self.printReadable_re(r)
        self.printReadableP()
        data = self.calculateMemberForce(r)
        print("F'" + str(self.getId()) + " = ")
        for item in data:
            print(item)
        print("")


    def printReadableEIL(self):
        """
        Display the details of the member matrix
        """
        print("----------------------------")
        print("Member " + str(self.getId()) + " : ")
        print("12EI/L^3 =", format(12*self.getEI()/(self._L**3), "5.2e"))
        print("")
        print("6EI/L^2 =", format(6*self.getEI()/(self._L**2), "5.2e"))
        print("")
        print("4EI/L =", format(4*self.getEI()/(self._L**1), "5.2e"))
        print("")
        print("2EI/L =", format(2*self.getEI()/(self._L**1), "5.2e"))


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


# testing only
"""
beam = BeamElement(2,9,7,9000,300,10)
print(beam.getId())
print(beam.geti())
print(beam.getj())
print(beam.getI())
print(beam.getE())
print(beam.getL())
print(beam.getCertainP(9))
"""
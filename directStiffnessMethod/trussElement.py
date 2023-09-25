from directStiffnessMethod.trussStiffness import TrussStiffness
from directStiffnessMethod import matrixCalculation
import math
from directStiffnessMethod.member import Member

class TrussElement(Member):
    """
    Truss element member
    """

    def __init__(self, id, i, j, A, E, L, angle):
        """
        Initiating the truss element

        :param id: member ID
        :param i: starting node
        :param j: ending node
        :param A: area value of this member
        :param E: elasticity
        :param L: length of the member
        :param angle: rotational angle of the member
        """
        super().__init__(id, i, j, E, L)
        self._A = A
        self._c = math.cos(angle)
        self._s = math.sin(angle)
        self._angle = angle

        self._stiffness = TrussStiffness(id, i, j, A, E, L, self._c, self._s)
        self._matrixCalculator = matrixCalculation.MatrixCalculation()


    def getP(self):
        """
        Return the loading matrix of this member

        :return: the loading matrix of this member
        """
        return self._allP[0]


    def getA(self):
        """
        Get the area value of this member

        :return: area value of this member
        """
        return self._A


    def getType(self):
        """
        Return the type string of this member

        :return: type string of this member
        """
        return "truss"


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


    def getStiffness(self):
        """
        Return the stiffness matrix of this member

        :return: stiffness matrix of this member
        """
        return self._stiffness


    def calculateMemberForce(self, r_e):
        """
        Calculate the member force of this member

        :param r_e: nodal displacement
        :return: member force of this member
        """
        k = [[-self.getc(), -self.gets(), self.getc(), self.gets()]]
        S = self.getAEL()*(self._matrixCalculator.matrixMultiplication(k, r_e))[0][0]
        return S


"""
# testing only
truss = TrussElement(1,2,5,1000,2000,10,math.pi)
print(truss.getId())
print(truss.geti())
print(truss.getj())
print(truss.getA())
print(truss.getE())
print(truss.getL())
print(truss.getAngle())
"""
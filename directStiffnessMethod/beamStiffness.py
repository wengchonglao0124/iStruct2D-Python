from directStiffnessMethod.matrixCalculation import MatrixCalculation

class BeamStiffness(object):
    """
    Beam stiffness for member
    """

    def __init__(self, id, i, j, I, E, L):
        """
        Initiating the beam stiffness for member

        :param id: member ID
        :param i: starting node
        :param j: ending node
        :param I: area Moment of Inertia
        :param E: elasticity
        :param L: length of the member
        """
        self._id = id
        self._i = i
        self._j = j
        self._I = I
        self._E = E
        self._L = L
        self._matrixCalculator = MatrixCalculation()


    def getEI(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return self._E*self._I


    def getId(self):
        """
        Return the member ID

        :return: member ID
        """
        return self._id


    def geti(self):
        """
        Return the starting node

        :return: starting node
        """
        return self._i


    def getj(self):
        """
        Return the ending node

        :return: ending node
        """
        return self._j


    def getij(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return [self.geti(), self.getj()]


    def getKxxSize(self):
        """
        Return the size of this stiffness matrix

        :return: size of this stiffness matrix
        """
        return 2


    def getType(self):
        """
        Return the member type string

        :return: the member type string
        """
        return "beam"


    def getKii(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        self._Kii = [[12*self.getEI()/(self._L**3), 6*self.getEI()/(self._L**2)],
                     [6*self.getEI()/(self._L**2), 4*self.getEI()/(self._L**1)]]
        return self._Kii


    def getKij(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        self._Kij = [[-12*self.getEI()/(self._L**3), 6*self.getEI()/(self._L**2)],
                     [-6*self.getEI()/(self._L**2), 2*self.getEI()/(self._L**1)]]
        return self._Kij


    def getKji(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        self._Kji = [[-12*self.getEI()/(self._L**3), -6*self.getEI()/(self._L**2)],
                     [6*self.getEI()/(self._L**2), 2*self.getEI()/(self._L**1)]]
        return self._Kji


    def getKjj(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        self._Kjj = [[12*self.getEI()/(self._L**3), -6*self.getEI()/(self._L**2)],
                     [-6*self.getEI()/(self._L**2), 4*self.getEI()/(self._L**1)]]
        return self._Kjj


    def getCertainK(self, i, j):
        """
        Return the K matrix by row and col

        :param i: row
        :param j: col
        :return: the K matrix by row and col
        """
        if i == self.geti() and j == self.geti():
            return self.getKii()
        elif i == self.geti() and j == self.getj():
            return self.getKij()
        elif i == self.getj() and j == self.geti():
            return self.getKji()
        elif i == self.getj() and j == self.getj():
            return self.getKjj()


    def getK(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        self._K = [[self.getKii(), self.getKij()],
                   [self.getKji(), self.getKjj()]]

        result = []
        for i in range(2):
            row1 = []
            row2 = []
            for j in range(2):
                row1.extend(self._K[i][j][0])
                row2.extend(self._K[i][j][1])
            result.append(row1)
            result.append(row2)

        return result


    def printReadableK(self):
        """
        Print the K matrix for read
        """
        matrixInformation = self._matrixCalculator.autoCommonFactorSimplify(self.getK())
        stiffness = matrixInformation[1]
        stiffness = self._matrixCalculator.matrixRoundDecimal(stiffness, 2)

        print("----------------------------------------")
        print("K" + str(self.getId()) + " = " + matrixInformation[2] + " x ")
        for row in stiffness:
            print(row)


# testing only
"""
x = BeamStiffness(1,1,2,2.5*(10**8),2.1*(10**5),4000)
x.printReadableK()

"""
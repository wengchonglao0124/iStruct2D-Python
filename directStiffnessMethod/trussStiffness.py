from directStiffnessMethod import matrixCalculation

class TrussStiffness(object):
    """
    Truss stiffness for member
    """

    def __init__(self, id, i, j, A, E, L, c, s):
        """
        Initiating the truss stiffness for member

        :param id: member ID
        :param i: starting node
        :param j: ending node
        :param A: area value of this member
        :param E: elasticity
        :param L: length of the member
        :param c: cosine value of the member angle
        :param s: sine value of the member angle
        """
        self._id = id
        self._i = i
        self._j = j
        self._A = A
        self._E = E
        self._L = L
        self._c = c
        self._s = s
        self._matrixCalculator = matrixCalculation.MatrixCalculation()


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


    def getAEL(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return (self._A*self._E)/self._L


    def getType(self):
        """
        Return the member type string

        :return: the member type string
        """
        return "truss"


    def getKxxSize(self):
        """
        Return the size of this stiffness matrix

        :return: size of this stiffness matrix
        """
        return 2


    def getKii(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        self._Kii = [[self._c**2, self._c*self._s],
                     [self._c*self._s, self._s**2]]
        return self._matrixCalculator.matrixScale(self._Kii, self.getAEL())


    def getKij(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        self._Kij = [[-self._c**2, -self._c*self._s],
                     [-self._c*self._s, -self._s**2]]
        return self._matrixCalculator.matrixScale(self._Kij, self.getAEL())


    def getKji(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        self._Kji = [[-self._c**2, -self._c*self._s],
                     [-self._c*self._s, -self._s**2]]
        return self._matrixCalculator.matrixScale(self._Kji, self.getAEL())


    def getKjj(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        self._Kjj = [[self._c**2, self._c*self._s],
                     [self._c*self._s, self._s**2]]
        return self._matrixCalculator.matrixScale(self._Kjj, self.getAEL())


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
        print("K"+str(self.getId())+" = ")
        for row in self.getK():
            print(row)
        print("")


# testing only
"""
x = TrussStiffness(1,1,2,10**4,2*(10**5),5000,1,0)
for y in x.getK():
    print(y)
"""
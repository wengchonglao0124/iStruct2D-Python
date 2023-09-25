from directStiffnessMethod.matrixCalculation import MatrixCalculation

class FrameStiffness(object):
    """
    Frame stiffness for member
    """

    def __init__(self, id, i, j, A, I, E, L, c, s):
        """
        Initiating the frame stiffness for member

        :param id: member ID
        :param i: starting node
        :param j: ending node
        :param A: area value of this member
        :param I: area Moment of Inertia
        :param E: elasticity
        :param L: length of the member
        :param c: cosine value of the member angle
        :param s: sine value of the member angle
        """
        self._id = id
        self._i = i
        self._j = j
        self._I = I
        self._E = E
        self._L = L
        self._A = A
        self._c = c
        self._s = s
        self._matrixCalculator = MatrixCalculation()
        self._K = self.getK()


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


    def getAEL(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return (self._A*self._E)/self._L


    def getK(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        k = [[4*self.getEI()/self._L, 2*self.getEI()/self._L, 0],
             [2*self.getEI()/self._L, 4*self.getEI()/self._L, 0],
             [0, 0, self.getAEL()]]

        T = [[0, 1/self._L, 1, 0, -1/self._L, 0],
             [0, 1/self._L, 0, 0, -1/self._L, 1],
             [-1, 0, 0, 1, 0, 0]]

        T_transpose = self._matrixCalculator.matrixTranspose(T)
        local_k = self._matrixCalculator.matrixMultiplication(T_transpose, k)
        local_k = self._matrixCalculator.matrixMultiplication(local_k, T)

        LB = [[self._c, self._s, 0],
              [-self._s, self._c, 0],
              [0, 0, 1]]

        LD_outlook = [[LB, 0],
                      [0, LB]]

        LD = []
        for i in range(2):
            LD_row1 = []
            LD_row2 = []
            LD_row3 = []
            for j in range(2):
                if LD_outlook[i][j] == 0:
                    LD_row1.extend([0,0,0])
                    LD_row2.extend([0,0,0])
                    LD_row3.extend([0,0,0])
                else:
                    LD_row1.extend(LD_outlook[i][j][0])
                    LD_row2.extend(LD_outlook[i][j][1])
                    LD_row3.extend(LD_outlook[i][j][2])
            LD.append(LD_row1)
            LD.append(LD_row2)
            LD.append(LD_row3)

        self._LD = LD

        self._LD_transpose = self._matrixCalculator.matrixTranspose(LD)
        K = self._matrixCalculator.matrixMultiplication(self._LD_transpose, local_k)
        K = self._matrixCalculator.matrixMultiplication(K, LD)

        return K


    def get_LD_transpose(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return self._LD_transpose


    def get_LD(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return self._LD


    def getKxxSize(self):
        """
        Return the size of this stiffness matrix

        :return: size of this stiffness matrix
        """
        return 3


    def getType(self):
        """
        Return the member type string

        :return: the member type string
        """
        return "frame"


    def getKii(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        K = self.getK()
        Kii = [K[0][0:3],
               K[1][0:3],
               K[2][0:3]]
        return Kii


    def getKij(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        K = self.getK()
        Kij = [K[0][3:6],
               K[1][3:6],
               K[2][3:6]]
        return Kij


    def getKji(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        K = self.getK()
        Kji = [K[3][0:3],
               K[4][0:3],
               K[5][0:3]]
        return Kji


    def getKjj(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        K = self.getK()
        Kjj = [K[3][3:6],
               K[4][3:6],
               K[5][3:6]]
        return Kjj


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


    def printReadableK(self):
        """
        Print the K matrix for read
        """
        print("K"+str(self.getId())+" = ")
        for row in self.getK():
            newRow = []
            for num in row:
                newRow.append(format(num, "5.2e"))
            print(newRow)
        print("")


# testing only
"""
stiffness1 = FrameStiffness(1,2,1,10,10**3,10**4,100,1,0)
stiffness1.printReadableK()

stiffness2 = FrameStiffness(2,1,3,10,10**3,10**4,125,0.8,-0.6)
stiffness2.printReadableK()
"""
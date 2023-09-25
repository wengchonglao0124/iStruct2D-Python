import time
from itertools import permutations
import random


class MatrixCalculation(object):
    """
    Matrix calculator
    """

    def matrixAddition(self, matrix1, operator, matrix2):
        """
        Addition for two matrix

        :param matrix1: first matrix
        :param operator: operator string
        :param matrix2: second matrix
        :return: result of the addition
        """
        matrixRow = len(matrix1)
        matrixCol = len(matrix1[0])
        result = []

        for i in range(matrixRow):
            resultRow = []
            for j in range(matrixCol):
                if operator == "+":
                    resultRow.append(matrix1[i][j] + matrix2[i][j])
                elif operator == "-":
                    resultRow.append(matrix1[i][j] - matrix2[i][j])

            result.append(resultRow)

        return result


    def matrixMultiplication(self, matrixA, matrixB):
        """
        Multiplication for two matrix

        :param matrixA: first matrix
        :param matrixB: second matrix
        :return: result of the multiplication
        """
        matrixARow = len(matrixA)
        matrixACol = len(matrixA[0])
        matrixBRow = len(matrixB)
        matrixBCol = len(matrixB[0])

        result = []
        resultRow = []
        resultNum = 0

        for i in range(matrixARow):

            for j in range(matrixBCol):

                for k in range(matrixBRow):
                    resultNum += (matrixB[k][j] * matrixA[i][k])

                resultRow.append(resultNum)
                resultNum = 0

            result.append(resultRow)
            resultRow = []

        return result


    def matrixMinors(self, matrix):
        """
        Minors of a matrix

        :param matrix: input matrix
        :return: minors of the matrix
        """
        matrixSize = len(matrix)
        result =[]

        for i in range(matrixSize):
            resultRow = []

            for j in range(matrixSize):
                minor = []
                for x in matrix:
                    minor.append(x.copy())

                minor.pop(i)
                for row in minor:
                    row.pop(j)
                resultRow.append(self.matrixDeterminant(minor))

            result.append(resultRow)

        return result


    def matrixScale(self, matrix, scale):
        """
        Scale the matrix by a number

        :param matrix: input matrix
        :param scale: scaling number
        :return: result of the scaling matrix
        """
        result = []

        for row in matrix:
            resultRow = []
            for col in row:
                resultRow.append(col*scale)
            result.append(resultRow)

        return result


    def matrixTranspose(self, matrix):
        """
        Transpose of a matrix

        :param matrix: input matrix
        :return: transpose of the matrix
        """
        matrixRow = len(matrix)
        if matrixRow == 0:
            print("Matrix is invalid")
            return None

        matrixCol = len(matrix[0])
        if matrixCol == 0:
            print("Matrix is invalid")
            return None

        for row in matrix:
            if len(row) != matrixCol:
                print("Matrix is invalid")
                return None

        result = []

        for j in range(matrixCol):
            newRow = []
            for row in matrix:
                newRow.append(row[j])
            result.append(newRow)

        return result


    def matrixRoundDecimal(self, matrix, decimalPlace):
        """
        Round the decimal number for a matrix

        :param matrix: input matrix
        :param decimalPlace: number of decimal place
        :return: rounded matrix
        """
        if decimalPlace == None:
            return matrix

        result = []
        for row in matrix:
            resultRow = []
            for col in row:
                num = round(col, decimalPlace)
                if num == 0:
                    num = round(0, decimalPlace)
                resultRow.append(num)

            result.append(resultRow)

        return result


    """
    def matrixInversion(self, matrix, decimalPlace):

        # we have made sure that the matrix is square before using this function
        matrixSize = len(matrix)

        determinant = self.matrixDeterminant(matrix)
        if determinant == 0:
            print("Determinant equals to 0, so matrix is singular")
            return None

        minor = self.matrixMinors(matrix)

        # sign conversion
        minorForInversion = []
        for i in range(matrixSize):
            minorForInversionRow = []
            for j in range(matrixSize):
                minorForInversionRowNum = minor[i][j]
                if (i+j)%2 == 1:
                    minorForInversionRowNum = minorForInversionRowNum*(-1)
                minorForInversionRow.append(minorForInversionRowNum)
            minorForInversion.append(minorForInversionRow)

        transpose = self.matrixTranspose(minorForInversion)
        result = self.matrixScale(transpose, 1/determinant)
        if decimalPlace == None:
            return result
        resultRounded = self.matrixRoundDecimal(result, decimalPlace)

        return resultRounded
    """


    def checkMatrixSize(self, matrix):
        """
        Return the size of a matrix

        :param matrix: input matrix
        :return: the size of the matrix
        """
        return (len(matrix), len(matrix[0]))


    def autoCommonFactorSimplify(self, matrix):
        """
        Simplify the matrix by the common factor
        This function is only for direct stiffness method matrix simplify

        :param matrix: input matrix
        :return: simplified matrix
        """
        powerList = []
        for row in matrix:
            for col in row:
                if col > 10:
                    power = 1
                    while col > 10:
                        col = col/10
                        power = power * 10
                    powerList.append(power)

        minPower = min(powerList)
        minPowerStr = minPower
        i = 0
        while minPowerStr > 10:
            minPowerStr = minPowerStr/10
            i = i + 1
        minPowerStr = "10^" + str(i+1)
        return [minPower, self.matrixScale(matrix, 1/minPower), minPowerStr]


    def signDetermination(self, list):
        """
        Determine the sign for the matrix part

        :param list: matrix part
        :return: positive or negative
        """
        size = len(list)
        time = 0
        for num in range(1, size+1):
            while list.index(num) != num-1:
                time = time + 1
                index = list.index(num)
                list.pop(index)
                list.insert(index-1, num)

        if time%2 == 0:
            return 1
        else:
            return -1


    def matrixDeterminant(self, matrix):
        """
        Calculate the determinant of a matrix
        For square matrix only

        :param matrix: input matrix
        :return: the determinant of the matrix
        """
        i_Index = []
        for num in range(1, len(matrix)+1):
            i_Index.append(num)
        j_items = permutations(i_Index)

        result = 0
        for j_index in j_items:

            j_Index = []
            for x in j_index:
                j_Index.append(x)

            itemResult = 1
            for index in range(len(matrix)):
                itemResult = itemResult * matrix[i_Index[index]-1][j_Index[index]-1]
            sign = self.signDetermination(j_Index)
            result = result + sign*itemResult

        return result


    def gaussElimination(self, originalMatrix, constant):
        """
        Using Gauss Elimination to solve the equation

        :param originalMatrix: matrix part
        :param constant: constant part
        :return: parameter result part
        """
        matrix = []
        for row in originalMatrix:
            matrix.append(row.copy())

        n = len(matrix)

        x = []
        for i in range(n):
            x.append(0)

        for index in range(len(matrix)):
            matrix[index].extend(constant[index])

        for i in range(n):
            if matrix[i][i] == 0.0:
                raise Exception('Divide by zero detected!')

            for j in range(i+1, n):
                ratio = matrix[j][i]/matrix[i][i]

                for k in range(n+1):
                    matrix[j][k] = matrix[j][k] - ratio * matrix[i][k]

        # Back Substitution
        x[n-1] = matrix[n-1][n]/matrix[n-1][n-1]

        for i in range(n-2,-1,-1):
            x[i] = matrix[i][n]

            for j in range(i+1,n):
                x[i] = x[i] - matrix[i][j]*x[j]
            x[i] = x[i]/matrix[i][i]

        return x


    def matrixInversion(self, matrix, decimalPlace):
        """
        Calculate the inversion of a matrix

        :param matrix: input matrix
        :param decimalPlace: required decimal place for the matrix
        :return: inversion of the matrix
        """
        result = []
        n = len(matrix)
        
        for index in range(n):
            I = []
            for num in range(n):
                I.append([0,])
            I[index][0] = 1
            result.append(self.gaussElimination(matrix, I))

        result = self.matrixTranspose(result)

        if decimalPlace == None:
            return result
        resultRounded = self.matrixRoundDecimal(result, decimalPlace)

        return resultRounded


# testing only

"""
B = [[2,3,8,9],
     [3,7,8,9],
     [5,9,9,9],
     [0,2,0,2]]

matrixCalculator = MatrixCalculation()

m = matrixCalculator.matrixInversion(B, 2)
if m != None:
    for x in m:
        print(x)
"""


"""
A = [[1,1,1],
     [2,-3,4],
     [3,4,5]]
B = [9,13,40]
matrixCalculator = MatrixCalculation()
print(matrixCalculator.gaussElimination(A,B))
"""


"""
# Matrix Inversion test
A = []
n = 150 # 150 -> 36.35305595397949 s
matrixCalculator = MatrixCalculation()
for i in range(n):
    row = []
    for j in range(n):
        row.append(random.random())
    A.append(row)

start = time.time()
result = matrixCalculator.matrixInversion(A, 2)
end = time.time()
for x in result:
    print(x)
print("")
print("time:", end-start, "s")
"""


"""
# Gauss Elimination test using factor of 25 to estimate the whole system calculation with Kff(n x n)
A = []
n = 300 # n=300 -> Whole system= 52.72955298423767 s
matrixCalculator = MatrixCalculation()
for i in range(n):
    row = []
    for j in range(n):
        row.append(random.random())
    A.append(row)

B = []
for num in range(n):
    B.append([random.random(),])

start = time.time()
result = matrixCalculator.gaussElimination(A, B)
end = time.time()

print(result)
print("")
timeCount = end-start
print("time:", timeCount, "s")
print("Calculation factor: 25")
print(timeCount, "x 25")
print("")
print("Whole system =", timeCount*25, "s")
"""


"""
# CIVL3340 L6 example get rf test
A = [[4.75e5,0,0,-0.75e5,-1.3e5],[0,4.75e5,1.3e5,-4e5,0],[0,1.3e5,5.71e5,0,0],[-0.75e5,-4e5,0,4.75e5,1.3e5],[-1.3e5,0,0,1.3e5,2.25e5]]
B = [[0], [0], [0], [2.82e5], [-2.82e5]]
matrixCalculator = MatrixCalculation()
print(matrixCalculator.gaussElimination(A,B))
"""
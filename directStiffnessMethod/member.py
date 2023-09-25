
class Member(object):
    """
    Member for the structure
    """

    def __init__(self, id, i, j, E, L):
        """
        Initiating the member

        :param id: member ID
        :param i: starting node
        :param j: ending node
        :param E: elasticity
        :param L: length of the member
        """
        self._id = id
        self._i = i
        self._j = j
        self._E = E
        self._L = L
        self._allP = [[[0,],
                       [0,],
                       [0,],
                       [0,]] ,]


    def getId(self):
        """
        Return the member ID

        :return: the member ID
        """
        return self._id


    def geti(self):
        """
        Return the starting node

        :return: the starting node
        """
        return self._i


    def getj(self):
        """
        Return the ending node

        :return: the ending node
        """
        return self._j


    def get_ij(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return (self.geti(), self.getj())


    def getE(self):
        """
        Return the elasticity of the member

        :return: elasticity of the member
        """
        return self._E


    def getL(self):
        """
        Return the length of member

        :return: the length of member
        """
        return self._L


    def add_xy_Axis(self, x, y):
        """
        Set the member local axes

        :param x: member local x_axis
        :param y: member local y_axis
        """
        self._x = x
        self._y = y


    def get_x_Axis(self):
        """
        Return the member local x_axis

        :return: member local x_axis
        """
        return self._x


    def get_y_Axis(self):
        """
        Return the member local y_axis

        :return: member local y_axis
        """
        return self._y
class Node(object):
    """
    Node for the structure
    """

    def __init__(self, id, x, y, restraint):
        """
        Initiating the node

        :param id: nodal ID
        :param x: x coordinate
        :param y: y coordinate
        :param restraint: nodal restraint string
        """
        self._id = id
        self._x = x
        self._y = y
        self._restraint = restraint
        self._load = [0, 0, 0]


    def getID(self):
        """
        Return the nodal ID

        :return: nodal ID
        """
        return self._id


    def getx(self):
        """
        Return the x coordinate of the node

        :return: x coordinate of the node
        """
        return self._x


    def gety(self):
        """
        Return the y coordinate of the node

        :return: y coordinate of the node
        """
        return self._y


    def get_xy(self):
        """
        Calculate the function title value

        :return: the function title value
        """
        return (self._x, self._y)


    def getRestraint(self):
        """
        Return the nodal restraint string

        :return: the nodal restraint string
        """
        return self._restraint


    def addRestraint(self, restraint):
        """
        Set the nodal restraint string

        :param restraint: nodal restraint string
        """
        self._restraint = restraint


    def getNodalDisplacement(self):
        """
        Return the nodal displacement

        :return: the nodal displacement
        """
        restraint = self.getRestraint()
        id = str(self.getID())
        nodalDisplacement = []

        if restraint == None:
            #RRR type
            restraint = "RRR"

        for index in range(0, 3):
            if restraint[index] == "F":
                nodalDisplacement.append(0)
            elif restraint[index] == "R":
                if index == 0:
                    name = "u"+id
                elif index == 1:
                    name = "v"+id
                else:
                    name = "θ"+id
                nodalDisplacement.append(name)
        return nodalDisplacement


    def addNodalLoad(self, fx, fy, moment):
        """
        Add the nodal loading

        :param fx: x value of the force
        :param fy: y value of the force
        :param moment: bending moment value of the force
        """
        self._load[0] = self._load[0] + fx
        self._load[1] = self._load[1] + fy
        self._load[2] = self._load[2] + moment


    def getNodalLoad(self):
        """
        Return the nodal loading

        :return: the nodal loading
        """
        restraint = self.getRestraint()
        id = str(self.getID())
        nodalLoad = []
        if restraint == None:
            restraint = "RRR"

        for index in range(0, 3):
            if restraint[index] == "R":
                nodalLoad.append(self._load[index])
            elif restraint[index] == "F":
                if index == 0:
                    name = "Fx,"+id
                elif index == 1:
                    name = "Fy,"+id
                else:
                    name = "M"+id
                nodalLoad.append(name)
        return nodalLoad
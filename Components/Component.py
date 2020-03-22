from abc import ABC, abstractmethod
from Node import Node


class Component(ABC):
    """
    provides a base class for all other Components to inherit from

    All Components will be modelled with the following voltage-current relation:
        AV+BI=C
    """

    def __init__(self, name, n1, n2):
        """
        Creates a component
        :type name: str
        :type n1: Node
        :type n2: Node
        :param n1: negative node connection
        :param n2: positive node connection
        """
        if type(name) is not str:
            raise TypeError("name is not of type string")
        if type(n1) is not Node:
            raise TypeError("negative component connection is not to a node")
        if type(n2) is not Node:
            raise TypeError("positive component connection is not to a node")

        self.name = name
        self.n1 = n1
        self.n2 = n2

        n1.add_connection(self, False)
        n1.add_connection(self, True)

    @abstractmethod
    def get_A(self):
        """
        calculates A from known parameters
        :return: A from equation AV+BI=C
        """

    @abstractmethod
    def get_B(self):
        """
        calculates B from known parameters
        :return: B from equation AV+BI=C
        """

    @abstractmethod
    def get_C(self):
        """
        calculates C from known parameters
        :return: C from equation AV+BI=C
        """

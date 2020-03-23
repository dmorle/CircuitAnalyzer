from abc import ABC, abstractmethod
from Node import Node


class Component(ABC):
    """
    provides a base class for all other Components to inherit from

    All Components will be modelled with the following voltage-current relation:
        AV+BI=C
    """

    def __init__(self, name, n_neg, n_pos):
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
        self.n_neg = n_neg
        self.n_pos = n_pos

        n_neg.add_connection(self, False)
        n_pos.add_connection(self, True)

    @abstractmethod
    def get_params(self, state_dict):
        """
        calculates A, B and C from known parameters
        :type state_dict dict
        :param state_dict a dictionary of all external circuit parameters
        :return: (A, B, C) from equation AV+BI=C
        """

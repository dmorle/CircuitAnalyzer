from abc import ABC, abstractmethod


class Component(ABC):
    """
    provides a base class for all other components to inherit from

    All components will be modelled with the following voltage-current relation:
        AV+BI=C
    """

    def __init__(self, name, n1, n2):
        """
        Creates a component
        :param n1: negative node connection
        :param n2: positive node connection
        """

        self.name = name
        self.n1 = n1
        self.n2 = n2

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

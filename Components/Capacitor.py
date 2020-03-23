from Components import Component
from Node import Node
from math import pi


class Capacitor(Component):
    def __init__(self, name, n_neg, n_pos, capacitance):
        """
        :type name: str
        :type n_neg: Node
        :type n_pos: Node
        :type capacitance: float
        :param name: name of the component
        :param n_neg: negative node connection
        :param n_pos: positive node connection
        :param capacitance: capacitance of the capacitor
        """
        super(Capacitor, self).__init__(name, n_neg, n_pos)

        self.capacitance = capacitance

    def get_params(self, state_dict):
        if "frequency" not in state_dict:
            raise KeyError("frequency not provided")

        return 1, -1/(2 * pi * state_dict["frequency"] * self.capacitance), 0


Capacitor.get_params.__doc__ = Component.get_params.__doc__

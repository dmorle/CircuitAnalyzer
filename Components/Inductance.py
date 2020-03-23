from Components import Component
from Node import Node
from math import pi


class Inductor(Component):
    def __init__(self, name, n_neg, n_pos, inductance):
        """
        :type name: str
        :type n_neg: Node
        :type n_pos: Node
        :type inductance: float
        :param name: name of the component
        :param n_neg: negative node connection
        :param n_pos: positive node connection
        :param inductance: inductance of the inductor
        """
        super(Inductor, self).__init__(name, n_neg, n_pos)

        self.inductance = inductance

    def get_params(self, state_dict):
        if "frequency" not in state_dict:
            raise KeyError("frequency not provided")

        return 1, -2 * pi * state_dict["frequency"] * self.inductance, 0


Inductor.get_params.__doc__ = Component.get_params.__doc__

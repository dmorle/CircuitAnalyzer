from Node import Node
from Components import Component


class Resistor(Component):
    def __init__(self, name, n_neg, n_pos, resistance):
        """
        :type name: str
        :type n_neg: Node
        :type n_pos: Node
        :type resistance:
        :param name: name of the component
        :param n_neg: negative node connection
        :param n_pos: positive node connection
        :param resistance: resistance of the resistor
        """
        super(Resistor, self).__init__(name, n_neg, n_pos)

        self.B = -resistance

    def get_params(self, state_dict):
        return 1, self.B, 0


Resistor.get_params.__doc__ = Component.get_params.__doc__

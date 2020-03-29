from math import pi
from Circuit import Node, Component


class Resistor(Component):
    def __init__(self, name, n_neg, n_pos, resistance):
        """
        :type name: str
        :type n_neg: Node
        :type n_pos: Node
        :type resistance: float
        :param name: name of the component
        :param n_neg: negative node connection
        :param n_pos: positive node connection
        :param resistance: resistance of the resistor
        """
        super(Resistor, self).__init__(name, n_neg, n_pos)

        self.B = -resistance

    def get_params(self, state_dict):
        return 1, self.B, 0


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

        return 1, -1 / (2 * pi * state_dict["frequency"] * self.capacitance), 0


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


class VoltageSource(Component):
    def __init__(self, name, n_neg, n_pos, voltage):
        """
        :type name: str
        :type n_neg: Node
        :type n_pos: Node
        :type voltage: float
        :param name: name of the component
        :param n_neg: negative node connection
        :param n_pos: positive node connection
        :param voltage: voltage across the source
        """
        super(VoltageSource, self).__init__(name, n_neg, n_pos)

        self.voltage = voltage

    def get_params(self, state_dict):
        return 1, 0, self.voltage


class CurrentSource(Component):
    def __init__(self, name, n_neg, n_pos, current):
        """
        :type name: str
        :type n_neg: Node
        :type n_pos: Node
        :type current: float
        :param name: name of the component
        :param n_neg: negative node connection
        :param n_pos: positive node connection
        :param current: current through the source
        """
        super(CurrentSource, self).__init__(name, n_neg, n_pos)

        self.current = current

    def get_params(self, state_dict):
        return 0, 1, self.current


Resistor.get_params.__doc__ = Component.get_params.__doc__
Capacitor.get_params.__doc__ = Component.get_params.__doc__
Inductor.get_params.__doc__ = Component.get_params.__doc__
VoltageSource.get_params.__doc__ = Component.get_params.__doc__
CurrentSource.get_params.__doc__ = Component.get_params.__doc__
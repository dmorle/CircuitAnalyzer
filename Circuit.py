import os
import json
import pprint
from math import pi
from abc import abstractmethod
import numpy as np
from util.Comparable import Comparable


class CircuitError(Exception):
    pass


class Node(Comparable):
    def __init__(self, name, ground=False):
        """
        :type name: str
        :type ground: bool
        :param name: the name of the node to be used
        :param ground: whether or note the node is directly connected to ground
        """
        super(Node, self).__init__()

        if type(name) is not str:
            raise TypeError("argument name is not of type string")
        if type(ground) is not bool:
            raise TypeError("argument ground is not of type bool")

        self.name = name
        self.ground = ground
        self.pos_cons = list()
        self.neg_cons = list()

        self.circuit = None

    def add_component(self, cmp, polarity):
        """
        called by a component on initialization
        :type cmp: Component
        :type polarity: bool
        :param cmp: component instance to be connected
        :param polarity: True => Positive, False => Negative
        """
        if not isinstance(cmp, Component):
            raise TypeError("invalid component argument")
        if type(polarity) is not bool:
            raise TypeError("invalid polarity argument")

        if polarity:
            self.pos_cons.append(cmp)
        else:
            self.neg_cons.append(cmp)


class Component(Comparable):
    """
    provides a base class for all other Components to inherit from

    All Components will be modelled with the following voltage-current relation:
        AV+BI=C
    """

    def __init__(self, name, n_neg, n_pos):
        """
        Creates a component
        :type name: str
        :type n_neg: Node
        :type n_pos: Node
        :param name: name of the component
        :param n_neg: negative node connection
        :param n_pos: positive node connection
        """
        super(Component, self).__init__()

        if type(name) is not str:
            raise TypeError("name is not of type string")
        if type(n_neg) is not Node:
            raise TypeError("negative component connection is not to a node")
        if type(n_pos) is not Node:
            raise TypeError("positive component connection is not to a node")

        if n_neg.circuit is None:
            raise CircuitError("node {} does not belong to a circuit".format(n_neg.name))
        if n_pos.circuit is None:
            raise CircuitError("node {} does not belong to a circuit".format(n_pos.name))
        if n_neg.circuit != n_pos.circuit:
            raise CircuitError("nodes {} and {} belong to different circuits".format(n_neg.name, n_pos.name))

        for e in n_neg.circuit.nodes + n_pos.circuit.components:
            if e.name == name:
                raise NameError("name {} already exists in the circuit".format(name))

        self.name = name
        self.n_neg = n_neg
        self.n_pos = n_pos

        n_neg.add_component(self, False)
        n_pos.add_component(self, True)

        n_neg.circuit.components.append(self)

    def get_type(self):
        return str(type(self)).split("'")[1].split(".")[-1]

    @abstractmethod
    def get_params(self, state_dict):
        """
        calculates A, B and C from known parameters
        :type state_dict dict
        :param state_dict a dictionary of all external circuit parameters
        :return: (A, B, C) from equation AV+BI=C
        """

    @abstractmethod
    def get_attributes(self):
        """
        creates a dictionary of arguments needed for reconstruction
        """


class Circuit(Comparable):
    def __init__(self, name=""):
        super(Circuit, self).__init__()

        self.name = name
        self.nodes = list()
        self.components = list()

    def __str__(self):
        data = self.__serialize()
        return pprint.pformat(data, indent=4)

    def add_node(self, node):
        """
        Adds a new node to the circuit
        :type node: Node
        :param node: the node to be added
        """

        if type(node) is not Node:
            raise TypeError("argument node is not of type Node")

        if node.circuit is not None:
            raise CircuitError("node {} already belongs to a circuit".format(node.name))

        node.circuit = self
        self.nodes.append(node)

    def get_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node

        raise CircuitError("Circuit {} does not have node {}", self.name, name)

    def ac_sweep(self, state_dict):
        """
        performs an ac sweep of the circuit based on the parameters given
        :param state_dict: a collection of all the external parameters needed to simulate the circuit
        :return: a dictionary of each voltage and current value, indexed by the parameter's name
        """

        found_ground = False
        for node in self.nodes:
            found_ground = found_ground or node.ground

        if not found_ground:
            raise CircuitError("All circuits require at least one ground node")

        mrx = np.zeros([
            len(self.nodes) + len(self.components)
        ] * 2)
        vct = np.empty([
            len(self.nodes) + len(self.components)
        ])

        # setting an id for each node and connection
        # the id will identify the row and column that the corresponding variable and resulting equation is assigned
        for enum in enumerate(self.nodes + self.components):
            enum[1].num = enum[0]

        # doing all the appropriate KCLs
        for node in self.nodes:
            if node.ground:
                # the ground node will not have a KCL, but instead a voltage assignment
                mrx[node.num, node.num] = 1
                vct[node.num] = 0

            else:
                # all non-ground nodes will produce a KCL
                for neg_con in node.neg_cons:
                    mrx[node.num, neg_con.num] = 1

                for pos_con in node.pos_cons:
                    mrx[node.num, pos_con.num] = -1

                vct[node.num] = 0

        # doing all the appropriate KVLs
        for cmp in self.components:
            # all connections will produce a KVL equation
            a, b, c = cmp.get_params(state_dict)

            if cmp.n_neg.ground and cmp.n_pos.ground:
                # both sides of the component are connected to ground => no current
                mrx[cmp.num, cmp.num] = 1
                vct[cmp.num] = 0

            # Note: middle two elifs are only an optimization, algorithm would work fine without
            elif cmp.n_neg.ground:
                # negative terminal of the component is connected to ground
                mrx[cmp.num, cmp.n_pos.num] = a
                mrx[cmp.num, cmp.num] = b
                vct[cmp.num] = c

            elif cmp.n_pos.ground:
                # positive terminal of the component is connected to ground
                mrx[cmp.num, cmp.n_neg.num] = -a
                mrx[cmp.num, cmp.num] = b
                vct[cmp.num] = c

            else:
                # neither terminal of the component is connected to ground
                mrx[cmp.num, cmp.n_pos.num] = a
                mrx[cmp.num, cmp.n_neg.num] = -a
                mrx[cmp.num, cmp.num] = b
                vct[cmp.num] = c

        solutions = np.linalg.solve(mrx, vct)

        results = dict()

        for node in self.nodes:
            results[node.name] = solutions[node.num]

        for cmp in self.components:
            results[cmp.name] = solutions[cmp.num]

        return results

    def load(self, path, overwrite=False):
        """
        Loads the circuit found at path to self
        :type path: str
        :type overwrite: bool
        :param path: the location from which a circuit will be loaded
        :param overwrite ignore any existing circuit data
        """

        if type(path) is not str:
            raise TypeError("argument path is not of type string")

        if not os.path.isfile(path):
            raise IOError("could not find file at provided path")

        if overwrite:
            self.nodes = list()
            self.components = list()
        else:
            if len(self.nodes) != 0:
                raise CircuitError("Cannot overwrite existing circuit without explicit direction")

        with open(path, "r") as f:
            data = json.load(f)

        self.name = data["Name"]

        # building the nodes of the circuit
        for node_info in data["Nodes"]:
            self.add_node(Node(node_info["Name"], node_info["Ground"]))

        # building the components of the circuit
        for component_info in data["Components"]:
            globals()[component_info["Type"]](
                component_info["Name"],
                self.get_node(component_info["Negative"]),
                self.get_node(component_info["Positive"]),
                **component_info["Attributes"]
            )

    def save(self, path, overwrite=False, pretty_printing=True):
        """
        Saves the current circuit to path
        :type path: str
        :type overwrite: bool
        :type pretty_printing: bool
        :param path: the location to which the circuit will be saved
        :param overwrite: do not check if the file already exists
        :param pretty_printing: includes indents and new-lines to make the file more readable
        """

        if type(path) is not str:
            raise TypeError("argument path is not of type string")

        if not overwrite:
            if os.path.isfile(path):
                raise FileExistsError("file {} already exists".format(path))

        serialized = self.__serialize()

        with open(path, "w") as f:
            if pretty_printing:
                json.dump(serialized, f, indent=4)
            else:
                json.dump(serialized, f)

    def __serialize(self):
        """
        :return: a string representation of the circuit
        """

        node_list = list()
        for node in self.nodes:
            node_list.append({
                "Name": node.name,
                "Ground": node.ground
            })

        component_list = list()
        for component in self.components:
            component_list.append({
                "Name": component.name,
                "Type": component.get_type(),
                "Negative": component.n_neg.name,
                "Positive": component.n_pos.name,
                "Attributes": component.get_attributes()
            })

        return {
            "Name": self.name,
            "Nodes": node_list,
            "Components": component_list
        }


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

        self.resistance = resistance

    def get_params(self, state_dict):
        return 1, -self.resistance, 0

    def get_attributes(self):
        return {
            "resistance": self.resistance
        }


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

    def get_attributes(self):
        return {
            "capacitance": self.capacitance
        }


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

    def get_attributes(self):
        return {
            "inductance": self.inductance
        }


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

    def get_attributes(self):
        return {
            "voltage": self.voltage
        }


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

    def get_attributes(self):
        return {
            "current": self.current
        }


Resistor.get_params.__doc__ = Component.get_params.__doc__
Capacitor.get_params.__doc__ = Component.get_params.__doc__
Inductor.get_params.__doc__ = Component.get_params.__doc__
VoltageSource.get_params.__doc__ = Component.get_params.__doc__
CurrentSource.get_params.__doc__ = Component.get_params.__doc__

import os
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

    def add_connection(self, cmp, polarity):
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

        for e in n_neg.circuit.nodes + n_pos.circuit.connections:
            if e.name == name:
                raise NameError("name {} already exists in the circuit".format(name))

        self.name = name
        self.n_neg = n_neg
        self.n_pos = n_pos

        n_neg.add_connection(self, False)
        n_pos.add_connection(self, True)

        n_neg.circuit.connections.append(self)

    @abstractmethod
    def get_params(self, state_dict):
        """
        calculates A, B and C from known parameters
        :type state_dict dict
        :param state_dict a dictionary of all external circuit parameters
        :return: (A, B, C) from equation AV+BI=C
        """


class Circuit(Comparable):
    def __init__(self):
        super(Circuit, self).__init__()

        self.nodes = list()
        self.connections = list()

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
            len(self.nodes) + len(self.connections)
        ] * 2)
        vct = np.empty([
            len(self.nodes) + len(self.connections)
        ])

        # setting an id for each node and connection
        # the id will identify the row and column that the corresponding variable and resulting equation is assigned
        for enum in enumerate(self.nodes + self.connections):
            enum[1].num = enum[0]

        # doing all the appropriate KCLs
        for node in self.nodes:
            if node.ground:
                # the ground node will not have a KCL, but instead a voltage assignment
                mrx[node.num] = 1
                vct[node.num] = 0

            else:
                # all non-ground nodes will produce a KCL
                for neg_con in node.neg_cons:
                    mrx[node.num, neg_con.num] = 1

                for pos_con in node.pos_cons:
                    mrx[node.num, pos_con.num] = -1

                vct[node.num] = 0

        # doing all the appropriate KVLs
        for cmp in self.connections:
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

        for cmp in self.connections:
            results[cmp.name] = solutions[cmp.num]

        return results

    def load(self, path):
        """
        Loads the circuit found at path to self
        :type path: str
        :param path: the location from which a circuit will be loaded
        """

        if type(path) is not str:
            raise TypeError("argument path is not of type string")

        if not os.path.isfile(path):
            raise IOError("could not find file at provided path")

        # TODO: determine a method for loading the circuit

    def save(self, path, ignore_existing=False):
        """
        Saves the current circuit to path
        :type path: str
        :type ignore_existing: bool
        :param path: the location to which the circuit will be saved
        :param ignore_existing: do not check if the file already exists
        """

        if type(path) is not str:
            raise TypeError("argument path is not of type string")

        if not ignore_existing:
            if os.path.isfile(path):
                raise FileExistsError("file {} already exists".format(path))

        serialized = self.__serialize()
        with open(path, "w") as f:
            f.write(serialized)

    def __serialize(self):
        """
        :return: a string representation of the circuit
        """

        # TODO: determine a method for serializing the circuit

        return ""

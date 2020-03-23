from Components import Component
from Node import Node
import numpy as np
import os


class Circuit:
    nodes = list()
    connections = list()

    def add_node(self, node):
        """
        adds a new node to the circuit
        :type node: Node
        :param node: the new node to be added
        """

        if type(node) is not Node:
            raise TypeError("argument node is not of type Node")

        self.nodes.append(node)

    def add_connection(self):
        pass

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

    def ac_sweep(self, state_dict):
        """
        performs an ac sweep of the circuit based on the parameters given
        :param state_dict: a collection of all the external parameters needed to simulate the circuit
        :return: a dictionary of each voltage and current value, indexed by the parameter's name
        """

        mrx = np.zeros([
            len(self.nodes) + len(self.connections)
        ] * 2)
        vct = np.empty([
            len(self.nodes) + len(self.connections)
        ])

        # setting an id for each node and connection
        # the id will identify the row and column that the corresponding variable and resulting equation is assigned
        for enum in enumerate(self.nodes + self.connections):
            enum[1].id = enum[0]

        # doing all the appropriate KCLs
        for node in self.nodes:
            if node.ground:
                # the ground node will not have a KCL, but instead a voltage assignment
                mrx[node.id] = 1
                vct[node.id] = 0

            else:
                # all non-ground nodes will produce a KCL
                for neg_con in node.neg_cons:
                    mrx[node.id, neg_con.id] = 1

                for pos_con in node.pos_cons:
                    mrx[node.id, pos_con.id] = -1

                vct[node.id] = 0

        # doing all the appropriate KVLs
        for cmp in self.connections:
            # all connections will produce a KVL equation
            a, b, c = cmp.get_params(state_dict)

            if cmp.n_neg.ground and cmp.n_pos.ground:
                # both sides of the component are connected to ground => no current
                mrx[cmp.id, cmp.id] = 1
                vct[cmp.id] = 0

            # Note: middle two elifs are only an optimization, algorithm would work fine without
            elif cmp.n_neg.ground:
                # negative terminal of the component is connected to ground
                mrx[cmp.id, cmp.n_pos.id] = a
                mrx[cmp.id, cmp.id] = b
                vct[cmp.id] = c

            elif cmp.n_pos.ground:
                # positive terminal of the component is connected to ground
                mrx[cmp.id, cmp.n_neg.id] = -a
                mrx[cmp.id, cmp.id] = b
                vct[cmp.id] = c

            else:
                # neither terminal of the component is connected to ground
                mrx[cmp.id, cmp.n_pos.id] = a
                mrx[cmp.id, cmp.n_neg.id] = -a
                mrx[cmp.id, cmp.id] = b
                vct[cmp.id] = c

        solutions = np.linalg.solve(mrx, vct)

        results = dict()

        for node in self.nodes:
            results[node.name] = solutions[node.id]

        for cmp in self.connections:
            results[cmp.name] = solutions[cmp.id]

        return results

    def __serialize(self):
        """
        :return: a string representation of the circuit
        """

        # TODO: determine a method for serializing the circuit

        return ""

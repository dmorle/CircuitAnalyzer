from Components import Component
from Node import Node
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

    def save(self, path):
        """
        Saves the current circuit to path
        :type path: str
        :param path: the location to which the circuit will be saved
        """

        if type(path) is not str:
            raise TypeError("argument path is not of type string")

        # TODO: determine a method for serializing the circuit

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

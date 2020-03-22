from components import *


class Node:
    def __init__(self, name, isground):
        self.name = name
        self.isground = isground
        self.connections = list()

    def add_connection(self, cmp, polarity):
        """
        called by a component on initialization
        :param cmp: component instance to be connected
        :param polarity: True => Positive, False => Negative
        """
        if not isinstance(cmp, component):
            raise TypeError("invalid component argument")
        if type(polarity) is not bool:
            raise TypeError("invalid polarity argument")

        self.connections.append((cmp, polarity))

from Components import Component


class Node:
    def __init__(self, name, ground):
        """
        :type name: str
        :type ground: bool
        :param name: the name of the node to be used
        :param ground: whether or note the node is directly connected to ground
        """
        if type(name) is not str:
            raise TypeError("argument name is not of type string")
        if type(ground) is not bool:
            raise TypeError("argument ground is not of type bool")

        self.name = name
        self.ground = ground
        self.pos_cons = list()
        self.neg_cons = list()

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

import unittest
from Circuit import Circuit, Node


class CircuitBuilding(unittest.TestCase):
    def test_single_node_circuit(self):
        circ = Circuit()
        circ.add_node(Node("ground node", True))

        self.assertTrue(
            len(circ.nodes) == 1 and
            len(circ.connections) == 0
        )

    def test_multi_node_circuit(self):
        circ = Circuit()
        circ.add_node(Node("ground node", True))
        circ.add_node(Node("non-ground"))

        self.assertTrue(
            len(circ.nodes) == 2 and
            len(circ.connections) == 0
        )


if __name__ == '__main__':
    unittest.main()

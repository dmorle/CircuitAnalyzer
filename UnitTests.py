import unittest
from Circuit import *
from Components import *


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

    def test_component_circuit_1(self):
        circ = Circuit()

        ground = Node("ground node", True)
        node = Node("non-ground")

        circ.add_node(ground)
        circ.add_node(node)

        Resistor("R", node, ground, 1000)
        VoltageSource("V0", ground, node, 5)

        self.assertTrue(
            len(circ.nodes) == 2 and
            len(circ.connections) == 2
        )

    def test_component_rejection(self):
        circ = Circuit()

        ground = Node("ground node", True)
        node = Node("non-ground")

        circ.add_node(ground)

        try:
            Resistor("R", node, ground, 1000)
        except CircuitError as e:
            self.assertEqual(str(e), "node non-ground does not belong to a circuit", "Incorrect exception type")
            return

        self.assertTrue(False, "Component was not rejected")


if __name__ == '__main__':
    unittest.main()

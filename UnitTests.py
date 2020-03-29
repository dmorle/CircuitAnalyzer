import unittest
from Circuit import *


def create_tmp_file():
    circ = Circuit("Circ")

    n1 = Node("N1", True)
    n2 = Node("N2")
    circ.add_node(n1)
    circ.add_node(n2)

    Resistor("R1", n2, n1, 1000)
    VoltageSource("V1", n1, n2, 5)

    circ.save("tmp.circ", overwrite=True)


class CircuitBuilding(unittest.TestCase):
    def test_single_node_circuit(self):
        circ = Circuit("Circ")
        circ.add_node(Node("ground node", True))

        self.assertTrue(
            len(circ.nodes) == 1 and
            len(circ.components) == 0
        )

    def test_multi_node_circuit(self):
        circ = Circuit("Circ")
        circ.add_node(Node("ground node", True))
        circ.add_node(Node("non-ground"))

        self.assertTrue(
            len(circ.nodes) == 2 and
            len(circ.components) == 0
        )

    def test_component_circuit_1(self):
        circ = Circuit("Circ")

        ground = Node("ground node", True)
        node = Node("non-ground")

        circ.add_node(ground)
        circ.add_node(node)

        Resistor("R", node, ground, 1000)
        VoltageSource("V0", ground, node, 5)

        self.assertTrue(
            len(circ.nodes) == 2 and
            len(circ.components) == 2
        )

    def test_component_rejection(self):
        circ = Circuit("Circ")

        ground = Node("ground node", True)
        node = Node("non-ground")

        circ.add_node(ground)

        try:
            Resistor("R", node, ground, 1000)
        except CircuitError as e:
            self.assertEqual(str(e), "node non-ground does not belong to a circuit", "Incorrect exception type")
            return

        self.assertTrue(False, "Component was not rejected")

    def test_save_circuit(self):
        create_tmp_file()
        circ = Circuit("Circ")

        with open("tmp.circ", "r") as f:
            data = json.load(f)

        self.assertEqual(data, circ._Circuit__serialize())

    def test_load_circuit(self):
        create_tmp_file()
        circ = Circuit()
        circ.load(path="tmp.circ")

        self.assertEqual(len(circ.nodes), 2)
        self.assertEqual(len(circ.components), 2)

        print(circ)


if __name__ == '__main__':
    unittest.main()

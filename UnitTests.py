import unittest
from Circuit import *


def create_tmp_file():
    circ = Circuit("Circ")

    n1 = Node("N1", True)
    n2 = Node("N2")
    circ.add_node(n1)
    circ.add_node(n2)

    Resistor("R1", n1, n2, 1000)
    VoltageSource("V1", n1, n2, 5)

    circ.save("tmp.circ", overwrite=True)
    return circ


def two_node_circuit():
    circ = Circuit()
    n0 = Node("N0", True)
    n1 = Node("N1")
    circ.add_node(n0)
    circ.add_node(n1)

    return circ, n0, n1


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
        circ = create_tmp_file()

        with open("tmp.circ", "r") as f:
            data = json.load(f)

        self.assertEqual(data, circ._Circuit__serialize())

    def test_load_circuit(self):
        create_tmp_file()
        circ = Circuit()
        circ.load(path="tmp.circ")

        self.assertEqual(len(circ.nodes), 2)
        self.assertEqual(len(circ.components), 2)


class ACAnalysis(unittest.TestCase):
    def test_single_node(self):
        circ = Circuit()
        circ.add_node(Node("ground-node", True))

        results = circ.ac_sweep({"frequency": 1e3})

        self.assertEqual(0, results["ground-node"])

    def test_voltage_source(self):
        circ, n0, n1 = two_node_circuit()

        VoltageSource("V0", n0, n1, 5)
        results = circ.ac_sweep({"frequency": 1e3})

        self.assertEqual(0, results["N0"], "Voltage at N0 is wrong")
        self.assertEqual(5, results["N1"], "Voltage at N1 is wrong")
        self.assertEqual(0, results["V0"], "Current through the voltage source is wrong")

    def test_resistor(self):
        circ, n0, n1 = two_node_circuit()

        Resistor("R0", n0, n1, 1e3)
        results = circ.ac_sweep({"frequency": 1e3})

        self.assertEqual(0, results["N0"], "Voltage at N0 is wrong")
        self.assertEqual(0, results["N1"], "Voltage at N1 is wrong")
        self.assertEqual(0, results["R0"], "Current through the resistor is non-zero")

    def test_capacitor(self):
        circ, n0, n1 = two_node_circuit()

        Capacitor("C0", n0, n1, 1e-6)
        results = circ.ac_sweep({"frequency": 1e3})

        self.assertEqual(0, results["N0"], "Voltage at N0 is wrong")
        self.assertEqual(0, results["N1"], "Voltage at N1 is wrong")
        self.assertEqual(0, results["C0"], "Current through the capacitor is non-zero")

    def test_inductor(self):
        circ, n0, n1 = two_node_circuit()

        Inductor("L0", n0, n1, 1e-3)
        results = circ.ac_sweep({"frequency": 1e3})

        self.assertEqual(0, results["N0"], "Voltage at N0 is wrong")
        self.assertEqual(0, results["N1"], "Voltage at N1 is wrong")
        self.assertEqual(0, results["L0"], "Current through the inductor is non-zero")

    def test_resistor_circuit(self):
        circ, n0, n1 = two_node_circuit()

        VoltageSource("V0", n0, n1, 5)
        Resistor("R0", n0, n1, 1e3)
        results = circ.ac_sweep({"frequency": 1e3})

        self.assertEqual(0, results["N0"], "Voltage at N0 is wrong")
        self.assertEqual(5, results["N1"], "Voltage at N1 is wrong")
        self.assertEqual(-5e-3, results["V0"], "Current through the voltage source is wrong")
        self.assertEqual(5e-3, results["R0"], "Current through resistor is wrong")

    def test_current_source(self):
        circ, n0, n1 = two_node_circuit()

        CurrentSource("I0", n0, n1, -5e-3)
        Resistor("R0", n0, n1, 1e3)
        results = circ.ac_sweep({"frequency": 1e3})

        self.assertEqual(0, results["N0"], "Voltage at N0 is wrong")
        self.assertEqual(5, results["N1"], "Voltage at N1 is wrong")
        self.assertEqual(-5e-3, results["I0"], "Current through the current source is wrong")
        self.assertEqual(5e-3, results["R0"], "Current through the resistor is wrong")


if __name__ == '__main__':
    unittest.main()

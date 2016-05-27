try:
    import unittest2 as unittest
except ImportError:
    import unittest
try:
    import cStringIO
except ImportError:
    import io as cStringIO
import os
import sys
sys.path.append("..")
from src.parameter import ParameterTable

class TestParameterTable(unittest.TestCase):
    """
    """
    @classmethod
    def setUpClass(cls):
        cls.tempf = "./temp.test_pt"
        with open(cls.tempf, "wt") as f:
            f.write("# a b\n")
        cls.obj = ParameterTable(cls.tempf)
        cls.stdout = sys.stdout
        sys.stdout = cStringIO.StringIO()

    def test_init(self):
        _pt = self.obj
        self.assertEqual(self.tempf, _pt.table)
        self.assertEqual("b", _pt.names[1])
        self.assertEqual(0, _pt.len)

        with open(self.tempf, "wt") as f:
            f.write("a b")
        self.assertRaises(ValueError, ParameterTable, self.tempf)

    def test_current_parameter(self):
        _pt = self.obj
        self.assertRaises(IndexError, _pt.current_parameter)

        _pt.paraLines.append("0 1\n")
        self.assertEqual(1.0, _pt.current_parameter()[1])

    def test_update_table(self):
        _pt = self.obj
        self.assertRaises(ValueError, _pt.update_table, [0.0, 1.0, 2.0])
        self.assertIsNone(_pt.update_table([0.0, 1.0]))

    def test_write_line(self):
        pass

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.tempf)
        sys.stdout = cls.stdout

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParameterTable)
    unittest.TextTestRunner(verbosity=2).run(suite)

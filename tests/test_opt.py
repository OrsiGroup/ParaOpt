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
sys.path.append('..')
import opt as _opt

class TestOpt(unittest.TestCase):

    def setUp(self):
        self.tempf = "./temp.test_opt"
        self.stdout = sys.stdout

        with open(self.tempf, "wt") as f:
            f.write("# aa bb cc\n")
        sys.stdout = cStringIO.StringIO()

    def test_initialize_parameters(self):
        self.assertRaises(IndexError,
                          _opt.initialize_parameters,
                          self.tempf, "temp.test_init"
        )

        with open(self.tempf, "at") as f:
            f.write("1 2")
        r = _opt.initialize_parameters(self.tempf, "temp.test_init")
        self.assertIsInstance(r[1], _opt.ParameterTable)
        self.assertEqual(r[1].table, "temp.test_init")

        with open("temp.test_init", "rt") as f:
            lineOut = f.readline()
        with open(self.tempf, "rt") as f:
            lineIn = f.readline()
        os.remove("temp.test_init")
        self.assertEqual(lineIn, lineOut)

    def test_initialize_properties(self):
        name = ['0', '']
        ref = [1, 2]
        spec = ['', 'foo']
        #TODO no error here?
        n = 1
        self.assertRaises(ValueError,
                          _opt.initialize_properties,
                          name, ref, spec, n
        )

        n += 1
        r = _opt.initialize_properties(name, ref, spec, n)
        self.assertIsInstance(r, list)
        self.assertIsInstance(r[0], _opt.Property)
        self.assertEqual(r[1].name, 'q_2')

    def test_simultion_flow(self):
        #TODO nothing here yet.
        self.assertNotEqual(1, 2)

    def tearDown(self):
        sys.stdout = self.stdout
        os.remove(self.tempf)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOpt)
    unittest.TextTestRunner(verbosity=2).run(suite)

try:
    import unittest2 as unittest
except ImportError:
    import unittest
try:
    import cStringIO
except ImportError:
    import io as cStringIO
import os
import re
import sys
sys.path.append('..')
from src.configuration import Configuration

class TestConfiguration(unittest.TestCase):
    """Tests for the 'Configuration' module.
    Test cases are numberred to be run in order, so that the temp file
    ('self.tempf') can be re-used, but each case is independent if rewrote
    "self.string2" into "self.tempf" every execution.
    """

    def setUp(self):
        self.stdout = sys.stdout
        self.obj = Configuration()
        self.tempf = "./temp.test_cfg"
        self.string1 = ("[foo]\n"
                        "foo = bar\n")
        self.string2 = self.gen_configs()
        sys.stdout = cStringIO.StringIO()

    def gen_configs(self):
        """ Read the required options ('_optionsDict') from 'self.obj', and
        generate a correct config string for following tests.
        """
        configs = self.obj._optionsDict
        strings = []
        for section in configs.keys():
            strings.append("[%s]" %section)
            for option in configs[section]:
                strings.append("%s = %s" %(option, option))
        return "\n".join(strings)

    def write(self, string, filename):
        with open(filename, "wt") as f:
             f.write(string)

    def test0_read(self):
        self.write(self.string1, self.tempf)
        _cfg = Configuration()
        self.assertRaises(ValueError, _cfg.read, self.tempf)

        self.write(self.string2, self.tempf)
        _cfg.clear()
        self.assertEqual(None, _cfg.read(self.tempf))

    def test1_get_config(self):
        _cfg = Configuration()
        _cfg.read(self.tempf)
        self.assertEqual(["optmethod"], _cfg.get_config("optimization"))
        self.assertTrue("fftemplate" in _cfg.get_config("parameters"))

    def test2_get_config_simulation(self):
        _cfg = Configuration()
        _cfg.read(self.tempf)
        self.assertRaises(ValueError, _cfg.get_config, "simulation")

        self.string2 = re.sub(r"= mode", r"= simulation", self.string2)
        self.write(self.string2, self.tempf)
        _cfg.clear()
        _cfg.read(self.tempf)
        self.assertTrue("path" in _cfg.get_config("simulation"))

    def test3_get_config_properties(self):
        _cfg = Configuration()
        _cfg.read(self.tempf)
        # totalProperties
        self.assertRaises(ValueError, _cfg.get_config, "properties")

        self.string2 = re.sub(r"= total.*", r"= 0", self.string2)
        self.write(self.string2, self.tempf)
        _cfg.clear()
        _cfg.read(self.tempf)
        self.assertRaises(ValueError, _cfg.get_config, "properties")

        more_configs = (r"= 1\n"
                            r"property1Name = \n"
                            r"property1Ref = 1\n")
        self.string2 = re.sub(r"= 0", more_configs, self.string2)
        self.write(self.string2, self.tempf)
        _cfg.clear()
        _cfg.read(self.tempf)
        self.assertEqual([1.0], _cfg.get_config("properties")[2])

    def tearDown(self):
        sys.stdout = self.stdout

if __name__ == "__main__":
    #unittest.TestLoader.sortTestMethodsUsing = lambda _, x, y: cmp(y, x)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConfiguration)
    unittest.TextTestRunner(verbosity=2).run(suite)
    os.remove("./temp.test_cfg")

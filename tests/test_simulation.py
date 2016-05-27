try:
    import unittest2 as unittest
except ImportError:
    import unittest
try:
    import cStringIO
except ImportError:
    import io as cStringIO
import os
import subprocess
import sys
sys.path.append("..")
from src.simulation import Simulation

class TestSimulation(unittest.TestCase):
    """ Tests for module 'simulation'.
    The test case "test_run" might not work correctly if under synchronizing
    dropbox folder or other situation that can delay fileIO.    
    """
    @classmethod
    def setUpClass(cls):
        cls.tempf = "./temp.test_sim"
        cls.runlog = "log.screen"
        cls.obj = Simulation(".")
        cls.string = "echo 0 1.1"
        cls.stdout = sys.stdout
        
        sys.stdout = cStringIO.StringIO()
        #if os.name == "nt":
        #    string = "type 0 1.1 > res.preprocess"
        #else:
        #    string = "echo 0 1.1 > res.preprocess"
        with open(cls.tempf, "wt") as f:
            f.write(cls.string)

    def test_init(self):
        _sim = self.obj
        self.assertEqual(os.path.abspath("."), _sim.path)
        
    def test_run(self):
        _sim = self.obj
        self.assertRaises(subprocess.CalledProcessError, _sim.run, "")
        self.assertFalse(os.path.exists(self.runlog))
        self.assertIsNone(_sim.run(self.string))
        self.assertTrue(os.path.exists(self.runlog))

    def test_post_process(self):
        #_sim = self.obj
        #with open(cls.tempf, "wt") as f:
        #    f.write(self.string + " > res.preprocess")
        # TODO This is platform-dependent.
        pass

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.tempf)
        os.remove(cls.runlog)
        sys.stdout = cls.stdout

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSimulation)
    unittest.TextTestRunner(verbosity=2).run(suite)
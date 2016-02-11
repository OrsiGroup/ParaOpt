#
#   simulation.py
#
# Created:  2016/Jan/29
# Purpose:  Deal with simulation, including post-processing.
# Notes:    
#
# -------------------------------------------------------------------------- #

import fileinput
import os.path
import subprocess


# -------------------------------------------------------------------------- #

class Simulation(object):
    def __init__(self, simuPath, simuInFile):
        self.path = os.path.abspath(simuPath)
        self.infile = simuInFile

    def run(self, lmpExe, thread=2):
        """ Call the simulator to run your simulation.

        lmpExe: your local LAMMPS executable;
        thread: mpirun thread (default: 2).

        type_lmpExe: str
        type_thread: int
        rtype: None
        """
        subprocess.check_call(
            'cd %s && mpirun -np %d %s < %s > log.screen' % (
                self.path, thread, lmpExe, self.infile
            ),
            shell=True,
        )

    def post_process(self, scriptFileName):
        # TODO why not return list??
        """ Post-process the simulation data by calling your script file.
        Return all properties' value as a list.

        scriptFileName: the post-processing script. It should process the
            data produced by the simulation, and save all targeted property
            values in a single line file named "res.postprocess" like this:
                "Q1 Q2 Q3 Q4 ...".

        type_scriptFileName: str
        rtype: str list
        """
        print "Results being processed by: \"%s\" " % scriptFileName
        subprocess.check_call(
            'cd %s && ./%s' % (self.path, scriptFileName),
            shell=True,
        )
        resFile = fileinput.FileInput(os.path.join(self.path, 'res.postprocess'))
        result = resFile.readline()
        print "Current properties:", result
        return result.split()

        # TODO def back_up_simulation_files(self, anyFilesName, destination):

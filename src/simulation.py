#
#   simulation.py
#
# Created:  2016/Jan/29
# Purpose:  Deal with simulation, including post-processing.
# Notes:    
#
# -------------------------------------------------------------------------- #

from __future__ import print_function

import fileinput
import os
import subprocess


# -------------------------------------------------------------------------- #

class Simulation(object):
    def __init__(self, simuPath, postScript=None):
        self.path = os.path.abspath(simuPath)
        self.script = postScript

    def run(self, inCommand):
        """ Execute the input command (inCommand).

        inCommand: command to run the simulation;

        type_inCommand: str
        rtype: None
        """
        preSimDir = os.getcwd()
        os.chdir(self.path)
        exeCommand = inCommand + ' > log.screen'
        subprocess.check_call(exeCommand, shell=True)
        # TODO 1) Handle the stdout in subprocess if possible (rather than 
        #         using '> log');
        #      2) Be careful about 'shell-True'. 
        os.chdir(preSimDir)

    def post_process(self, scriptFileName=None):
        # TODO why not return list??
        """ Post-process the simulation data by calling your script file.
        Return all properties' value as a list.

        scriptFileName: the post-processing script ('self.script' by default).
            It should process the data produced by the simulation, and save
            all targeted property values in a single line file, named as
            "res.postprocess" like this:
                "Q1 Q2 Q3 Q4 ...".

        type_scriptFileName: str
        rtype: str list
        """
        if not scriptFileName:
            scriptFileName = self.script
        if not scriptFileName:
            raise ValueError("Post-process file not provided.")

        print("Results being processed by: \"%s\" " % scriptFileName)
        subprocess.check_call(
            'cd %s && ./%s' % (self.path, scriptFileName),
            shell=True,
        )
        resFile = fileinput.FileInput(os.path.join(self.path, 'res.postprocess'))
        result = resFile.readline()
        print("Current properties:", result)
        return result.split()

        # TODO def back_up_simulation_files(self, anyFilesName, destination):

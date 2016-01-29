#!/usr/bin/env python 
#
#   opt.py
#
# Created:  2015/Jan/15
# Purpose:  A generic routine to optimize CG-lipid parameters
# Syntex:   opt.py configureFile
# Options:  
# Example:
# Notes:    Based on "framework-6.py" from Michalis
#
#----------------------------------------------------------------------------#

import fileinput
import math
import re
import sys
import subprocess 
import time
import os.path
import scipy.optimize
from src.configuration import Configuration
from src.parameter import ParameterTable

#----------------------------------------------------------------------------#

class Simulation(object):

    def __init__(self, simuPath, simuInFile): 
        self.path = os.path.abspath(simuPath)        
        self.infile = simuInFile

    def run(self, lmpExe, thread=2):
        ''' Call the simulator to run your simulation.

        lmpExe: 
            your local lammps executebale;
        thread: 
            mpirun thread (default: 2).

        type_lmpExe: str 
        type_thread: int
        rtype: None
        '''
        subprocess.check_call('cd %s && mpirun -np %d %s < %s '
                              '> log.screen.test' 
                              % (self.path, thread, lmpExe, self.infile), 
                              shell=True)                      

    def post_process(self, scriptFileName):
        ''' Postprocess the simulation data by calling your script file. 
        Return all result values as one string.
        
        scriptFileName: 
            the post-processing script. Here it requires it to save the final
            targeted properties in a file named "res.postprocess", which only
            contains one line listing property values like below:               
                "Q1 Q2 Q3 Q4 ...".

        type_scriptFileName: str 
        rtype: str
        '''
        print "    Results being processed by: \"%s\" " % (scriptFileName)
        subprocess.check_call('cd %s && ./%s'
                              % (self.path, scriptFileName),
                              shell=True)
        resFile = fileinput.FileInput(os.path.join(self.path,'res.postprocess'))
        result = resFile.readline()
        print "    Current properties:", result
        return result

    # TODO def back_up_simulation_files(self, anyFilesName, destination):

class Property(object):

    def __init__(self, value, refValue, name='nameless'): 
        self.value = value
        self.name = name
        self.reference = refValue

    def update_property_list(self):
        ''' Update (create at 1st iteration) the file saving the property, 
        which is named with the "propertyName". 
        
        rtype: None
        '''
        if os.path.exists(self.name):
            with open(self.name, 'at') as f:
                f.write(self.value)
                f.write('\n') 
        else:
            with open(self.name, 'wt') as f:
                f.write('# ' + self.name + '\n')
                f.write(self.value)
                f.write('\n') 
                
    def target_function(self):
        targFunc = (float(self.value)/float(self.reference) - 1.0)**2
        return targFunc

    def target_function_special(self, *funcType):
        '''For the property whose target function needs special definition.

        Currently support:
            log: base 10 logarithm of the property;
            scaled: scale the target function by a given ratio.

        type_*funcType: ['log',]
                        ['scaled', float,]  
        '''
        value = float(self.value)
        ref = float(self.reference)
        
        if funcType[0] == 'log':
            targFunc = (math.log10(value)/math.log10(ref) - 1.0)**2
        elif funcType[0] == 'scaled':
            targFunc = (value/ref - 1.0)**2
            targFunc = float(funcType[1]) * targFunc

        else:
            raise ValueError(("Function type '%s' not supported." 
                              "Use 'log' or 'scaled'.") 
                             % (funcType))
        return targFunc


#----------------------------------------------------------------------------#

if len(sys.argv) == 2:
    confFile = sys.argv[1]
elif len(sys.argv) == 1:
    confFile = 'config.sample'
else:
    print "Syntax: opt.py configureFile"
    sys.exit()

print "\nPreparations...:"
cfg = Configuration()
cfg.read(confFile)
[
    lmp, 
    path, 
    inFileName,
] = cfg.get_config('simulation')
[
    totalProperties, 
    propertyNames, 
    propertyRefs, 
    propertySpecials, 
] = cfg.get_config('properties') 
[
    initParaTableFile, 
    paraTableFile, 
    ffForSimulation, 
    ffTemplate, 
] = cfg.get_config('parameters')
[
    optMethod
] = cfg.get_config('optimization')

print "    Fetch initial parameters from \"%s\"." %(
           initParaTableFile)
paraTableInitial = ParameterTable(initParaTableFile)
paraValuesInitial = paraTableInitial.current_parameter()

print "    Parameters will be saved in \"%s\" during simulation." %(
           paraTableFile)
subprocess.call("head -1 %s > %s" %(
                 initParaTableFile, paraTableFile), 
                shell=True)

for i, name in enumerate(propertyNames):
    if not name:
        propertyNames[i] = "q_" + str(i+1)
        name = propertyNames[i]
        print "    Property %d name not set, Reset as \"%s\"." % (i+1, name)
    if os.path.exists(name):
        now = time.strftime("%Y-%m-%d-%H-%M-%S")
        nameBackUpTo = ''.join([name, '#', now])
        subprocess.call("mv %s '%s'" % (name, nameBackUpTo), shell=True)
        print "    Backup %s to %s." %(name, nameBackUpTo)

def simulation_flow(parameters):
    ''' A set of parameters is passed in, and a targeted function value is
    returned.

    type_parameters: float list 
    rtype: float
    '''
    paraTable = ParameterTable(paraTableFile)
    paraTable.update_table(parameters)
    print "\n#---- Step %d -------------#\n" %(paraTable.len)
    p = paraTable.current_parameter()
    paraTable.write_datafile(p, ffForSimulation, ffTemplate)

    print "\nRunning Simulation...:"
    simulation = Simulation(path, inFileName)
    simulation.run(lmp)
    processedResult = simulation.post_process('preProcess.sh')
    #processedResult = "70.8745 29.7267241379 1005.19 1.146949"

    print "\nPassing Properties To Optimization...:"
    properties = []
    targetValue = 0.0
    
    propertyValues = processedResult.split()
    if not len(propertyValues) == int(totalProperties):
        raise ValueError('%s properties indicated, but %d detected.' %(
                          totalProperties, len(propertyValues))
                        )
    for i, propertyValue in enumerate(propertyValues):
        properties.append(Property(propertyValue, 
                                   propertyRefs[i], 
                                   propertyNames[i]))
        properties[i].update_property_list()
        if not propertySpecials[i]:
            targetValue += properties[i].target_function()
        else:
            targetValue += properties[i].target_function_special(
                               *propertySpecials[i])
    print "    Current targeted value:", targetValue
    
    return targetValue

#simulation_flow(paraValuesInitial)
print "\nOptimizing...:"
optParaValues=scipy.optimize.minimize(simulation_flow, 
                                      paraValuesInitial,
                                      method=optMethod, 
                                      options={'disp':True, 
                                               'maxiter':100, 
                                               'ftol':0.0001}, 
                                      #callback=callbackF,
                                     )

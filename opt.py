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

import sys
import subprocess 
import time
import os.path
import scipy.optimize
from src.configuration import Configuration
from src.parameter import ParameterTable
from src.simulation import Simulation
from src.property import Property

#----------------------------------------------------------------------------#

def back_up(fileName):
    ''' Backup a file (named as "fileName") to "fileName#currentTime".
    '''
    now = time.strftime("%Y-%m-%d-%H-%M-%S")
    nameBackUpTo = ''.join([name, '#', now])
    subprocess.call("mv %s '%s'" % (name, nameBackUpTo), shell=True)
    print "Backup existing %s to %s." %(name, nameBackUpTo)
    return None
        
#----------------------------------------------------------------------------#
# Preparations

if len(sys.argv) == 2:
    confFile = sys.argv[1]
elif len(sys.argv) == 1:
    confFile = 'config.sample'
else:
    print "Syntax: opt.py configureFile"
    sys.exit()
    
print ""
cfg = Configuration()
cfg.read(confFile)

optConfigs = cfg.get_config('optimization')
print ""
optMethod = optConfigs[0]
print "The \"%s\" optimizing method will be used." % optMethod

paraConfigs = cfg.get_config('parameters')
print ""
initParaTableFile = paraConfigs[0]
paraTableFile = paraConfigs[1]
ffForSimulation = paraConfigs[2]
ffTemplate = paraConfigs[3]
print "Fetch initial parameters from \"%s\"." % initParaTableFile
paraTableInitial = ParameterTable(initParaTableFile)
paraValuesInitial = paraTableInitial.current_parameter()
print "Optimized parameters will be saved in \"%s\"." % paraTableFile
subprocess.call("head -1 %s > %s" %(initParaTableFile, paraTableFile),
                shell=True)

simuConfigs = cfg.get_config('simulation')
print ""
lmp = simuConfigs[0] 
path = simuConfigs[1]
inFileName = simuConfigs[2]
print "Simulation will be performed in folder: %s." % path

propConfigs = cfg.get_config('properties')
print ""
totalProperties = propConfigs[0]
propertyNames = propConfigs[1]
propertyRefs = propConfigs[2]
propertySpecials = propConfigs[3]
if not int(totalProperties) == len(propertyNames):
    raise ValueError('%s properties indicated, but %d given.' % (
                      totalProperties, len(propertyValues)))
else:
    properties = [''] * len(propertyNames)
for i, name in enumerate(propertyNames):
    if not name:
        name = "q_" + str(i+1)
        print "Property%d name not set, Reset as \"%s\"." % (i+1, name)
    if os.path.exists(name):
        back_up(name)
    properties[i] = Property(name)
    properties[i].reference = propertyRefs[i]
    properties[i].special = propertySpecials[i]
    # TODO @setter here?

#----------------------------------------------------------------------------#

def simulation_flow(parameters):
    ''' The sub-routine to be optimized. Take in a set of parameters, and 
    return a targeted function value.

    type_parameters: float list 
    rtype: float
    '''
    paraTable = ParameterTable(paraTableFile)
    paraTable.update_table(parameters)
    print "\n#---- Step %d -------------#\n" % paraTable.len
    p = paraTable.current_parameter() # p == parameter
    paraTable.write_datafile(p, ffForSimulation, ffTemplate)

    print "\nRunning Simulation...:"
    simulation = Simulation(path, inFileName)
    simulation.run(lmp)
    propertyValues = simulation.post_process('preProcess.sh')
    #propertyValues= ['70.8745', '29.7267', '1005.19', '1.146']
    
    if not len(propertyValues) == int(totalProperties):
        raise ValueError('%s target properties needed, but %d produced.' % (
                          totalProperties, len(propertyValues)))
    print "\nSaving Properties & Calculating Target Value...:"
    targetValue = 0.0
    for i, property in enumerate(properties):
        property.value = propertyValues[i]
        property.update_property_list()
        if not property.special:
            targetValue += property.target_function()
        else:
            targetValue += property.target_function_special(*property.special)                               
        # TODO maybe better to wrap this in the target_function method?
    print "Current targeted value:", targetValue
    
    return targetValue        
        
#simulation_flow(paraValuesInitial)
print "\nOptimizing...:"
optParaValues = scipy.optimize.minimize(simulation_flow, 
                                        paraValuesInitial,
                                        method=optMethod, 
                                        options={'disp':True, 
                                                 'maxiter':100, 
                                                 'ftol':0.0001,
                                                }, 
                                        #callback=callbackF,
                                       )

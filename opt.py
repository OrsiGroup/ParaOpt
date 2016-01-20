#!/usr/bin/env python 
#
# Script:   opt.py
# Created:  2015/Jan/15
# Purpose:  A generic routine to optimize CG-lipid parameters
# Syntex:   opt.py inputFile
# Options:  
# Example:
# Notes:    Based on "framework-6.py" from Michalis
#
#----------------------------------------------------------------------------#

import fileinput
import math
import re
import sys     # argv, exit,
import subprocess 
import os.path
import scipy.optimize

if not len(sys.argv) == 2:
    print "Syntax: opt.py configureFile"
    sys.exit()

#----------------------------------------------------------------------------#

class Simulation(object):

    def __init__(self, simuPath, simuInFile):
        #TODO refactor this part using os.path.join
        if len(simuPath) > 0 and simuPath[-1] == '/':
            pass
        elif len(simuPath) == 0:
            simuPath = "./"
        else:
            simuPath = simuPath + '/'  
        self.path = simuPath
        
        self.infile = simuInFile

    def run(self, lmpExe, thread=2):
        ''' 
        Run simulation. Return Nothing.

        lmpExe: 
            your local lammps executebale;
        thread: 
            mpirun thread (default: 2).
        '''
        subprocess.check_call('cd %s && mpirun -np %d %s < %s > log.screen.test' 
                        % (self.path, thread, lmpExe, self.infile), 
                        shell=True)                      

    def post_process(self, scriptFileName):
        ''' 
        Postprocess the simulation data by calling your script file. Return
        all result values as one string.

        scriptFileName: 
            usually a shell script, that save the final targeted properties 
            in a file named "res.postprocess". It contains only one line 
            like below:              
                "Q1 Q2 Q3 Q4 ...".
        '''
        print "    Results being processed by: \"%s\" " % (scriptFileName)
        subprocess.check_call('cd %s && ./%s'
                        % (self.path, scriptFileName),
                        shell=True)
        resFile = fileinput.FileInput(self.path + 'res.postprocess')
        result = resFile.readline()
        print "    Current properties:", result
        return result


class Property(object):

    def __init__(self, value, refValue, name='nameless'): 
        self.value = value
        self.name = name
        self.reference = refValue

    def update_property_list(self):
        '''
        Update (create at 1st iteration) the file named with the property 
        name.
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
        '''
        Used for properties whose target function needs special definition.
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

  
class ParameterSets(object):

    def __init__(self, paraTable='paraTable.dat'): 
        self.table = paraTable 
        f = open(self.table, 'rt')
        nameLine = f.readline()

        if not nameLine[0:2] == '# ':
            raise ValueError('Headline in paraTable missing.')
        else:
            self.names = nameLine[2:-1].split()

        self.paraLines = f.readlines()
        self.len = len(self.paraLines)
        #self.dimension = 
        #self.tableFile = paraTable

    def get_parameter(self):
        ''' 
        Return parameters as a list. 

        Seems the built-in opt.minimize needs only one initial point to do 
        the simplex. If confirmed, merge this method into __init__.
        '''
        parameterStrings = self.paraLines[-1].split()
        parameters = map(float, parameterStrings)
        print "    Current parameters:", parameterStrings
        return parameters

    def update_table(self, parameterSet):
        ''' 
        Similar to get_parameter(): if confirmed, delete this method.
        '''
        parameterLine = ' '.join(map(str, parameterSet))
        with open(self.table, 'at') as fTable:
            fTable.write(parameterLine)
            fTable.write('\n')
        self.paraLines.append(parameterLine)
        self.len += 1

    def write_datafile(self, parameterSet, dataFileOut, 
                       dataFileTemp='forcefield.temp'):
        ''' 
        Replace every @paraName in the datafile template with the desired 
        parameter Value (the arguments). 
             
        parameterSet (float list): 
            the parameter set to be written into datafiles;
        dataFileOut: 
            the output file name; 
        dataFileTemp: 
            the template based on which to write (the default file: 
            'forcefield.temp').
        '''

        def update_line_in_datafile(line, stringSet, valueSet):
            ''' 
            A method that update lines in the datafile template, with both the
            parameter name set and value set given. Return the updated new 
            line line as a string.

            stringSet: 
                list that contains all possible strings that may occurred in
                the line;
            valueSet: 
                list taht contains all corresponding values that we want to 
                replace the strings.
            '''
            pattern = re.compile(r'@\w+\b')

            parasFoundInLine = pattern.findall(line)
            for para in parasFoundInLine:
                try: 
                    index = stringSet.index(para[1:])
                    line = line.replace(para, valueSet[index])
                except ValueError:
                # omit strings starting with "@" but not found in stringSet. 
                # E.g. something in the comments.
                    pass
            return line

        print "    Datafile written: \"%s\" " % (dataFileOut)

        parameterStrings = map(str, parameterSet)
        with open(dataFileOut, 'wt') as fOut:
            fTemplate = open(dataFileTemp, 'rt')
            for line in fTemplate:
                if '@' in line:
                    line = update_line_in_datafile(line, self.names, 
                                                   parameterStrings)
                fOut.write(line)
            fTemplate.close()
        return fOut


#-- main --------------------------------------------------------------------#

# simulation  
path = './simulation'
inFileName = 'in.2xlipid'
lmp = 'lammps'

# property
totalProperties = '4'
propertyName1 = ''
propertyNames = []
if propertyName1 == '':
    for i in range(int(totalProperties)):
        propertyNames.append("q_" + str(i+1))
propertyRef1 = 70.0
propertyRefList = [propertyRef1, 37.0, 220.0, 1.0]
propertySpecial4 = 'scaled'
property4SpecialArg = 100
propertySpecialList = ['', '', '', [propertySpecial4, property4SpecialArg]]

# parameters
initParaTableFile = 'initParaTable.dat'
paraTableFile = 'paraTable.dat'
ffTemplate = 'forcefield.temp'

# optimization
optMethod = 'Nelder-Mead'

#----------------------------------------------------------------------------#

print "\nPreparations...:"
print "    Parsing input settings from \"%s\"..." % ('TODO')
## TODO: add a class to deal with input settings from an input file. 

print "    Fetch initial parameters from \"%s\"" % (initParaTableFile)
initParaSets = ParameterSets(initParaTableFile)
paraInitials = initParaSets.get_parameter()
print "    Parameters will be saved in \"%s\"" % (paraTableFile)
subprocess.call("head -1 %s > %s" % (initParaTableFile, paraTableFile), 
                shell=True)

def simulation_flow(parameters):
    ''' 
    Receive the optimized parameters (float list), and return the targeted 
    function value (float)
    '''
    print "\n#---------------#"
    lipid = Simulation(path, inFileName)

    print "Passing Parameters To Simulation...:"
    paraSets = ParameterSets(paraTableFile)
    paraSets.update_table(parameters)
    p = paraSets.get_parameter()
    dataFile = 'forcefield.DOPC'
    newFile = paraSets.write_datafile(p, dataFile)
    
    print "\nRunning Simulation...:"
    #lipid.run(lmp)
    processedResult = lipid.post_process('preProcess.sh')

    print "\nPassing Properties To Optimization...:"
    properties = []
    targetValue = 0.0
    
    propertyValues = processedResult.split()
    if not len(propertyValues) == int(totalProperties):
        raise ValueError('%s properties indicated, but %d detected.' 
                         % (totalProperties, len(propertyValues)))
    for i, propertyValue in enumerate(propertyValues):
        properties.append(Property(propertyValue, 
                                   propertyRefList[i], 
                                   propertyNames[i]))
        properties[i].update_property_list()
        if not propertySpecialList[i]:
            targetValue += properties[i].target_function()
        else:
            targetValue += properties[i].target_function_special(
                               *propertySpecialList[i])
    print "    Current targeted value:", targetValue
    
    return targetValue

print "\nOptimizing...:"

optParaValues=scipy.optimize.minimize(simulation_flow, 
                    paraInitials, 
                    method=optMethod, 
                    options={'disp':True, 
                             'maxiter':100, 
                             'ftol':0.0001},         
                    #callback=callbackF,
                   )

#
#   parameter.py
#
# Created:  2015/Jan/28
# Purpose:  Deal with parameters.
# Notes:    
#
#----------------------------------------------------------------------------#

import re

#----------------------------------------------------------------------------#

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

        print "    Datafile written to: \"%s\" " % (dataFileOut)

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

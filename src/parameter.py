#
#   parameter.py
#
# Created:  2015/Jan/28
# Purpose:  Deal with parameters.
# Notes:    
#
# -------------------------------------------------------------------------- #

import re


# -------------------------------------------------------------------------- #

class ParameterTable(object):
    def __init__(self, paraTable):
        self.table = paraTable
        f = open(self.table, 'rt')
        nameLine = f.readline()
        if nameLine[0:2] == '# ':
            self.names = nameLine[2:-1].split()
        else:
            raise ValueError('Headline in %s missing.' % paraTable)
        self.dimension = len(self.names)
        self.paraLines = f.readlines()
        self.len = len(self.paraLines)

    def current_parameter(self):
        """ Get the current parameters (the last line of para-table).

        rtype: float list
        """
        parameterStr = self.paraLines[-1].split()
        parameterList = map(float, parameterStr)
        print "Current parameters:", parameterStr
        return parameterList

    def update_table(self, paraList):
        """ Append a set of parameters to para-table, and update attributes.

        type_paraList: float list
        rtype: None
        """
        if len(paraList) == self.dimension:
            paraLine = ' '.join(map(str, paraList))
            with open(self.table, 'at') as fTable:
                fTable.write(paraLine)
                fTable.write('\n')
            self.paraLines.append(paraLine)
            self.len += 1
        else:
            raise ValueError(
                'Parameters (%d) doesn\'t match table columns (%d).' % (
                    len(paraList), self.dimension
                )
            )

    def write_datafile(self, paraList, dataFileOut, dataFileTemp):
        """ Replace every @para-name in the prepared datafile template (
        dataFileTemp) with the corresponding para-value from paraList. Output
        file (dataFileOut) is used for running your simulation.

        type_paraList: float list
        type_dataFileOut: str
        type_dataFileTemp: str
        rtype: None
        """

        def update_line(line, stringSet, valueSet):
            """ Update a line (line) in the datafile template, with both the
            para-name set (stringSet) and value set (valueSet) given. Return
            the updated new line as a string.

            line:
                A line read from the datafile template;
            stringSet:
                A list that contains all possible strings that may occurred
                in the line;
            valueSet:
                A list that contains all corresponding values that we want
                to replace the strings.

            type_line: str
            type_stringSet: str list
            type_valueSet: str list
            rtype: str
            """
            pattern = re.compile(r'@\w+\b')
            paraNamesFoundInLine = pattern.findall(line)
            for paraName in paraNamesFoundInLine:
                try:
                    index = stringSet.index(paraName[1:])
                    line = line.replace(paraName, valueSet[index])
                except ValueError:
                    pass
                # omit strings starting with "@" but not found in stringSet,
                # e.g. something in the comments.
            return line

        print "Parameters written to: \"%s\" " % dataFileOut
        parameterStrings = map(str, paraList)
        with open(dataFileOut, 'wt') as fOut:
            fTemplate = open(dataFileTemp, 'rt')
            for line in fTemplate:
                if '@' in line:
                    line = update_line(line, self.names, parameterStrings)
                fOut.write(line)
            fTemplate.close()

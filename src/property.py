#
#   property.py
#
# Created:  2016/Jan/29
# Purpose:  Deal with a single property.
# Notes: 
#
# -------------------------------------------------------------------------- #

import math
import os.path
import subprocess
import time


# -------------------------------------------------------------------------- #

class Property(object):

    def __init__(self, name):
        self.name = name
        self.value = None
        self.reference = None
        self.special = None

        def back_up(fileName):
            """ Backup a file (named as "fileName") to "fileName#currentTime".
            """
            now = time.strftime("%Y-%m-%d-%H-%M-%S")
            backUpTo = ''.join([fileName, '#', now])
            subprocess.call("mv %s '%s'" % (fileName, backUpTo), shell=True)
            print "Backup existing %s to %s." % (fileName, backUpTo)

        if os.path.exists(self.name):
            back_up(self.name)

    def update_property_list(self):
        """ Update (create at 1st iteration) the file saving the property,
        which is named with the "propertyName".

        rtype: None
        """
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
        """ The RMSD of a property regarding to its reference value. For
        those needs special definition, additional arguments are required.

        Currently support:
            log: base 10 logarithm of the property;
            scaled: scale the target function by a given ratio.

        type_*funcType: ['log',]
                        ['scaled', float,]
        rtype: float
        """
        value = float(self.value)
        ref = float(self.reference)

        if not self.special:
            targFunc = (value / ref - 1.0) ** 2
        else:
            if self.special[0] == 'log':
                targFunc = (math.log10(value) / math.log10(ref) - 1.0) ** 2
            elif self.special[0] == 'scaled':
                targFunc = float(self.special[1]) * (value / ref - 1.0) ** 2

            else:
                raise ValueError(
                    "Function type '%s' not supported." % (self.special[0])
                )

        return targFunc

#
#   property.py
#
# Created:  2016/Jan/29
# Purpose:  Deal with a single property.
# Notes: 
#
#----------------------------------------------------------------------------#

import math
import os.path

#----------------------------------------------------------------------------#

class Property(object):

    def __init__(self, name):
        self.name = name
        self.value = None
        self.reference = None
        self.special = None
        
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
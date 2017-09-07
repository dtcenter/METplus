#!/usr/bin/env python

'''
Program Name: CG_GempakToCF.py
Contact(s): George McCabe
Abstract: Runs GempakToCF
History Log:  Initial version
Usage: CG_GempakToCF.py
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
'''

from __future__ import (print_function, division)

from CommandGen import CommandGen


class CG_GempakToCF(CommandGen):

    def __init__(self, p, logger):
        super(CG_GempakToCF, self).__init__(p, logger)
        self.app_name = "GempakToCF"
        self.class_path = self.p.getstr('exe', 'GEMPAKTOCF_CLASSPATH')

    def get_command(self):
        cmd = "java -classpath " + self.class_path + " GempakToCF "

        if len(self.infiles) != 1:
            self.logger.error(self.app_name +
                              ": Only 1 input file can be selected")
            return None

        for f in self.infiles:
            cmd += f + " "

        if self.outfile == "":
            (self.logger).error(self.app_name+": No output file specified")
            return None

        cmd += self.get_output_path()
        return cmd

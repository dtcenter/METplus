#!/usr/bin/env python

import os
import sys
import types

import argparse

# Create an Action subclass that prints the
# default params for us without having to force the user to query the argparse
# print_params by hand
def make_PrintParamsAction(paramString):
    class CMPPAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            print(paramString)
            setattr(args, self.dest, values)
            exit(1)
    return CMPPAction

def make_ConfigAction(cm):
  class CMCAction(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
      cm.handleConfigFile(values)
  return CMCAction

class ConfigMaster:
  opt = {}

  defaultParamsHeader = "#!/usr/bin/env python\n"
  defaultParams = ""
  #optionsToIgnore = ['dt', 'os']
  parser = None

  configFilePath = None

  def setDefaultParams(self, dp):
    if dp.lstrip()[0:2] == "#!":
      self.defaultParams = dp
    else:
      self.defaultParams = self.defaultParamsHeader + dp

  def printParams(self):
    for o in self.opt:
      #if o not in self.optionsToIgnore:
        #if type(self.opt[o]) != types.ModuleType:
          print o + ": " + str(self.opt[o])
        #    print self.opt

  def assignParameters(self,p):
    global opt
    self.opt = p

  def printDefaultParams(self):
    print self.defaultParams

  def assignDefaultParams(self):
#    global defaultParams
#    self.defaultParams = dp
    exec self.defaultParams in self.opt
    del self.opt['__builtins__']
    for ko in self.opt.keys():
      if type(self.opt[ko]) == types.ModuleType:
        del self.opt[ko]    

  
  def getConfigFilePath(self):
    return self.configFilePath
        
  # config file path
  def handleConfigFile(self,cfp):
    self.configFilePath = cfp
    config_path, config_file = os.path.split(cfp)

    if config_file[-3:] == ".py":
      config_file = config_file[:-3]

    if config_path != '':
      sys.path.append(config_path)

    #print "importing config file: {}".format(config_file)
    cf = __import__(config_file, globals(), locals(), [])
    for o in self.opt:
      #print "looking at {}".format(o)
      if o in dir(cf):
        #print "found in cf: setting to {}".format(getattr(cf,o))
        self.opt[o] = getattr(cf,o)

    dcf = dir(cf)
    for cfo in dcf:
      #cfo = dcf[kcfo]
      #print cfo,type(cf.__dict__[cfo])      
      if cfo in ["__builtins__","__doc__","__file__","__name__","__package__"]:
        continue
      if type(cf.__dict__[cfo]) == types.ModuleType:
        continue
      if cfo not in self.opt:
        print "\nERROR: Invalid parameter in configuration file {}: {}\n".format(cfp,cfo)
        exit(1)
    


  def init(self, program_description=None, **kwargs):
    self.assignDefaultParams()

    self.parser = argparse.ArgumentParser(description=program_description)

    if "add_param_args" in kwargs:
      self.addParseArgs(add_param_args = kwargs["add_param_args"])
    else:
      self.addParseArgs()

    self.handleArgParse()


  def handleArgParse(self):
    args = self.parser.parse_args()

    for o in self.opt:
      #if o in self.optionsToIgnore:
      #  continue
      if o in dir(args):
        if getattr(args,o) != None:
          #print "seting {} to {} from command line".format(o,getattr(args,o))
          self.opt[o] = getattr(args,o)

  def addParseArgs(self, add_param_args=True):
    #parser.add_argument('-c','--config', help="The configuration file.")
    self.parser.add_argument('-c', '--config', help="The configuration file.", action=make_ConfigAction(self))
    self.parser.add_argument('-p', '--print_params', action=make_PrintParamsAction(self.defaultParams),
                        nargs=0, help="Generate a default configuration file.")

    if add_param_args:
      self.addAdvancedParseArgs()

    
  def addAdvancedParseArgs(self):
    #self.addParseArgs()

    for o in self.opt:
      #print "o is {} {} {}".format(o,self.opt[o],type(self.opt[o]))
      #if o in self.optionsToIgnore:
      #  continue

      #print "Type of {} is {}".format(o,type(self.opt[o]))
      
      if isinstance(self.opt[o], bool):
        bool_parser = self.parser.add_mutually_exclusive_group(required=False)
        #print "{} is a bool".format(o)
        argument = "--" + o
        action = "store_true"
        helpString = "Set " + o + " to True"
        bool_parser.add_argument(argument, action=action, help=helpString, default=None)
        argument = "--no-" + o
        action = "store_false"
        helpString = "Set " + o + " to False"
        bool_parser.add_argument(argument, action=action, help=helpString, default=None)
      elif isinstance(self.opt[o], (int,long,float,str)):
        #print "working on {}".format(o)
        argument = "--" + o
        helpString = "Overide the param file value of " + o
        self.parser.add_argument(argument, help=helpString)
              
      
        
			
			
			
		


#!/usr/bin/env python3

"""
Plot a Hovmoeller diagram using METplotpy functionality

"""
import os
import metplotpy.plots.hovmoeller.hovmoeller as Hovmoeller

if __name__ == '__main__':
    config_file = os.environ.get('YAML_CONFIG_NAME')
#    config_file = os.path.join(os.path.dirname(__file__), "hovmoeller.yaml")
    Hovmoeller.main(config_file)

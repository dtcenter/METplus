#! /usr/bin/env python

from __future__ import absolute_import
import os, produtil.log

##@var __all__
# List of symbols to import during "from produtil.ecflow import all"
__all__=['set_ecflow_event', 'set_ecflow_label', 'set_ecflow_meter',
          "in_ecflow"]

ecflow_task_name=os.environ.get('ECF_NAME','')
if ecflow_task_name:
    import ecflow
    ecflow_client=ecflow.Client()
    ecflow_client.set_child_path(ecflow_task_name)
    ecflow_client.set_child_pid(int(os.environ['ECF_RID']))
    ecflow_client.set_child_password(os.environ['ECF_PASS'])
    ecflow_client.set_child_try_no(int(os.environ['ECF_TRYNO']))
else:
    ecflow_client=None

def in_ecflow():
    """!Are we running in ecflow?

    Checks environment variables that were set at the initialization
    of this module to decide whether the job is inside ecflow or not.

    @returns True if the job is inside ecflow, False otherwise. """
    return ecflow_client is not None

def set_ecflow_event(event_name,logger=None):
    """!If this job is running in ecFlow, sets the specified ecFlow
    event.

    @param event_name The name of the event in the ecFlow task definition.
    @param logger Optional: a logging.Logger to log messages"""
    if ecflow_client is not None:
        ecflow_client.child_event(event_name)
    elif logger is not None:
        logger.debug('Not in ecFlow.  Skipping ecFlow communication.')

def set_ecflow_label(label_name,text_value,logger=None):
    """!If this job is running in ecFlow, updates the specified ecFlow
    label to have the given text string.

    When a model is running in the ecflow workflow management system,
    various parts of the model give text or graphical feedback.  Among other
    uses, this function allows the ocean init to describe the method
    used to initialize the ocean model via a text label.

    @param label_name The name of the label in the ecFlow task definition.
    @param text_value The text to place in the label.
    @param logger Optional: a logging.Logger to log messages"""
    if ecflow_client is not None:
        #ecflow_client.alter(ecf_name,'change','label',str(label),str(text))
        ecflow_client.child_label(str(label_name),str(text_value))
    elif logger is not None:
        logger.debug('Not in ecFlow.  Skipping ecFlow communication.')

def set_ecflow_meter(meter_name,meter_value,logger=None):
    """!If this job is running in ecFlow, changes the level of the
    specified ecflow meter.

    When a model is running in the ecflow workflow management system,
    various parts of the model give text or graphical feedback.  Among
    other uses, this function allows the boundary processing job to
    tell the operator how far it is has gotten processing inputs from GFS.

    @param meter_name The name of the meter in the ecFlow task definition.
    @param text_value The new value for the meter.
    @param logger Optional: a logging.Logger to log messages"""
    if ecflow_client is not None:
        #ecflow_client.alter(ecf_name,'change','label',str(label),str(text))
        ecflow_client.child_meter(str(meter_name),int(meter_value))
    elif logger is not None:
        logger.debug('Not in ecFlow.  Skipping ecFlow communication.')


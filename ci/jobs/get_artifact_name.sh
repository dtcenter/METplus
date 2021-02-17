#! /bin/bash

artifact_name=$1
artifact_name=`echo $artifact_name | awk -F: '{print $1}'`
artifact_name=use_cases_${artifact_name}
artifact_name=`echo $artifact_name | tr , _`
echo $artifact_name

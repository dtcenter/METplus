import os
import sys
from os.path import dirname, realpath
import glob
import shutil
import subprocess
import filecmp
import logging
import time
import calendar
import argparse

# find  top level of METplus repository
# this will need to change if this file is moved
metplus_home = dirname(dirname(dirname(realpath(__file__))))
use_case_dir = os.path.join(metplus_home, "parm/use_cases")

# additional python requirements that are handled either via a simple pip
# or a script that installs various packages
PYTHON_REQUIREMENTS = {
    'netCDF4': 'pip3 install netCDF4',
    'cartopy': '${DOCKER_WORK_DIR}/METplus/ci/travis_jobs/get_cartopy.sh',
    'pygrib': '${DOCKER_WORK_DIR}/METplus/ci/travis_jobs/get_pygrib.sh',
    'h5py': 'pip3 install h5py',
    'matplotlib': 'pip3 install matplotlib',
    'metpy': 'pip3 install metpy',
}

class METplusUseCaseSuite:
    def __init__(self):
        self.category_groups = {}

    def add_category_group(self, name, cases_by_requirement):
        if name in self.category_groups.keys():
            raise KeyError(f"ERROR: Group name already exists: {name}")

        self.category_groups[name] = cases_by_requirement

    def print(self):
        for name, use_cases_list in self.category_groups.items():
            print(f'Category Group: {name}')
            for use_cases in use_cases_list:
                use_cases.print(2)
            print()

    def get_total_cases(self):
        total = 0
        for _, use_cases_list in self.category_groups.items():
            for use_cases in use_cases_list:
                total += use_cases.get_total_cases()

        return total


    def add_use_case_groups(self, get_methods,
                            simple_slice='all', complex_slice='all'):
        if not isinstance(get_methods, list):
            get_methods = [get_methods]

        data_volumes = []
        all_simple_cases = []
        all_complex_cases = []
        for get_method in get_methods:
            data_volume, simple_cases, complex_cases = get_method()
            data_volumes.append(data_volume)
            all_simple_cases.extend(simple_cases)
            all_complex_cases.extend(complex_cases)

        if simple_slice is None:
            all_simple_cases = []
        elif simple_slice != 'all':
            all_simple_cases = all_simple_cases[simple_slice]

        if complex_slice is None:
            all_complex_cases = []
        elif complex_slice != 'all':
            all_complex_cases = all_complex_cases[complex_slice]

        self.add_use_case_group('&'.join(data_volumes),
                                simple_cases=all_simple_cases,
                                complex_cases=all_complex_cases,
                                )

    def add_use_case_group(self, category, simple_cases=[], complex_cases=[]):

        group_name = self._get_next_group_name(category)

        group_list = self._get_use_case_list(simple_cases, complex_cases)

        self.add_category_group(group_name, group_list)

    def _get_next_group_name(self, category):
        # check if any groups for category already exists
        # groups are named {category}-group<n>
        groups = [group for group in self.category_groups.keys()
                  if category in group]
        if not groups:
            next_group_name = f'{category}-group0'
        else:
            highest_group_num = max([group.split('-group')[-1]
                                     for group in groups])
            next_num = int(highest_group_num) + 1
            next_group_name = f'{category}-group{next_num}'

        return next_group_name

    def _get_use_case_list(self, simple_cases, complex_cases):
        use_cases_list = []

        # create use cases by requirement object to hold cases
        # with no additional requirements
        use_cases_no_requirements = METplusUseCasesByRequirement()

        if not isinstance(simple_cases, list):
            simple_cases = [simple_cases]

        if not isinstance(complex_cases, list):
            complex_cases = [complex_cases]

        # add simple use cases
        for config_args in simple_cases:
            name = os.path.basename(config_args).replace('.conf', '')
            use_case = METplusUseCase(name, config_args)
            use_cases_no_requirements.add_use_case(use_case)

        # add complex cases
        for complex_case in complex_cases:
            # get or determine name of use case
            name = complex_case.get('name')
            if not name:
                # use last config arg as name if not set
                last_arg = complex_case['config_args'][-1]
                name = os.path.basename(last_arg).replace('.conf', '')

            new_use_case = METplusUseCase(name, complex_case['config_args'])

            # cases with no requirements get added with simple use cases
            requirements = complex_case.get('requirements')
            if not requirements:
                use_cases_no_requirements.add_use_case(new_use_case)
                continue

            # check existing use cases by requirement to see if
            # case with the same requirements exists
            found = False
            for use_cases in use_cases_list:
                # if found, add use case
                if use_cases.has_same_requirements(requirements):
                    use_cases.add_use_case(new_use_case)
                    found = True
                    break

            # otherwise create new use cases by requirements object
            if not found:
                use_cases_by_req = METplusUseCasesByRequirement()
                use_cases_by_req.add_requirements(requirements)
                use_cases_by_req.add_use_case(new_use_case)

                # add new use case to list of use cases by requirement
                use_cases_list.append(use_cases_by_req)

        # add use cases with no requirements if not empty
        if use_cases_no_requirements.has_use_cases():
            use_cases_list.append(use_cases_no_requirements)

        return use_cases_list

class METplusUseCasesByRequirement:
    def __init__(self):
        self.requirements = []
        self.use_cases = []

    def add_requirements(self, requirements):
        if isinstance(requirements, str):
            requirements = [requirements]

        self.requirements.extend(requirements)

    def add_use_case(self, use_case):
        if not isinstance(use_case, METplusUseCase):
            raise TypeError()

        self.use_cases.append(use_case)

    def has_same_requirements(self, requirements):
        if len(self.requirements) != len(requirements):
            return False

        if sorted(self.requirements) != sorted(requirements):
            return False

        return True

    def has_use_cases(self):
        if not self.use_cases:
            return False
        return True


    def print(self, indent=0):
        padding = indent * ' '

        if self.requirements:
            requirements_list = ','.join(self.requirements)
        else:
            requirements_list = "No additional requirements"

        print(f"{padding}Requirements: {requirements_list}")

        for index, use_case in enumerate(self.use_cases):
            use_case.print(indent*2, index=index)
        print()

    def get_total_cases(self):
        return len(self.use_cases)

class METplusUseCase:
    def __init__(self, name, config_args):
        self.name = name
        if isinstance(config_args, str):
            config_args = [config_args]

        self.config_args = config_args

    def print(self, indent=0, index=None):
        padding = indent * ' '
        arg_indent = padding * 2
        if index is not None:
            padding = f'{padding}{index}: '
        print(f"{padding}{self.name}: ")
        for config_arg in self.config_args:
            print(f'{arg_indent}{config_arg}')


##################################################
# met_tool_wrapper
##################################################
def get_met_tool_wrapper():
    data_volume = 'met_tool_wrapper'
    case_dir = data_volume
    simple_use_cases = [
        f"{case_dir}/ASCII2NC/ASCII2NC.conf",
        f"{case_dir}/ASCII2NC/ASCII2NC_python_embedding.conf",
        f"{case_dir}/ASCII2NC/ASCII2NC_python_embedding_user_py.conf",
        f"{case_dir}/PyEmbedIngest/PyEmbedIngest.conf",
        f"{case_dir}/EnsembleStat/EnsembleStat.conf",
        f"{case_dir}/EnsembleStat/EnsembleStat_python_embedding.conf",
        f"{case_dir}/Example/Example.conf",
        f"{case_dir}/GempakToCF/GempakToCF.conf",
        f"{case_dir}/GenVxMask/GenVxMask.conf",
        f"{case_dir}/GenVxMask/GenVxMask_multiple.conf",
        f"{case_dir}/GenVxMask/GenVxMask_with_arguments.conf",
        f"{case_dir}/GridDiag/GridDiag.conf",
        f"{case_dir}/GridStat/GridStat.conf",
        f"{case_dir}/MODE/MODE.conf",
        f"{case_dir}/MTD/MTD.conf",
        f"{case_dir}/MTD/MTD_python_embedding.conf",
        f"{case_dir}/PB2NC/PB2NC.conf",
        f"{case_dir}/PCPCombine/PCPCombine_sum.conf",
        f"{case_dir}/PCPCombine/PCPCombine_add.conf",
        f"{case_dir}/PCPCombine/PCPCombine_bucket.conf",
        f"{case_dir}/PCPCombine/PCPCombine_user_defined.conf",
        f"{case_dir}/PCPCombine/PCPCombine_derive.conf",
        f"{case_dir}/PCPCombine/PCPCombine_loop_custom.conf",
        f"{case_dir}/PCPCombine/PCPCombine_subtract.conf",
        f"{case_dir}/PointStat/PointStat.conf",
        f"{case_dir}/Point2Grid/Point2Grid.conf",
        f"{case_dir}/PointStat/PointStat_once_per_field.conf",
        f"{case_dir}/RegridDataPlane/RegridDataPlane.conf",
        f"{case_dir}/RegridDataPlane/RegridDataPlane_multi_field_multi_file.conf",
        f"{case_dir}/RegridDataPlane/RegridDataPlane_multi_field_one_file.conf",
        f"{case_dir}/RegridDataPlane/RegridDataPlane_python_embedding.conf",
        f"{case_dir}/StatAnalysis/StatAnalysis.conf",
        f"{case_dir}/StatAnalysis/StatAnalysis_python_embedding.conf",
        f"{case_dir}/SeriesAnalysis/SeriesAnalysis.conf",
        f"{case_dir}/SeriesAnalysis/SeriesAnalysis_python_embedding.conf",
        f"{case_dir}/TCGen/TCGen.conf",
        f"{case_dir}/TCPairs/TCPairs_extra_tropical.conf",
        f"{case_dir}/TCPairs/TCPairs_tropical.conf",
        f"{case_dir}/TCRMW/TCRMW.conf",
        f"{case_dir}/TCStat/TCStat.conf",
    ]

    # complex use cases: contain multiple conf files or extra dependencies
    complex_use_cases = [

        {'name': 'GridStat_multiple_config',
         'config_args': [
             f'{case_dir}/GridStat/GridStat.conf',
             f'{case_dir}/GridStat/GridStat_forecast.conf',
             f'{case_dir}/GridStat/GridStat_observation.conf'
         ],
         'requirements': [],
         },

        {'name': 'CyclonePlotter',
         'config_args': [
             f'{case_dir}/CyclonePlotter/CyclonePlotter.conf',
             'user_env_vars.MET_PYTHON_EXE=python3',
             'user_env_vars.DISPLAY=localhost:0.0'
         ],
         'requirements': ['cartopy', 'matplotlib'],
         },

        {'name': 'PCPCombine_python_embedding',
         'config_args': [
             f'{case_dir}/PCPCombine/PCPCombine_python_embedding.conf',
             'user_env_vars.MET_PYTHON_EXE=python3'
         ],
         'requirements': ['h5py'],
         },

    ]

    return data_volume, simple_use_cases, complex_use_cases

##################################################
# climate
##################################################
def get_climate():
    data_volume = 'climate'
    case_dir = f'model_applications/{data_volume}'
    simple_use_cases = [
        f'{case_dir}/GridStat_fcstCESM_obsGFS_ConusTemp.conf',
        f'{case_dir}/MODE_fcstCESM_obsGPCP_AsianMonsoonPrecip.conf',
    ]

    complex_use_cases = []

    return data_volume, simple_use_cases, complex_use_cases

##################################################
# convection_allowing_models
##################################################
def get_convection_allowing_models():
    data_volume = 'convection_allowing_models'
    case_dir = f'model_applications/{data_volume}'
    simple_use_cases = [
        f'{case_dir}/EnsembleStat_fcstHRRRE_obsHRRRE_Sfc_MultiField.conf',
        f'{case_dir}/MODE_fcstHRRR_obsMRMS_Hail_GRIB2.conf',
        f'{case_dir}/EnsembleStat_fcstHRRR_fcstOnly_SurrogateSevere.conf',
        f'{case_dir}/GridStat_fcstHRRR_obsPracPerfect_SurrogateSevere.conf',
        f'{case_dir}/GridStat_fcstHRRR_obsPracPerfect_SurrogateSevereProb.conf',
        f'{case_dir}/Point2Grid_obsLSR_ObsOnly_PracticallyPerfect.conf',
    ]

    complex_use_cases = []

    return data_volume, simple_use_cases, complex_use_cases

##################################################
# cryosphere
##################################################
def get_cryosphere():
    data_volume = 'cryosphere'
    case_dir = f'model_applications/{data_volume}'
    simple_use_cases = [
        f'{case_dir}/GridStat_MODE_fcstIMS_obsNCEP_sea_ice.conf',
    ]

    complex_use_cases = []

    return data_volume, simple_use_cases, complex_use_cases

##################################################
# data_assimilation
##################################################
def get_data_assimilation():
    data_volume = 'data_assimilation'
    case_dir = f'model_applications/{data_volume}'

    simple_use_cases = []

    complex_use_cases = [
        {'name': 'StatAnalysis_fcstHAFS_obsPrepBufr_JEDI_IODA_interface',
         'config_args': [
            f'{case_dir}/StatAnalysis_fcstHAFS_obsPrepBufr_JEDI_IODA_interface.conf',
            'user_env_vars.MET_PYTHON_EXE=python3',
         ],
         'requirements': ['netCDF4'],
         },
    ]

    return data_volume, simple_use_cases, complex_use_cases

##################################################
# medium_range
##################################################
def get_medium_range(simple_splice=None, complex_splice=None):
    data_volume = 'medium_range'
    case_dir = f'model_applications/{data_volume}'

    simple_use_cases = [
        f'{case_dir}/PointStat_fcstGFS_obsNAM_Sfc_MultiField_PrepBufr.conf',
        f'{case_dir}/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByInit.conf',
        f'{case_dir}/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead.conf',
        f'{case_dir}/GridStat_fcstGFS_obsGFS_climoNCEP_MultiField.conf',
        f'{case_dir}/GridStat_fcstGFS_obsGFS_Sfc_MultiField.conf',
        f'{case_dir}/PointStat_fcstGFS_obsGDAS_UpperAir_MultiField_PrepBufr.conf', #2
    ]

    complex_use_cases = [
        {'name': 'TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT',
         'config_args': [
             f'{case_dir}/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_IVT.conf',
             'user_env_vars.MET_PYTHON_EXE=python3',
         ],
         'requirements': ['pygrib', 'metpy'],
         },

        {'name': 'TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics',
         'config_args': [
             f'{case_dir}/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics.conf',
             'user_env_vars.MET_PYTHON_EXE=python3',
         ],
         'requirements': ['pygrib', 'metpy'],
         },
    ]

    return data_volume, simple_use_cases, complex_use_cases

##################################################
# precipitation
##################################################
def get_precipitation():
    data_volume = 'precipitation'
    case_dir = f'model_applications/{data_volume}'
    simple_use_cases = [
        f'{case_dir}/GridStat_fcstGFS_obsCCPA_GRIB.conf',
        f'{case_dir}/EnsembleStat_fcstHRRRE_FcstOnly_NetCDF.conf',
        f'{case_dir}/GridStat_fcstHREFmean_obsStgIV_Gempak.conf',
        f'{case_dir}/GridStat_fcstHREFmean_obsStgIV_NetCDF.conf',
        f'{case_dir}/GridStat_fcstHRRR-TLE_obsStgIV_GRIB.conf',
        f'{case_dir}/MTD_fcstHRRR-TLE_FcstOnly_RevisionSeries_GRIB.conf',
        f'{case_dir}/MTD_fcstHRRR-TLE_obsMRMS.conf',
    ]

    complex_use_cases = []

    return data_volume, simple_use_cases, complex_use_cases

##################################################
# s2s
##################################################

def get_s2s():
    data_volume = 's2s'
    case_dir = f'model_applications/{data_volume}'

    simple_use_cases = [
        f'{case_dir}/GridStat_SeriesAnalysis_fcstNMME_obsCPC_seasonal_forecast.conf',
    ]

    complex_use_cases = []

    return data_volume, simple_use_cases, complex_use_cases

##################################################
# space_weather
##################################################
def get_space_weather():
    data_volume = 'space_weather'
    case_dir = f'model_applications/{data_volume}'

    simple_use_cases = [
        f'{case_dir}/GridStat_fcstGloTEC_obsGloTEC_vx7.conf',
        f'{case_dir}/GenVxMask_fcstGloTEC_FcstOnly_solar_altitude.conf',
    ]

    complex_use_cases = []

    return data_volume, simple_use_cases, complex_use_cases

##################################################
# tc_and_extra_tc
##################################################
def get_tc_and_extra_tc():
    data_volume = 'tc_and_extra_tc'
    case_dir = f'model_applications/{data_volume}'

    simple_use_cases = [
        f'{case_dir}/TCRMW_fcstGFS_fcstOnly_gonzalo.conf',
    ]

    complex_use_cases = []

    return data_volume, simple_use_cases, complex_use_cases

def get_use_case_suite():
    all_use_cases = METplusUseCaseSuite()
    all_use_cases.add_use_case_groups(get_met_tool_wrapper)

    all_use_cases.add_use_case_groups(get_climate)

    all_use_cases.add_use_case_groups(get_convection_allowing_models)

    all_use_cases.add_use_case_groups(get_cryosphere)

    all_use_cases.add_use_case_groups(get_data_assimilation)

    # medium_range 0-4 of simple
    all_use_cases.add_use_case_groups(get_medium_range,
                                      simple_slice=slice(0,4,1),
                                      complex_slice=None)

    # medium_range 5 of simple
    all_use_cases.add_use_case_groups(get_medium_range,
                                      simple_slice=5,
                                      complex_slice=None)

    # medium_range all complex
    all_use_cases.add_use_case_groups(get_medium_range,
                                      simple_slice=None,
                                      )

    all_use_cases.add_use_case_groups(get_precipitation)

    all_use_cases.add_use_case_groups([get_s2s,
                                       get_space_weather,
                                       get_tc_and_extra_tc])

    return all_use_cases

if __name__ == "__main__":
    all_use_cases = get_use_case_suite()
    all_use_cases.print()
    total_cases = all_use_cases.get_total_cases()
    print(f'Total number of use cases: {total_cases}')
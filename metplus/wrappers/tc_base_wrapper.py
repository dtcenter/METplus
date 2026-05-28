"""
Program Name: tc_base_wrapper.py
Contact(s): George McCabe
"""

from . import RuntimeFreqWrapper

from ..util import get_lead_sequence, sub_var_list
from ..util.time_util import ti_get_hours_from_relativedelta

'''!@namespace TCBaseWrapper
@brief parent class for the tropical cyclone wrappers
@endcode
'''

class TCBaseWrapper(RuntimeFreqWrapper):

    def __init__(self, config, instance=None):
        super().__init__(config, instance=instance)

    def add_met_config_tc_wind(self):
        self.add_met_config(name='compute_tangential_and_radial_winds', data_type='bool')
        self.add_met_config(name='u_wind_field_name', data_type='string')
        self.add_met_config(name='v_wind_field_name', data_type='string')
        self.add_met_config(name='tangential_velocity_field_name', data_type='string')
        self.add_met_config(name='tangential_velocity_long_field_name', data_type='string')
        self.add_met_config(name='radial_velocity_field_name', data_type='string')
        self.add_met_config(name='radial_velocity_long_field_name', data_type='string')

    def _set_lead_list(self, time_info, lead_seq=None):
        self.env_var_dict['METPLUS_LEAD_LIST'] = ''

        if lead_seq is None:
            lead_seq = get_lead_sequence(self.config, time_info)

        # set LEAD_LIST to list of forecast leads used
        if lead_seq == [0]:
            return

        lead_list = []
        for lead in lead_seq:
            lead_hours = (
                ti_get_hours_from_relativedelta(lead, valid_time=time_info['valid'])
                )
            lead_list.append(f'"{str(lead_hours).zfill(2)}"')

        self.env_var_dict['METPLUS_LEAD_LIST'] = f"lead = [{', '.join(lead_list)}];"

    def _set_data_field(self, time_info):
        """!Get list of fields from config to process. Build list of field info
            that are formatted to be read by the MET config file. Set DATA_FIELD
            item of c_dict with the formatted list of fields.
            Args:
                @param time_info time dictionary to use for string substitution
                @returns True if field list could be built, False if not.
        """
        field_list = sub_var_list(self.c_dict['VAR_LIST_TEMP'], time_info)
        if not field_list:
            self.log_error("Could not get field information from config.")
            return False

        all_fields = []
        for field in field_list:
            field_list = self.get_field_info(d_type='FCST',
                                             v_name=field['fcst_name'],
                                             v_level=field['fcst_level'],
                                             )
            if field_list is None:
                self.log_error(f'Could not get field info from {field}')
                return False

            all_fields.extend(field_list)

        data_field = ','.join(all_fields)
        self.env_var_dict['METPLUS_DATA_FIELD'] = f'field = [{data_field}];'
        return True

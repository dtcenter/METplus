"""
Program Name: data_ingest_wrapper.py
Contact(s): George McCabe
Abstract: Wrapper used to obtain input data
"""

import os

from ..util import do_string_sub, find_indices_in_config_section, download_file_http
from . import RuntimeFreqWrapper


class DataIngestWrapper(RuntimeFreqWrapper):
    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = 'ALL'

    """!Wrapper used to obtain input data"""
    def __init__(self, config, instance=None):
        self.app_name = 'data_ingest'
        super().__init__(config, instance=instance)

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        # skip logic used to find input files for each run time
        c_dict['FIND_FILES'] = False

        # read config variables for each DATA_INGEST<n>
        # url, local path, (optional) username/password
        indices = list(
            find_indices_in_config_section(r'DATA_INGEST_(\d+)_INPUT_TEMPLATE$',
                                           self.config,
                                           index_index=1).keys()
        )

        if not indices:
            self.log_error('No DATA_INGEST_<n>_INPUT_TEMPLATE variables found in config')
            return None

        c_dict['DATA_INGEST_INFO'] = []
        for index in indices:
            url_top = self.config.getdir(f'DATA_INGEST_{index}_INPUT_DIR', keep_double_slash=True)
            url = self.config.getraw('config', f'DATA_INGEST_{index}_INPUT_TEMPLATE', keep_double_slash=True)
            if url_top:
                url = f"{url_top}/{url}"

            local_dir = self.config.getdir(f'DATA_INGEST_{index}_OUTPUT_DIR')
            local_path = self.config.getraw('config', f'DATA_INGEST_{index}_OUTPUT_TEMPLATE')
            local_path = os.path.join(local_dir, local_path)

            # allow user to specify an empty username
            username = None
            if self.config.has_option('config', f'DATA_INGEST_{index}_USERNAME'):
                username = self.config.getraw('config', f'DATA_INGEST_{index}_USERNAME')

            # allow user to specify an empty password
            password = None
            if self.config.has_option('config', f'DATA_INGEST_{index}_PASSWORD'):
                password = self.config.getraw('config', f'DATA_INGEST_{index}_PASSWORD')

            # set skip-if-output-exists setting per index, using global DataIngest setting if unset
            skip_if_output_exists = c_dict['SKIP_IF_OUTPUT_EXISTS']
            if self.config.has_option('config', f'DATA_INGEST_{index}_SKIP_IF_OUTPUT_EXISTS'):
                skip_if_output_exists = self.config.getbool('config', f'DATA_INGEST_{index}_SKIP_IF_OUTPUT_EXISTS')

            # auto decompress by default unless set to False in config
            auto_decompress = self.config.getbool('config', f'DATA_INGEST_{index}_AUTO_DECOMPRESS', True)

            info = {
                'index': index,
                'url': url,
                'local_path': local_path,
                'username': username,
                'password': password,
                'skip_if_output_exists': skip_if_output_exists,
                'auto_decompress': auto_decompress,
            }

            # Add the entry to the list
            c_dict['DATA_INGEST_INFO'].append(info)

        return c_dict

    def run_at_time_once(self, time_info):
        """!Obtain data for each data ingest configuration for the current run time
        if the local file does not already exist.

        @param time_info dictionary with time information of the current run
        """
        success = True
        for ingest_info in self.c_dict['DATA_INGEST_INFO']:
            index = ingest_info['index']
            self.logger.info(f'Processing DATA_INGEST_{index}')

            local_path = do_string_sub(ingest_info['local_path'], **time_info)
            if os.path.exists(local_path):
                if ingest_info['skip_if_output_exists']:
                    self.logger.info(f'Local file {local_path} already exists. Skipping download.')
                    continue

                self.logger.debug(f'Local file {local_path} already exists. Downloading again.')

            url = do_string_sub(ingest_info['url'], **time_info)
            self.logger.info(f'Downloading file {url} to {local_path}')
            result = download_file_http(url=url, output_path=local_path,
                                        username=ingest_info['username'],
                                        password=ingest_info['password'],
                                        auto_decompress=ingest_info['auto_decompress'],
                                        config=self.config)
            if not result['success']:
                self.log_error(f'Failed to download file {url} to {local_path}\n'
                               f'ERROR: {result["error"]}')
                success = False
                continue

            self.logger.info('Downloaded completed successfully')

        return success

import pytest

import os
import shutil
import uuid

from metplus.util.diff_util import dirs_are_equal, ROUNDING_OVERRIDES
from metplus.util import mkdir_p

test_output_dir = os.path.join(os.environ['METPLUS_TEST_OUTPUT_BASE'],
                               'test_output')

stat_header = 'VERSION MODEL DESC     FCST_LEAD FCST_VALID_BEG  FCST_VALID_END  OBS_LEAD OBS_VALID_BEG   OBS_VALID_END   FCST_VAR FCST_UNITS FCST_LEV OBS_VAR OBS_UNITS OBS_LEV OBTYPE VX_MASK INTERP_MTHD INTERP_PNTS FCST_THRESH OBS_THRESH COV_THRESH ALPHA LINE_TYPE'
mpr_line_1 = 'V11.1.0 HRRR  ALL_1.25 120000    20220701_200000 20220701_200000 000000   20220701_200000 20220701_200000 HPBL     m          L0       HPBL    m         L0      ADPSFC DENVER  BILIN       4           NA          NA         NA         NA    MPR       5    4       DENVER            39.78616    -104.41425       0         0       2160.80324 1498.06763 AMDAR NA NA NA'
mpr_line_2 = 'V11.1.0 HRRR  ALL_1.25 120000    20220701_200000 20220701_200000 000000   20220701_200000 20220701_200000 HPBL     m          L0       HPBL    m         L0      ADPSFC DENVER  BILIN       4           NA          NA         NA         NA    MPR       5    4       DENVER            39.78616    -104.41425       0         0       2160.80324 1498.05994 AMDAR NA NA NA'
file_path_1 = '/some/path/of/fake/file/one'
file_path_2 = '/some/path/of/fake/file/two'
file_path_3 = '/some/path/of/fake/file/three'
csv_header = 'Last Name, First Name, Progress'
csv_val_1 = 'Mackenzie, Stu, 0.9999'
csv_val_2 = 'Kenny-Smith, Ambrose, 0.8977'


def create_diff_files(files_a, files_b):
    unique_id = str(uuid.uuid4())[0:8]
    dir_a = os.path.join(test_output_dir, f'diff_{unique_id}', 'a')
    dir_b = os.path.join(test_output_dir, f'diff_{unique_id}', 'b')
    mkdir_p(dir_a)
    mkdir_p(dir_b)
    write_test_files(dir_a, files_a)
    write_test_files(dir_b, files_b)
    return dir_a, dir_b


def write_test_files(dirname, files):
    for filename, lines in files.items():
        filepath = os.path.join(dirname, filename)
        if os.path.sep in filename:
            parent_dir = os.path.dirname(filepath)
            mkdir_p(parent_dir)

        with open(filepath, 'w') as file_handle:
            for line in lines:
                file_handle.write(f'{line}\n')


@pytest.mark.parametrize(
    'a_files, b_files, rounding_override, expected_is_equal', [
        # txt both empty dir
        ({}, {}, None, True),
        # txt A empty dir
        ({}, {'filename.txt': ['some', 'text']}, None, False),
        # txt B empty dir
        ({'filename.txt': ['some', 'text']}, {}, None, False),
        # txt both empty file
        ({'filename.txt': []}, {'filename.txt': []}, None, True),
        # txt A empty file
        ({'filename.txt': []}, {'filename.txt': ['some', 'text']}, None, False),
        # txt B empty file
        ({'filename.txt': ['some', 'text']}, {'filename.txt': []}, None, False),
        # stat header columns
        ({'filename.stat': [stat_header, mpr_line_1]},
         {'filename.stat': [f'{stat_header} NEW_COLUMN', mpr_line_1]},
         None, False),
        # stat number of lines
        ({'filename.stat': [stat_header, mpr_line_1]},
         {'filename.stat': [stat_header, mpr_line_1, mpr_line_2]},
         None, False),
        # stat number of columns
        ({'filename.stat': [stat_header, mpr_line_1]},
         {'filename.stat': [stat_header, f'{mpr_line_1} extra_value']},
         None, False),
        # stat string
        ({'filename.stat': [stat_header, mpr_line_1]},
         {'filename.stat': [stat_header, mpr_line_1.replace('L0', 'Z0')]},
         None, False),
        # stat default precision
        ({'filename.stat': [stat_header, mpr_line_1]},
         {'filename.stat': [stat_header, mpr_line_1.replace('39.78616', '39.78615')]},
         None, False),
        # stat float override precision
        ({'filename.stat': [stat_header, mpr_line_1]},
         {'filename.stat': [stat_header, mpr_line_1.replace('39.78616', '39.78615')]},
         4, True),
        # stat out of order
        ({'filename.stat': [stat_header, mpr_line_1, mpr_line_2]},
         {'filename.stat': [stat_header, mpr_line_2, mpr_line_1]},
         4, True),
        # stat version differs
        ({'filename.stat': [stat_header, mpr_line_1]},
         {'filename.stat': [stat_header, mpr_line_1.replace('V11.1.0', 'V12.0.0')]},
         None, True),
        # file_list A without file_list line
        ({'file_list.txt': [file_path_1, file_path_2, file_path_3]},
         {'file_list.txt': ['file_list', file_path_1, file_path_2, file_path_3]},
         None, True),
        # file_list B without file_list line
        ({'file_list.txt': ['file_list', file_path_1, file_path_2, file_path_3]},
         {'file_list.txt': [file_path_1, file_path_2, file_path_3]},
         None, True),
        # file_list out of order
        ({'file_list.txt': ['file_list', file_path_1, file_path_2, file_path_3]},
         {'file_list.txt': ['file_list', file_path_2, file_path_3, file_path_1]},
         None, True),
        # csv equal
        ({'file_list.csv': [csv_header, csv_val_1, csv_val_2]},
         {'file_list.csv': [csv_header, csv_val_1, csv_val_2]},
         None, True),
        # csv number of columns A
        ({'file_list.csv': [csv_header, csv_val_1, csv_val_2]},
         {'file_list.csv': [f'{csv_header}, Position', f'{csv_val_1}, flute', f'{csv_val_2}, harmonica']},
         None, False),
        # csv number of columns B
        ({'file_list.csv': [f'{csv_header}, Position', f'{csv_val_1}, flute', f'{csv_val_2}, harmonica']},
         {'file_list.csv': [csv_header, csv_val_1, csv_val_2]},
         None, False),
        # csv number of lines A
        ({'file_list.csv': [csv_header, csv_val_1, csv_val_2]},
         {'file_list.csv': [csv_header, csv_val_1]},
         None, False),
        # csv number of lines B
        ({'file_list.csv': [csv_header, csv_val_1]},
         {'file_list.csv': [csv_header, csv_val_1, csv_val_2]},
         None, False),
        # csv diff default precision
        ({'file_list.csv': [csv_header, csv_val_1, csv_val_2]},
         {'file_list.csv': [csv_header, csv_val_1.replace('0.9999', '0.9998'), csv_val_2]},
         None, False),
        # csv diff default precision
        ({'file_list.csv': [csv_header, csv_val_1, csv_val_2]},
         {'file_list.csv': [csv_header, csv_val_1.replace('0.9999', '0.9998'), csv_val_2]},
         3, True),
        # csv diff first item
        ({'file_list.csv': [csv_header, csv_val_1, csv_val_2]},
         {'file_list.csv': [csv_header, csv_val_1.replace('Mackenzie', 'Art'), csv_val_2]},
         None, False),
    ]
)
@pytest.mark.diff
def test_diff_dir_text_files(a_files, b_files, rounding_override, expected_is_equal):
    if rounding_override:
        for filename in a_files:
            ROUNDING_OVERRIDES[filename] = rounding_override

    a_dir, b_dir = create_diff_files(a_files, b_files)
    assert dirs_are_equal(a_dir, b_dir) == expected_is_equal

    # pass individual files instead of entire directory
    for filename in a_files:
        if filename in b_files:
            a_path = os.path.join(a_dir, filename)
            b_path = os.path.join(b_dir, filename)
            assert dirs_are_equal(a_path, b_path) == expected_is_equal

    shutil.rmtree(os.path.dirname(a_dir))

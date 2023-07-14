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


def create_diff_files(files_a, files_b):
    unique_id = str(uuid.uuid4())[0:8]
    dir_a = os.path.join(test_output_dir, f'diff_{unique_id}', 'a')
    dir_b = os.path.join(test_output_dir, f'diff_{unique_id}', 'b')
    mkdir_p(dir_a)
    mkdir_p(dir_b)
    write_files(dir_a, files_a)
    write_files(dir_b, files_b)
    return dir_a, dir_b


def write_files(dirname, files):
    for filename, lines in files.items():
        filepath = os.path.join(dirname, filename)
        if os.path.sep in filename:
            parent_dir = os.path.dirname(filepath)
            mkdir_p(parent_dir)

        with open(filepath, 'w') as file_handle:
            for line in lines:
                file_handle.write(f'{line}\n')


@pytest.mark.util
def test_diff_dirs_both_empty():
    a_dir, b_dir = create_diff_files({}, {})
    assert dirs_are_equal(a_dir, b_dir)
    shutil.rmtree(os.path.dirname(a_dir))


@pytest.mark.util
def test_diff_dirs_one_empty():
    test_files = {'filename.txt': ['some', 'text']}
    for empty_one in ('a', 'b'):
        a_files = b_files = {}
        if empty_one == 'a':
            b_files = test_files
        else:
            a_files = test_files
        a_dir, b_dir = create_diff_files(a_files, b_files)
        assert not dirs_are_equal(a_dir, b_dir)
        shutil.rmtree(os.path.dirname(a_dir))


@pytest.mark.util
def test_diff_files_both_empty():
    test_files = {'filename.txt': []}
    a_dir, b_dir = create_diff_files(test_files, test_files)
    assert dirs_are_equal(a_dir, b_dir)
    shutil.rmtree(os.path.dirname(a_dir))


@pytest.mark.util
def test_diff_files_one_empty():
    filename = 'filename.txt'
    test_content = ['some', 'text']
    for empty_one in ('a', 'b'):
        a_files = {filename: []}
        b_files = {filename: []}
        if empty_one == 'a':
            b_files[filename].extend(test_content)
        else:
            a_files[filename].extend(test_content)
        a_dir, b_dir = create_diff_files(a_files, b_files)
        assert not dirs_are_equal(a_dir, b_dir)
        shutil.rmtree(os.path.dirname(a_dir))


@pytest.mark.util
def test_diff_stat_header_columns():
    filename = 'filename.stat'
    a_content = [stat_header, mpr_line_1]
    b_content = [f'{stat_header} NEW_COLUMN', mpr_line_1]
    a_files = {filename: a_content}
    b_files = {filename: b_content}
    a_dir, b_dir = create_diff_files(a_files, b_files)
    assert not dirs_are_equal(a_dir, b_dir)
    shutil.rmtree(os.path.dirname(a_dir))


@pytest.mark.util
def test_diff_stat_number_of_lines():
    filename = 'filename.stat'
    a_content = [stat_header, mpr_line_1]
    b_content = [stat_header, mpr_line_1, mpr_line_2]
    a_files = {filename: a_content}
    b_files = {filename: b_content}
    a_dir, b_dir = create_diff_files(a_files, b_files)
    assert not dirs_are_equal(a_dir, b_dir)
    shutil.rmtree(os.path.dirname(a_dir))


@pytest.mark.util
def test_diff_stat_number_of_columns():
    filename = 'filename.stat'
    a_content = [stat_header, mpr_line_1]
    b_content = [stat_header, f'{mpr_line_1} extra_value']
    a_files = {filename: a_content}
    b_files = {filename: b_content}
    a_dir, b_dir = create_diff_files(a_files, b_files)
    assert not dirs_are_equal(a_dir, b_dir)
    shutil.rmtree(os.path.dirname(a_dir))


@pytest.mark.util
def test_diff_stat_string():
    filename = 'filename.stat'
    a_content = [stat_header, mpr_line_1]
    b_content = [stat_header, mpr_line_1.replace('L0', 'Z0')]
    a_files = {filename: a_content}
    b_files = {filename: b_content}
    a_dir, b_dir = create_diff_files(a_files, b_files)
    assert not dirs_are_equal(a_dir, b_dir)
    shutil.rmtree(os.path.dirname(a_dir))


@pytest.mark.util
def test_diff_stat_float_default_precision():
    filename = 'filename.stat'
    a_content = [stat_header, mpr_line_1]
    b_content = [stat_header, mpr_line_1.replace('39.78616', '39.78615')]
    a_files = {filename: a_content}
    b_files = {filename: b_content}
    a_dir, b_dir = create_diff_files(a_files, b_files)
    assert not dirs_are_equal(a_dir, b_dir)
    shutil.rmtree(os.path.dirname(a_dir))


@pytest.mark.util
def test_diff_stat_float_override_precision():
    filename = 'filename.stat'
    ROUNDING_OVERRIDES[filename] = 4
    a_content = [stat_header, mpr_line_1]
    b_content = [stat_header, mpr_line_1.replace('39.78616', '39.78615')]
    a_files = {filename: a_content}
    b_files = {filename: b_content}
    a_dir, b_dir = create_diff_files(a_files, b_files)
    assert dirs_are_equal(a_dir, b_dir)
    shutil.rmtree(os.path.dirname(a_dir))


@pytest.mark.util
def test_diff_stat_out_of_order():
    filename = 'filename.stat'
    ROUNDING_OVERRIDES[filename] = 4
    a_content = [stat_header, mpr_line_1, mpr_line_2]
    b_content = [stat_header, mpr_line_2, mpr_line_1]
    a_files = {filename: a_content}
    b_files = {filename: b_content}
    a_dir, b_dir = create_diff_files(a_files, b_files)
    assert dirs_are_equal(a_dir, b_dir)
    shutil.rmtree(os.path.dirname(a_dir))

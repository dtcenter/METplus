import pytest

import os
from unittest import mock
from PIL import Image
import numpy as np

from metplus.util import diff_util as du
from metplus.util import mkdir_p


STAT_HEADER = 'VERSION MODEL DESC     FCST_LEAD FCST_VALID_BEG  FCST_VALID_END  OBS_LEAD OBS_VALID_BEG   OBS_VALID_END   FCST_VAR FCST_UNITS FCST_LEV OBS_VAR OBS_UNITS OBS_LEV OBTYPE VX_MASK INTERP_MTHD INTERP_PNTS FCST_THRESH OBS_THRESH COV_THRESH ALPHA LINE_TYPE'
MPR_LINE_1 = 'V11.1.0 HRRR  ALL_1.25 120000    20220701_200000 20220701_200000 000000   20220701_200000 20220701_200000 HPBL     m          L0       HPBL    m         L0      ADPSFC DENVER  BILIN       4           NA          NA         NA         NA    MPR       5    4       DENVER            39.78616    -104.41425       0         0       2160.80324 1498.06763 AMDAR NA NA NA'
MPR_LINE_2 = 'V11.1.0 HRRR  ALL_1.25 120000    20220701_200000 20220701_200000 000000   20220701_200000 20220701_200000 HPBL     m          L0       HPBL    m         L0      ADPSFC DENVER  BILIN       4           NA          NA         NA         NA    MPR       5    4       DENVER            39.78616    -104.41425       0         0       2160.80324 1498.05994 AMDAR NA NA NA'
REFORMATTER_HEADER = 'Idx	version	model	desc	fcst_lead	fcst_valid_beg	fcst_valid_end	fcst_init_beg	obs_lead	obs_valid_beg	obs_valid_end	fcst_var	fcst_units	fcst_lev	obs_var	obs_units	obs_lev	obtype	vx_mask	interp_mthd	interp_pnts	fcst_thresh	obs_thresh	cov_thresh	alpha	line_type	total	stat_name	stat_value	stat_ncl	stat_ncu	stat_bcl	stat_bcu'
REFORMATTER_LINE_1 = '17	V12.1.0	SFS-GSL	NA	60000	1991-06-01	1991-06-01	1991-05-31 18:00:00	0	1991-06-01	1991-06-01	Soil_moisture	mm	0-1m	soilm1m	mm	19910601_000000,*,*	ERA5	FULL	NEAREST	1	NA	NA	-9999	0.05	CNT	21510	FBAR	504.27735	499.27867	509.27604	NA	NA'
TC_STAT_LINE_1 = 'V12.2.0 GPMI BEST EVENT_EQUAL AL012015 AL 01 ANA 20150508_120000 240000 20150509_120000 NA NA PROBRIRW 31.6 -77.7 32.5 -77.8 NA 54.23894 5.08551 -54 135.63956 80.31028 0 24 24 44 40 50 10 10 TS TS 5 -30 0 -10 0 0 100 10 0 30 0'
FILE_PATH_1 = '/some/path/of/fake/file/one'
FILE_PATH_2 = '/some/path/of/fake/file/two'
FILE_PATH_3 = '/some/path/of/fake/file/three'
CVS_HEADER = 'Last Name, First Name, Progress'
CSV_VAL_1 = 'Mackenzie, Stu, 0.9999'
CSV_VAL_2 = 'Kenny-Smith, Ambrose, 0.8977'


DEFAULT_NC = [
    [359, 0, 1],  # lon
    [-1, 0, 1],  # lat
    [0, 1],  # z
    [  # data
        [[1, 2], [3, 4], [5, 6]],
        [[2, 3], [4, 5], [6, 7]],
        [[30, 31], [33, 32], [34, 39]],
    ],
    "Temp",  # variable
]

DEFAULT_NC_WITH_NAN = [
    DEFAULT_NC[0],
    DEFAULT_NC[1],
    DEFAULT_NC[2],
    [
        [[1, 2], [3, 4], [5, 6]],
        [[2, 3], [4, 5], [6, 7]],
        [[30, 31], [33, 32], [34, np.nan]],
    ],
    DEFAULT_NC[4],
]


@pytest.fixture()
def dummy_nc1(tmp_path_factory, make_dummy_nc):
    # Construct a temporary netCDF file
    return make_dummy_nc(
        tmp_path_factory.mktemp("data1"),
        DEFAULT_NC[0],
        DEFAULT_NC[1],
        DEFAULT_NC[2],
        DEFAULT_NC[3],
        DEFAULT_NC[4],
        # Note: "nc5" is not included in NETCDF_EXTENSIONS, hence
        # we use it here to specifically trigger the call to
        # netCDF.Dataset in get_file_type.
        file_name= "fake.nc5"
    )


def _statment_in_capfd(capfd, check_print):
    out, _ = capfd.readouterr()
    print("out: ", out)
    for statement in check_print:
        assert statement in out


def create_diff_files(tmp_path_factory, files_a, files_b):
    dir_a = tmp_path_factory.mktemp('dir_a')
    dir_b = tmp_path_factory.mktemp('dir_b')

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
        ({'filename.stat': [STAT_HEADER, MPR_LINE_1]},
         {'filename.stat': [f'{STAT_HEADER} NEW_COLUMN', MPR_LINE_1]},
         None, False),
        # stat number of lines
        ({'filename.stat': [STAT_HEADER, MPR_LINE_1]},
         {'filename.stat': [STAT_HEADER, MPR_LINE_1, MPR_LINE_2]},
         None, False),
        # stat number of columns
        ({'filename.stat': [STAT_HEADER, MPR_LINE_1]},
         {'filename.stat': [STAT_HEADER, f'{MPR_LINE_1} extra_value']},
         None, False),
        # stat string
        ({'filename.stat': [STAT_HEADER, MPR_LINE_1]},
         {'filename.stat': [STAT_HEADER, MPR_LINE_1.replace('L0', 'Z0')]},
         None, False),
        # stat default precision
        ({'filename.stat': [STAT_HEADER, MPR_LINE_1]},
         {'filename.stat': [STAT_HEADER, MPR_LINE_1.replace('39.78616', '39.78615')]},
         None, False),
        # stat float override precision
        ({'filename.stat': [STAT_HEADER, MPR_LINE_1]},
         {'filename.stat': [STAT_HEADER, MPR_LINE_1.replace('39.78616', '39.78615')]},
         4, True),
        # stat out of order
        ({'filename.stat': [STAT_HEADER, MPR_LINE_1, MPR_LINE_2]},
         {'filename.stat': [STAT_HEADER, MPR_LINE_2, MPR_LINE_1]},
         4, True),
        # stat version differs
        ({'filename.stat': [STAT_HEADER, MPR_LINE_1]},
         {'filename.stat': [STAT_HEADER, MPR_LINE_1.replace('V11.1.0', 'V12.0.0')]},
         None, True),
        # file_list A without file_list line
        ({'file_list.txt': [FILE_PATH_1, FILE_PATH_2, FILE_PATH_3]},
         {'file_list.txt': ['file_list', FILE_PATH_1, FILE_PATH_2, FILE_PATH_3]},
         None, True),
        # file_list B without file_list line
        ({'file_list.txt': ['file_list', FILE_PATH_1, FILE_PATH_2, FILE_PATH_3]},
         {'file_list.txt': [FILE_PATH_1, FILE_PATH_2, FILE_PATH_3]},
         None, True),
        # file_list out of order
        ({'file_list.txt': ['file_list', FILE_PATH_1, FILE_PATH_2, FILE_PATH_3]},
         {'file_list.txt': ['file_list', FILE_PATH_2, FILE_PATH_3, FILE_PATH_1]},
         None, True),
        # csv equal
        ({'file_list.csv': [CVS_HEADER, CSV_VAL_1, CSV_VAL_2]},
         {'file_list.csv': [CVS_HEADER, CSV_VAL_1, CSV_VAL_2]},
         None, True),
        # csv number of columns A
        ({'file_list.csv': [CVS_HEADER, CSV_VAL_1, CSV_VAL_2]},
         {'file_list.csv': [f'{CVS_HEADER}, Position', f'{CSV_VAL_1}, flute', f'{CSV_VAL_2}, harmonica']},
         None, False),
        # csv number of columns B
        ({'file_list.csv': [f'{CVS_HEADER}, Position', f'{CSV_VAL_1}, flute', f'{CSV_VAL_2}, harmonica']},
         {'file_list.csv': [CVS_HEADER, CSV_VAL_1, CSV_VAL_2]},
         None, False),
        # csv number of lines A
        ({'file_list.csv': [CVS_HEADER, CSV_VAL_1, CSV_VAL_2]},
         {'file_list.csv': [CVS_HEADER, CSV_VAL_1]},
         None, False),
        # csv number of lines B
        ({'file_list.csv': [CVS_HEADER, CSV_VAL_1]},
         {'file_list.csv': [CVS_HEADER, CSV_VAL_1, CSV_VAL_2]},
         None, False),
        # csv diff default precision
        ({'file_list.csv': [CVS_HEADER, CSV_VAL_1, CSV_VAL_2]},
         {'file_list.csv': [CVS_HEADER, CSV_VAL_1.replace('0.9999', '0.9998'), CSV_VAL_2]},
         None, False),
        # csv diff default precision
        ({'file_list.csv': [CVS_HEADER, CSV_VAL_1, CSV_VAL_2]},
         {'file_list.csv': [CVS_HEADER, CSV_VAL_1.replace('0.9999', '0.9998'), CSV_VAL_2]},
         3, True),
        # csv diff first item
        ({'file_list.csv': [CVS_HEADER, CSV_VAL_1, CSV_VAL_2]},
         {'file_list.csv': [CVS_HEADER, CSV_VAL_1.replace('Mackenzie', 'Art'), CSV_VAL_2]},
         None, False),
        # csv diff trunc not equal round
        ({'file_list.csv': [CVS_HEADER, CSV_VAL_1, CSV_VAL_2]},
         {'file_list.csv': [CVS_HEADER, CSV_VAL_1.replace('0.9999', '1.0001'), CSV_VAL_2, ]},
         3, True),
        # METdataio reformatter output - equal
        ({'reformatted.txt': [REFORMATTER_HEADER, REFORMATTER_LINE_1]},
         {'reformatted.txt': [REFORMATTER_HEADER, REFORMATTER_LINE_1]},
         None, True),
        # METdataio reformatter output - version differs
        ({'reformatted.txt': [REFORMATTER_HEADER, REFORMATTER_LINE_1]},
         {'reformatted.txt': [REFORMATTER_HEADER, REFORMATTER_LINE_1.replace('V12.1.0', 'V12.1.1')]},
         None, True),
        # TC-Stat output - equal
        ({'PROBRIRW_filter_ee.tcst': [TC_STAT_LINE_1]},
         {'PROBRIRW_filter_ee.tcst': [TC_STAT_LINE_1]},
         None, True),
        # TC-Stat output - version differs
        ({'PROBRIRW_filter_ee.tcst': [TC_STAT_LINE_1]},
         {'PROBRIRW_filter_ee.tcst': [TC_STAT_LINE_1.replace('V12.1.0', 'V12.2.0')]},
         None, True),
    ],
)
@pytest.mark.diff
def test_diff_dir_text_files(tmp_path_factory, a_files, b_files, rounding_override, expected_is_equal):
    if rounding_override:
        for filename in a_files:
            du.ROUNDING_OVERRIDES[filename] = rounding_override

    a_dir, b_dir = create_diff_files(tmp_path_factory, a_files, b_files)
    assert du.dirs_are_equal(str(a_dir), str(b_dir)) == expected_is_equal

    # pass individual files instead of entire directory
    for filename in a_files:
        if filename in b_files:
            a_path = os.path.join(a_dir, filename)
            b_path = os.path.join(b_dir, filename)
            assert du.dirs_are_equal(a_path, b_path) == expected_is_equal


@pytest.mark.parametrize(
    "path,expected",
    [
        ("/path/to/file.csv", "csv"),
        ("/path/to/file.jpeg", "image"),
        ("/path/to/file.jpg", "image"),
        ("/path/to/file.nc", "netcdf"),
        ("/path/to/file.cdf", "netcdf"),
        ("/path/to/file.pdf", "pdf"),
        ("/path/to/file.zip", "skip .zip"),
        ("/path/to/file.png", "image"),
        ("/path/to/file.bigfoot", "unknown"),
    ],
)
@pytest.mark.util
def test_get_file_type(path, expected):
    actual = du.get_file_type(path)
    assert actual == expected


@pytest.mark.util
def test_get_file_type_netcdf4(dummy_nc1):
    actual = du.get_file_type(dummy_nc1)
    assert actual == 'netcdf'


@mock.patch.object(du, "UNSUPPORTED_EXTENSIONS", [".foo"])
@pytest.mark.util
def test_get_file_type_unsupported():
    actual = du.get_file_type("/path/to/file.foo")
    assert actual == "unsupported .foo"


@pytest.mark.util
def test_get_file_type_extensions():
    # Check all extensions are unique, otherwise we may
    # get unexpected result from get_file_type
    extensions = [
        du.IMAGE_EXTENSIONS,
        du.NETCDF_EXTENSIONS,
        du.SKIP_EXTENSIONS,
        du.PDF_EXTENSIONS,
        du.CSV_EXTENSIONS,
        du.UNSUPPORTED_EXTENSIONS,
    ]
    flat_list = [ext for x in extensions for ext in x]
    assert len(set(flat_list)) == len(flat_list)


@pytest.mark.parametrize(
    "nc_data,fields,expected,check_print",
    [
        (
            # Compare exact same data
            [
                DEFAULT_NC[0],
                DEFAULT_NC[1],
                DEFAULT_NC[2],
                DEFAULT_NC[3],
                DEFAULT_NC[4],
            ],
            None,
            True,
            None,
        ),
        # Field name differ
        (
            [
                DEFAULT_NC[0],
                DEFAULT_NC[1],
                DEFAULT_NC[2],
                DEFAULT_NC[3],
                "Foo",
            ],
            None,
            False,
            [
                "ERROR: Field list differs between files",
                "File_A: ['Latitude', 'Levels', 'Longitude', 'Temp', 'Time']",
                "File_B:['Foo', 'Latitude', 'Levels', 'Longitude', 'Time']",
            ],
        ),
        # One small value change
        (
            [
                DEFAULT_NC[0],
                DEFAULT_NC[1],
                DEFAULT_NC[2],
                [
                    [[1, 2], [3, 4], [5, 6]],
                    [[2, 3], [4, 5], [6, 7]],
                    [[30, 31], [33, 32], [34, 39.1]],
                ],
                DEFAULT_NC[4],
            ],
            None,
            False,
            [
                "ERROR: Field (Temp) values differ",
            ],
        ),
        # Value changed but not comparing that field
        (
            [
                DEFAULT_NC[0],
                DEFAULT_NC[1],
                DEFAULT_NC[2],
                [
                    [[1, 2], [3, 4], [5, 6]],
                    [[2, 3], [4, 5], [6, 7]],
                    [[30, 31], [33, 32], [34, 39.001]],
                ],
                DEFAULT_NC[4],
            ],
            ["Longitude", "Latitude", "Levels"],
            True,
            None,
        ),
        # Contains nan difference
        (
            DEFAULT_NC_WITH_NAN,
            None,
            False,
            ["Variable Temp contains NaN. Comparing each value"],
        ),
        # Contains difference in masked count
        (
            [
                DEFAULT_NC[0],
                DEFAULT_NC[1],
                DEFAULT_NC[2],
                [
                    [[1, 2], [3, 4], [5, 6]],
                    [[2, 3], [4, 5], [6, 7]],
                    [[30, 31], [33, 32], [34, -9999]],
                ],
                DEFAULT_NC[4],
            ],
            None,
            False,
            ["Field Temp has differing number of missing data values"],
        ),
        # Field doesn't exist
        (
            [
                DEFAULT_NC[0],
                DEFAULT_NC[1],
                DEFAULT_NC[2],
                DEFAULT_NC[3],
                DEFAULT_NC[4],
            ],
            "Bar",
            False,
            ["ERROR: Field Bar not found"],
        ),
    ],
)
@pytest.mark.util
def test_nc_is_equal(
    capfd, tmp_path_factory, make_dummy_nc, dummy_nc1, nc_data, fields, expected, check_print
):
    # make a dummy second file to compare to dummy_nc1
    dummy_nc2 = make_dummy_nc(tmp_path_factory.mktemp("data2"), *nc_data)
    assert du.nc_is_equal(dummy_nc1, dummy_nc2, fields=fields, debug=True) == expected

    if check_print:
        _statment_in_capfd(capfd, check_print)

@pytest.mark.parametrize(
    "nc_data,fields,expected,check_print",
    [
        (
            DEFAULT_NC_WITH_NAN,
            None,
            True,
            ["Variable Temp contains NaN. Comparing each value"],
        ),
    ]
)
@pytest.mark.util
def test_nc_is_equal_both_nan(
    capfd, tmp_path_factory, make_dummy_nc, nc_data, fields, expected, check_print
):
    dummy_nc = make_dummy_nc(tmp_path_factory.mktemp("data2"), *nc_data)
    assert du.nc_is_equal(dummy_nc, dummy_nc, fields=fields, debug=True) == expected

    if check_print:
        _statment_in_capfd(capfd, check_print)


@pytest.mark.parametrize(
    "val,expected",[
    (np.float32(44.54), True),
    (-0.15, True),
    ("-123,456.5409", False),
    ("2345j", False),
    ("-12345.244", True),
    ("foo", False)
    ]
)
@pytest.mark.util
def test__is_number(val, expected):
    assert du._is_number(val) == expected


@pytest.mark.parametrize(
    'func, args, patch_func, patch_return, expected',
    [
        (
            du._handle_csv_files,
            ['path/file1.csv', 'path/file2.csv'],
            'compare_csv_files',
            True,
            True,
        ),
        (
            du._handle_csv_files,
            ['path/file1.csv', 'path/file2.csv'],
            'compare_csv_files',
            False,
            ('path/file1.csv', 'path/file2.csv', 'CSV diff', ''),
        ),
        (
            du._handle_netcdf_files,
            ['path/file1.nc', 'path/file2.nc'],
            'nc_is_equal',
            True,
            True,
        ),
        (
            du._handle_netcdf_files,
            ['path/file1.nc', 'path/file2.nc'],
            'nc_is_equal',
            False,
            ('path/file1.nc', 'path/file2.nc', 'NetCDF diff', ''),
        ),
        (
            du._handle_pdf_files,
            ['path/file1.pdf', 'path/file2.pdf', True],
            'compare_pdf_as_images',
            True,
            True,
        ),
        (
            du._handle_pdf_files,
            ['path/file1.pdf', 'path/file2.pdf', True],
            'compare_pdf_as_images',
            False,
            ('path/file1.pdf', 'path/file2.pdf', 'PDF diff', ''),
        ),
        (
            du._handle_image_files,
            ['path/file1.png', 'path/file2.png', True],
            'compare_image_files',
            True,
            True,
        ),
        (
            du._handle_image_files,
            ['path/file1.png', 'path/file2.png', True],
            'compare_image_files',
            False,
            ('path/file1.png', 'path/file2.png', 'Image diff', ''),
        ),
    ],
)
@pytest.mark.util
def test__handle_funcs(func, args, patch_func, patch_return, expected):
    with mock.patch.object(du, patch_func, return_value=patch_return):
        actual = func(*args)
        assert actual == expected


@pytest.mark.parametrize(
    'cmp_return, comp_txt_return, expected',
    [
        (True, True, True),
        (False, True, True),
        (False, False, ('file1.txt', 'file2.txt', 'Text diff', '')),
    ],
)
@pytest.mark.util
def test__handle_text_files(cmp_return, comp_txt_return, expected):
    with mock.patch.object(du.filecmp, 'cmp', return_value=cmp_return):
        with mock.patch.object(du, 'compare_txt_files', return_value=comp_txt_return):
            actual = du._handle_text_files(
                'file1.txt', 'file2.txt', '/dir_a/', '/dir_b/'
            )
            assert actual == expected


@pytest.mark.parametrize(
    "colour_a, colour_b, save_diff, expected, check_print",
    [
        (
            255,
            255,
            False,
            True,
            None
         ),
        (
            255,
            253,
            False,
            False,
            ['Difference pixel: (1, 1, 0)'],
        ),
        (
            255,
            0,
            True,
            False,
            ['Difference pixel: (254, 0, 0)'],
        ),
    ],
)
@pytest.mark.util
def test_compare_image_files(
    capfd, tmp_path_factory, colour_a, colour_b, save_diff, expected, check_print
):
    image_dir = tmp_path_factory.mktemp('images')
    image1 = image_dir / 'img1.jpg'
    image2 = image_dir / 'img2.jpg'

    expected_diff = os.path.join(image_dir, 'img2_diff.png')

    def _make_test_img(file_path, col):
        im = Image.new('RGB', [1, 1], col)
        im.save(file_path)
        im.close()

    _make_test_img(image1, colour_a)
    _make_test_img(image2, colour_b)

    actual = du.compare_image_files(image1, image2, save_diff)

    if save_diff:
        assert actual == expected_diff
        assert os.path.exists(actual)
    else:
        assert actual == expected

    # Just to check the diffs are correctly output
    if check_print:
        _statment_in_capfd(capfd, check_print)


@pytest.mark.parametrize(
    'array_a, array_b, expected, check_print',
    [
        # basic test
        (
            np.array([1, 2, 3.9]),
            np.array([1, 2, 3.9]),
            True,
            None,
        ),
        # diff test
        (
            np.array([1, 2, 3.9]),
            np.array([1, 2, 4]),
            False,
            ["val_a: 3.9, val_b: 4"],
        ),
        # stored as strings
        (
            '[1, 2, 3.9]',
            '[1, 2, 3.9]',
            True,
            None,
        ),
        # multi dimentional with nan
        (
            np.array([[1, 2, 3.9],[np.nan, 5, 6]]),
            np.array([[1, 2, 3.9],[np.nan, 5, 6]]),
            True,
            None,
        ),
    ],
)
@pytest.mark.util
def test__all_values_are_equal(capfd, array_a, array_b, expected, check_print):
    
    actual = du._all_values_are_equal(array_a, array_b)
    assert actual == expected
    if check_print:
        _statment_in_capfd(capfd, check_print)


@pytest.mark.parametrize(
    'extension,check_print',
    [
        ('.zip', ["Skipping .zip file"]),
        ('.gif', ["Skipping .gif file"]),
        ('.ix', ["Skipping .ix file"]),
        ('.log', ["Skipping .log file"]),
        #('', ["Skipping file without extension"]),
    ],
)
@pytest.mark.util
def test_compare_files_skip_extensions(capfd, tmp_path_factory, extension, check_print):
    dir_a = tmp_path_factory.mktemp('dir_a')
    dir_b = tmp_path_factory.mktemp('dir_b')
    file_a = str(dir_a / f'file{extension}')
    file_b = str(dir_b / f'file{extension}')
    open(file_a, 'w').close()
    open(file_b, 'w').close()
    assert du.compare_files(file_a, file_b, debug=True, dir_a=dir_a, dir_b=dir_b) is None
    _statment_in_capfd(capfd, check_print)


@pytest.mark.parametrize(
    'value_a,value_b,expected_result',
    [
        # equal numbers
        ('1.1', '1.1', True),
        # equal strings
        ('abc', 'abc', True),
        # one not a number
        ('1.1', 'abc', False),
        # another one not a number
        ('abc', '1.1', False),
        # almost zero
        ('0.0', '0.000000000001', True),
        # significant figures
        ('300124.88', '300124.89', True),
        # truncate float
        ('1.1238', '1.1239', True),
        # round float
        ('1.1241', '1.1239', True),
    ],
)
@pytest.mark.util
def test_is_equal_rounded(value_a, value_b, expected_result):
    du.rounding_precision = 3
    assert du._is_equal_rounded(value_a, value_b) == expected_result

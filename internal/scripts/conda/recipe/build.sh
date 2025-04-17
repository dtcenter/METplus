#!/bin/bash
set -ex

# set env vars to ensure libraries and headers from install are used
export CFLAGS="-I${PREFIX}/include $CFLAGS"
export CPPFLAGS="-I${PREFIX}/include $CPPFLAGS"
export LIBRARY_PATH="${PREFIX}/lib:$LIBRARY_PATH"
export CPATH="${PREFIX}/include:$CPATH"
export LDFLAGS="${LDFLAGS} -Wl,-rpath,${PREFIX}/lib -L${PREFIX}/lib -Wl,-rpath,${PREFIX}/lib/metview-bundle/lib -L${PREFIX}/lib/metview-bundle/lib"

# prevent isatty conflict in MET install
export CXXFLAGS="-DHAVE_ISATTY ${CXXFLAGS}"

# set env vars used by MET install
export MET_PYTHON_CC=$(${PREFIX}/bin/python3-config --cflags)
export MET_PYTHON_LD=$(${PREFIX}/bin/python3-config --ldflags --embed)
export MET_PYTHON_BIN_EXE=${PREFIX}/bin/python3
export MET_FREETYPELIB="${PREFIX}/lib"
export MET_FREETYPEINC="${PREFIX}/include/freetype2"
export MET_CAIROINC="${PREFIX}/include/cairo"
export MET_CAIROLIB="${PREFIX}/lib"
export MET_ECKIT="${PREFIX}/lib/metview-bundle"
export MET_ATLAS="${PREFIX}/lib/metview-bundle"


###
# GS fonts
###

# Add GS fonts to the package
mv "${SRC_DIR}/gs-fonts" "${PREFIX}/gs-fonts"

# Create an activate script to set env vars:
#  - location of GS fonts, for use by mode graphics
#  - location of METplus parm directory to find use case config files

mkdir -p "${PREFIX}/etc/conda/activate.d"
printf "export MET_FONT_DIR=${PREFIX}/gs-fonts\n" > "${PREFIX}/etc/conda/activate.d/${PKG_NAME}-activate.sh"

PYTHON_VERSION=$(${MET_PYTHON_BIN_EXE} -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
printf "export METPLUS_PARM_BASE=${PREFIX}/lib/python${PYTHON_VERSION}/site-packages/metplus/parm\n" >> "${PREFIX}/etc/conda/activate.d/${PKG_NAME}-activate.sh"


###
# Install MET executables
###

# Update config.sub and config.guess before running configure
cp ${BUILD_PREFIX}/share/gnuconfig/config.sub ./MET/
cp ${BUILD_PREFIX}/share/gnuconfig/config.guess ./MET/

(cd MET &&
     ./configure --prefix="${PREFIX}" --enable-all BUFRLIB_NAME=-lbufr_4 GRIB2CLIB_NAME=-lg2c &&
     make install -j${CPU_COUNT} &&
     make test)

# Run sed with the proper in-place option
sed -i.bak "s|MET_INSTALL_DIR = /path/to|MET_INSTALL_DIR = ${PREFIX}|g" parm/metplus_config/defaults.conf
rm parm/metplus_config/defaults.conf.bak

$PYTHON -m pip install . --no-deps --prefix=$PREFIX

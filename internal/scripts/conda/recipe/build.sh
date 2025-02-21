#!/bin/bash
set -ex

# set env vars to ensure libraries and headers from install are used
export CFLAGS="-I${PREFIX}/include $CFLAGS"
export CPPFLAGS="-I${PREFIX}/include $CPPFLAGS"
export LIBRARY_PATH="${PREFIX}/lib:$LIBRARY_PATH"
export CPATH="${PREFIX}/include:$CPATH"
export LDFLAGS="${LDFLAGS} -Wl,-rpath,${PREFIX}/lib -L${PREFIX}/lib"

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

# Determine the number of processors
NUM_PROCS=$(sysctl -n hw.ncpu || grep -c ^processor /proc/cpuinfo || 1)


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
printf "export METPLUS_PARM_BASE=${PREFIX}/lib/python3.10/site-packages/metplus/parm\n" > "${PREFIX}/etc/conda/activate.d/${PKG_NAME}-activate.sh"

###
# Install eckit and atlas for ugrid support (requires ecbuild)
###

# install ecbuild

mkdir ecbuild/build
(cd ecbuild/build &&
     cmake ../ -DCMAKE_INSTALL_PREFIX=${PREFIX} &&
     make -j${NUM_PROCS} install)

# install eckit
cmake_args=""
if [[ "$OSTYPE" == "darwin"* ]]; then
  cmake_args="-DCURSES_LIBRARY=${PREFIX}/lib/libncurses.dylib"
fi

mkdir eckit/build
(cd eckit/build &&
     cmake ../ -DCMAKE_INSTALL_PREFIX=${PREFIX} -DCMAKE_PREFIX_PATH=${PREFIX} -DMPI_C_COMPILER=${PREFIX}/bin/mpicc -DMPI_CXX_COMPILER=${PREFIX}/bin/mpicxx ${cmake_args} &&
     make -j${NUM_PROCS} && make install)

# install atlas
mkdir atlas/build
(cd atlas/build &&
     cmake ../ -DCMAKE_INSTALL_PREFIX=${PREFIX} -DCMAKE_PREFIX_PATH=${PREFIX} &&
     make -j${NUM_PROCS} install)


###
# Install MET executables
###

# Update config.sub and config.guess before running configure
curl -o ./MET/config.sub http://git.savannah.gnu.org/cgit/config.git/plain/config.sub
curl -o ./MET/config.guess http://git.savannah.gnu.org/cgit/config.git/plain/config.guess

(cd MET &&
     ./configure --prefix="${PREFIX}" --enable-all BUFRLIB_NAME=-lbufr_4 GRIB2CLIB_NAME=-lg2c &&
     make install -j${NUM_PROCS} &&
     make test)

# Run sed with the proper in-place option
sed -i.bak "s|MET_INSTALL_DIR = /path/to|MET_INSTALL_DIR = ${PREFIX}|g" parm/metplus_config/defaults.conf
rm parm/metplus_config/defaults.conf.bak

$PYTHON -m pip install . --no-deps --prefix=$PREFIX

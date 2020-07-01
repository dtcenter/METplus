##@namespace produtil.testing
# Test suite automation utilities.
#
# The produtil.testing package contains a system that automates
# testing of a suite of programs.  This is intended to be used for
# regression testing, not large-scale retrospective science tests.
#
# The produtil.testing suite has its own test description language.  A
# parser, produtil.testing.parse, parses this into an object tree.  A
# set of compilers (produtil.testing.rocoto and
# produtil.testing.script) compiles the object tree into a script or
# set of scripts for testing.

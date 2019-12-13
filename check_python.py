import argparse
import subprocess
import sys

def main():
    check_python_version()
    return 0

def check_python_version():
    major = sys.version_info.major
    minor = sys.version_info.minor
    your_version = (str)(major)+ '.' + (str)(minor)
    if major != 3:
        print('Only Python 3.6 is supported, you have version ', your_version)
        sys.exit(1)
    else:
        if minor != 6:
            # Print warning that minimum supported
            # version of Python is 3.6
            print('Only Python 3.6 is supported, you have version {major}.{minor}')
        else:
            # OK
            print('You are using the correct version of Python: ', your_version)

if __name__ == "__main__":
    main()
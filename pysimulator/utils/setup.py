from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import sys

if __name__ == '__main__':
    file_name = ''
    for arg in sys.argv:
        prefix_len = len('--py-file=')
        if len(arg) > prefix_len and arg[:prefix_len] == '--py-file=':
            file_name = arg[prefix_len:]
            sys.argv.remove(arg)

    if file_name == '':
        raise NameError('Source file name is empty')
    setup(ext_modules = cythonize([file_name]))

import sys
sys.path.append('./lib')
from optparse import OptionParser
from alpha_engine import AlphaEngine

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-c',dest='config')
    (options, args) = parser.parse_args()

    engine = AlphaEngine(options.config)
    engine.run()

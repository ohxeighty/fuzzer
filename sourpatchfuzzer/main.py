import harness
from argparse import ArgumentParser
from os.path import isfile
from sys import exit, argv

def fuzz(binary, sample):
    binls = harness.Harness(binary, sample) # not how this works - pls fix
    binls.spawn_process()
    binls.cont()
    binls.send(b"{}")

if __name__ == '__main__':
    parser = ArgumentParser(description='a warm and fuzzy feeling')
    parser.add_argument('binary', help='binary to fuzz through')
    parser.add_argument('sample', help='sample valid input for binary')
    args = parser.parse_args()
    
    if not isfile(args.binary):
        print('"{}" not found!'.format(args.binary))
        exit(-1)
    elif not isfile(args.sample):
        print('"{}" not found!'.format(args.sample))
        exit(-1)
    
    fuzz(args.binary, args.sample)

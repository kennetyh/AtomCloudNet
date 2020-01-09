from configparser import ConfigParser
import argparse
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Specify setting (generates all corresponding .ini files).')
    parser.add_argument('--setting', type=int, default=1) # setting == 0 if you want to run coulombnet
    args = parser.parse_args()
    if args.setting == 1:
        path = 'config_ACN/'
    else:
        path = 'config/'

    num_runs = len([name for name in os.listdir(path)]) - 1 # do not add other config files (except the base one)
    print("Running a total of {} jobs!".format(num_runs))

    if args.setting == 1:
        for i in range(num_runs):
            ini_id = i + 1
            print("Running configuration N°" + str(ini_id).zfill(5))
            os.system('bsub -W 24:00 -R "rusage[mem=16382]" python sandbox.py --run ' + str(ini_id))
            # os.system('bsub -W 24:00 python sandbox.py --run ' + str(ini_id))
            # os.system('python sandbox.py --run ' + str(int(ini_id)))

    if args.setting == 0:
        for i in range(24):
            ini_id = i + 1
            print("Running configuration N°" + str(ini_id).zfill(5))
            os.system('bsub -W 24:00 -R "rusage[mem=16382]" python nnCM.py --run ' + str(ini_id))
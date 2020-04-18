#!/usr/bin/python3

import os
import math
import argparse
import subprocess

from fill_generator import *

PACKAGE_BASE_PATH = "packbase"
FUNCTION_PATH = os.path.join(PACKAGE_BASE_PATH,  "functions")

print(PACKAGE_BASE_PATH)
print(FUNCTION_PATH)

PACKAGE_NAME = "Pickle_Functions"

SERVER_ADDRESS = "mason@nastypickle"
SERVER_PATHS = [
    "minecraftbe/PickleWorld/worlds/'Pickle Level'/development_behavior_packs",
    "minecraftbe/PickleWorld/development_behavior_packs",
    ]

LOCAL_DIRS = [os.path.join("C:","Users","there","AppData","Local","Packages",
    "Microsoft.MinecraftUWP_8wekyb3d8bbwe","LocalState","games","com.mojang",
    "development_behavior_packs")]


parser = argparse.ArgumentParser()
parser.add_argument("--copy-to-server", default=False, action="store_true")
parser.add_argument("--copy-to-sandbox", default=False, action="store_true")
args = parser.parse_args()

if args.copy_to_server:
    for path in SERVER_PATHS:
        ssh_cmd = ['scp', '-r', PACKAGE_NAME, "{}:{:s}".format(
            PACKAGE_NAME,SERVER_ADDRESS, path)]
        subprocess.run(ssh_cmd)
    
    exit()

if args.copy_to_sandbox:
    for path in LOCAL_DIRS:
        cmd = "cp -r Pickle_Functions {}".format(PATH)
        cmd = cmd.split()
        subprocess.run(cmd)
    
    exit()


MAX_CMDS = 10000

# note, these make the objects are created with the center at 
# the player's current position

def write_commands(fname, commands):
    pathname = os.path.join(FUNCTION_PATH, "{}.mcfunction".format(fname))

    
    if len(commands) <= MAX_CMDS:
        with open(pathname, 'w') as f:
            print("{}: {}".format(pathname,len(commands)))
            for cmd in commands:
                f.write(cmd + "\n")
    else:
        raise Exception("Commands exceed limit ({})".format(len(commands)))

if __name__ == '__main__':
    for Shape, label in [(HemisphereSolid, 'dome'), (SphereSolid, 'sphere')]:
        for diameter in [17, 33, 65]:
            outer = Shape(diameter)
            outer.generate_regions()
            inner = Shape(diameter - 2)
            inner.generate_regions()

            cmds_outer = cmd_fill(outer.regions, 'glass')
            cmds_inner = cmd_fill(inner.regions, 'air')

            fname = "{}-shell-r{}".format(label, (diameter-1)//2)
            cmds = cmds_outer + cmds_inner

            write_commands(fname, cmds)
        

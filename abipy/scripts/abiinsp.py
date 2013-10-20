#!/usr/bin/env python
"""Script to inspect the status of Abinit calculations at run-time."""
from __future__ import division, print_function

import sys
import os
import warnings
import argparse

from pymatgen.io.abinitio.events import EventParser
from pymatgen.io.abinitio.abiinspect import plottable_from_outfile
from pymatgen.io.abinitio.abitimer import AbinitTimerParser
from abipy import abilab

def str_examples():
    examples = """
Usage example:\n
    abiinsp.py OUTFILE status  ==> Report the list of Warning, Commments, Errors
    abiinsp.py OUTFILE plot    ==> Plot results of the GS Scf cycle, Phonon Scf cycle...
    abiinsp.py OUTFILE timer   ==> Visualize timing data with matplotlib.
"""
    return examples


def show_examples_and_exit(err_msg=None, error_code=1):
    """Display the usage of the script."""
    sys.stderr.write(str_examples())
    if err_msg: 
        sys.stderr.write("Fatal Error\n" + err_msg + "\n")

    sys.exit(error_code)

def main():
    parser = argparse.ArgumentParser(epilog=str_examples(), formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('filepath', nargs="?", help="File to inspect (output file or log file)")

    # Create the parsers for the sub-commands
    subparsers = parser.add_subparsers(dest='command', help='sub-command help', description="Valid subcommands")

    # Subparser for status command.
    p_status = subparsers.add_parser('status', help="Check the status of the run (errors, warning, completion)")

    #p_status.add_argument('format', nargs="?", default="cif", type=str, help="Format of the output file (ciff, POSCAR, json).")

    # Subparser for plot command.
    p_plot = subparsers.add_parser('plot', help="Plot data")
    #p_plot.add_argument('visualizer', nargs="?", default="xcrysden", type=str, help="Visualizer.")

    p_timer = subparsers.add_parser('timer', help="Show timing data.")

    # Parse command line.
    try:
        options = parser.parse_args()
    except: 
        show_examples_and_exit(error_code=1)

    if options.command == "status":
        parser = EventParser()
        report = parser.parse(options.filepath)

        print(report)
        #print("completed", report.run_completed)

    elif options.command == "plot":
        # TODO: At present only GS runs are supported by plottable_from_outfile
        obj = plottable_from_outfile(options.filepath)

        if obj is not None:
            obj.plot()
        else:
            raise ValueError("Don't know how to extract plottable data from %s" % options.filepath)

    elif options.command == "timer":
        parser = AbinitTimerParser()

        parser.parse(options.filepath)
        parser.show_pie(key="wall_time", minfract=0.05)


    else:
        raise ValueError("Unsupported command %s" % options.command)

    return 0


if __name__ == "__main__":
    sys.exit(main())
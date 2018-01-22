#!/usr/bin/env python
r"""
Flow to analyze the convergen of phonons in metals wrt ngkpt and tsmear
=======================================================================

This examples shows how to build a Flow to compute the
phonon band structure in a metallic system (MgB2) with different
k-point samplings and values of the electronic smearing tsmear
"""
from __future__ import print_function, division, unicode_literals, absolute_import

import os
import sys
import abipy.data as abidata
import abipy.abilab as abilab
from abipy import flowtk


def make_scf_input(structure, ngkpt, tsmear, pseudos, paral_kgb=1):
    """return GS input."""

    scf_inp = abilab.AbinitInput(structure, pseudos=pseudos)

    # Global variables
    scf_inp.set_vars(
        ecut=35,
        nband=8,
        occopt=4,    # Marzari smearing
        tsmear=tsmear,
        paral_kgb=paral_kgb,
   )

    # Dataset 1 (GS run)
    scf_inp.set_kmesh(ngkpt=ngkpt, shiftk=structure.calc_shiftk())
    scf_inp.set_vars(tolvrs=1e-10)

    return scf_inp


def build_flow(options):
    # Working directory (default is the name of the script with '.py' removed and "run_" replaced by "flow_")
    if not options.workdir:
        options.workdir = os.path.basename(__file__).replace(".py", "").replace("run_", "flow_")

    structure = abidata.structure_from_ucell("MgB2")

    # Get pseudos from a table.
    table = abilab.PseudoTable(abidata.pseudos("12mg.pspnc", "5b.pspnc"))
    pseudos = table.get_pseudos_for_structure(structure)

    nval = structure.num_valence_electrons(pseudos)
    #print(nval)

    flow = flowtk.Flow(workdir=options.workdir)

    scf_work = flowtk.Work()
    ngkpt_list = [[4, 4, 4], [8, 8, 8], [12, 12, 12]]
    tsmear_list = [0.01, 0.02, 0.04]
    for ngkpt in ngkpt_list:
        for tsmear in tsmear_list:
            scf_input = make_scf_input(structure, ngkpt, tsmear, pseudos)
            scf_work.register_scf_task(scf_input)
    flow.register_work(scf_work)

    # This call uses the information reported in the GS task to
    # compute all the independent atomic perturbations corresponding to a [4, 4, 4] q-mesh.
    for scf_task in scf_work:
        ph_work = flowtk.PhononWork.from_scf_task(scf_task, qpoints=[4, 4, 4], is_ngqpt=True)
        flow.register_work(ph_work)

    return flow.allocate(use_smartio=True)


# This block generates the thumbnails in the Abipy gallery.
# You can safely REMOVE this part if you are using this script for production runs.
if os.getenv("READTHEDOCS", False):
    __name__ = None
    import tempfile
    options = flowtk.build_flow_main_parser().parse_args(["-w", tempfile.mkdtemp()])
    build_flow(options).plot_networkx(with_edge_labels=True, tight_layout=True)


@flowtk.flow_main
def main(options):
    """
    This is our main function that will be invoked by the script.
    flow_main is a decorator implementing the command line interface.
    Command line args are stored in `options`.
    """
    return build_flow(options)


if __name__ == "__main__":
    sys.exit(main())


############################################################################
#
# Run the script with:
#
#     run_mgb2_phonons_nkpt_tsmear.py -s
#
# then use:
#
#    abirun.py flow_mgb2_phonons_nkpt_tsmear phbands
#
# to get info about the electronic properties:
#
# .. code-block:: shell
#
# Our main goal is to analyze the convergence of the phonons wrt to the k-point sampling and tsmear.
# As we know that ``w0_t2``, `w0_t3`` and ``w0_t4`` are DOS calculations, we can
# build a GSR robot for these tasks with:
#
#    abirun.py flow_mgb2_edoses/ ebands -nids=241034,241035,241036
#
# then, inside the ipython shell, one can use:
#
# .. code-block:: ipython
#
#    In [1]: %matplotlib
#    In [2]: robot.combiplot_edos()
#
# to plot the electronic DOS obtained with different number of k-points in the IBZ.
#
# .. image:: https://github.com/abinit/abipy_assets/blob/master/run_mgb2_edoses.png?raw=true
#    :alt: Convergence of electronic DOS in MgB2 wrt k-points.
#
#!/usr/bin/env python

"""A kernel that runs Gromacs mdrun
"""

__author__    = "ExTASY project <ardita.shkurti@nottingham.ac.uk>"
__copyright__ = "Copyright 2015, http://www.extasy-project.org/"
__license__   = "MIT"

from copy import deepcopy

from radical.ensemblemd.exceptions import ArgumentError
from radical.ensemblemd.exceptions import NoKernelConfigurationError
from radical.ensemblemd.engine import get_engine
from radical.ensemblemd.kernel_plugins.kernel_base import KernelBase

# ------------------------------------------------------------------------------
#
_KERNEL_INFO = {
    "name":         "custom.mdrun",
    "description":  "Molecular dynamics with the gromacs software package. http://www.gromacs.org/",
    "arguments":   {"--deffnm=":
                        {
                            "mandatory": True,
                            "description": "Base name for all files"
                        }
                    },
    "machine_configs":
    {
        "*": {
            "environment"   : {"FOO": "bar"},
            "pre_exec"      : [],
            "executable"    : "mdrun_mpi",
            "uses_mpi"      : True
        },

        "ncsa.bw": {
	        "environment"   : {"FOO": "bar"},
            "pre_exec"      : ["export PATH=$PATH:/projects/sciteam/gkd/gromacs/5.1.1/20151210_OMPI20151210-DYN/install-cpu/bin",
                                "export GROMACS_LIB=/projects/sciteam/gkd/gromacs/5.1.1/20151210_OMPI20151210-DYN/install-cpu/lib64",
                                "export GROMACS_INC=/projects/sciteam/gkd/gromacs/5.1.1/20151210_OMPI20151210-DYN/install-cpu/include",
                                "export GROMACS_BIN=/projects/sciteam/gkd/gromacs/5.1.1/20151210_OMPI20151210-DYN/install-cpu/bin",
                                "export GROMACS_DIR=/projects/sciteam/gkd/gromacs/5.1.1/20151210_OMPI20151210-DYN/install-cpu",
                                "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/projects/sciteam/gkd/gromacs/5.1.1/20151210_OMPI20151210-DYN/install-cpu/lib64"],
            "executable"    : ["gmx_mpi mdrun"],
            "uses_mpi"      : True
        } 
    }
}


# ------------------------------------------------------------------------------
#
class mdrun_Kernel(KernelBase):

    # --------------------------------------------------------------------------
    #
    def __init__(self):
        """Le constructor.
        """
        super(mdrun_Kernel, self).__init__(_KERNEL_INFO)

    # --------------------------------------------------------------------------
    #
    @staticmethod
    def get_name():
        return _KERNEL_INFO["name"]

    # --------------------------------------------------------------------------
    #
    def _bind_to_resource(self, resource_key):
        """(PRIVATE) Implements parent class method.
        """
        if resource_key not in _KERNEL_INFO["machine_configs"]:
            if "*" in _KERNEL_INFO["machine_configs"]:
                # Fall-back to generic resource key
                resource_key = "*"
            else:
                raise NoKernelConfigurationError(kernel_name=_KERNEL_INFO["name"], resource_key=resource_key)

        cfg = _KERNEL_INFO["machine_configs"][resource_key]

        arguments = ['-deffnm','{0}'.format(self.get_arg("--deffnm="))]

        self._executable  = cfg["executable"]
        self._arguments   = arguments
        self._environment = cfg["environment"]
        self._uses_mpi    = cfg["uses_mpi"]
        self._pre_exec    = cfg["pre_exec"]

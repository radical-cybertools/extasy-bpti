#!/usr/bin/env python

"""A kernel that runs trjconv to fix box jumps in trajectory files.
"""

__author__    = "The ExTASY project <ardita.shkurti@nottingham.ac.uk>"
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
    "name":         "custom.trjconv",
    "description":  "Performs the preprocessing necessary for the following MD simulation. ",
    "arguments":    {"--echo=":
                        {
                            "mandatory": True,
                            "description": "Command passed to trjconv"
                        },
                     "--f=":   
                        {
                            "mandatory": True,
                            "description": "A coordinates file - gro or trj."
                        },
                     "--o=":   
                        {
                            "mandatory": True,
                            "description": "New coordinates file - gro or trj."
                        },
                     "--s=":   
                        {
                            "mandatory": True,
                            "description": "A topology file "
                        },
                     "--pbc=":   
                        {
                            "mandatory": True,
                            "description": "Type of periodic boundary fix to do"
                        }
                    },
    "machine_configs":
    {
        "*": {
            "environment"   : {"FOO": "bar"},
            "pre_exec"      : [],
            "executable"    : ["/bin/bash"],
            "uses_mpi"      : False
        },

        "ncsa.bw": {
	        "environment"   : {"FOO": "bar"},
            "pre_exec"      : ["export PATH=$PATH:/projects/sciteam/gkd/gromacs/5.1.1/20151210-NO_MPI/install-cpu/bin",
                                "export GROMACS_LIB=/projects/sciteam/gkd/gromacs/5.1.1/20151210-NO_MPI/install-cpu/lib64",
                                "export GROMACS_INC=/projects/sciteam/gkd/gromacs/5.1.1/20151210-NO_MPI/install-cpu/include",
                                "export GROMACS_BIN=/projects/sciteam/gkd/gromacs/5.1.1/20151210-NO_MPI/install-cpu/bin",
                                "export GROMACS_DIR=/projects/sciteam/gkd/gromacs/5.1.1/20151210-NO_MPI/install-cpu",
                                "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/projects/sciteam/gkd/gromacs/5.1.1/20151210-NO_MPI/install-cpu/lib64"],
            "executable"    : ["/bin/bash"],
            "uses_mpi"      : False
        }                
    }
}


# ------------------------------------------------------------------------------
#
class trjconv_Kernel(KernelBase):

    # --------------------------------------------------------------------------
    #
    def __init__(self):
        """Le constructor.
        """
        super(trjconv_Kernel, self).__init__(_KERNEL_INFO)

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
        
        arguments = ['-l','-c','echo {0} | gmx trjconv -f {1} -o {3} -s {2} -pbc {4}'.format(self.get_arg("--echo="),
                                                                                             self.get_arg("--f="),
                                                                                             self.get_arg("--s="),
                                                                                             self.get_arg("--o="),
                                                                                             self.get_arg("--pbc="))]
        
        self._executable  = cfg['executable']
        self._arguments   = arguments
        self._environment = cfg["environment"]
        self._uses_mpi    = cfg["uses_mpi"]
        self._pre_exec    = cfg["pre_exec"]

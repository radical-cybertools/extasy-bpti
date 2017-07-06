#!/usr/bin/env python

__author__        = "The ExTASY project <ardita.shkurti@nottingham.ac.uk>"
__copyright__     = "Copyright 2015, http://www.extasy-project.org/"
__license__       = "MIT"
__use_case_name__ = "'Gromacs + CoCo' simulation-analysis (ExTASY)."


from radical.ensemblemd import Kernel
from radical.ensemblemd import EnsemblemdError
from radical.ensemblemd import SimulationAnalysisLoop
from radical.ensemblemd import ResourceHandle
from radical.ensemblemd.engine import get_engine

import imp
import argparse
import sys
import os
import os.path as op
import json

def opb(str):
   return op.basename(str)

# ------------------------------------------------------------------------------
# Set default verbosity

if os.environ.get('RADICAL_ENMD_VERBOSE') == None:
    os.environ['RADICAL_ENMD_VERBOSE'] = 'REPORT'

# ------------------------------------------------------------------------------
#Load all custom Kernels

from kernel_defs.grompp import grompp_Kernel
get_engine().add_kernel_plugin(grompp_Kernel)

from kernel_defs.mdrun import mdrun_Kernel
get_engine().add_kernel_plugin(mdrun_Kernel)

from kernel_defs.trjconv import trjconv_Kernel
get_engine().add_kernel_plugin(trjconv_Kernel)

from kernel_defs.coco import kernel_coco
get_engine().add_kernel_plugin(kernel_coco)

# ------------------------------------------------------------------------------
#

class Extasy_CocoGromacs_Static(SimulationAnalysisLoop):            

    def __init__(self, maxiterations, simulation_instances, analysis_instances):
        SimulationAnalysisLoop.__init__(self, maxiterations, 
                                        simulation_instances, 
                                        analysis_instances)

    def pre_loop(self):
		pass

    def simulation_stage(self, iteration, instance):
        
        kernel_list = []
        iter1 = iteration - 1
        inst1 = instance - 1
        outbase, ext = opb(Kconfig.output).split('.')
        shrd = '$SHARED/{0}'
        if ext == '':
            ext = '.pdb'

        if ((iter1)!=0):
            # Kernel 1: Grompp before energy min step.    
            k1 = Kernel(name="custom.grompp")
            k1.link_input_data = [shrd.format(opb(Kconfig.grompp_1_mdp)),
                                  shrd.format(opb(Kconfig.top_file)),
                                  shrd.format(opb(Kconfig.restr_file)),
                                  shrd.format(opb(Kconfig.grompp_1_itp_file))]			
            prev = '$PREV_ANALYSIS_INSTANCE_1/{0}_{1}{2}.{3} > {0}_{1}{2}.{3}'
            k1.link_input_data += [prev.format(outbase,iteration-2, inst1,ext)]
            k1.arguments = ["--mdp={0}".format(opb(Kconfig.grompp_1_mdp)),
                            "--ref={0}_{1}{2}.{3}".format(outbase,iteration-2,
                                                          inst1,ext),
                            "--top={0}".format(opb(Kconfig.top_file)),
                            "--gro={0}".format(opb(Kconfig.restr_file)),
                            "--tpr=min-{0}_{1}.tpr".format(iter1, inst1)]
            cout = 'min-{0}_{1}.tpr > $SHARED/min-{0}_{1}.tpr'    
            k1.copy_output_data = [cout.format(iter1,inst1)]    
            kernel_list.append(k1)
            

            # Kernel 2: Restrained energy min step.
            k2 = Kernel(name="custom.mdrun")
            lind = '$SHARED/min-{0}_{1}.tpr > min-{0}_{1}.tpr'
            k2.link_input_data = [lind.format(iter1,inst1)]
            k2.cores = Kconfig.num_cores_per_sim_cu
            k2.arguments = ["--deffnm=min-{0}_{1}".format(iter1,inst1)]
            cout = 'min-{0}_{1}.gro > $SHARED/min-{0}_{1}.gro'
            k2.copy_output_data = [cout.format(iter1,inst1)]
            kernel_list.append(k2)
            

            # Kernel 3: Grompp before restrained MD step
            k3 = Kernel(name="custom.grompp")
            k3.link_input_data = [shrd.format(opb(Kconfig.grompp_2_mdp)),
                                  shrd.format(opb(Kconfig.top_file)),
                                  shrd.format(opb(Kconfig.restr_file)),
                                  shrd.format(opb(Kconfig.grompp_2_itp_file))]
            lind = '$SHARED/min-{0}_{1}.gro > min-{0}_{1}.gro'
            k3.link_input_data += [lind.format(iter1,inst1)]
            k3.arguments = ["--mdp={0}".format(opb(Kconfig.grompp_2_mdp)),
                            "--ref=min-{0}_{1}.gro".format(iter1,inst1),
                            "--top={0}".format(opb(Kconfig.top_file)),
                            "--gro={0}".format(opb(Kconfig.restr_file)),
                            "--tpr=eq-{0}_{1}.tpr".format(iter1,inst1)]
            cout = 'eq-{0}_{1}.tpr > $SHARED/eq-{0}_{1}.tpr'
            k3.copy_output_data = [cout.format(iter1,inst1)]
            kernel_list.append(k3)


            # Kernel 4: Restrained MD step.
            k4 = Kernel(name="custom.mdrun")
            lind = '$SHARED/eq-{0}_{1}.tpr > eq-{0}_{1}.tpr'
            k4.link_input_data = [lind.format(iter1,inst1)]
            k4.cores = Kconfig.num_cores_per_sim_cu
            k4.arguments = ["--deffnm=eq-{0}_{1}".format(iter1,inst1)]
            cout = 'eq-{0}_{1}.gro > $SHARED/eq-{0}_{1}.gro'
            k4.copy_output_data = [cout.format(iter1,inst1)]
            kernel_list.append(k4)
            
        # Kernel 5: Grompp before unrestrained (production) MD.
        k5 = Kernel(name="custom.grompp")
        k5.link_input_data = [shrd.format(opb(Kconfig.grompp_3_mdp)),
                              shrd.format(opb(Kconfig.top_file))]
        if((iter1)==0):
            k5.link_input_data += [shrd.format(opb(Kconfig.initial_crd_file))]
            k5.arguments = ["--mdp={0}".format(opb(Kconfig.grompp_3_mdp)),
                            "--gro={0}".format(opb(Kconfig.initial_crd_file)),
                            "--top={0}".format(opb(Kconfig.top_file)),
                            "--tpr=md-{0}_{1}.tpr".format(iter1,inst1)]  
        else:
            lind = '$SHARED/eq-{0}_{1}.gro > eq-{0}_{1}.gro'
            k5.link_input_data += [lind.format(iter1,inst1)]
            k5.arguments = ["--mdp={0}".format(opb(Kconfig.grompp_3_mdp)),
                            "--gro=eq-{0}_{1}.gro".format(iter1,inst1),
                            "--top={0}".format(opb(Kconfig.top_file)),
                            "--tpr=md-{0}_{1}.tpr".format(iter1,inst1)]  
        cout = 'md-{0}_{1}.tpr > $SHARED/md-{0}_{1}.tpr'
        k5.copy_output_data = [cout.format(iter1,inst1)]        
        kernel_list.append(k5)
        

        #Kernel 6: Production MD step.
        k6 = Kernel(name="custom.mdrun")
        lind = '$SHARED/md-{0}_{1}.tpr > md-{0}_{1}.tpr'
        k6.link_input_data = [lind.format(iter1,inst1)]
        k6.cores = Kconfig.num_cores_per_sim_cu
        k6.arguments = ["--deffnm=md-{0}_{1}".format(iter1,inst1)]
        cout = 'md-{0}_{1}.gro > $SHARED/md-{0}_{1}.gro'
        xout = 'md-{0}_{1}.xtc > $SHARED/md-{0}_{1}.xtc'
        k6.copy_output_data = [cout.format(iter1,inst1),
                               xout.format(iter1,inst1)]
        kernel_list.append(k6)


        #Kernel 7: Post-processing of output structure file to correct 
        #          PBC effects.
        k7 = Kernel(name="custom.trjconv")
        lind = '$SHARED/md-{0}_{1}.gro > md-{0}_{1}.gro'
        tpin = '$SHARED/md-{0}_{1}.tpr > md-{0}_{1}.tpr'
        k7.link_input_data = [lind.format(iter1,inst1),
                              tpin.format(iter1,inst1)]
        k7.arguments = ["--echo=System",
                        "--f=md-{0}_{1}.gro".format(iter1,inst1),
                        "--s=md-{0}_{1}.tpr".format(iter1,inst1),
                        "--o=md-{0}_{1}_whole.gro".format(iter1,inst1),
                        "--pbc=whole"]
        cout = 'md-{0}_{1}_whole.gro > $SHARED/md-{0}_{1}.gro'
        k7.copy_output_data = [cout.format(iter1,inst1)]        
        kernel_list.append(k7)              


        #Kernel 8: Post-processing of output trajectory file to correct 
        #          PBC effects.
        k8 = Kernel(name="custom.trjconv")
        lind = '$SHARED/md-{0}_{1}.xtc > md-{0}_{1}.xtc'
        tpin = '$SHARED/md-{0}_{1}.tpr > md-{0}_{1}.tpr'
        k8.link_input_data = [lind.format(iter1,inst1),
                              tpin.format(iter1,inst1)]
        k8.arguments = ["--echo=System",
                        "--f=md-{0}_{1}.xtc".format(iter1,inst1),
                        "--s=md-{0}_{1}.tpr".format(iter1,inst1),
                        "--o=md-{0}_{1}_whole.xtc".format(iter1,inst1),
                        "--pbc=whole"]
        if(iteration%Kconfig.nsave==0):
            dout = "md-{0}_{1}_whole.xtc > output/iter{0}/md-{0}_{1}_whole.xtc"
            k8.download_output_data = [dout.format(iter1,inst1)]	        
        xout = 'md-{0}_{1}_whole.xtc > $SHARED/md-{0}_{1}.xtc'
        k8.copy_output_data = [xout.format(iter1,inst1)]        
        kernel_list.append(k8)              

        
        return kernel_list
        

    def analysis_stage(self, iteration, instance):
        '''
        function : Perform CoCo Analysis on the output of the simulation from 
        the current iteration. Using the .xtc files generated in all instances,
        generate .gro files (as many as the num_CUs) to be used in the next 
        simulations. 
        

        coco :-

            Purpose : Runs CoCo analysis on a set of MD trajectory files 
                      in this case xtc files and generates several 
                      coordinates file to be used in next cycle

            Arguments : --grid           = Number of points along each dimension
                                           of the CoCo histogram
                        --dims           = The number of projections to 
                                           consider from the input pcz file
                        --frontpoints    = Number of CUs
                        --topfile        = Topology filename
                        --mdfile         = MD Input filename
                        --output         = Output filename
                        --cycle          = Current iteration number
                        --atom_selection = Selection of the biological part of 
                                           the system we want to consider for 
                                           analysis
        '''

        k1 = Kernel(name="custom.coco")
        iter1 = iteration - 1

        outbase, ext = opb(Kconfig.output).split('.')
        if ext == '':
            ext = '.pdb'        
        
        k1.arguments = ["--grid={0}".format(Kconfig.grid),
                        "--dims={0}".format(Kconfig.dims),
                        "--frontpoints={0}".format(Kconfig.num_CUs),
                        "--topfile=md-{0}_0.gro".format(iter1),
                        "--mdfile=*.xtc",
                        "--output={0}_{1}.gro".format(outbase,iter1),
                        "--atom_selection={0}".format(Kconfig.sel)]
        k1.cores = min(Kconfig.num_CUs,RPconfig.PILOTSIZE)
        k1.uses_mpi = True
        lind = '$SHARED/md-{0}_0.gro > md-{0}_0.gro'
        k1.link_input_data = [lind.format(iter1)]
        lind = '$SHARED/md-{0}_{1}.xtc > md-{0}_{1}.xtc'
        for iter in range(iteration):
            for i in range(Kconfig.num_CUs):        
                k1.link_input_data += [lind.format(iter,i)]
        
        k1.copy_output_data = []
        cout = '{0}_{1}{2}.gro > $SHARED/{0}_{1}{2}.gro'
        for i in range(Kconfig.num_CUs):
            k1.copy_output_data += [cout.format(outbase,iter1,i)]

        dod = "coco.log > output/coco-iter{0}.log"	
        k1.download_output_data = [dod.format(iter1)]	
        
        return [k1]
        
    def post_loop(self):
        pass

# ------------------------------------------------------------------------------
#
if __name__ == "__main__":

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--RPconfig', help='link to Radical Pilot related configurations file')
        parser.add_argument('--Kconfig', help='link to Kernel configurations file')

        args = parser.parse_args()

        if args.RPconfig is None:
            parser.error('Please enter a RP configuration file')
            sys.exit(1)
        if args.Kconfig is None:
            parser.error('Please enter a Kernel configuration file')
            sys.exit(0)

        RPconfig = imp.load_source('RPconfig', args.RPconfig)
        Kconfig = imp.load_source('Kconfig', args.Kconfig)

        # Create a new static execution context with one resource and a fixed
        # number of cores and runtime.

        cluster = ResourceHandle(
            resource=RPconfig.REMOTE_HOST,
            cores=RPconfig.PILOTSIZE,
            walltime=RPconfig.WALLTIME,
            username = RPconfig.UNAME, #username
            project = RPconfig.ALLOCATION, #project
            queue = RPconfig.QUEUE,
            database_url = RPconfig.DBURL,
	    access_schema = 'ssh'
        )

        cluster.shared_data = [
                                Kconfig.initial_crd_file,
                                Kconfig.grompp_1_mdp,
                                Kconfig.grompp_2_mdp,
                                Kconfig.grompp_3_mdp,
                                Kconfig.grompp_1_itp_file,
                                Kconfig.grompp_2_itp_file,
                                Kconfig.top_file,
                                Kconfig.restr_file
                            ]

        cluster.allocate()

        coco_gromacs_static = Extasy_CocoGromacs_Static(maxiterations=Kconfig.num_iterations, simulation_instances=Kconfig.num_CUs, analysis_instances=1)
        cluster.run(coco_gromacs_static)

        cluster.deallocate()

    except EnsemblemdError, er:

        print "The gromacs-coco ExTASY workflow not completed correctly due to an Ensemble MD Toolkit Error: {0}".format(str(er))
        raise # Just raise the execption again to get the backtrace

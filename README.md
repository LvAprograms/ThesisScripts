## ThesisScripts
Collection of python scripts used to make figures for thesis/paper.
Some I used all the time, others were more experimental

## Working scripts
* ForceCalculator.py - class which is inherited by GPE.py. Is able to plot topography, read marker data, etc.
* GPE.py - class inheriting from ForceCalculator. Calculates gravitational potential energy difference between two columns of rocks
* find_x.py - stupid script, but essentially finds an x position for a given node number, or vice versa.
* oceantemp.py - cooling halfspace model temperature visualisation
* Trench_suction.py - Calculates the integral of (dVx/dy * eta_eff) over the length of the overriding plate for 4 consecutive z nodes to quantify viscous drag beneath OP. First attempt, use the matlab version instead.
* slabdetachment.py - plots a dataset of detachment depths versus durations, but is outdated at this point.
* GradualTransition.py - Calculates necessary node x or y coordinates to implement a gradual transition from one grid spacing to one another. Could use some automation.
* plot_dragdata.py - plots output of viscous drag calculations (from matlab script ForceAnalysis.m, can't publish here unfortunately)
* plot_slabpull.py - plots output of slab pull calcuations (from matlab script ForceAnalysis.m)
* plot_grids.py - plots x and y grids by reading an init_ls.t3c file. 
* rupture_widths.py - experiment with Coppersmith et al., 1984 formula for Rupture Width (W)
* minor_plots.py - just some convenience plotting script. 

## Scripts you shouldn't waste any time with
* SlabPull.py 
* Slab_pull_v2.py
* strprofs.py - source of about 100 hours of wasted time for me. Tried to make realistic lithospheric strength profiles, but they always are too strong without a ductile domain. 
* klooiprofiel.py - attempt at hardcoded strength profile
* znode.py - connected to the above two scripts
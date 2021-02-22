import openmc
import numpy as np
from numpy import sin, cos, tan, pi
import sys 
sys.path.insert(1, '../')
from constants import *

# Templating
total_pf = 0.05
sine_a = {{sine_a}}
sine_b = {{sine_b}}
sine_c = {{sine_c}}
vol_total = 20 * 2 * 2
vol_slice = 2 * 2 * 2

# geometry
# shape of reactor (core: 20 x 2 x 2)
prism_1 = create_prism(0, 2, True, False)
prism_2 = create_prism(2, 4, False, False)
prism_3 = create_prism(4, 6, False, False)
prism_4 = create_prism(6, 8, False, False)
prism_5 = create_prism(8, 10, False, False)
prism_6 = create_prism(10, 12, False, False)
prism_7 = create_prism(12, 14, False, False)
prism_8 = create_prism(14, 16, False, False)
prism_9 = create_prism(16, 18, False, False)
prism_10 = create_prism(18, 20, False, True)

# triso PF distribution
vol_triso = 4 / 3 * pi * T_r5 ** 3
no_trisos = total_pf * vol_total / vol_triso
boundaries = np.arange(0,22,2)
midpoints = [] 
for x in range(len(boundaries)-1):
    midpoints.append((boundaries[x]+boundaries[x+1])/2)
midpoints = np.array(midpoints)
sine_val = sine_a * sin(sine_b * midpoints + sine_c) + 1
sine_val = np.where(sine_val<0, 0, sine_val)
triso_z = sine_val / sum(sine_val) * no_trisos
pf_z = triso_z * vol_triso / vol_slice

prism_cell_1, lattice = create_lattice(prism_1, pf_z[0])
prism_cell_1.fill = lattice
prism_cell_2, lattice = create_lattice(prism_2, pf_z[1])
prism_cell_2.fill = lattice
prism_cell_3, lattice = create_lattice(prism_3, pf_z[2])
prism_cell_3.fill = lattice
prism_cell_4, lattice = create_lattice(prism_4, pf_z[3])
prism_cell_4.fill = lattice
prism_cell_5, lattice = create_lattice(prism_5, pf_z[4])
prism_cell_5.fill = lattice
prism_cell_6, lattice = create_lattice(prism_6, pf_z[5])
prism_cell_6.fill = lattice
prism_cell_7, lattice = create_lattice(prism_7, pf_z[6])
prism_cell_7.fill = lattice
prism_cell_8, lattice = create_lattice(prism_8, pf_z[7])
prism_cell_8.fill = lattice
prism_cell_9, lattice = create_lattice(prism_9, pf_z[8])
prism_cell_9.fill = lattice
prism_cell_10, lattice = create_lattice(prism_10, pf_z[9])
prism_cell_10.fill = lattice

univ = openmc.Universe(
    cells=[
        prism_cell_1,
        prism_cell_2,
        prism_cell_3,
        prism_cell_4,
        prism_cell_5,
        prism_cell_6,
        prism_cell_7,
        prism_cell_8,
        prism_cell_9,
        prism_cell_10,
    ]
)
geom = openmc.Geometry(univ)

# settings
point = openmc.stats.Point((10, 1, 1))
src = openmc.Source(space=point)
settings = openmc.Settings()
settings.source = src
settings.batches = 100
settings.inactive = 20
settings.particles = 8000
settings.temperature = {"multipole": True, "method": "interpolation"}

plot = openmc.Plot()
plot.basis = "xz"
plot.origin = (10, 1, 1)
plot.width = (22, 3)
plot.pixels = (1000, 200)
colors = {
    uoc_9: "yellow",
    por_c: "black",
    si_c: "orange",
    graphite: "grey",
    flibe: "blue",  
    lm_graphite: "green",
}
plot.color_by = "material"
plot.colors = colors
plots = openmc.Plots()
plots.append(plot)

# export 
mats.export_to_xml()
geom.export_to_xml()
settings.export_to_xml()
#plots.export_to_xml()

openmc.run(openmc_exec="openmc-ccm")
#openmc.run()
import openmc
import numpy as np
from numpy import sin, cos, tan, pi

# Templating
total_pf = 0.05
sine_b = {{sine_b}}
sine_c = {{sine_c}}
volume, slices, height = 10, 10, 25

# Constants
T_r1 = 2135e-5
T_r2 = 3135e-5
T_r3 = 3485e-5
T_r4 = 3835e-5
T_r5 = 4235e-5

uoc_9 = openmc.Material()
uoc_9.set_density("g/cc", 11)
uoc_9.add_nuclide("U235", 2.27325e-3)
uoc_9.add_nuclide("U238", 2.269476e-2)
uoc_9.add_nuclide("O16", 3.561871e-2)
uoc_9.add_nuclide("C0", 9.79714e-3)
uoc_9.temperature = 1110
uoc_9.volume = 4 / 3 * pi * (T_r1 ** 3) * 101 * 210 * 4 * 36

por_c = openmc.Material()
por_c.set_density("g/cc", 1)
por_c.add_nuclide("C0", 5.013980e-2)
por_c.temperature = 948

si_c = openmc.Material()
si_c.set_density("g/cc", 3.2)
si_c.add_nuclide("Si28", 4.431240e-2)
si_c.add_nuclide("Si29", 2.25887e-3)
si_c.add_nuclide("Si30", 1.48990e-3)
si_c.add_nuclide("C0", 4.806117e-2)
si_c.temperature = 948

graphite = openmc.Material()
graphite.set_density("g/cc", 1.8)
graphite.add_nuclide("C0", 9.025164e-2)
graphite.temperature = 948

lm_graphite = openmc.Material()
lm_graphite.set_density("g/cc", 1.8)
lm_graphite.add_nuclide("C0", 9.025164e-2)
lm_graphite.temperature = 948

flibe = openmc.Material()
flibe.set_density("g/cc", 1.95)
flibe.add_nuclide("Li6", 1.383014e-6)
flibe.add_nuclide("Li7", 2.37132e-2)
flibe.add_nuclide("Be9", 1.18573e-2)
flibe.add_nuclide("F19", 4.74291e-2)
flibe.temperature = 948

mats = openmc.Materials((uoc_9, por_c, si_c, graphite, lm_graphite, flibe))

spheres = [openmc.Sphere(r=r) for r in [T_r1, T_r2, T_r3, T_r4, T_r5]]
triso_cells = [
    openmc.Cell(fill=uoc_9, region=-spheres[0]),
    openmc.Cell(fill=por_c, region=+spheres[0] & -spheres[1]),
    openmc.Cell(fill=graphite, region=+spheres[1] & -spheres[2]),
    openmc.Cell(fill=si_c, region=+spheres[2] & -spheres[3]),
    openmc.Cell(fill=graphite, region=+spheres[3] & -spheres[4]),
]
triso_univ = openmc.Universe(cells=triso_cells)

mats.export_to_xml()

# shape of reactor
outer = openmc.Cell(fill=graphite)
outer.region = (
    +openmc.XPlane(x0=0, boundary_type="reflective")
    & -openmc.XPlane(x0=2.2, boundary_type="reflective")
    & +openmc.YPlane(y0=0, boundary_type="reflective")
    & -openmc.YPlane(y0=0.4, boundary_type="reflective")
    & +openmc.ZPlane(z0=0, boundary_type="reflective")
    & -openmc.ZPlane(z0=0.2 + height, boundary_type="reflective")
)

# triso PF distribution
vol_total = volume
vol_triso = 4 / 3 * pi * T_r5 ** 3
no_trisos = total_pf * vol_total / vol_triso
dz_vals = np.linspace(0, height, slices)
sine_val = 1 * sin(sine_b * dz_vals + sine_c) + 1
triso_z = sine_val / sum(sine_val) * no_trisos
print(triso_z)
pf_z = sine_val / sum(sine_val) * no_trisos * vol_triso / vol_total
print(pf_z)
z_thick = height / slices
# core
all_prism_univ = openmc.Universe()
small_prism = (
    +openmc.XPlane(x0=0.1)
    & -openmc.XPlane(x0=2.1)
    & +openmc.YPlane(y0=0.1)
    & -openmc.YPlane(y0=0.3)
    & +openmc.ZPlane(z0=0.1)
    & -openmc.ZPlane(z0=0.1 + z_thick)
)
all_prism_regions = small_prism
for i, pf in enumerate(pf_z):
    prism_region = small_prism
    try:
        centers = openmc.model.pack_spheres(radius=T_r5, region=prism_region, pf=pf)
    except ZeroDivisionError:
        print(i, "ZERO ERROR")
        centers = []
    trisos = [openmc.model.TRISO(T_r5, triso_univ, c) for c in centers]
    prism_cell = openmc.Cell(region=prism_region)
    lower_left, upper_right = prism_cell.region.bounding_box
    shape = (1, 1, 1)
    pitch = (upper_right - lower_left) / shape
    lattice = openmc.model.create_triso_lattice(
        trisos, lower_left, pitch, shape, lm_graphite
    )
    prism_cell.fill = lattice
    prism_univ = openmc.Universe(cells=(prism_cell,))
    z_trans = i * z_thick
    prism_region_new = prism_region.translate((0, 0, z_trans))
    prism_cell_new = openmc.Cell(fill=prism_univ, region=prism_region_new)
    prism_cell_new.translation = (0, 0, z_trans)
    all_prism_univ.add_cell(prism_cell_new)
    all_prism_regions |= prism_region_new
prism_areas = openmc.Cell(fill=all_prism_univ, region=all_prism_regions)
outer.region &= ~all_prism_regions
print("out")
# geometry
univ = openmc.Universe(cells=[outer, prism_areas])
geom = openmc.Geometry(univ)
geom.export_to_xml()

# settings
point = openmc.stats.Point((0.2, 0.2, 12.5))
src = openmc.Source(space=point)
settings = openmc.Settings()
settings.source = src
settings.batches = 50
settings.inactive = 10
settings.particles = 1000
settings.temperature = {"multipole": True, "method": "interpolation"}
settings.export_to_xml()

plot = openmc.Plot()
plot.basis = "xz"
plot.origin = (1.1, 0.2, 13)
plot.width = (4, 26)
plot.pixels = (2000, 2000)
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
plots.export_to_xml()
openmc.run(openmc_exec="openmc-ccm")
#openmc.run()
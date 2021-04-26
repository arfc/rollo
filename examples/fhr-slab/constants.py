import openmc
from numpy import pi

# Constants
T_r1 = 2135e-5
T_r2 = 3135e-5
T_r3 = 3485e-5
T_r4 = 3835e-5
T_r5 = 4235e-5
T_pitch = 0.09266

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

triso_4_layers = openmc.Material()
triso_4_layers.add_nuclide("C0", 0.06851594519357823)
triso_4_layers.add_nuclide("Si28", 0.009418744960032735)
triso_4_layers.add_nuclide("Si29", 0.00048013017638108395)
triso_4_layers.add_nuclide("Si30", 0.0003166830980933728)
triso_4_layers.set_density("sum")
triso_4_layers.temperature = 948

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

mats = openmc.Materials((uoc_9, por_c, si_c, graphite, lm_graphite, flibe, triso_4_layers))

# 4 layer triso 
two_spheres = [openmc.Sphere(r=r) for r in [T_r1, T_r5]]
two_triso_cells = [
    openmc.Cell(fill=uoc_9, region=-two_spheres[0]),
    openmc.Cell(fill=triso_4_layers, region=+two_spheres[0] & -two_spheres[1]),
    openmc.Cell(fill=lm_graphite, region=+two_spheres[1])]
two_triso_univ = openmc.Universe(cells=two_triso_cells)

def create_prism(left, right, left_refl, right_refl):
    if left_refl:
        xplane_left = +openmc.XPlane(x0=left, boundary_type="reflective")
    else: 
        xplane_left = +openmc.XPlane(x0=left)
    if right_refl: 
        xplane_right = -openmc.XPlane(x0=right, boundary_type="reflective")
    else: 
        xplane_right= -openmc.XPlane(x0=right)
    prism = (
        xplane_left
        & xplane_right
        & +openmc.YPlane(y0=0.35)
        & -openmc.YPlane(y0=0.35+2.55)
        & +openmc.ZPlane(z0=0, boundary_type="reflective")
        & -openmc.ZPlane(z0=T_pitch*20, boundary_type="reflective")
    )
    return prism 

def create_prism_vertical(bot,top):
    yplane_bot = +openmc.YPlane(y0=bot)
    yplane_top= -openmc.YPlane(y0=top)
    prism = (
        +openmc.XPlane(x0=2)
        & -openmc.XPlane(x0=2+23.1)
        & yplane_bot
        & yplane_top
        & +openmc.ZPlane(z0=0, boundary_type="reflective")
        & -openmc.ZPlane(z0=T_pitch*20, boundary_type="reflective")
    )
    return prism

def create_lattice(region, pf):
    try:
        centers_1 = openmc.model.pack_spheres(radius=T_r5, region=region, pf=pf)
        trisos_1 = [openmc.model.TRISO(T_r5, two_triso_univ, c) for c in centers_1]
        prism = openmc.Cell(region=region)
        lower_left_1, upper_right_1 = prism.region.bounding_box
        shape = tuple(((upper_right_1 - lower_left_1)/0.4).astype(int)) 
        pitch_1 = (upper_right_1 - lower_left_1) / shape
        lattice_1 = openmc.model.create_triso_lattice(
            trisos_1, lower_left_1, pitch_1, shape, lm_graphite
        )
        prism.fill = lattice_1
    except: 
        prism = openmc.Cell(region=region)
        prism.fill = lm_graphite
    return prism
import openmc 
import numpy as np

pu = openmc.Material()
pu.set_density("g/cm3", 19.84)
pu.add_nuclide("Pu238", 1)
mats = openmc.Materials([pu])

radius = {{radius}}

fuel_sphere = openmc.Sphere(r=radius, boundary_type='vacuum')
fuel_cell = openmc.Cell(fill=pu, region=-fuel_sphere)
univ = openmc.Universe(cells=[fuel_cell])
geom = openmc.Geometry(univ)

settings = openmc.Settings()
settings.batches = 100
settings.inactive = 20
settings.particles = 20000
settings.temperature = {"multipole": True, "method": "interpolation"}


mats.export_to_xml()
geom.export_to_xml()
settings.export_to_xml()
openmc.run()
import openmc
h5file = "statepoint.100.h5"
sp = openmc.StatePoint(h5file, autolink=False)
keff = sp.k_combined.nominal_value

print({"keff": keff})
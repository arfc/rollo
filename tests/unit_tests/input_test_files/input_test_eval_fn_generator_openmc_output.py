import openmc

sp = openmc.StatePoint("statepoint.10.h5")
keff = sp.k_combined.nominal_value
num_batches = sp.n_batches
print({"num_batches": num_batches, "keff": keff})

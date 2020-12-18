import openmc 

sp = openmc.StatePoint("statepoint.10.h5")
num_batches = sp.n_batches
print({"num_batches":num_batches})
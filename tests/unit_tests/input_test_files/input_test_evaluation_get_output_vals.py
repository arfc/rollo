import openmc

sp = openmc.StatePoint("statepoint_input_openmc_evaluation.20.h5")
keff = sp.k_combined.nominal_value

print({"random": 3, "keff": keff})

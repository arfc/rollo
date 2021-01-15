from realm.backend import BackEnd
from deap import base, creator, tools, algorithms

def test_initialize_new_backend():
    b = BackEnd("square_checkpoint.pkl")
    b.initialize_new_backend()
    assert b.backend["start_gen"] == 0
    assert type(b.backend["halloffame"]) == tools.HallOfFame
    assert type(b.backend["logbook"]) == tools.Logbook
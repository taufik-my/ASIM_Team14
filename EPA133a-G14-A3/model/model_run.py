from model import BangladeshModel

"""
    Run simulation
    Print output at terminal
"""

# ---------------------------------------------------------------

# run time 5 x 24 hours; 1 tick 1 minute
#run_length = 5 * 24 * 60

# run time 1000 ticks
run_length = 1000

seed = 1234567

sim_model = BangladeshModel(seed=seed)

# Check if the seed is set
print("SEED " + str(sim_model._seed))

# One run with given steps
for i in range(run_length):
    sim_model.step()


#print out the paths to verify it manually or whatever
for (source, sink), path_series in sim_model.path_ids_dict.items():
        print(f"Route from {source} to {sink}:")
        print(f"  -> Path: {path_series.tolist()}")
        print("-" * 40)

sim_model.draw_graph(save_png=True)
from model import BangladeshModel
import pandas as pd
from mesa.datacollection import DataCollector
"""
    Run simulation
    Print output at terminal
"""

# ---------------------------------------------------------------

# run time 5 x 24 hours; 1 tick 1 minute
#run_length = 5 * 24 * 60

# run time 1000 ticks
run_length = 1000

seeds = pd.Series(range(1234567)).sample(10, random_state=None).tolist() #generate randomized seeds
#uncomment below to try with controlled seed
#seeds=[1234567,1234567,1234567]
for scenario in range(9):
    a=0
    all_runs = []
    for seed in seeds:
        #seed = 1234567
        a+=1
        sim_model = BangladeshModel(seed=seed,scenario=scenario)

        # Check if the seed is set
        #print("SEED " + str(sim_model._seed))

        # One run with given steps
        for i in range(run_length):
            sim_model.step()

        #data collection for vehicle
        mdf = sim_model.datacollector.get_agent_vars_dataframe().reset_index()
        mdf = mdf[mdf["type"] == "Vehicle"]

        #duration
        mdf['duration']=mdf['remove']-mdf['generated']
        mdf=mdf.dropna(subset=['duration'])

        #tag seed
        mdf['seed']=seed
        mdf['iteration']=a
        all_runs.append(mdf)
        #mdf.to_csv(f"scenario{scenario} - seed {a}.csv")

    # combine all seeds into one dataframe
    out_df = pd.concat(all_runs, ignore_index=True)

    # one output file PER scenario (with all seeds inside)
    out_df.to_csv(f"../experiment/scenario{scenario}.csv", index=False)



"""
#seeds to be randomized 10 times
scenario=0
seeds = pd.Series(range(1234568)).sample(3, random_state=None).tolist()
#seeds=[1234567,1234567,1234567]
a=0
all_runs = []
for seed in seeds:
    #seed = 1234567
    a+=1
    sim_model = BangladeshModel(seed=seed,scenario=scenario)

    # Check if the seed is set
    #print("SEED " + str(sim_model._seed))

    # One run with given steps
    for i in range(run_length):
        sim_model.step()

    #data collection for vehicle
    mdf = sim_model.datacollector.get_agent_vars_dataframe().reset_index()
    mdf = mdf[mdf["type"] == "Vehicle"]

    #duration
    mdf['duration']=mdf['remove']-mdf['generated']
    mdf=mdf.dropna(subset=['duration'])

    #tag seed
    mdf['seed']=seed
    mdf['iteration']=a
    all_runs.append(mdf)
    #mdf.to_csv(f"scenario{scenario} - seed {a}.csv")

# combine all seeds into one dataframe
out_df = pd.concat(all_runs, ignore_index=True)

# one output file PER scenario (with all seeds inside)
out_df.to_csv(f"scenario{scenario}.csv", index=False)
"""
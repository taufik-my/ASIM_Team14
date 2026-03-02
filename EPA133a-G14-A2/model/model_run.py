from model import BangladeshModel
import pandas as pd
from mesa.datacollection import DataCollector
"""
    Run simulation
    Print output at terminal
"""

# ---------------------------------------------------------------

# run time 5 x 24 hours; 1 tick 1 minute
run_length= 5 * 24 * 60

# run time 1000 ticks
#run_length = 1000

seeds = pd.Series(range(1234567)).sample(10, random_state=None).tolist() #generate randomized seeds
#uncomment below to try with controlled seed
#seeds=[1234567,1234567,1234567]

#change the list if other roads needs to be simulated
roads=['N1']

for scenario in range(0,9,1):
    a=0
    all_runs = []
    all_runs_bridge_delay = []
    for seed in seeds:
        #seed = 1234567
        a+=1
        sim_model = BangladeshModel(seed=seed,scenario=scenario, roads=roads)

        # Check if the seed is set
        #print("SEED " + str(sim_model._seed))

        # One run with given steps
        for i in range(run_length):
            sim_model.step()

        #data collection for vehicle
        mdf = sim_model.datacollector.get_agent_vars_dataframe().reset_index()
        bridge_delay=mdf.copy() #retrieve required information for bridge longest delay (bonus)

        mdf = mdf[mdf["type"] == "Vehicle"]

        #duration
        mdf['duration']=mdf['remove']-mdf['generated']
        mdf=mdf.dropna(subset=['duration'])

        #add identifier of iteration number and seeds used
        mdf['seed']=seed
        mdf['iteration']=a
        all_runs.append(mdf)
        all_runs_bridge_delay.append(bridge_delay)

    # combine all seeds into one dataframe
    out_df = pd.concat(all_runs, ignore_index=True)
    bridge_delay_df=pd.concat(all_runs_bridge_delay, ignore_index=True)

    #get the information of delay time for every bridge
    bridge_delay_df=bridge_delay_df[bridge_delay_df["type"] == "Bridge"]
    bridge_delay_df=bridge_delay_df[['lrp','name','total delay']]
    bridge_delay_df = bridge_delay_df.loc[
        bridge_delay_df.groupby(["lrp", "name"])["total delay"].idxmax()
    ].reset_index(drop=True)

    # one output file PER scenario (with all seeds inside)
    out_df.to_csv(f"../experiment/scenario{scenario}.csv", index=False)
    bridge_delay_df.to_csv(f"../experiment/bonus-scenario{scenario}.csv", index=False)
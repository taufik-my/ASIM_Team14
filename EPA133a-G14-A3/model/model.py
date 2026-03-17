from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import ContinuousSpace
from components import Source, Sink, SourceSink, Bridge, Link, Intersection
import pandas as pd
from collections import defaultdict
import networkx as nx
import numpy as np
from matplotlib import pyplot as plt


# ---------------------------------------------------------------
def set_lat_lon_bound(lat_min, lat_max, lon_min, lon_max, edge_ratio=0.02):
    """
    Set the HTML continuous space canvas bounding box (for visualization)
    give the min and max latitudes and Longitudes in Decimal Degrees (DD)

    Add white borders at edges (default 2%) of the bounding box
    """

    lat_edge = (lat_max - lat_min) * edge_ratio
    lon_edge = (lon_max - lon_min) * edge_ratio

    x_max = lon_max + lon_edge
    y_max = lat_min - lat_edge
    x_min = lon_min - lon_edge
    y_min = lat_max + lat_edge
    return y_min, y_max, x_min, x_max


# ---------------------------------------------------------------
class BangladeshModel(Model):
    """
    The main (top-level) simulation model

    One tick represents one minute; this can be changed
    but the distance calculation need to be adapted accordingly

    Class Attributes:
    -----------------
    step_time: int
        step_time = 1 # 1 step is 1 min

    path_ids_dict: defaultdict
        Key: (origin, destination)
        Value: the shortest path (Infra component IDs) from an origin to a destination

        Only straight paths in the Demo are added into the dict;
        when there is a more complex network layout, the paths need to be managed differently

    sources: list
        all sources in the network

    sinks: list
        all sinks in the network

    """

    step_time = 1

    file_name = '../data/demo-4_Copy.csv' #using the copy made for now

    def __init__(self, seed=None, x_max=500, y_max=500, x_min=0, y_min=0):

        self.schedule = BaseScheduler(self)
        self.running = True
        self.path_ids_dict = defaultdict(lambda: pd.Series())
        self.space = None
        self.sources = []
        self.sinks = []
        self.G = nx.Graph() #added this

        self.generate_model()

    def generate_model(self):
        """
        generate the simulation model according to the csv file component information

        Warning: the labels are the same as the csv column labels
        """

        df = pd.read_csv(self.file_name)

        # a list of names of roads to be generated
        # TODO You can also read in the road column to generate this list automatically
        roads = ['N1', 'N2']

        df_objects_all = []
        for road in roads:
            # Select all the objects on a particular road in the original order as in the cvs
            df_objects_on_road = df[df['road'] == road]

            if not df_objects_on_road.empty:
                df_objects_all.append(df_objects_on_road)

                """
                Set the path 
                1. get the serie of object IDs on a given road in the cvs in the original order
                2. add the (straight) path to the path_ids_dict
                3. put the path in reversed order and reindex
                4. add the path to the path_ids_dict so that the vehicles can drive backwards too
                """
                #Commenting this out
                # path_ids = df_objects_on_road['id']
                # path_ids.reset_index(inplace=True, drop=True)
                # self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids
                # self.path_ids_dict[path_ids[0], None] = path_ids
                # path_ids = path_ids[::-1]
                # path_ids.reset_index(inplace=True, drop=True)
                # self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids
                # self.path_ids_dict[path_ids[0], None] = path_ids

        # put back to df with selected roads so that min and max and be easily calculated
        df = pd.concat(df_objects_all)
        y_min, y_max, x_min, x_max = set_lat_lon_bound(
            df['lat'].min(),
            df['lat'].max(),
            df['lon'].min(),
            df['lon'].max(),
            0.05
        )

        # add graph generation just from Brenda's notebook
        nodes = df.drop_duplicates(subset='id')
        for _, row in nodes.iterrows():
            self.G.add_node(
                int(row["id"]),
                road=row["road"],
                pos=(row["lat"], row["lon"]),
            )

        # Add edges
        df["from_id"] = df.groupby("road")["id"].shift(1)
        df["to_id"] = df["id"]
        edges = df.dropna(subset=["from_id"]).copy()

        for _, row in edges.iterrows():
            self.G.add_edge(
                int(row["from_id"]),
                int(row["to_id"]),
                road=row["road"],
                type=row["model_type"],
                length=row["length"],
                weight=row["length"]  # <-- Assigning the weight directly!
            )

        pos = nx.get_node_attributes(self.G, "pos")
        labels = nx.get_edge_attributes(self.G, "weight")

        # ContinuousSpace from the Mesa package;
        # not to be confused with the SimpleContinuousModule visualization
        self.space = ContinuousSpace(x_max, y_max, True, x_min, y_min)

        for df in df_objects_all:
            for _, row in df.iterrows():  # index, row in ...

                # create agents according to model_type
                model_type = row['model_type'].strip()
                agent = None

                name = row['name']
                if pd.isna(name):
                    name = ""
                else:
                    name = name.strip()

                if model_type == 'source':
                    agent = Source(row['id'], self, row['length'], name, row['road'])
                    self.sources.append(agent.unique_id)
                elif model_type == 'sink':
                    agent = Sink(row['id'], self, row['length'], name, row['road'])
                    self.sinks.append(agent.unique_id)
                elif model_type == 'sourcesink':
                    agent = SourceSink(row['id'], self, row['length'], name, row['road'])
                    self.sources.append(agent.unique_id)
                    self.sinks.append(agent.unique_id)
                elif model_type == 'bridge':
                    agent = Bridge(row['id'], self, row['length'], name, row['road'], row['condition'])
                elif model_type == 'link':
                    agent = Link(row['id'], self, row['length'], name, row['road'])
                elif model_type == 'intersection':
                    if not row['id'] in self.schedule._agents:
                        agent = Intersection(row['id'], self, row['length'], name, row['road'])

                if agent:
                    self.schedule.add(agent)
                    y = row['lat']
                    x = row['lon']
                    self.space.place_agent(agent, (x, y))
                    agent.pos = (x, y)

    #New function to calculate the shortest path
    def find_shortest_path(self, source, sink):
        if (source, sink) in self.path_ids_dict:
            return self.path_ids_dict[(source, sink)]
        try:
            path_list = nx.shortest_path(self.G, source=source, target=sink, weight='weight')
            path_series = pd.Series(path_list)

            self.path_ids_dict[(source, sink)] = path_series
            self.path_ids_dict[(sink, source)] = pd.Series(path_list[::-1])
            return path_series

        except nx.NetworkXNoPath:
            print(f"No path between {source} and {sink}")
            return pd.Series([])

    def get_random_route(self, source):
        """
        pick up a random route given an origin
        """
        while True:
            # different source and sink
            sink = self.random.choice(self.sinks)
            if sink is not source:
                break
        #Update the return statement here
        return self.find_shortest_path(source, sink)

        #return self.path_ids_dict[source, sink]

    # TODO: just use the random route
    def get_route(self, source):
        return self.get_random_route(source)

    #Deprecate
    # def get_straight_route(self, source):
    #     """
    #     pick up a straight route given an origin
    #     """
    #     return self.path_ids_dict[source, None]
    # New function to create the graph
    def draw_graph(self, save_png=False):
        pos = nx.get_node_attributes(self.G, "pos")
        plt.figure(figsize=(10, 10))
        nx.draw(self.G, pos=pos, with_labels=True)
        plt.title("Network Routing Map of N1 and N2 with side roads >25km")
        if save_png:
            image_path = '../data/bangladesh_network.png'
            plt.savefig(image_path, dpi=300, bbox_inches='tight')
            plt.close()  # Closes the figure to free up memory
            print(f"Map successfully saved to: {image_path}")
        else:
            plt.show()

    def step(self):
        """
        Advance the simulation by one step.
        """
        self.schedule.step()

# EOF -----------------------------------------------------------

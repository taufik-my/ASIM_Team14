from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import ContinuousSpace
from components import Source, Sink, SourceSink, Bridge, Link, Intersection
import pandas as pd
import networkx as nx
from collections import defaultdict


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

    file_name = '../data/raw/network_data.csv'

    def __init__(self, seed=None, x_max=500, y_max=500, x_min=0, y_min=0,
                 breakdown_probs=None):

        self.schedule = BaseScheduler(self)
        self.running = True
        self.path_ids_dict = defaultdict(lambda: pd.Series())
        self.space = None
        self.sources = []
        self.sinks = []

        # NetworkX graph for shortest-path routing between SourceSinks
        self.G = nx.Graph()

        # collected trip data for analysis
        self.trip_data = []

        # bridge breakdown probabilities per condition category
        # e.g. {'A': 0.05, 'B': 0.10, 'C': 0.20, 'D': 0.40}
        self.breakdown_probs = breakdown_probs if breakdown_probs else {}

        self.generate_model()

    def generate_model(self):
        """
        generate the simulation model according to the csv file component information

        Also builds a NetworkX graph for shortest-path routing.
        Cross-reference entries at the end of each road's data connect
        side roads to main roads via shared intersection IDs.

        Warning: the labels are the same as the csv column labels
        """

        df = pd.read_csv(self.file_name)

        # automatically read the list of roads from the data
        roads = df['road'].unique().tolist()

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
                path_ids = df_objects_on_road['id']
                path_ids.reset_index(inplace=True, drop=True)
                self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids
                self.path_ids_dict[path_ids[0], None] = path_ids
                path_ids = path_ids[::-1]
                path_ids.reset_index(inplace=True, drop=True)
                self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids
                self.path_ids_dict[path_ids[0], None] = path_ids

                # --- Build NetworkX graph edges for this road ---
                df_road = df_objects_on_road.reset_index(drop=True)
                ss_mask = df_road['model_type'].str.strip() == 'sourcesink'
                ss_positions = df_road[ss_mask].index.tolist()

                if len(ss_positions) >= 2:
                    first_ss_pos = ss_positions[0]
                    last_ss_pos = ss_positions[-1]

                    # Main body: first SourceSink to last SourceSink
                    main_body = df_road.iloc[first_ss_pos:last_ss_pos + 1]
                    main_ids = main_body['id'].tolist()

                    # Add edges between consecutive main body components
                    for i in range(len(main_ids) - 1):
                        w = max(float(main_body.iloc[i]['length']), 1)
                        self.G.add_edge(main_ids[i], main_ids[i + 1], weight=w)

                    # Cross-references: entries after the last SourceSink
                    if last_ss_pos < len(df_road) - 1:
                        cross_refs = df_road.iloc[last_ss_pos + 1:]
                        first_ss_id = main_ids[0]
                        last_ss_id = main_ids[-1]
                        first_lat = float(main_body.iloc[0]['lat'])
                        first_lon = float(main_body.iloc[0]['lon'])
                        last_lat = float(main_body.iloc[-1]['lat'])
                        last_lon = float(main_body.iloc[-1]['lon'])

                        for _, ref in cross_refs.iterrows():
                            ref_id = ref['id']
                            lrp_val = ref.get('lrp', '')
                            lrp = '' if pd.isna(lrp_val) else str(lrp_val).strip()

                            if lrp == 'LRPS':
                                # connects to start of this road
                                self.G.add_edge(first_ss_id, ref_id, weight=1)
                            elif lrp == 'LRPE':
                                # connects to end of this road
                                self.G.add_edge(last_ss_id, ref_id, weight=1)
                            else:
                                # match by coordinate proximity
                                d_start = ((float(ref['lat']) - first_lat) ** 2 +
                                           (float(ref['lon']) - first_lon) ** 2)
                                d_end = ((float(ref['lat']) - last_lat) ** 2 +
                                         (float(ref['lon']) - last_lon) ** 2)
                                if d_start <= d_end:
                                    self.G.add_edge(first_ss_id, ref_id, weight=1)
                                else:
                                    self.G.add_edge(last_ss_id, ref_id, weight=1)

                elif len(ss_positions) == 1:
                    # single sourcesink road — add all consecutive edges
                    all_ids = df_road['id'].tolist()
                    for i in range(len(all_ids) - 1):
                        w = max(float(df_road.iloc[i]['length']), 1)
                        self.G.add_edge(all_ids[i], all_ids[i + 1], weight=w)

        # put back to df with selected roads so that min and max and be easily calculated
        df = pd.concat(df_objects_all)
        y_min, y_max, x_min, x_max = set_lat_lon_bound(
            df['lat'].min(),
            df['lat'].max(),
            df['lon'].min(),
            df['lon'].max(),
            0.05
        )

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
                    if row['id'] in self.schedule._agents:
                        # replace existing agent (e.g. intersection) with SourceSink
                        # so that vehicles can be generated at shared nodes
                        existing = self.schedule._agents[row['id']]
                        self.schedule.remove(existing)
                        self.space.remove_agent(existing)
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

    def get_random_route(self, source):
        """
        Pick a random sink destination and find shortest path via NetworkX.
        Caches discovered paths in path_ids_dict for future lookups.
        """
        while True:
            sink = self.random.choice(self.sinks)
            if sink != source:
                break

        # check cache first
        if (source, sink) in self.path_ids_dict:
            cached = self.path_ids_dict[source, sink]
            if len(cached) > 0:
                return cached

        # compute shortest path using NetworkX
        try:
            path = nx.shortest_path(self.G, source=source, target=sink, weight='weight')
            path_series = pd.Series(path)
            path_series.reset_index(inplace=True, drop=True)
            self.path_ids_dict[source, sink] = path_series
            return path_series
        except nx.NetworkXNoPath:
            # no path exists, fall back to straight route
            return self.get_straight_route(source)

    def get_route(self, source):
        """
        Get a route for a vehicle generated at the given source.
        Uses random routing with NetworkX shortest path.
        """
        return self.get_random_route(source)

    def get_straight_route(self, source):
        """
        pick up a straight route given an origin
        """
        return self.path_ids_dict[source, None]

    def step(self):
        """
        Advance the simulation by one step.
        """
        self.schedule.step()

    def record_trip(self, vehicle):
        """
        Record completed trip data for a vehicle that has reached its destination.
        """
        origin_id = vehicle.generated_by.unique_id
        dest_id = vehicle.path_ids.iloc[-1]
        dest_agent = self.schedule._agents.get(dest_id)

        self.trip_data.append({
            'vehicle_id': vehicle.unique_id,
            'origin_id': origin_id,
            'origin_road': vehicle.generated_by.road_name,
            'dest_id': dest_id,
            'dest_road': dest_agent.road_name if dest_agent else 'unknown',
            'generated_at': vehicle.generated_at_step,
            'removed_at': vehicle.removed_at_step,
            'travel_time': vehicle.removed_at_step - vehicle.generated_at_step,
            'total_waiting_time': vehicle.total_waiting_time,
            'bridges_passed': vehicle.bridges_passed,
            'path_length': len(vehicle.path_ids),
        })

    def export_data(self, file_path):
        """
        Export collected trip data to a CSV file.
        """
        df = pd.DataFrame(self.trip_data)
        df.to_csv(file_path, index=False)
        return df

    def get_bridge_data(self):
        """
        Return data for all bridges in the model.
        """
        bridges = [a for a in self.schedule._agents.values()
                   if isinstance(a, Bridge)]
        return [{
            'bridge_id': b.unique_id,
            'name': b.name,
            'road': b.road_name,
            'condition': b.condition,
            'length': b.length,
            'broken_down': b.broken_down,
            'total_delay_min': b.total_delay_caused,
            'vehicles_delayed': b.vehicles_delayed,
        } for b in bridges]

# EOF -----------------------------------------------------------

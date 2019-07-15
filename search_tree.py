import pandas as pd
import numpy as np
import math

class Node:
    def __init__(self, split_name, split_value):
        self.split_name = split_name
        self.split_value = split_value
        self.left_child = None
        self.right_child = None

    def __repr__(self):
        return str([self.split_name, self.split_value])

    def set_right_child(self, node):
        self.right_child = node

    def set_left_child(self, node):
        self.left_child = node


class LatLngSearchTree:

    def __init__(self, features):
        self.head = None
        self.features = features

    def __find_best_split__(self, fbscol):
        splits = self.__find_splits__(fbscol)
        split_function = self.__division_from_split_function__(fbscol)

        return pd.DataFrame(list(map(split_function, fbscol))).sort_values("diff").iloc[0].to_dict()

    def __find_splits__(self, fscol):

        srt = np.sort(np.unique(fscol))

        shift = np.delete(np.insert(srt,0,0), -1)

        splits = np.delete(srt,-1) + np.delete((srt-shift)/2,0)

        return splits

    def __division_from_split_function__(self, dfscol):
        def toReturn(split_value):
            less = len(dfscol[dfscol<= split_value])
            return {"split":split_value, "diff":abs(less - (len(dfscol) - less))}

        return toReturn

    def fit_tree(self, data):
        cols = data[self.features].values.T
        best_splits = pd.DataFrame([{'feature':name, **self.__find_best_split__(data[name].values)} for name in self.features])
        # best_splits = pd.DataFrame([ {"feature": name, **self.__find_best_split__(col)} for name, col in zip(self.features, cols)])
        # print(best_splits)

        best_split = best_splits.sort_values("diff").iloc[0][['feature', 'split']]
        node = Node(best_split.feature, best_split.split)
        if self.head == None:
            self.head = node

        l_data = data.loc[data[best_split.feature] <= best_split.split, :]
        r_data = data.loc[data[best_split.feature] > best_split.split, :]

        if len(l_data[l_data["name"] == "Laramie"]) > 0:
            print("left", best_split.split)
        if len(r_data[r_data["name"] == "Laramie"]) > 0:
            print("right", best_split.split)
        # print(l_data.shape)
        # print(r_data.shape)
        if len(l_data) < 3:
            node.set_left_child(l_data)
        else:
            node.set_left_child(self.fit_tree(l_data))

        if len(r_data) < 3:
            node.set_right_child(r_data)
        else:
            node.set_right_child(self.fit_tree(r_data))

        return node

    def buffer_to_deg_lng(self, lat, buffer):
        rad = math.radians(lat)
        one_degree = 69.172 * math.cos(rad)
        return buffer / one_degree

    def buffer_to_deg_lat(self, buffer):
        return buffer / 69.1

    def generate_buffer_dict(self, lat, buffer):
        return {
        'lng': self.buffer_to_deg_lng(lat, buffer),
        'lat': self.buffer_to_deg_lat(buffer)
        }

    def find_poi(self, lat, lng, buffer):
        potentials = self.search(lat,lng, buffer)

        if len(potentials) > 0:
            places = pd.concat(potentials)
            buffers = self.generate_buffer_dict(lat, buffer)

            lng_filter = ((places.SWLng < lng + buffers['lng']) & (places.NELng > lng- buffers['lng']))
            lat_filter = ((places.SWLat - buffers['lat'] < lat) & (places.NELat + buffers['lat'] > lat))

            filtered_poi = places[lng_filter & lat_filter]
            if len(filtered_poi) == 0:
                return None
            else:
                return filtered_poi

        else:
            return None


    def search(self, lat, lng, buffer, node = None ):
        if type(node) == type(None):
            node = self.head

        if type(node) == type(pd.DataFrame()):
            return [node]

        if type(buffer) != dict:
            buffers = self. generate_buffer_dict(lat, buffer)
        else:
            buffers = buffer
        # print(node.split_value, node.split_name, buffers['lat'])
        # print(node.split_value + buffers['lat'], node.split_value - buffers['lat'])

        if node.split_name[-3:] == "Lat":
            if self.within_buffer(node.split_value, buffers['lat'], lat):
                # print("both")
                # print(str([*self.search(lat,lng, buffers, node.left_child), *self.search(lat,lng, buffers, node.right_child)]))
                # print("------------")
                return [*self.search(lat,lng, buffers, node.left_child), *self.search(lat,lng, buffers, node.right_child)]
            elif lat <= node.split_value:
                # print("left")
                # print(str([*self.search(lat,lng, buffers, node.left_child)]))
                # print("-------------")
                return [*self.search(lat,lng, buffers, node.left_child)]
            else:
                # print("right")
                # print(str([*self.search(lat,lng, buffers, node.right_child)]))
                # print("-----------")
                return [*self.search(lat,lng, buffers, node.right_child)]
        else:
            if self.within_buffer(node.split_value, buffers['lng'], lng):
                return [*self.search(lat,lng, buffers, node.left_child), *self.search(lat,lng, buffers, node.right_child)]
            elif lng <= node.split_value:
                return [*self.search(lat,lng, buffers, node.left_child)]
            else:
                return [*self.search(lat,lng, buffers, node.right_child)]


    def within_buffer(self, split_value, buffer, observed):
        if (observed > split_value - buffer) & (observed < split_value + buffer):
            return True
        else:
            return False

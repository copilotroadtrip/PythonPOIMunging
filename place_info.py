import shapefile
import pandas as pd
import numpy as np

class PlaceInfo:

    def __init__(self, file_paths, population_path = 'subest2018_all.csv'):
        self._population_table = pd.read_csv(population_path, encoding = "ISO-8859-1" )
        shape_records = []
        if type(file_paths) == str:
            shape_records.extend(shapefile.Reader(file_paths).shapeRecords())
        else:
            for sr_list in [shapefile.Reader(path).shapeRecords() for path in file_paths]:
                shape_records.extend(sr_list)

        self.shape_table = self.__build_shape_table__(shape_records)

    def __find_population__(self, state, place, data = None):
        if data == None:
            data = self._population_table

        placeRecords = data[(data.STATE == state) & (data.PLACE == place)]
        if len(placeRecords) == 1:
            return placeRecords.iloc[0, -1]
        else:
            try:
                topRecord = placeRecords[placeRecords["POPESTIMATE2018"] == max(placeRecords["POPESTIMATE2018"])]
                return topRecord.iloc[0,-1]
            except:
                return 0

    def __build_shape_table__(self, shape_records):

        """
        Indicies in info correspond to:
        0 : STATEFP - State FIPS code
        1 : PLACEFP - Place FIPS code
        2 : PLACENS - Place GNIS code
        3 : GEOID - Concat. of State / Place FIPS
        4 : NAME - Current Name
        5 : NAMELSAD - Current Name + legal/statistical suffix (e.g. town, village)
        6 : LSAD - Legal/statistical area description
        7 : CLASSFP - FIPS class code
        8 : PCICBSA - Yes or no, principal city of CBSA
        9 : PCINECTA - Yes or no, principal city of NECTA
        10 : MTFCC - MAF/ TIGER feature class code
        11 : FUNCSTAT - Current functional status
        12 : ALAND - Area Land
        13 : AWATER - Area Water
        14 : INTPTLAT - Latitude of internal point
        15 : INTPTLON - Longitude of internal point
        """

        parsed = []
        for record in shape_records:
            to_add = {}
            info = record.record
            population = self.__find_population__(int(info[0]), int(info[1]))
            if population > 0:
                points = record.shape.points

                to_add = {
                    "population": population,
                    "name": info[4],
                    "total_area": int(info[-3]) + int(info[-4]),
                    "land_area": int(info[-4]),
                    "points": points
                }

                to_add["NELng"], to_add["NELat"] = np.apply_along_axis(max, 0, points)
                to_add["SWLng"], to_add["SWLat"] = np.apply_along_axis(min, 0, points)

                parsed.append(to_add)
        return pd.DataFrame(parsed)

    def return_db_information(self):
        return self.shape_table.drop('points', axis = 1)

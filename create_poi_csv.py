from place_info import PlaceInfo
import pandas as pd

files_paths = "place_files.txt"
files = open(files_paths, 'r')
files_list = ["./POIData/"+line.replace("\n","") for line in files]

all_states =  PlaceInfo(files_list)

all_states.return_db_information().to_csv('all_poi.csv', index = False)

### Note, this will take between 1 and 2 minutes

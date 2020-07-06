import os
import json
for file in os.listdir('BGB'):
    with open(os.path.join('BGB',file), "r") as file_:
        data = json.load(file_)
    data['Full_ID'] = file
    with open(os.path.join('BGB',file), "w") as file_:
        json.dump(data, file_, ensure_ascii= False)
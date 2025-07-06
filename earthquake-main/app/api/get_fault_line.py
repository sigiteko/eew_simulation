import json

def get_fault_line():
    with open("datas/IndonesiaFaultModels_Pusgen2016.geojson", "r") as f:
        fault_line = json.load(f)
    return fault_line

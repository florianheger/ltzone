import pandas as pd


class Athlete:
    data = None

    def __init__(self, data):
        self.get_data(data)
    
    # intended for data entry from the table
    def get_data_from_table(self, get_attr):
        id = int(get_attr["id"][0])
        task = str(get_attr["task"][0])
        stage_length = str(get_attr["stage_length"][0])
        last_stage_length = str(get_attr["last_stage_length"][0])
        del get_attr["id"]
        del get_attr["task"]
        del get_attr["stage_length"]
        del get_attr["last_stage_length"]
        keys = get_attr.keys()
        print(keys)

    # get the data from a .csv file or a buffer
    def get_data(self, filename: str):
        self.data = pd.read_csv(filename, delimiter=";")
        stage_length_str = self.data["stage_length"].str.split(":").tolist()
        stage_length_int = []
        for s in stage_length_str:
            stage_length_int.append(int(s[2]) + 60 * int(s[1]) + 60 * 60 * int(s[0]))
        self.data["stage_length"] = pd.DataFrame(data=stage_length_int)
        self.add_x_axis()
    
    def add_x_axis(self):
        self.data = self.data.fillna(0)
        x_axis = pd.DataFrame(self.data['velocity_kmh']+self.data['power_W'], columns=["x_axis"])
        self.data = self.data.join(x_axis)

    def get_athlete(self, id: int):
        if id not in self.data["ID"].unique():
            raise ValueError("ID does not exist. Possible IDs: " + str(self.data["ID"].unique()))
        return self.data[self.data["ID"] == id].reset_index()

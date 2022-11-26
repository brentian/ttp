class Train(object):
    def __init__(self, traNo, down, macro_time):
        self.traNo = traNo  # 列车车次
        self.down = down  # up or down
        # 1     - in
        # 0     - out
        # -1    - in and out
        # None  - irrelevant
        #   passing or circulation (到达后需要离开到站界）
        # todo, this is not a single attribute,
        # todo, it should be recognized by stations
        # todo, change to something like:
        #   {station: bool_in_station}
        self.bool_in_station = None
        self.macro_time = macro_time

    def __hash__(self):
        return self.traNo.__hash__()

    def __eq__(self, other):
        return self.traNo == other.traNo

    def __repr__(self):
        return "train" + str(self.traNo)
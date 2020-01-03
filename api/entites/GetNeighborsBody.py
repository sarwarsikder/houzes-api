class GetNeighborsBody:
    # is_power_trace = 0
    # is_owner_info = 1
    # address = None

    def __init__(self, data):
        self.is_power_trace = data['is_power_trace']
        self.is_owner_info = data['is_owner_info']
        self.address = data['address']
        if self.is_power_trace == 1:
            self.is_power_trace = True
        else:
            self.is_power_trace = False

        if self.is_owner_info == 1:
            self.is_owner_info = True
        else:
            self.is_owner_info = False

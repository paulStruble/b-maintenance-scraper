# A work order request

from typing import List


class WORequest:
    def __init__(self, number):
        self.id = number
        self.room = None
        self.status = None
        self.building = None
        self.tag = None
        self.accept_date = None
        self.reject_date = None
        self.reject_reason = None
        self.location = None
        self.item_description = None
        self.work_order_num = None
        self.area_description = None
        self.requested_action = None

    # returns a list of all datapoints in string format
    def to_list(self) -> list:
        return [self.id,
                self.room,
                self.status,
                self.building,
                self.tag,
                self.accept_date,
                self.reject_date,
                self.reject_reason,
                self.location,
                self.item_description,
                self.work_order_num,
                self.area_description,
                self.requested_action]

    # returns a comma-separated string of all datapoints
    def to_csv(self) -> str:
        string_list = [str(datapoint).replace('\n', '\\n') for datapoint in self.to_list()]
        return ','.join(string_list)

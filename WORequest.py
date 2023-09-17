# A work order request

from typing import Callable


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

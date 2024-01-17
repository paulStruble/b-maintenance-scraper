class WorkOrder:
    def __init__(self, order_number: str):
        """A work order containing all relevant data.

        Args:
            order_number: Work order number for this work order (ex. 'HM-463785').
        """
        self.order_number = order_number
        self.facility = None
        self.building = None
        self.location_id = None
        self.priority = None
        self.request_date = None
        self.schedule_date = None
        self.work_status = None
        self.date_closed = None
        self.main_charge_account = None
        self.task_code = None
        self.reference_number = None
        self.tag_number = None
        self.item_description = None
        self.request_time = None
        self.date_last_posted = None
        self.trade = None
        self.contractor_name = None
        self.est_completion_date = None
        self.task_description = None
        self.requested_action = None
        self.corrective_action = None

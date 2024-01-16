class WORequest:
    def __init__(self, request_id: int):
        """A work order request containing all data pertaining to the request.

        Args:
            request_id: id of the work request.
        """
        self.id = request_id
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

    def to_list(self) -> list:
        """Convert this request into an ordered list of all datapoints.

        Returns: List of datapoints in order."""
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

    def to_csv(self) -> str:
        """Return a csv-entry-representation of this work request.

        Returns:
            Comma-separated string of all datapoints.
        """
        string_list = [str(datapoint).replace('\n', '\\n') for datapoint in self.to_list()]
        return ','.join(string_list)

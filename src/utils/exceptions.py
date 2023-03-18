
class NotInRange(Exception):
    def __init__(self, message = "Values entered are not in range"):
        self.message = message
        super().__init__(self.message)


class NotInCols(Exception):
    def __init__(self, message = "Not in columns"):
        self.message = message
        super().__init__(self.message)
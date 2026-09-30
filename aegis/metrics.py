class MissionMetrics:
    def __init__(self):
        self.steps = 0
        self.replans = 0
        self.discoveries = 0
        self.planning_time_ms = 0.0
        self.safety_stops = 0
        self.events = []

    def record(self, event, **data):
        self.events.append({"event": event, **data})

    def record_plan(self, milliseconds):
        self.replans += 1
        self.planning_time_ms += milliseconds

    @property
    def average_planning_time_ms(self):
        if not self.replans:
            return 0.0
        return self.planning_time_ms / self.replans

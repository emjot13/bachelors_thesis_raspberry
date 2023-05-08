# Klasa ktora przechowuje log z datą oraz ziewnięciami i spaniami
class FatigueLog:
    def __init__(self, timestamp, yawns, sleeps, yawns_increase, sleeps_increase):
        self.timestamp = timestamp
        self.yawns = yawns
        self.sleeps = sleeps
        self.yawns_increase = yawns_increase
        self.sleeps_increase = sleeps_increase

    def to_json(self):
        return {
            'timestamp': self.timestamp,
            'yawns': self.yawns,
            'sleeps': self.sleeps,
            'yawns_increase': self.yawns_increase,
            'sleeps_increase': self.sleeps_increase
        }

    def to_array(self):
        return [self.timestamp, self.yawns, self.sleeps, self.yawns_increase, self.sleeps_increase]

    def __str__(self):
        return f"{self.timestamp},{self.yawns},{self.sleeps},{self.yawns_increase},{self.sleeps_increase}"
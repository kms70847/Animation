class Event:
    def __init__(self):
        pass
    def tick(self):
        pass
    def isDone(self):
        return True

class ChainedEvent(Event):
    def __init__(self, *events):
        self.events = events
    def tick(self):
        if self.isDone(): return
        self.events[0].tick()
        if self.events[0].isDone():
            self.events = self.events[1:]
    def isDone(self):
        return len(self.events) == 0

class SimulEvent(Event):
    def __init__(self, *events):
        self.events = events
    def tick(self):
        if self.isDone(): return
        nextEvents = []
        for e in self.events:
            e.tick()
            if not e.isDone():
                nextEvents.append(e)
        self.events = nextEvents
    def isDone(self):
        return len(self.events) == 0
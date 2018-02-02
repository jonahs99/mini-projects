import numpy as np
import math
import random

class Agent:
    def __init__(self):
        self.pos = np.array([0.0, 0.0])
        self.dir = 0
        self.speed = 4
        self.rad = 10
    def update(self):
        self.pos[0] += math.cos(self.dir) * self.speed
        self.pos[1] += math.sin(self.dir) * self.speed
        self.dir += 0.01
    def packet(self):
        return {
            'type': 'agent',
            'rad': self.rad,
            'pos': [int(self.pos[0]), int(self.pos[1])],
            'dir': self.dir
        }

class Blob:
    def __init__(self, sim):
        r = 40 + math.sqrt(random.random() * (sim.rad - 40 - 20) ** 2)
        t = random.random() * 2 * math.pi
        self.pos = np.array([int(math.cos(t) * r), int(math.sin(t) * r)])
        self.rad = int(5 + random.random() * 5)
        self.reward = -1 if random.random() < 0.4 else 1
    def update(self): pass
    def packet(self):
        return {
            'type': 'blob',
            'rad': self.rad,
            'pos': [int(self.pos[0]), int(self.pos[1])],
            'reward': self.reward
        }

class Simulation:
    def __init__(self):
        self.rad = 400
        self.entities = []
        self.agent = self.add_entity(Agent())
        for _ in range(20):
            self.add_entity(Blob(self))
    def add_entity(self, e):
        for i, entity in enumerate(self.entities):
            if entity is None:
                self.entities[i] = e
        self.entities.append(e)
        return e
    def update(self):
        for e in self.entities:
            e.update()
    def get_packet(self):
        entity_list = list(map(lambda e: e.packet(), self.entities))
        packet = {'environment': {'rad': self.rad}, 'entities': entity_list}
        return packet
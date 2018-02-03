import numpy as np
import math
import random

import model

class Agent:
    def __init__(self, sim):
        self.sim = sim
        self.pos = np.array([0.0, 0.0])
        self.dir = 0
        self.speed = 1
        self.max_speed = 2
        self.rad = 10

        self.decay_rate = 0.95
        self.fov = math.pi / 3
        self.n_bins = 16
        self.eye_dist = [0.0] * self.n_bins
        self.eye_r = [0.0] * self.n_bins
        self.eye_g = [0.0] * self.n_bins
        self.eye_decay = [0.0] * self.n_bins

        self.brain = model.Network(self)
    def update(self):
        for i in range(len(self.eye_decay)):
            self.eye_decay[i] *= self.decay_rate

        raydir = (random.random() * 2 - 1) * self.fov
        ray = self.sim.test_ray(self.pos, self.dir + raydir)
        i_bin = math.floor((raydir + self.fov) * self.n_bins / 2 / self.fov)
        self.eye_dist[i_bin] = ray[0]
        self.eye_decay[i_bin] = 1
        self.eye_r[i_bin] = ray[1][0]
        self.eye_g[i_bin] = ray[1][1]

        outputs = self.brain.forward(self.brain.create_input(self))
        left, right = outputs.data[0, 0], outputs.data[0, 1]
        left = min(max(left, -1), 1) * self.max_speed + 2
        right = min(max(right, -1), 1) * self.max_speed + 2
        self.speed = (left + right) / 2
        self.dir += (right - left) / self.rad / 3

        self.pos[0] += math.cos(self.dir) * self.speed
        self.pos[1] += math.sin(self.dir) * self.speed

        dist = np.linalg.norm(self.pos)
        if dist > self.sim.rad - 2 * self.rad:
            self.pos *= (self.sim.rad - 2 * self.rad) / dist
    def packet(self):
        return {
            'type': 'agent',
            'rad': self.rad,
            'pos': [int(self.pos[0]), int(self.pos[1])],
            'dir': self.dir,
            'fov': self.fov,
            'eye_dist': self.eye_dist,
            'eye_r': self.eye_r,
            'eye_g': self.eye_g,
            'eye_decay': self.eye_decay
        }

class Blob:
    def __init__(self, sim):
        r = 40 + math.sqrt(random.random() * (sim.rad - 40 - 20) ** 2)
        t = random.random() * 2 * math.pi
        self.pos = np.array([int(math.cos(t) * r), int(math.sin(t) * r)])
        self.rad = int(5 + random.random() * 5)
        self.reward = -1 if random.random() < 0.4 else 1
        self.color = (1, 0) if self.reward == -1 else (1, 1)
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
        self.pos = np.array([0.0, 0.0])
        self.rad = 400
        self.color = (0, 1)

        self.entities = []
        self.blobs = []
        self.agent = self.add_entity(Agent(self))
        for _ in range(100):
            self.blobs.append(self.add_entity(Blob(self)))
    def add_entity(self, e):
        for i, entity in enumerate(self.entities):
            if entity is None:
                self.entities[i] = e
        self.entities.append(e)
        return e
    def update(self):
        for e in self.entities:
            e.update()
    def test_ray(self, ro, rd):
        closestt = math.inf
        clr = (0, 0)
        for blob in self.blobs + [self]:
            p = blob.pos - ro
            d = np.array([math.cos(rd), math.sin(rd)])
            a = np.dot(d, d)
            b = -2 * np.dot(p, d)
            c = np.dot(p, p) - blob.rad**2
            discr = b**2 - 4*a*c
            if discr < 0:
                continue
            discr = math.sqrt(discr)
            t0 = (-b + discr) / 2 / a
            t1 = (-b - discr) / 2 / a
            if t0 < 0:
                t0 = math.inf
            if t1 < 0:
                t1 = math.inf
            blobt = min(t0, t1)
            if blobt < closestt:
                closestt = blobt
                clr = blob.color
        return (closestt, clr)
        
    def get_packet(self):
        entity_list = list(map(lambda e: e.packet(), self.entities))
        packet = {'environment': {'rad': self.rad}, 'entities': entity_list}
        return packet
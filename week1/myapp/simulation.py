import numpy as np
import math
import random

import model

class Agent:
    def __init__(self, sim, parent=None):
        self.sim = sim
        self.pos = np.array([0.0, 0.0])
        self.dir = random.random() * 2 * math.pi
        self.speed = 0
        self.max_speed = 4
        self.rad = 10

        self.move_cost = 0#0.002

        self.fitness = 0

        self.decay_rate = 0.95
        self.fov = math.pi / 3
        self.n_bins = 8
        self.eye_dist = [0.0] * self.n_bins
        self.eye_r = [0.0] * self.n_bins
        self.eye_g = [0.0] * self.n_bins
        self.eye_decay = [0.0] * self.n_bins

        if parent is None:
            self.brain = model.Network(self)
        else:
            self.brain = model.Network(self, parent.brain.mutate())
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

        self.fitness -= self.move_cost * (abs(left) + abs(right))

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
            'eye_decay': self.eye_decay,
            'fitness': self.fitness
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

        self.tick = 0
        self.generation = 0
        self.n_ticks = 800

        self.n_blobs = 128

        self.n_agents = 16
        self.n_winners = 8
        self.n_random = 1

        self.entities = []
        self.blobs = []
        self.agents = []
        for _ in range(self.n_agents):
            self.agents.append(self.add_entity(Agent(self)))
        for _ in range(self.n_blobs):
            self.blobs.append(self.add_entity(Blob(self)))
    def new_generation(self):
        ranking = sorted(self.agents, key=lambda a: a.fitness)
        winners = ranking[-self.n_winners:]
        
        self.entities = []
        self.blobs = []
        self.agents = []
        for _ in range(self.n_random):
            self.agents.append(self.add_entity(Agent(self)))
        for _ in range(self.n_agents - self.n_random):
            parent = random.choice(winners)
            self.agents.append(self.add_entity(Agent(self, parent)))
        for _ in range(self.n_blobs):
            self.blobs.append(self.add_entity(Blob(self)))
    def add_entity(self, e):
        for i, entity in enumerate(self.entities):
            if entity is None:
                self.entities[i] = e
                return e
        self.entities.append(e)
        return e
    def remove_entity(self, e):
        for i, entity in enumerate(self.entities):
            if entity is e:
                self.entities[i] = None
                return
    def get_entities(self):
        for i, entity in enumerate(self.entities):
            if entity is not None:
                yield entity
    def update(self):
        if self.tick > self.n_ticks:
            self.tick = 0
            self.generation += 1
            self.new_generation()

        for e in self.get_entities():
            e.update()
        for a in self.get_entities():
            if not isinstance(a, Agent):
                continue
            for b in self.get_entities():
                if not isinstance(b, Blob):
                    continue
                dist = np.linalg.norm(a.pos - b.pos)
                if dist < a.rad + b.rad:
                    a.fitness += b.reward
                    self.remove_entity(b)
                    self.add_entity(Blob(self))
        self.tick += 1

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
        entity_list = list(map(lambda e: None if e is None else e.packet(), self.entities))
        packet = {'environment': {'rad': self.rad}, 'entities': entity_list}
        return packet
from abc import ABCMeta, abstractmethod
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class BaseBlock(metaclass=ABCMeta):
    def __init__(self, name: str = 'block'):
        self.name = name

    @abstractmethod
    def get(self, t: float):
        pass


class StatefulBlock(BaseBlock):
    def __init__(self, name: str = 'state', y0: float = 0):
        super().__init__(name)
        self.t = 0
        self.y = y0

    def get(self, t: float) -> float:
        if t == self.t:
            return self.y
        else:
            self.t = t
            return self.y


class Step(BaseBlock):
    def __init__(self, name: str = 'step', ts: float = 1, yi: float = 0, yf: float = 1):
        super().__init__(name)
        self.ts = ts
        self.yi = yi
        self.yf = yf

    def get(self, t: float):
        if t <= self.ts:
            return self.yi
        else:
            return self.yf


class FirstOrderDelay(StatefulBlock):
    def __init__(self, name: str = '1st-order-delay', K: float = 1, T: float = 1, y0: float = 0, input: BaseBlock = Step()):
        super().__init__(name, y0=y0)
        self.K = K
        self.T = T
        self.input = input

    def get(self, t: float):
        if t == self.t:
            return self.y
        else:
            u = self.input.get(t)
            dy = (self.K*u - self.y)/self.T
            self.y += dy*(t-self.t)
            self.t = t
            return self.y


class Add(BaseBlock):
    def __init__(self, inputs: list[BaseBlock], name: str = 'add'):
        super().__init__(name)
        self.inputs = inputs

    def get(self, t: float):
        res = 0
        for input in self.inputs:
            res += input.get(t)
        return res


class Recorder:
    def __init__(self, inputs: list[BaseBlock]):
        self.inputs = inputs
        self.output = {}
        for input in self.inputs:
            name = input.name
            self.output[name] = {'t': [], 'y': []}

    def get(self, t: float):
        for input in self.inputs:
            name = input.name
            y = input.get(t)
            self.output[name]['t'].append(t)
            self.output[name]['y'].append(y)

    def plot(self):
        n = len(self.inputs)
        fig = make_subplots(n, 1, True)
        i = 1
        for input in self.inputs:
            name = input.name
            fig.add_trace(
                go.Scatter(
                    x=self.output[name]['t'],
                    y=self.output[name]['y'],
                    name=input.name
                ), i, 1
            )
            i += 1
        fig.show()


class System:
    def __init__(self):
        self.models = []

    def add(self, model):
        self.models.append(model)

    def get(self, t):
        for model in self.models:
            model.get(t)

    def run(self, tend: float, dt: float):
        for t in np.arange(0, tend, dt):
            self.get(t)

from .generator import Generator
from ..entity.data_context import DataContext


class RiderGenerator(Generator):
    def __init__(self, data_context: DataContext, seed: int = 0):
        super().__init__(id="RiderGenerator", seed=seed)
        self.data_context = data_context
        self.schedule(self._generate_rider)

    def _generate_rider(self):
        self.arrive(self.data_context.rider)

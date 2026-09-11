from .generator import Generator
from ..entity.data_context import DataContext


class RestaurantGenerator(Generator):
    def __init__(self, data_context: DataContext, seed: int = 0):
        super().__init__(id="RestaurantGenerator", seed=seed)
        self.data_context = data_context
        self.schedule(self._generate_restaurant)

    def _generate_restaurant(self):
        for restaurant in self.data_context.restaurants:
            self.arrive(restaurant)

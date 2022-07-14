from element import Element


class Background(Element):
    steps = []

    def __init__(self, element_type, location, steps):
        super().__init__(element_type, location)
        self.steps = steps


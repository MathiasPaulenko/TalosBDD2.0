
class Element:
    ELEMENT_BACKGROUND = 'background'
    ELEMENT_SCENARIO = "scenario"
    ELEMENT_FEATURE = "feature"
    ELEMENT_TYPES = (ELEMENT_BACKGROUND, ELEMENT_SCENARIO, ELEMENT_FEATURE)

    passed_steps = 0
    failed_steps = 0

    def __init__(self, element_type, location, name=""):
        if element_type in self.ELEMENT_TYPES:
            self.element_type = element_type
        else:
            raise ValueError(f"Element type must be one of {self.ELEMENT_TYPES}")
        self.location = location
        self.name = name

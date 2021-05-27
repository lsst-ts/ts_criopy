from .TopicData import TopicData

__all__ = ["Thermals"]


class Thermals:
    """
    Class constructing list of all available topics.
    """

    def __init__(self):
        self.lastIndex = None

        self.topics = [
            TopicData(
                "Thermal Data",
                [
                    [
                        "Differential temperature",
                        lambda x: x.differentialTemperature,
                        lambda: None,
                    ],
                    ["Fan RPM", lambda x: x.fanRPM, lambda: None],
                    [
                        "Absolute temperature",
                        lambda x: x.absoluteTemperature,
                        lambda: None,
                    ],
                ],
                "thermalData",
                False,
            ),
        ]

    def changeTopic(self, index, slot, m1m3ts):
        if self.lastIndex is not None:
            getattr(m1m3ts, self.topics[self.lastIndex].topic).disconnect(slot)

        self.lastIndex = index
        if index is None:
            return

        getattr(m1m3ts, self.topics[index].topic).connect(slot)

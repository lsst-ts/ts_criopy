from .TopicData import TopicData, TopicField
from .ActuatorsDisplay import Scales

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
                    TopicField(
                        "Differential temperature", "differentialTemperature", None
                    ),
                    TopicField("Fan RPM", "fanRPM", None),
                    TopicField("Absolute temperature", "absoluteTemperature", None),
                ],
                "thermalData",
                False,
            ),
            TopicData(
                "Thermal ILCs",
                [
                    TopicField("ILC Fault", "ilcFault", None, Scales.WARNING),
                    TopicField(
                        "Heater disabled", "heaterDisabled", None, Scales.WARNING
                    ),
                    TopicField("Heater breaker", "heaterBreaker", None, Scales.ONOFF),
                    TopicField("Fan breaker", "fanBreaker", None, Scales.ONOFF),
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

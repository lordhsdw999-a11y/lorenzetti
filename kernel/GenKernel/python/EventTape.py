"""
EventTape coordinator module for event generation and serialization.
"""

from typing import Optional, Union, List
import ROOT

from GaugiKernel import Configurable, LoggingLevel
from GaugiKernel.macros import MSG_FATAL

__all__ = ["EventTapeCfg", "EventTape"]


class EventTape(Configurable):
    """
    Coordinates event generation and serialization into ROOT TTree.
    """

    def __init__(
        self,
        name: str = "EventTape",
        OutputFile: str = "particles",
        RunNumber: int = 0,
        NumberOfEvents: int = 1,
        OutputLevel: int = LoggingLevel.toC("INFO"),
        **kwargs
    ):
        super().__init__(
            ROOT.generator.EventTape,
            name,
            OutputFile=OutputFile,
            RunNumber=RunNumber,
            OutputLevel=OutputLevel,
            **kwargs
        )
        self._algs = []

    def push_back(self, tool):
        if hasattr(tool, "c_ptr"):
            self._c_ptr.push_back(tool.c_ptr())
        else:
            self._c_ptr.push_back(tool)
        self._algs.append(tool)

    def __add__(self, tool):
        if isinstance(tool, list):
            for t in tool:
                self.push_back(t)
        else:
            self.push_back(tool)
        return self

    def run(self, evt: Optional[Union[int, List[int]]] = None):
        if isinstance(evt, int):
            evts = list(range(evt))
        elif isinstance(evt, list):
            evts = [int(e) for e in evt]
        else:
            MSG_FATAL(self, "input argument type not supported. Should be int value or a list of ints")

        if len(evts) == 0:
            MSG_FATAL(self, "No events to process")

        self.setProperty("EventNumbers", evts)
        self._c_ptr.initialize()
        self._c_ptr.execute()
        self._c_ptr.finalize()


def EventTapeCfg(
    name: str = "EventTape",
    OutputFile: str = "particles",
    RunNumber: int = 0,
    NumberOfEvents: int = 1,
    OutputLevel: int = LoggingLevel.toC("INFO"),
    **kwargs
) -> EventTape:
    """
    Configures and returns an EventTape coordinator instance.

    Args:
        name: Name of the EventTape instance.
        OutputFile: Output file path for generated particles.
        RunNumber: Run number for the generation session.
        NumberOfEvents: Number of events to generate.
        OutputLevel: Logging verbosity level.

    Returns:
        EventTape: Configured EventTape coordinator instance.
    """
    return EventTape(
        name=name,
        OutputFile=OutputFile,
        RunNumber=RunNumber,
        NumberOfEvents=NumberOfEvents,
        OutputLevel=OutputLevel,
        **kwargs
    )

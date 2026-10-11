__all__ = ["EventReader"]

from GaugiKernel import Configurable, LoggingLevel
from GaugiKernel.macros import *
import ROOT, os


class EventReader(Configurable):

    def __init__(
        self,
        name: str,
        InputFileName: str = "",
        OutputEventKey: str = "EventInfo",
        OutputTruthKey: str = "Particles",
        OutputSeedKey: str = "Seeds",
        BunchDuration: int = 25,
        OutputLevel: int = LoggingLevel.toC("INFO"),
    ):
        super().__init__(
            ROOT.generator.EventReader,
            name,
            InputFileName=InputFileName,
            OutputEventKey=OutputEventKey,
            OutputSeedKey=OutputSeedKey,
            OutputTruthKey=OutputTruthKey,
            BunchDuration=BunchDuration,
            OutputLevel=OutputLevel,
        )

        if self.InputFileName != "":
            if not os.path.exists(self.InputFileName):
                MSG_FATAL(self, f"Input file not found into the system: {self.InputFileName}")
            f = ROOT.TFile(InputFileName)
            t = f.Get("particles")
            self.__entries = t.GetEntries()
            f.Close()
        else:
            self.__entries = 0

    def merge(self, acc):
        acc.setGenerator(self)

    def GetEntries(self):
        return self.__entries
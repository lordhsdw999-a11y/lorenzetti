__all__ = ["ComponentAccumulator"]

from GaugiKernel import Configurable, LoggingLevel
from GaugiKernel.constants import MINUTES
from G4Kernel import EventReader
import os
import time
import gc
import ROOT


class ComponentAccumulator(Configurable):
    """
    Component Accumulator for Geant4 simulations.
    Uses the G4Kernel RunManager as a backend.
    """

    def __init__(self, 
                 name, 
                 detector,
                 OutputFile: str = "output.root",
                 Seed: int = 512,
                 NumberOfThreads: int = 1,
                 Timeout: int = 120*MINUTES,
                 UseGUI: bool = False,
                 ):

        super().__init__(ROOT.RunManager, name,
                         OutputFile=OutputFile,
                         Seed=Seed,
                         NumberOfThreads=NumberOfThreads,
                         Timeout=Timeout,
                         UseGUI=UseGUI)

        # convert python to geant4
        self.__detector = detector
        self.__detector.compile()
        # set the geant detector into the geant
        self._c_ptr.setDetectorConstruction(self.__detector.c_ptr())

        if UseGUI:
            [self._c_ptr.addUICommand(cmd) for cmd in detector.get_ui_commands()] 
        self.outputFiles = [ f"{self.OutputFile}.{thread}" for thread in range(self.NumberOfThreads)]

    def __del__(self):
        super().__del__()
        gc.collect()
        time.sleep(2)

    def run(self, evt: int = -1):
        """
        Runs the events in the simulation.

        Parameters
        ----------
        evt : int, optional
            Number of events to run if None, runs all, by default None
        """
        if evt < 0:
            evt = self.__numberOfEvents
        if evt > self.__numberOfEvents:
            evt = self.__numberOfEvents
        self._c_ptr.run(evt)
        self.merge()

    def __add__(self, algs):
        if type(algs) is not list:
            algs = [algs]
        for alg in algs:
            self._c_ptr.push_back(alg.c_ptr())
        return self

    def setGenerator(self, gen: EventReader):
        """
        Sets the generator reader for the simulation.
        The reader is used to read EVT files and return the seeds for G4

        Parameters
        ----------
        gen : EventReader
            Generator reader object
        """
        self.__numberOfEvents = gen.GetEntries()
        self._c_ptr.setGenerator(gen.c_ptr())

    def detector(self):
        """
        Returns the detector construction object.
        """
        return self.__detector

    def merge(self):
        os.system(f"hadd -f {self.OutputFile} {' '.join(self.outputFiles)}")
        [os.remove(f) for f in self.outputFiles]

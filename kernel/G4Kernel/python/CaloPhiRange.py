__all__ = ["CaloPhiRange"]

from GaugiKernel import Logger
from GaugiKernel.macros import *


class CaloPhiRange(Logger):

  def __init__(self):     
    Logger.__init__(self)
    import ROOT
    ROOT.gSystem.Load('liblorenzetti')
    from ROOT import CaloPhiRange
    # Create the algorithm
    self._c_ptr = CaloPhiRange()

  def c_ptr(self):
    return self._c_ptr

  def diff(self, phi1, phi2):
    return self.c_ptr().diff(phi1, phi2)

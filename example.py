import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from Athlete import Athlete
from LactateAnalysisInteractive import LactateAnalysisInteractive

athlete = Athlete("data_lactate.csv")
print(athlete.data)

analysis = LactateAnalysisInteractive(athlete.data)
analysis.analysis()

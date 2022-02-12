
from bokeh.models import  FileInput
from bokeh.plotting import curdoc

import os
import sys
import inspect

from pybase64 import b64decode
from io import BytesIO

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from Athlete import Athlete
from LactateAnalysisInteractive import LactateAnalysisInteractive


button_input = FileInput(id="fileSelect", accept=".csv")

def get_data(attr, old, new):
            # decode data
            decoded = b64decode(new)
            decoded = BytesIO(decoded)
            # read csv
            athlete = Athlete(decoded)
            # create lactate analysis
            analysis = LactateAnalysisInteractive(athlete.data)
            analysis.analysis()
            
button_input.on_change("value", get_data)

curdoc().add_root(button_input)

get_attr = curdoc().session_context.request.arguments
get_keys = get_attr.keys()
if (len(get_keys) != 0):
    athlete = Athlete(get_attr)
    # create lactate analysis
    #analysis = LactateAnalysisInteractive(athlete.data)
    #analysis.show_analysis()
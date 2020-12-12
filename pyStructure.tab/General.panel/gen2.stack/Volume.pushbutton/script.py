__doc__="This addin calculates total volume of selected items"
__title__="Total\nVolume" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB, UI
from pyrevit import forms
import sys
import os

dir_name = os.path.dirname(sys.path[0])
sys.path.append(dir_name)
import units # imported from one directory above by appending the path to sys

# Getting selection from user
__context__ = 'Selection'

doc =__revit__.ActiveUIDocument.Document

# make sure active view is not a sheet
curview = doc.ActiveView
if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

selection = revit.get_selection()
builtin_enum =DB.BuiltInParameter.HOST_VOLUME_COMPUTED
   
total_quant,warning_count = units.total(selection,builtin_enum)
if total_quant:
    if warning_count: # if some selected element has no associated parameter
        forms.alert("Total volume is {0} but {1} items didnot had any associated volume parameter ".\
                                                                    format(total_quant,warning_count),exitscript=True)
    else:
        forms.alert("Total volume is {0}".format(total_quant,warning_count),
                exitscript=True)
else:
    forms.alert("No value found for selected item",exitscript=True)
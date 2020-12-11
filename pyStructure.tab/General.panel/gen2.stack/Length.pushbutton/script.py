__doc__="This addin calculates total length of selected items"
__title__="Total\nLength" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB, UI
from pyrevit import forms
import sys
import os

dir_name = os.path.dirname(sys.path[0])
sys.path.append(dir_name)
import units

# Getting selection from user
__context__ = 'Selection'

doc =__revit__.ActiveUIDocument.Document

# make sure active view is not a sheet
curview = doc.ActiveView
if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

selection = revit.get_selection()
builtin_enum =DB.BuiltInParameter.CURVE_ELEM_LENGTH
   
total_quant,warning_count = units.total(doc,"length",selection,builtin_enum)

if total_quant:
    forms.alert("Total length is {0}".format(total_quant),
                    exitscript=True)
else: # is this needed now?
    forms.alert("Total area negligible in current units\n Change project units for result"
                                                    ,exitscript=True)
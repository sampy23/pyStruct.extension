__doc__="This addin calculates length of selected items"
__title__="Total\nLength" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB, UI
from pyrevit import forms

# Getting selection from user
__context__ = 'Selection'

# make sure active view is not a sheet
curview = revit.activeview
if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

selection = revit.get_selection()
curview = revit.activeview
builtin_enum =DB.BuiltInParameter.CURVE_ELEM_LENGTH
if selection:    
    total_length = 0.0
    for ele in selection:
        len_para = ele.Parameter[builtin_enum]
        if len_para:
            total_length+=len_para.AsDouble()

total_length = total_length*0.3048
forms.alert("Total Length is {} m".format(total_length),
                exitscript=True)
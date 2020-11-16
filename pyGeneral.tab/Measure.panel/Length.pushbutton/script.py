__doc__="This addin calculates length of selected items"
__title__="Total\nLength" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB, UI
from pyrevit import forms

# Getting selection from user
__context__ = 'Selection'

doc =__revit__.ActiveUIDocument.Document

# make sure active view is not a sheet
curview = doc.ActiveView
if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

warning_count = 0 # warning fuse
total_length = 0.0

selection = revit.get_selection()
builtin_enum =DB.BuiltInParameter.CURVE_ELEM_LENGTH
if selection:    
    for ele in selection:
        len_para = ele.Parameter[builtin_enum]
        if len_para:
            total_length+=len_para.AsDouble()
        else:
            if warning_count < 10:
                forms.alert("Warning!!! {0} in the selection has no length parameter".format(ele.Category.Name),
                        exitscript=False)
                warning_count+=1


if total_length:
    total_length = total_length*0.3048
    forms.alert("Total Length is {} m".format(total_length),
                    exitscript=True)
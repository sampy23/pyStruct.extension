__doc__="This addin calculates volume of selected items"
__title__="Total\nVolume" #Title of the extension
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
    total_volume = 0.0
    for ele in selection:
        vol_para = ele.Parameter[DB.BuiltInParameter.HOST_VOLUME_COMPUTED]
        if vol_para:
            total_volume+=vol_para.AsDouble()

total_volume = total_volume*0.3048
forms.alert("Total Volume is {} m3".format(total_volume),
                exitscript=True)


__doc__="This addin calculates volume of selected items"
__title__="Total\nVolume" #Title of the extension
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

selection = revit.get_selection()
builtin_enum = DB.BuiltInParameter.HOST_VOLUME_COMPUTED

warning_count = 0 # warning fuse
total_volume = 0.0

if selection:    
    for ele in selection:
        vol_para = ele.Parameter[builtin_enum]
        if vol_para:
            total_volume+=vol_para.AsDouble()
        else:
            if warning_count < 10:
                forms.alert("Warning!!! {0} in the selection has no volume parameter".format(ele.Category.Name),
                        exitscript=False)
                warning_count+=1

if total_volume:
    total_volume = total_volume*0.3048*0.3048*0.3048
    forms.alert("Total Volume is {} m3".format(total_volume),
                    exitscript=True)


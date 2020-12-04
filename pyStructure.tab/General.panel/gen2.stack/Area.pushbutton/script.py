__doc__="This addin calculates total area of selected items"
__title__="Total\nArea" #Title of the extension
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
total_area = 0.0
unit = []

selection = revit.get_selection()
builtin_enum =DB.BuiltInParameter.HOST_AREA_COMPUTED
if selection:    
    for ele in selection:
        area_para = ele.Parameter[builtin_enum]
        if area_para:
            splitted_value = area_para.AsValueString().split(" ")
            area = float(splitted_value[0])
            unit.append(splitted_value[1])
            total_area+=area

        else:
            if warning_count < 10:
                forms.alert("Warning!!! {0} in the selection has no area parameter".format(ele.Category.Name),
                        exitscript=False)
                warning_count+=1

unit = list(set(unit))
if len(unit) > 1:
    print("Some issue")
else:
    reqd_unit = unit[0]

if total_area:
    # total_length = total_length*0.3048*0.3048
    forms.alert("Total area is {0} {1}".format(total_area,reqd_unit),
                    exitscript=True)
else:
    forms.alert("Total area negligible in {0} units\n Change project units for result".format(reqd_unit)
                                                    ,exitscript=True)
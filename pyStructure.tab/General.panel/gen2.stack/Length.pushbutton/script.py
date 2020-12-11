__doc__="This addin calculates total length of selected items"
__title__="Total\nLength" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB, UI
from pyrevit import forms

# Getting selection from user
__context__ = 'Selection'

doc =__revit__.ActiveUIDocument.Document

def unit_from_type(unittype):
    if unittype == DB.DisplayUnitType.DUT_MILLIMETERS:
        return "mm" 
    elif unittype == DB.DisplayUnitType.DUT_METERS:
        return "m"
    elif unittype == DB.DisplayUnitType.DUT_CENTIMETERS:
        return "cm"
    elif unittype == DB.DisplayUnitType.DUT_DECIMAL_FEET:
        return "decimal-feet"
    elif unittype == DB.DisplayUnitType.DUT_FEET_FRACTIONAL_INCHES:
        return "feet-fractional inches"
    elif unittype == DB.DisplayUnitType.DUT_FRACTIONAL_INCHES:
        return "fractional inches"
    elif unittype == DB.DisplayUnitType.DUT_DECIMAL_INCHES:
        return "decimal-inches"
    elif unittype == DB.DisplayUnitType.DUT_CUSTOM:
        return "custom"
    elif unittype == DB.DisplayUnitType.DUT_UNDEFINED:
        return "undefined"

# make sure active view is not a sheet
curview = doc.ActiveView
if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

warning_count = 0 # warning fuse
total_length = 0.0
unit = []
unittype = []

selection = revit.get_selection()
builtin_enum =DB.BuiltInParameter.CURVE_ELEM_LENGTH
if selection:    
    for ele in selection:
        len_para = ele.Parameter[builtin_enum]
        if len_para:
            splitted_value = len_para.AsValueString().split(" ")
            length = float(splitted_value[0])
            if len(splitted_value) > 1:
                unit.append(splitted_value[0]) # for area revit return unit
            else:
                unittype.append(len_para.DisplayUnitType) # for length and volume unit is not returned so we use unit type

            total_length+=length

        else:
            if warning_count < 10:
                forms.alert("Warning!!! {0} in the selection has no length parameter".format(ele.Category.Name),
                        exitscript=False)
                warning_count+=1

if unit:
    unit = list(set(unit))
    if len(unit) > 1:
        print("Some issue")
    else:
        reqd_unit = unit[0]
else:
    unittype = list(set(unittype))
    if len(unittype) > 1:
        print("Some issue")
    else:
        reqd_unit = unit_from_type(unittype[0])

if total_length:
    forms.alert("Total length is {0} {1}".format(total_length,reqd_unit),
                    exitscript=True)
else:
    forms.alert("Total length negligible in {0} units\n Change project units for result".format(reqd_unit)
                                                                                            ,exitscript=True)
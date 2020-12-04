__doc__="This addin calculates total volume of selected items"
__title__="Total\nVolume" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB, UI
from pyrevit import forms

# Getting selection from user
__context__ = 'Selection'

doc =__revit__.ActiveUIDocument.Document

def formatter(string):
    return u'{0}\xb3'.format(string)

def unit_from_type(unitype):
    if unittype == [DB.DisplayUnitType.DUT_CUBIC_FEET]:
        return formatter("ft")
    elif unittype == [DB.DisplayUnitType.DUT_CUBIC_METERS]:
        return formatter("m")
    elif unittype == [DB.DisplayUnitType.DUT_CUBIC_INCHES]:
        return formatter("in")
    elif unittype == [DB.DisplayUnitType.DUT_CUBIC_CENTIMETERS]:
        return formatter("cm")
    elif unittype == [DB.DisplayUnitType.DUT_CUBIC_MILLIMETERS]:
        return formatter("mm")
    elif unittype == [DB.DisplayUnitType.DUT_LITERS]:
        return "litres"
    elif unittype == [DB.DisplayUnitType.DUT_GALLONS_US]:
        return "US gallons"
    elif unittype == [DB.DisplayUnitType.DUT_CUBIC_YARDS]:
        return formatter("yd")


# make sure active view is not a sheet
curview = doc.ActiveView
if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

warning_count = 0 # warning fuse
total_volume = 0.0
unit = []
unitype = []

selection = revit.get_selection()
builtin_enum =DB.BuiltInParameter.HOST_VOLUME_COMPUTED
if selection:    
    for ele in selection:
        vol_para = ele.Parameter[builtin_enum]
        if vol_para:
            splitted_value = vol_para.AsValueString().split(" ")
            volume = float(splitted_value[0])
            if len(splitted_value) > 1:
                unit.append(splitted_value[0]) # for area revit return unit
            else:
                unitype.append(vol_para.DisplayUnitType) # for volume and length  unit is not returned so we use unit type

            total_volume+=volume
        else:
            if warning_count < 10:
                forms.alert("Warning!!! {0} in the selection has no volume parameter".format(ele.Category.Name),
                        exitscript=False)
                warning_count+=1

if unit:
    unit = list(set(unit))
    if len(unit) > 1:
        print("Some issue")
    else:
        reqd_unit = unit[0]
else:
    unittype = list(set(unitype))
    if len(unittype) > 1:
        print("Some issue")
    else:
        reqd_unit = unit_from_type(unittype[0])

if total_volume:
    forms.alert("Total volume is {0} {1}".format(total_volume,reqd_unit),
                    exitscript=True)
else:
    forms.alert("Total volume negligible in {0} units\n Change project units for result".format(reqd_unit)
                                                                                            ,exitscript=True)
__doc__="This addin calculates total volume of Structural Columns/Framing/Floors/Walls which are visible in Active view"
__title__="Total\nVolume" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB, UI
from pyrevit import forms
 
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
unit = []
unitype = []

if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)
                
 # Creating a dictionary
options = {'Structural Columns': DB.BuiltInCategory.OST_StructuralColumns,
    'Walls': DB.BuiltInCategory.OST_Walls,
    'Structural Framing': DB.BuiltInCategory.OST_StructuralFraming,
    'Floors': DB.BuiltInCategory.OST_Floors,
    'Foundation':DB.BuiltInCategory.OST_StructuralFoundation
}

try:
    selected_switch = \
        forms.CommandSwitchWindow.show(sorted(options.keys()),
                                    message='Select volume of category:')

    if selected_switch:
        target = options[selected_switch]
        
        target_elements = DB.FilteredElementCollector(doc, curview.Id)\
                .OfCategory(target)\
                .WhereElementIsNotElementType()\
                .ToElements()
        
        total_volume = 0.0
        for ele in target_elements:
            vol_para = ele.Parameter[DB.BuiltInParameter.HOST_VOLUME_COMPUTED]
            if vol_para:
                splitted_value = vol_para.AsValueString().split(" ")
                volume = float(splitted_value[0])
                if len(splitted_value) > 1:
                    unit.append(splitted_value[0]) # for area and volume revit return unit
                else:
                    unitype.append(vol_para.DisplayUnitType) # for volume unit is not returned so we use unit type

                total_volume+=volume

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
        forms.alert("Total volume of {0} in current view is {1} {2}".format(selected_switch,total_volume,reqd_unit),
                        exitscript=True)
    else:
        forms.alert("Total volume negligible in {0} units\n Change project units for result".format(reqd_unit)
                                                                                                ,exitscript=True)
except Exception as e: # exception to deal with user exiting the application
    print(str(e))
    pass 
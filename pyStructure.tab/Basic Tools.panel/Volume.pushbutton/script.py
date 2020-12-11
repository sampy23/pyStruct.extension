__doc__="This addin calculates total volume of Structural Columns/Framing/Floors/Walls which are visible in Active view"
__title__="Volume\nStructure" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB, UI
from pyrevit import forms
 
doc =__revit__.ActiveUIDocument.Document



def formatter_cube(string):
    return u'{0}\xb3'.format(string)

def unit_from_type(display_unit_type):
    if display_unit_type == DB.DisplayUnitType.DUT_CUBIC_FEET:
        return formatter_cube("ft")
    elif display_unit_type == DB.DisplayUnitType.DUT_CUBIC_METERS:
        return formatter_cube("m")
    elif display_unit_type == DB.DisplayUnitType.DUT_CUBIC_INCHES:
        return formatter_cube("in")
    elif display_unit_type == DB.DisplayUnitType.DUT_CUBIC_CENTIMETERS:
        return formatter_cube("cm")
    elif display_unit_type == DB.DisplayUnitType.DUT_CUBIC_MILLIMETERS:
        return formatter_cube("mm")
    elif display_unit_type == DB.DisplayUnitType.DUT_LITERS:
        return "litres"
    elif display_unit_type == DB.DisplayUnitType.DUT_GALLONS_US:
        return "US gallons"
    elif display_unit_type == DB.DisplayUnitType.DUT_CUBIC_YARDS:
        return formatter_cube("yd")
    elif display_unit_type == DB.DisplayUnitType.DUT_UNDEFINED:
        return "undefined"

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
        
        total_quant = 0.0
        warning_count = 0
        for ele in target_elements:
            para = ele.Parameter[DB.BuiltInParameter.HOST_VOLUME_COMPUTED]
            if para:
                quant = para.AsDouble() # AsValueString() not recommended
                total_quant+=quant
            else:
                if warning_count < 10: # we don't wish to bomb the user
                    forms.alert("Warning!!! {0} in the selection has no volume parameter".format(ele.Category.Name),
                            exitscript=False)
                    warning_count+=1

        dut = para.DisplayUnitType # will be same for all elements
        total_quant = round(DB.UnitUtils.ConvertFromInternalUnits(total_quant,para.DisplayUnitType),4)
        try:
            formatted_total_quant = str(total_quant) + " " + unit_from_type(dut)
        except: # for none case
            formatted_total_quant = str(total_quant)

        if formatted_total_quant:
            forms.alert("Total volume of {0} in current view is {1}".format(selected_switch,formatted_total_quant),
                            exitscript=True)
        else: # is this needed now?
            forms.alert("Total volume negligible in {0} current units\n Change project units for result"
                                                                                                    ,exitscript=True)
except Exception as e: # exception to deal with user exiting the application
    print(str(e))
    pass 
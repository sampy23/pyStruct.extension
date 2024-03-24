__doc__="This addin calculates total volume of Structural Columns/Framing/Floors/Walls which are visible in Active view"
__title__="Volume\nStructure" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB, UI
from pyrevit import forms
from pyrevit import HOST_APP

doc =__revit__.ActiveUIDocument.Document



def formatter_cube(string):
    return u'{0}\xb3'.format(string)

def revit_volume_unit(unit_type):
    if HOST_APP.is_newer_than(2021):
        volume_metric_units = {   DB.UnitTypeId.CubicMeters:formatter_cube("m") ,
                                DB.UnitTypeId.CubicCentimeters:formatter_cube("cm"),
                                DB.UnitTypeId.CubicMillimeters:formatter_cube("mm"),
                                DB.UnitTypeId.Liters:"L"}
        volume_imperial_units = {   DB.UnitTypeId.CubicFeet:'CF' ,
                                DB.UnitTypeId.CubicInches:formatter_cube("in"),
                                DB.UnitTypeId.CubicYards:"CY",
                               DB.UnitTypeId.UsGallons: "gal"}
    else:
        volume_metric_units = {   DB.DisplayUnitType.DUT_CUBIC_METERS:formatter_cube("m") ,
                                DB.DisplayUnitType.DUT_CUBIC_CENTIMETERS:formatter_cube("cm"),
                                DB.DisplayUnitType.DUT_CUBIC_MILLIMETERS:formatter_cube("mm"),
                                DB.DisplayUnitType.DUT_LITERS:"L"}
        volume_imperial_units = {   DB.DisplayUnitType.DUT_CUBIC_FEET:'CF' ,
                                DB.DisplayUnitType.DUT_CUBIC_INCHES:formatter_cube("in"),
                                DB.DisplayUnitType.DUT_CUBIC_YARDS:"CY",
                               DB.DisplayUnitType.DUT_GALLONS_US: "gal"}

    volume_is_metric = unit_type in list(volume_metric_units.keys())
    volume_is_imperial = unit_type in list(volume_imperial_units.keys())
    if volume_is_metric:
        return volume_metric_units[unit_type]
    elif volume_is_imperial:
        return volume_imperial_units[unit_type]  

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
        doc_units = revit.doc.GetUnits() #get document units
        if HOST_APP.is_newer_than(2021):
            volume_ut = doc_units.GetFormatOptions(DB.SpecTypeId.Volume)
            unit_type = volume_ut.GetUnitTypeId()
        else:
            volume_ut = doc_units.GetFormatOptions(DB.UnitType.UT_Volume)
            unit_type = volume_ut.DisplayUnits

        unit_text = revit_volume_unit(unit_type) # get the unit in text form
        
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

        total_quant = round(DB.UnitUtils.ConvertFromInternalUnits(total_quant,unit_type),4)
        if total_quant:
            try:
                formatted_total_quant = str(total_quant) + " " + unit_text
            except: # for none case
                formatted_total_quant = str(total_quant) + " units"

            forms.alert("Total volume of {0} in current view is {1}".format(selected_switch,formatted_total_quant),
                            exitscript=True)
        else:
            forms.alert("No {0} is available in current view".format(selected_switch),exitscript=True)

except Exception as e: # exception to deal with user exiting the application
    print(str(e))
    pass 
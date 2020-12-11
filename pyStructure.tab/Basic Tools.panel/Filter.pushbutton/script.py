__doc__="This addin filters"
__title__="Filter" #Title of the extension
__author__ = "Shahabaz Sha"
"""This is an advanced filter that works Structural Columns,Walls,Beams,Floors,Foundation,Shaft opening to filter
it based on the chosen parameter.
"""

from pyrevit import revit
from pyrevit import forms
import Autodesk.Revit.DB as DB
import sys

# Getting selection from user
__context__ = 'Selection'

doc =__revit__.ActiveUIDocument.Document
uidoc =__revit__.ActiveUIDocument

def get_options(cat_name):
    if cat_name == 'Structural Columns':
        options_parameter = {
            "Base level":DB.BuiltInParameter.FAMILY_BASE_LEVEL_PARAM ,  #only columns
            "Top level":DB.BuiltInParameter.FAMILY_TOP_LEVEL_PARAM , #only columns
            "Base offset":DB.BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM , #only columns
            "Top offset":DB.BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM , #only columns
            }
    elif (cat_name == 'Walls') or (cat_name == 'Shaft Openings'): # share same inst parameters
        options_parameter = {
            "Base offset":DB.BuiltInParameter.WALL_BASE_OFFSET, # shafts,walls,columns
            "Top offset":DB.BuiltInParameter.WALL_TOP_OFFSET, # shafts,walls,columns
            "Base constraint":DB.BuiltInParameter.WALL_BASE_CONSTRAINT, # shafts,walls
            "Top constraint":DB.BuiltInParameter.WALL_HEIGHT_TYPE, # shafts,walls
            "Unconnected height":DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM, # shafts,walls
            }
    elif cat_name == 'Structural Framing':
        options_parameter = {
            'Z offset value': DB.BuiltInParameter.Z_OFFSET_VALUE, # beams
            'Z justification':DB.BuiltInParameter.Z_JUSTIFICATION,  # beams
            'Elevation at top':DB.BuiltInParameter.STRUCTURAL_ELEVATION_AT_TOP, #beams,floors,foundation
            'Elevation at bottom':DB.BuiltInParameter.STRUCTURAL_ELEVATION_AT_BOTTOM, #beams,floors,foundation
            'Reference level':DB.BuiltInParameter.INSTANCE_REFERENCE_LEVEL_PARAM, # beams only
            }
    elif (cat_name == 'Floors') or (cat_name == 'Structural Foundations'): # share same inst parameters
        options_parameter = {
            'Elevation at top':DB.BuiltInParameter.STRUCTURAL_ELEVATION_AT_TOP, #beams,floors,foundation
            'Elevation at bottom':DB.BuiltInParameter.STRUCTURAL_ELEVATION_AT_BOTTOM, #beams,floors,foundation
            "Height offset from level":DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM, # floors,foundation
            "Level": DB.BuiltInParameter.SCHEDULE_LEVEL_PARAM # floors,foundation
            }
    return options_parameter

def decode_valuestring(target_parameter_value,target_category,target_parameter):
    "Value strings are Revit representation and as such cannot be filtered using fast filters"
    elementids = DB.FilteredElementCollector(doc, curview.Id)\
        .OfCategory(target_category)\
        .WhereElementIsNotElementType()\
        .ToElementIds() # select category 
    collect_eleid = []
    for eleid in elementids:
        ele = revit.doc.GetElement(eleid)
        ele_parameter_value = ele.Parameter[target_parameter].AsValueString()
        if ele_parameter_value == target_parameter_value:
            collect_eleid.append(eleid)

    return collect_eleid

# make sure active view is not a sheet
curview = doc.ActiveView
if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

selection = revit.get_selection()
if len(selection) > 1:
    forms.alert("More than one elements selected.\nSelect one element an d continue",exitscript=True)
ele = selection[0]  # only one element is used. Warn user if more than one selected?
category_name = ele.Category.Name

# Creating a dictionary
options_category = {'Structural Columns': DB.BuiltInCategory.OST_StructuralColumns,
    'Walls': DB.BuiltInCategory.OST_Walls,
    'Structural Framing': DB.BuiltInCategory.OST_StructuralFraming,
    'Floors': DB.BuiltInCategory.OST_Floors,
    'Structural Foundations':DB.BuiltInCategory.OST_StructuralFoundation,
    'Shaft Openings':DB.BuiltInCategory.OST_ShaftOpening
}

if category_name not in options_category.keys():
    forms.alert("Category \"{0}\" not covered in this filter".format(category_name),exitscript=True)


options_parameter = get_options(category_name) # function call


selected_switch_parameter = \
    forms.CommandSwitchWindow.show(sorted(options_parameter.keys()),
                                message='Search for parameter in {0}'.format(category_name))

if selected_switch_parameter:
    target_parameter = options_parameter[selected_switch_parameter]
    target_category = options_category[category_name]
else:# to deal with user pressing esc button
    sys.exit()

valuestring = False
if selected_switch_parameter in ["Z offset value",'Elevation at top','Elevation at bottom',"Height offset from level",
                                "Top offset","Base offset","Unconnected height"]:# double values
    try:
        target_parameter_value = ele.Parameter[target_parameter].AsDouble()
    except:
        forms.alert("Parameter {0} not found in {1}".format(selected_switch_parameter,category_name),exitscript=True)
    param_id = DB.ElementId(target_parameter)
    param_prov = DB.ParameterValueProvider(param_id)
    param_equality = DB.FilterNumericEquals() # equality class for double
    value_rule = DB.FilterDoubleRule(param_prov,param_equality,target_parameter_value,1e-5)
    param_filter = DB.ElementParameterFilter(value_rule)
    elementids = DB.FilteredElementCollector(doc, curview.Id)\
            .OfCategory(target_category)\
            .WhereElementIsNotElementType()\
            .WherePasses(param_filter)\
            .ToElementIds() # select category based on the rule

    if len(elementids) > 1: # there atleast one element selected
        uidoc.Selection.SetElementIds(elementids)
    else:
        forms.alert("No other {0} have {1} value \"{2}\"".\
                                        format(category_name,selected_switch_parameter.lower(),target_parameter_value)\
                                        ,exitscript=True)

else :#  value Strings
    """This param equality for this type is not available so we go for for loop"""
    valuestring = True
    try:
        target_parameter_value = ele.Parameter[target_parameter].AsValueString()# As value strings got converted to strings
    except:
        forms.alert("Parameter \"{0}\" not found in {1}".format(selected_switch_parameter,category_name),exitscript=True)
    collect_eleid = decode_valuestring(target_parameter_value,target_category,target_parameter) #function call

    if len(collect_eleid) > 1: # there atleast one element selected
        revit.get_selection().set_to(collect_eleid) 
    else:
        forms.alert("No other {0} have {1} value \"{2}\"".\
                                        format(category_name,selected_switch_parameter.lower(),target_parameter_value)\
                                        ,exitscript=True)
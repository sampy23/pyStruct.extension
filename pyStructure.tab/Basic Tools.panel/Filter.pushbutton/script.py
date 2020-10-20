__doc__="This addin filters"
__title__="Filter" #Title of the extension
__author__ = "Shahabaz Sha"
"""
**General Information**
AsDouble
Z offset value : Z_OFFSET_VALUE : beams only
Ele at top : STRUCTURAL_ELEVATION_AT_TOP : beams,floors,foundation
Ele at bottom : STRUCTURAL_ELEVATION_AT_BOTTOM  : beams,floors,foundation
Height offset from level : FLOOR_HEIGHTABOVELEVEL_PARAM -Floors,Foundation 
unconnected height : WALL_USER_HEIGHT_PARAM-walls Shafts 
top offset : WALL_TOP_OFFSET -walls,shafts 
base offset : WALL_BASE_OFFSET -walls,shafts

AsString
type mark : ALL_MODEL_TYPE_MARK : Beams,Columns,Slabs,Foundation,Walls (Cannot be read from selection)
mark : ALL_MODEL_MARK: Beams,Columns,Slabs,Foundation,Walls
comments : ALL_MODEL_INSTANCE_COMMENTS : Beams,Columns,Slabs,Foundation,Walls

Asvaluestring
Family : ELEM_FAMILY_PARAM : common
Family and Type : ELEM_FAMILY_AND_TYPE_PARAM : common
Z justification : Z_JUSTIFICATION  : beams only
reference level : INSTANCE_REFERENCE_LEVEL_PARAM -beams only 
base level : FAMILY_BASE_LEVEL_PARAM : columns only
top level : FAMILY_TOP_LEVEL_PARAM : columns only
base offset : FAMILY_BASE_LEVEL_OFFSET_PARAM : columns only
top offset : FAMILY_TOP_LEVEL_OFFSET_PARAM : columns only
base constraint : WALL_BASE_CONSTRAINT : walls,Shafts 
top constraint : WALL_HEIGHT_TYPE : walls,Shafts 
Level : LEVEL_PARAM : Floors,Foundation
"""

from pyrevit import revit
from pyrevit import forms
import Autodesk.Revit.DB as DB
import sys

# Getting selection from user
__context__ = 'Selection'

doc =__revit__.ActiveUIDocument.Document
uidoc =__revit__.ActiveUIDocument

# make sure active view is not a sheet
curview = doc.ActiveView
if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

selection = revit.get_selection()
ele = selection[0]  
category_name = ele.Category.Name

# Creating a dictionary
options_category = {'Structural Columns': DB.BuiltInCategory.OST_StructuralColumns,
    'Walls': DB.BuiltInCategory.OST_Walls,
    'Structural Framing': DB.BuiltInCategory.OST_StructuralFraming,
    'Floors': DB.BuiltInCategory.OST_Floors,
    'Foundation':DB.BuiltInCategory.OST_StructuralFoundation,
    'Shaft Openings':DB.BuiltInCategory.OST_ShaftOpening
}

options_parameter = {'Mark': DB.BuiltInParameter.ALL_MODEL_MARK, # all
    'Comments':DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS , # all
    'Z offset value': DB.BuiltInParameter.Z_OFFSET_VALUE, #only beams
    "Base level":DB.BuiltInParameter.FAMILY_BASE_LEVEL_PARAM ,  #only columns
    "Top level":DB.BuiltInParameter.FAMILY_TOP_LEVEL_PARAM , #only columns
    "Column Base offset":DB.BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM , #only columns
    "Column Top offset":DB.BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM , #only columns
	'Z justification':DB.BuiltInParameter.Z_JUSTIFICATION,  #only beams
	'Elevation at top':DB.BuiltInParameter.STRUCTURAL_ELEVATION_AT_TOP, #beams,floors,foundation
	'Elevation at bottom':DB.BuiltInParameter.STRUCTURAL_ELEVATION_AT_BOTTOM, #beams,floors,foundation
    "Height offset from level":DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM, # floors foundation
    "Base offset":DB.BuiltInParameter.WALL_BASE_OFFSET, # shafts,walls
    "Top offset":DB.BuiltInParameter.WALL_TOP_OFFSET, # shafts,walls
    "Base constraint":DB.BuiltInParameter.WALL_BASE_CONSTRAINT, # shafts,walls
    "Top constraint":DB.BuiltInParameter.WALL_HEIGHT_TYPE, # shafts,walls
    "Unconnected height":DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM, # shafts,walls
    'Reference level':DB.BuiltInParameter.INSTANCE_REFERENCE_LEVEL_PARAM, # beams only
    "Level": DB.BuiltInParameter.LEVEL_PARAM
}

selected_switch_parameter = \
    forms.CommandSwitchWindow.show(sorted(options_parameter.keys()),
                                message='Search for parameter in {0}'.format(options_category.keys()))

target_parameter = options_parameter[selected_switch_parameter]
target_category = options_category[category_name]

valuestring = False
if selected_switch_parameter in ["Z offset value",'Elevation at top','Elevation at bottom',"Height offset from level",
                                "Top offset","Base offset","Unconnected height"]:# double values
    try:
        target_parameter_value = ele.Parameter[target_parameter].AsDouble()
    except:
        forms.alert("Parameter {0} not found in {1}".format(selected_switch_parameter,category_name),exitscript=True)
    param_id = DB.ElementId(target_parameter)
    param_prov = DB.ParameterValueProvider(param_id)
    param_equality = DB.FilterNumericEquals() # equality class for string
    value_rule = DB.FilterDoubleRule(param_prov,param_equality,target_parameter_value,1e-3)
    param_filter = DB.ElementParameterFilter(value_rule)
elif selected_switch_parameter in ["Mark","Comments"] :# string values
    try:
        target_parameter_value = ele.Parameter[target_parameter].AsString()
    except:
        forms.alert("Parameter {0} not found in {1}".format(selected_switch_parameter,category_name),exitscript=True)
    param_id = DB.ElementId(target_parameter)
    param_prov = DB.ParameterValueProvider(param_id)
    param_equality = DB.FilterStringEquals() # equality class for string
    value_rule = DB.FilterStringRule(param_prov,param_equality,target_parameter_value ,True)
    param_filter = DB.ElementParameterFilter(value_rule)
else :#  value Strings
    """This param equality for this usually fails in python, so we go for for loop"""
    valuestring = True
    try:
        target_parameter_value = ele.Parameter[target_parameter].AsValueString()# As value strings got converted to strings
    except:
        forms.alert("Parameter {0} not found in {1}".format(selected_switch_parameter,category_name),exitscript=True)
    elementids = DB.FilteredElementCollector(doc)\
        .OfCategory(target_category)\
        .WhereElementIsNotElementType()\
        .ToElementIds() # select category 
    collect_eleid = []
    for eleid in elementids:
        ele = revit.doc.GetElement(eleid)
        ele_parameter_value = ele.Parameter[target_parameter].AsValueString()
        if ele_parameter_value == target_parameter_value:
            collect_eleid.append(eleid)
    
if not valuestring:
    elementids = DB.FilteredElementCollector(doc)\
            .OfCategory(target_category)\
            .WhereElementIsNotElementType()\
            .WherePasses(param_filter)\
            .ToElementIds() # select category based on the rule

    uidoc.Selection.SetElementIds(elementids) 

else:
    revit.get_selection().set_to(collect_eleid) 
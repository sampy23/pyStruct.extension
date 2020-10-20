__doc__="""This addin searches for elements in active view with same height as the selected element with a tolerance of 300 mm"""
__title__="Height \nMatcher" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import forms

#getting selection from user
__context__ = 'Selection'

doc =__revit__.ActiveUIDocument.Document
uidoc =__revit__.ActiveUIDocument

# make sure active view is not a sheet
curview = doc.ActiveView

if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

selection = revit.get_selection()
for ele in selection:
    category_name = ele.Category.Name
    category_id = ele.Category.Id
    type_id = ele.GetTypeId()
    if category_name == "Walls":
        cparam = ele.Parameter[DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM]
        cparam = cparam.AsDouble()*.3048
        target_parameter =  DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM # FAMILY_TOP_LEVEL_PARAM, FAMILY_BASE_LEVEL_PARAM
    else:
        cparam = ele.Parameter[DB.BuiltInParameter.INSTANCE_LENGTH_PARAM]
        cparam = cparam.AsDouble()*.3048
        target_parameter =  DB.BuiltInParameter.INSTANCE_LENGTH_PARAM # FAMILY_TOP_LEVEL_PARAM, FAMILY_BASE_LEVEL_PARAM
    
param_id = DB.ElementId(target_parameter)
param_prov = DB.ParameterValueProvider(param_id)
param_equality = DB.FilterNumericEquals() # equality class
    
value_rule = DB.FilterDoubleRule(param_prov,param_equality,cparam/0.3048 ,0.5) # 0.5 will give us a tolerance of 304.8 mm
param_filter = DB.ElementParameterFilter(value_rule)

same_cat_elements = \
        DB.FilteredElementCollector(revit.doc, curview.Id)\
          .OfCategoryId(category_id)\
          .WhereElementIsNotElementType()\
          .WherePasses(param_filter)\
          .ToElements()
          
filered_elements = []    

for sim_element in same_cat_elements:
    r_type = sim_element.GetTypeId()
    if r_type == type_id:
        filered_elements.append(sim_element.Id)


if len(filered_elements) > 1:
    revit.get_selection().set_to(filered_elements) 
else:
    forms.alert("Elements with same height as selected object not found!!!")
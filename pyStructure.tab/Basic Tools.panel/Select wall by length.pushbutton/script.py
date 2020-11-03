__doc__="This addin selects walls in the current view whose length equals selected wall's length"
__title__="Wall\nLength" #Title of the extension
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
        cparam = ele.Parameter[DB.BuiltInParameter.CURVE_ELEM_LENGTH]
        cparam = cparam.AsDouble()*.3048
        target_parameter =  DB.BuiltInParameter.CURVE_ELEM_LENGTH # FAMILY_TOP_LEVEL_PARAM, FAMILY_BASE_LEVEL_PARAM
    else:
        print("Sorry!! This addin is only for Walls")
        exit()
    
param_id = DB.ElementId(target_parameter)
param_prov = DB.ParameterValueProvider(param_id)
param_equality = DB.FilterNumericEquals() # equality class
    
value_rule = DB.FilterDoubleRule(param_prov,param_equality,cparam/0.3048 ,1e-3) # 0.5 will give us a tolerance of 304.8 mm
param_filter = DB.ElementParameterFilter(value_rule)

same_cat_elements = \
        DB.FilteredElementCollector(revit.doc,curview.Id)\
          .OfCategoryId(category_id)\
          .WhereElementIsNotElementType()\
          .WherePasses(param_filter)\
          .ToElements()
          
filered_elements = []    

for sim_element in same_cat_elements:
    r_type = sim_element.GetTypeId()
    if r_type == type_id:
        filered_elements.append(sim_element.Id)
        num_walls = len(filered_elements)


if len(filered_elements) > 1:
    revit.get_selection().set_to(filered_elements) 
    forms.alert("{} Walls of length {} m selected!!!".format(num_walls,cparam))
else:
    forms.alert("No other walls of length {} m found!!!".format(cparam))

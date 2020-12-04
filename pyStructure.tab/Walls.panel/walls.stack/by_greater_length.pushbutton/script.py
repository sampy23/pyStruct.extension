__doc__="This addin selects walls in the current view whose length equals selected wall's length"
__title__="Wall\n Greater= Length" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import forms

#getting selection from user
# __context__ = 'Selection'

doc =__revit__.ActiveUIDocument.Document
uidoc =__revit__.ActiveUIDocument
curview = doc.ActiveView # gets current view


if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

length_feet = float(forms.ask_for_string("Enter length in meters"))/0.3048  # sometimes revit interprets 1 > 1.0
target_parameter =  DB.BuiltInParameter.CURVE_ELEM_LENGTH # FAMILY_TOP_LEVEL_PARAM, FAMILY_BASE_LEVEL_PARAM
param_id = DB.ElementId(target_parameter)
param_prov = DB.ParameterValueProvider(param_id)
param_equality = DB.FilterNumericGreaterOrEqual() #greater than equality class
    
value_rule = DB.FilterDoubleRule(param_prov,param_equality,length_feet ,1e-3/0.3048) # tolerance of 1 mm
param_filter = DB.ElementParameterFilter(value_rule)

same_cat_elements = \
        DB.FilteredElementCollector(doc,curview.Id)\
          .OfCategory(DB.BuiltInCategory.OST_Walls)\
          .WhereElementIsNotElementType()\
          .WherePasses(param_filter)\
          .ToElements()
          
filered_elements = []    

for sim_element in same_cat_elements:
    r_type = sim_element.GetTypeId()
    # if r_type == type_id: # for same family type
    filered_elements.append(sim_element.Id)

num_walls = len(filered_elements)
length_m = length_feet * 0.3048

if num_walls >= 1:
    revit.get_selection().set_to(filered_elements) 
    forms.alert("{} Walls of length greater than {} m selected!!!".format(num_walls,length_m))
else:
    forms.alert("No other walls of length greater than {} m found!!!".format(length_m))

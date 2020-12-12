__doc__="This addin selects walls in the current view whose length equals selected wall's length"
__title__="Wall\n Equal Length" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import forms
import sys
import os

dir_name = os.path.dirname(sys.path[0])
sys.path.append(dir_name)
import wallmagic # imported from one directory above by appending the path to sys

doc =__revit__.ActiveUIDocument.Document
uidoc =__revit__.ActiveUIDocument
curview = doc.ActiveView # gets current view

if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

walls = \
        DB.FilteredElementCollector(doc,curview.Id)\
          .OfCategory(DB.BuiltInCategory.OST_Walls)\
          .WhereElementIsNotElementType()\
          .ToElements()
if walls:
    target_parameter =  DB.BuiltInParameter.CURVE_ELEM_LENGTH 
    cur_units = wallmagic.get_type(walls[0],target_parameter)
    length = float(forms.ask_for_string("Enter length in {0}".format(cur_units)))
    length_feet = wallmagic.convert_to_internal(length,cur_units)
    param_filter = wallmagic.filter_rule(target_parameter,DB.FilterNumericEquals,length_feet)
    
    same_cat_elements = \
            DB.FilteredElementCollector(doc,curview.Id)\
            .OfCategory(DB.BuiltInCategory.OST_Walls)\
            .WhereElementIsNotElementType()\
            .WherePasses(param_filter)\
            .ToElements()   
            
    filered_elements = [i.Id for i in same_cat_elements]    
    num_walls = len(filered_elements)
    revit.get_selection().set_to(filered_elements) 

    wallmagic.print_output(num_walls,length,cur_units,"")
else:
    forms.alert("No wall found in current view",
                exitscript=True)

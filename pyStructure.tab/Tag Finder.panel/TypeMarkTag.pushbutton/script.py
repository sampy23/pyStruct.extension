__doc__="This addin searches and picks elements in current view based on input tag defined in Type Mark parameter"
__title__="Type Mark Tag\nFinder" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB, UI
from pyrevit import forms
from pyrevit.framework import List

doc =__revit__.ActiveUIDocument.Document
uidoc =__revit__.ActiveUIDocument

# make sure active view is not a sheet
curview = doc.ActiveView

try:
    if isinstance(curview, DB.ViewSheet):
        forms.alert("You're on a Sheet. Activate a model view please.",
                    exitscript=True)

    flag = 0
    wall_id = []

    target_tag = str(forms.ask_for_string("Enter tag name"))

    if target_tag != "None":
        categorys = [DB.BuiltInCategory.OST_StructuralColumns,DB.BuiltInCategory.OST_Walls,\
                    DB.BuiltInCategory.OST_StructuralFraming,DB.BuiltInCategory.OST_Floors,\
                    DB.BuiltInCategory.OST_StructuralFoundation]
                    
        for cat in categorys:     
            target_category = cat
            target_parameter =  DB.BuiltInParameter.ALL_MODEL_TYPE_MARK

            param_id = DB.ElementId(target_parameter)
            param_prov = DB.ParameterValueProvider(param_id)
            param_equality = DB.FilterStringEquals() # equality class
                
            value_rule = DB.FilterStringRule(param_prov,param_equality,target_tag ,True)
            param_filter = DB.ElementParameterFilter(value_rule)

            elements = DB.FilteredElementCollector(doc, curview.Id)\
                    .OfCategory(target_category)\
                    .WhereElementIsNotElementType()\
                    .WherePasses(param_filter)\
                    .ToElementIds() # select category based on the rule
                    
            if elements:
                uidoc.Selection.SetElementIds(elements) 
                flag = 1
                break
                
        if flag == 0:
            forms.alert("Tag \"{0}\" not found in this view!!!".format(target_tag))
except:# exception to deal with user exit
    pass
__doc__="This addin searches and picks elements in current view based on input tag defined in instance parameter"
__title__="Instance Tag\nFinder" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB, UI
from pyrevit import forms
from pyrevit.framework import List
from collections import defaultdict

doc =__revit__.ActiveUIDocument.Document
uidoc =__revit__.ActiveUIDocument

# make sure active view is not a sheet
curview = doc.ActiveView

if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

param_dic = defaultdict(list)
family_types_elements = defaultdict(list)
try:              
    wall_id = []
    target_tag = str(forms.ask_for_string("Enter tag name")).lower()
    wall_id_list = None

    # Creating a dictionary
    options_category = {'Structural Columns': DB.BuiltInCategory.OST_StructuralColumns,
        'Walls': DB.BuiltInCategory.OST_Walls,
        'Structural Framing': DB.BuiltInCategory.OST_StructuralFraming,
        'Floors': DB.BuiltInCategory.OST_Floors,
        'Foundation':DB.BuiltInCategory.OST_StructuralFoundation
    }

    selected_switch_category = \
        forms.CommandSwitchWindow.show(sorted(options_category.keys()),
            
            message='Search for tag {0} in category:'.format(target_tag))

    target_category = options_category[selected_switch_category]

    # import wall by excluding family types as stored as a collector
    elements=DB.FilteredElementCollector(doc,curview.Id)\
                        .OfCategory(target_category)\
                        .WhereElementIsNotElementType() \
                        .ToElements()
    
    if not elements:
        forms.alert("No elements of {0} found in active view".format(selected_switch_category),exitscript = True)
    for ele in elements:
        family_types_elements[ele.Name].append(ele)

    for k,v in family_types_elements.items():
        param_dic[k].append(v[0].GetOrderedParameters())

    col_para = []
    for k,v in param_dic.items():
        parameters = [j.Definition.Name for i in v for j in i] # parameters are list of lists due to c# lists
        for para in parameters:
            if para not in col_para:
                col_para.append(para)    

    options_parameter = {k:v for k,v in zip(col_para,col_para)}   

    selected_switch_parameter = \
    forms.CommandSwitchWindow.show(sorted(options_parameter.keys()),
                                message='Search for instance parameter')
    target_parameter = options_parameter[selected_switch_parameter]

    for wall in elements:
        para_list = wall.GetParameters(target_parameter)
        if len(para_list) > 1:
            forms.alert("More than one parameter with name {0} found".format(target_parameter),
            exitscript=True)
        try:
            para_value = para_list[0].AsString() #converts object into string)
        except:
            forms.alert("This addin is only for searching text based tags",exitscript=True)

        if para_value: # some time parameter value may not be assigned in walls
            para_value = para_value.lower()
        if para_value == target_tag:
            wall_id.append(wall.Id) # returns element id
            wall_id_list = List[DB.ElementId](wall_id)

    if wall_id:
        revit.get_selection().set_to(wall_id) 
    else :
        forms.alert("No {0} with tag \"{1}\" found!!!".format(target_category,target_tag))
            
except Exception as e: # exception to deal with user exiting form
    print(e)
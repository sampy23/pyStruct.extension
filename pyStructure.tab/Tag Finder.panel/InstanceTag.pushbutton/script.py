__doc__="This addin searches and picks elements in current view based on input tag defined in instance parameter"
__title__="Instance Tag\nFinder" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB, UI
from pyrevit import forms
from pyrevit.framework import List


doc =__revit__.ActiveUIDocument.Document
uidoc =__revit__.ActiveUIDocument

# make sure active view is not a sheet
curview = doc.ActiveView

if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

try:              
    wall_id = []
    target_tag = str(forms.ask_for_string("Enter tag name"))
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


    options_parameter = {'Mark': DB.BuiltInParameter.ALL_MODEL_MARK,
        'Comments':DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS ,
        # 'Wall Number': 'Wall Number'
    }

    selected_switch_parameter = \
        forms.CommandSwitchWindow.show(sorted(options_parameter.keys()),
                                    message='Search for instance parameter')
                                                                    

    target_category = options_category[selected_switch_category]
    target_parameter = options_parameter[selected_switch_parameter]


    # if target_parameter == 'Wall Number': # if parameter is shared
    # # import wall by excluding family types as stored as a collector
    #     wall_collector=DB.FilteredElementCollector(doc,curview.Id)\
    #                         .OfCategory(target_category)\
    #                         .WhereElementIsNotElementType()# Input case sensitive
                            
    #     for wall in wall_collector:
    #         para = wall.LookupParameter(target_parameter)
    #         para = para.AsString() #converts object into string
    #         para = para.lower()
        
    #         if para == target_tag.lower():
    #             wall_id.append(wall.Id) # returns element id
    #             wall_id_list = List[DB.ElementId](wall_id)
    #     try:
    #         uidoc.Selection.SetElementIds(wall_id_list)
    #     except :
    #         forms.alert("Tag \"{0}\" not found!!!".format(target_tag))
    #         pass
            
    if True: 
        param_id = DB.ElementId(target_parameter)
        param_prov = DB.ParameterValueProvider(param_id)
        param_equality = DB.FilterStringEquals() # equality class
            
        value_rule = DB.FilterStringRule(param_prov,param_equality,target_tag ,True)
        param_filter = DB.ElementParameterFilter(value_rule)

        elements = DB.FilteredElementCollector(doc)\
                .OfCategory(target_category)\
                .WhereElementIsNotElementType()\
                .WherePasses(param_filter)\
                .ToElementIds() # select category based on the rule
        if elements:
            uidoc.Selection.SetElementIds(elements) 
        else:
            forms.alert("Tag \"{0}\" not found!!!".format(target_tag))

except: # exception to deal with user exiting form
    pass
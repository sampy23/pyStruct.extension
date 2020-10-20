__doc__="This converts beam joints to \'Disallow\' Join state"
__title__="Disallow\nJoin" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB
from pyrevit import forms
from pyrevit.framework import List

doc =__revit__.ActiveUIDocument.Document
uidoc =__revit__.ActiveUIDocument

# make sure active view is not a sheet
curview = doc.ActiveView

if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

collect_beams = DB.FilteredElementCollector(revit.doc,curview.Id)\
               .OfCategory(DB.BuiltInCategory.OST_StructuralFraming)\
               .WhereElementIsNotElementType()\
               .ToElements()

# collect_beams = revit.get_selection()

with revit.Transaction("All beams disallow join"):
 
    for el in collect_beams:
        if el.GroupId.ToString() == '-1': # to make sure element is not inside a group)
            # el.Location.Move(DB.XYZ(2,0,0))
            # DB.Structure.StructuralFramingUtils.AllowJoinAtEnd(el,0) # 1 for one end and 0 for another end
            # DB.Structure.StructuralFramingUtils.AllowJoinAtEnd(el,1) # 1 for one end and 0 for another end
            DB.Structure.StructuralFramingUtils.DisallowJoinAtEnd(el,0) # 1 for one end and 0 for another end
            DB.Structure.StructuralFramingUtils.DisallowJoinAtEnd(el,1) # 1 for one end and 0 for another end
    
forms.alert("All beams in current view are joined at end now",
            exitscript=False)
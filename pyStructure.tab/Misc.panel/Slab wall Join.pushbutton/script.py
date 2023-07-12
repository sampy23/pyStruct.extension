__doc__="This scripts auto joins floor to wall in that order.\nSelect the wall and isolate the floors to be joined in 3D View."
__title__="Auto join wall,\nfloor_Beta" #Title of the extension
__author__ = "Shahabaz Sha"


#pylint: disable=import-error,invalid-name
from collections import namedtuple

from pyrevit import revit, DB
from pyrevit import forms

doc =__revit__.ActiveUIDocument.Document

# make sure active view is not a sheet
curview = doc.ActiveView

if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

# get selection
selection = revit.get_selection()
if selection:
    ele = selection[0]  # only one element is used. Warn user if more than one selected?
    if len(selection) > 1:
        forms.alert("More than one elements selected.\nSelect one element and continue",exitscript=True)
    elif ele.Category.Name != "Walls":
        forms.alert("Element other than walls selected",exitscript=True)
else:
    forms.alert("No wall selected!!! Atleast one wall to be selected",exitscript=True)

floorids = DB.FilteredElementCollector(doc, curview.Id)\
                .OfCategory(DB.BuiltInCategory.OST_Floors)\
                .WhereElementIsNotElementType()\
                .ToElementIds()

with DB.Transaction(doc, 'Join floors') as t:
    try:
        t.Start()
        for floorid in floorids:
            floor = revit.doc.GetElement(floorid) # convert id to element
            DB.JoinGeometryUtils.JoinGeometry(doc,ele,floor)
            DB.JoinGeometryUtils.SwitchJoinOrder(doc,floor,ele)
        t.Commit()
    except Exception as e:
        forms.alert(str(e),title="Error",ok = True,yes = False,no = False)
        t.RollBack()
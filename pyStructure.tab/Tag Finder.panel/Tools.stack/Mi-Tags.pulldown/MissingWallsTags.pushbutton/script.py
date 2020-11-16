__doc__="This scripts selects Wall with no associated tags in current view."
__title__="Missing Wall\nTag Finder" #Title of the extension
__author__ = "Shahabaz Sha"


#pylint: disable=import-error,invalid-name
from collections import namedtuple

from pyrevit import revit, DB
from pyrevit import forms


Taggable = namedtuple('Taggable', ['tag_type', 'element_type'])


doc =__revit__.ActiveUIDocument.Document

# make sure active view is not a sheet
curview = doc.ActiveView

if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)


target = Taggable(
    tag_type=DB.BuiltInCategory.OST_WallTags,
    element_type=DB.BuiltInCategory.OST_Walls
    )
selection = revit.get_selection()

# collect target elements and tags in view
target_tags = DB.FilteredElementCollector(revit.doc, curview.Id)\
            .OfCategory(target.tag_type)\
            .WhereElementIsNotElementType()\
            .ToElementIds()

target_elements = DB.FilteredElementCollector(revit.doc, curview.Id)\
        .OfCategory(target.element_type)\
        .WhereElementIsNotElementType()\
        .ToElementIds()

tagged_elements = []
untagged_elements = []
for eltid in target_tags:
    elt = revit.doc.GetElement(eltid)
    if elt.TaggedLocalElementId != DB.ElementId.InvalidElementId:
        tagged_elements.append(elt.TaggedLocalElementId.IntegerValue)

for elid in target_elements:
    el = revit.doc.GetElement(elid)
    if el.Id.IntegerValue not in tagged_elements:
        untagged_elements.append(elid)

if untagged_elements and tagged_elements:
    selection.set_to(untagged_elements)
elif not untagged_elements and tagged_elements:
    forms.alert('All walls in current view have tags.')
elif not tagged_elements:
    forms.alert('No walls have tags.')

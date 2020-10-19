__doc__="This addin selects Walls with duplicate tags in current view."
__title__="Duplicate Wall \nTag Finder" #Title of the extension
__author__ = "Shahabaz Sha"

#pylint: disable=import-error,invalid-name
from collections import namedtuple,Counter
from pyrevit import revit, DB
from pyrevit import forms

Taggable = namedtuple('Taggable', ['tag_type', 'element_type'])

# make sure active view is not a sheet
curview = revit.activeview
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

dupes_id = [item for item, count in Counter(tagged_elements).items() if count > 1]

if dupes_id:
    selection.set_to(dupes_id)
else:
    forms.alert('No walls with duplicate tags found')

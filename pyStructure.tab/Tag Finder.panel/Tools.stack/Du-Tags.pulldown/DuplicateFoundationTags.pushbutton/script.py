__doc__="This scripts selects Foundation withs duplicate tags in current view."
__title__="Duplicate Foundation\nTag Finder" #Title of the extension
__author__ = "Shahabaz Sha"

#pylint: disable=import-error,invalid-name
from collections import namedtuple,Counter
from pyrevit import revit, DB
from pyrevit import forms,HOST_APP
from System.Collections.Generic import List

Taggable = namedtuple('Taggable', ['tag_type', 'element_type'])


doc =__revit__.ActiveUIDocument.Document

# make sure active view is not a sheet
curview = doc.ActiveView

if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

target = Taggable(
    tag_type=DB.BuiltInCategory.OST_StructuralFoundationTags, 
    element_type=DB.BuiltInCategory.OST_StructuralFoundation
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
    if HOST_APP.is_newer_than(2023):
        if elt.GetTaggedLocalElementIds() != DB.ElementId.InvalidElementId:
            tagged_elements.append(List[DB.ElementId](elt.GetTaggedLocalElementIds())[0].IntegerValue)
    elif HOST_APP.is_newer_than(2022, or_equal=True):
        if elt.GetTaggedLocalElementIds() != DB.ElementId.InvalidElementId:
            tagged_elements.append(List[DB.ElementId](elt.GetTaggedLocalElementIds())[0].IntegerValue)
    else:
        if elt.TaggedLocalElementId != DB.ElementId.InvalidElementId:
            tagged_elements.append(elt.TaggedLocalElementId.IntegerValue)   

dupes_id = [item for item, count in Counter(tagged_elements).items() if count > 1]

if dupes_id:
    selection.set_to(dupes_id)
else:
    forms.alert('No Foundation with duplicate tags found')

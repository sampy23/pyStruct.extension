__doc__="This addin selects Columns with no associated tags in current view."
__title__="Missing Column\nTag Finder" #Title of the extension
__author__ = "Shahabaz Sha"

#pylint: disable=import-error,invalid-name
from collections import namedtuple
from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import HOST_APP

from System.Collections.Generic import List

Taggable = namedtuple('Taggable', ['tag_type', 'element_type'])

doc =__revit__.ActiveUIDocument.Document

# make sure active view is not a sheet
curview = doc.ActiveView

if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

target = Taggable(
    tag_type=DB.BuiltInCategory.OST_StructuralColumnTags,
    element_type=DB.BuiltInCategory.OST_StructuralColumns
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
            tagged_elements.append(List[DB.ElementId](elt.GetTaggedLocalElementIds())[0].Value)
    elif HOST_APP.is_newer_than(2022, or_equal=True):
        if elt.GetTaggedLocalElementIds() != DB.ElementId.InvalidElementId:
            tagged_elements.append(List[DB.ElementId](elt.GetTaggedLocalElementIds())[0].IntegerValue)
    else:
        if elt.TaggedLocalElementId != DB.ElementId.InvalidElementId:
            tagged_elements.append(elt.TaggedLocalElementId.IntegerValue)

for elid in target_elements:
    el = revit.doc.GetElement(elid)
    if el.Id.IntegerValue not in tagged_elements:
        untagged_elements.append(elid)

if untagged_elements and tagged_elements:
    selection.set_to(untagged_elements)
elif not untagged_elements and tagged_elements:
    forms.alert('All columns in current view have tags.')
elif not tagged_elements:
    forms.alert('No columns in current view have tags.')

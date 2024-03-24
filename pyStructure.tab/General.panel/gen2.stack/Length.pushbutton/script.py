__doc__="This addin calculates total length of selected items"
__title__="Total\nLength" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB, UI
from pyrevit import forms
from pyrevit import HOST_APP
import sys
import os

dir_name = os.path.dirname(sys.path[0])
sys.path.append(dir_name)
import genunits # imported from one directory above by appending the path to sys

# Getting selection from user
__context__ = 'Selection'

doc =__revit__.ActiveUIDocument.Document

# make sure active view is not a sheet
curview = doc.ActiveView
if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

selection = revit.get_selection() #get selection
builtin_enum =DB.BuiltInParameter.CURVE_ELEM_LENGTH
doc_units = revit.doc.GetUnits() #get document units
if HOST_APP.is_newer_than(2021):
    length_ut = doc_units.GetFormatOptions(DB.SpecTypeId.Length)
    unit_type = length_ut.GetUnitTypeId()
else:
    length_ut = doc_units.GetFormatOptions(DB.UnitType.UT_Length)
    unit_type = length_ut.DisplayUnits

unit_text = genunits.revit_unit(unit_type,quant_type = 'length') # get the unit in text form
total_quant,warning_count = genunits.total(selection,builtin_enum,unit_type)

if total_quant:
    formatted_total_quant = str(total_quant) + " " + unit_text
    if warning_count: # if some selected element has no associated parameter
        forms.alert("Total length is {0} but {1} items didnot had any associated length parameter ".\
                                                                    format(formatted_total_quant,warning_count),exitscript=True)
    else:
        forms.alert("Total length is {0}".format(formatted_total_quant,warning_count),
                exitscript=True)
else:
    forms.alert("No value found for selected item",exitscript=True)
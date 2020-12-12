__doc__="This addin selects walls in the current view whose length equals selected wall's length"
__title__="Wall\n Greater= Length" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit.framework import List
from pyrevit import revit, DB
from pyrevit import forms
import sys
import os

dir_name = os.path.dirname(sys.path[0])
sys.path.append(dir_name)
import wallmagic # imported from one directory above by appending the path to sys

doc =__revit__.ActiveUIDocument.Document
uidoc =__revit__.ActiveUIDocument
curview = doc.ActiveView # gets current view

if isinstance(curview, DB.ViewSheet):
    forms.alert("You're on a Sheet. Activate a model view please.",
                exitscript=True)

wallmagic.action(doc,curview,DB.FilterNumericGreaterOrEqual,">=")
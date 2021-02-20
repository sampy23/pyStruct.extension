__doc__= """Duplicate selected family type under a category"""
__title__="Duplicate\nFamily Typed" #Title of the extension

from pyrevit import revit, DB
from pyrevit import forms
import random

# Getting selection from user
__context__ = 'Selection'

doc =__revit__.ActiveUIDocument.Document

elements = revit.get_selection() # get selection of familytypes

if elements: # if elements under different category are selected null is returned

    cat_id = list(set([ele.Category.Id for ele in elements if ele.Category]))[0]

    element_types = DB.FilteredElementCollector(doc).OfCategoryId(cat_id).WhereElementIsElementType().ToElements()

    num = int(forms.ask_for_string("Enter number of duplicates"))
    name_list = [DB.Element.Name.__get__(ele) for ele in element_types]

    with DB.Transaction(doc, 'Change Name') as t:
        try:
            t.Start()
            duplicate_counter = 1
            for ele in elements:
                name = DB.Element.Name.__get__(ele)
                for i in range(num):
                    new_name = name + " ({})".format(duplicate_counter)
                    if new_name not in name_list:
                        if DB.NamingUtils.IsValidName(new_name):
                            ele.Duplicate(new_name)
                        else:
                            forms.alert("Couldnot duplicate family type {}".format(name),
                                exitscript=False)
                    else:
                        new_name = name + "({}{})".format(duplicate_counter,random.randint(1,1000))
                        if DB.NamingUtils.IsValidName(new_name):
                            ele.Duplicate(new_name)
                        else:
                           forms.alert("Couldnot duplicate family type {}".format(name),
                                exitscript=False)
                    duplicate_counter += 1
            t.Commit()

        except Exception as e:
            forms.alert(str(e),title="Error",ok = True,yes = False,no = False)
            t.RollBack()
        else:
            forms.alert("Process complete",
                        exitscript=False)
else:
    forms.alert("Only family types under one category can be duplicated",
                exitscript=True)
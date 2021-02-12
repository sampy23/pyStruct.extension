__doc__= """Duplicate selected family type under a category"""
__title__="Duplicate\nView" #Title of the extension

from pyrevit import revit, DB
from pyrevit import forms

# Getting selection from user
__context__ = 'Selection'

doc =__revit__.ActiveUIDocument.Document

elements = revit.get_selection() # get selection of familytypes

if elements:
    num = int(forms.ask_for_string("Enter number of views"))
    with DB.Transaction(doc, 'Change Name') as t:
        try:
            t.Start()
            for ele in elements:
                name = DB.Element.Name.__get__(ele)
                duplicate_counter = 1
                for i in range(num):
                    new_name = name + " ({})".format(duplicate_counter)
                    ele.Duplicate(new_name)
                    duplicate_counter += 1
            t.Commit()
        except Exception as e:
            forms.alert(str(e),title="Error",ok = True,yes = False,no = False)
            t.RollBack()
        else:
            forms.alert("Successfully Duplicated selected family types",
                        exitscript=False)
else:
    forms.alert("Only family types under one category can be duplicated",
                exitscript=True)
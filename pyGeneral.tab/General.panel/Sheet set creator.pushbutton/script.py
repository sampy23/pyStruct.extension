__doc__="This addin creates sheet based on selection of view or sheets by user"
__title__="Sheet Set\nCreator" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import framework
from pyrevit.framework import Drawing
from pyrevit import forms
from pyrevit import revit, DB

# Getting selection from user
__context__ = 'Selection'

doc =__revit__.ActiveUIDocument.Document

print_mgr = revit.doc.PrintManager
print_settings = [revit.doc.GetElement(x) for x in revit.doc.GetPrintSettingIds()] #List of print settings like A1,A3,..

selected_print_setting = print_mgr.PrintSetup.InSession #If no print setting defined we can use default <in-session>

printers = list(Drawing.Printing.PrinterSettings.InstalledPrinters) # list of printers like Adobe PDF,Blubeam PDF
printers = sorted(printers)
selected_printer = printers[0]

select_sheets = revit.get_selection() # get selection of sheets
sheetsetname = forms.ask_for_string("Sheet set name",prompt='Enter Name of new sheet set',title="Set creator")

if sheetsetname == "" or  sheetsetname == "Sheet set name":
    sheetsetname = "Default set-1"

with DB.Transaction(doc, 'Add range') as t:
    t.Start()
    print_mgr.PrintSetup.CurrentPrintSetting = selected_print_setting
    print_mgr.SelectNewPrintDriver(selected_printer)
    print_mgr.PrintRange = DB.PrintRange.Select
    t.Commit()
    # add non-printable char in front of sheet Numbers
    # to push revit to sort them per user
sheet_set = DB.ViewSet()
original_sheetnums = []
with DB.Transaction(doc,'Add Sheets') as tg:
    tg.Start()
    for rvtsheet in select_sheets:
        try:
            sheet_set.Insert(rvtsheet)
        except Exception as e:
            forms.alert(str(e),exitscript=True)
    tg.Commit()

# Collect existing sheet sets
cl = DB.FilteredElementCollector(revit.doc)
viewsheetsets = cl.OfClass(framework.get_type(DB.ViewSheetSet))\
                    .WhereElementIsNotElementType()\
                    .ToElements()

all_viewsheetsets = {vss.Name: vss for vss in viewsheetsets}
with revit.Transaction('Remove Previous Print Set') as t:
    # Delete existing matching sheet set
    if sheetsetname in all_viewsheetsets:
        print_mgr.ViewSheetSetting.CurrentViewSheetSet = \
            all_viewsheetsets[sheetsetname]
        print_mgr.ViewSheetSetting.Delete()

with revit.Transaction('Create Print Set') as t:
    try:
        viewsheet_settings = print_mgr.ViewSheetSetting
        viewsheet_settings.CurrentViewSheetSet.Views = sheet_set
        viewsheet_settings.SaveAs(sheetsetname)
    except Exception as viewset_err:
        print(viewset_err)
        raise viewset_err
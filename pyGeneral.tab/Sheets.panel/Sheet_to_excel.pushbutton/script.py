__doc__="This addin creates reads and write data from excel inorder to create sheets"
__title__="Sheet To\nExcel" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import forms
import Autodesk.Revit.DB as DB

import xlsxwriter
import xlrd
import sys
import os
import subprocess
import shutil
import datetime
import traceback

doc =__revit__.ActiveUIDocument.Document

global dest
global sheet_num 
global sheet_name 
global sheet_group 
global sheet_approved 
global sheet_designed 
global sheet_checked 
global sheet_drawn 
global sheet_issue 
global dest

sheet_num = []
sheet_name = []
sheet_group = []
sheet_approved = []
sheet_designed = []
sheet_checked = []
sheet_drawn = []
sheet_issue = []

def read_sheets(sheet_group_para):
    """Asks for sheets from revit"""
    exist_sheets = DB.FilteredElementCollector(doc) \
                                .OfClass(DB.ViewSheet) \
                                .WhereElementIsNotElementType() \
                                .ToElements()
    for sheet in exist_sheets:
        sheet_num.append(sheet.SheetNumber)
        sheet_name.append(sheet.Name)
        sheet_group.append(sheet.LookupParameter(sheet_group_para).AsString())
        sheet_approved.append(sheet.Parameter[DB.BuiltInParameter.SHEET_APPROVED_BY].AsString())
        sheet_designed.append(sheet.Parameter[DB.BuiltInParameter.SHEET_DESIGNED_BY].AsString())
        sheet_checked.append(sheet.Parameter[DB.BuiltInParameter.SHEET_CHECKED_BY].AsString())
        sheet_drawn.append(sheet.Parameter[DB.BuiltInParameter.SHEET_DRAWN_BY].AsString())
        sheet_issue.append(sheet.Parameter[DB.BuiltInParameter.SHEET_ISSUE_DATE].AsString())

def int_str(cell_val):
    """A helper function to convert floating values of excel. Excel stores every number as a float."""
    if isinstance(cell_val,str):
        if  ((cell_val[0] and cell_val[-1]) == "\"") or ((cell_val[0] and cell_val[-1]) == "\'") :
            cell_val = cell_val[1:] # removing first double quote
            cell_val = cell_val[:-1] # removing last double quote
        return cell_val
    else:
        cell_val = str(cell_val)
        list_cell_val = cell_val.split(".") 
        if list_cell_val[-1] == "0": # here we assume that user never wants a sheet number named "xxx.0".
        #                             # if he wants so, he is encouraged to input values in double quote
            list_cell_val.pop(-1)   
            cell_val = "".join(list_cell_val)
            return cell_val

def max_width(in_list):
    """Maximum width of contents in a column"""
    widths = []
    if in_list: 
        for x in in_list:
            if x: #to deal with none
                widths.append(len(x))
            else:
                widths.append(0)
        return max(widths) + 5
    else: # if there is no sheets
        return 12 + 5

def _create_sheet(inpu,t,sheet_group_para,_titleblock_id):
    exist_sheets = DB.FilteredElementCollector(doc) \
                                .OfClass(DB.ViewSheet) \
                                .WhereElementIsNotElementType() \
                                .ToElements()
    sheet_num = [x.SheetNumber for x in exist_sheets]
    if inpu[0]  not in sheet_num:
        new_phsheet = DB.ViewSheet.Create(doc,
                                    _titleblock_id)
        new_phsheet.SheetNumber = inpu[0]
        new_phsheet.Name = int_str(inpu[1])                              
        new_phsheet.LookupParameter(sheet_group_para).Set(int_str(inpu[2]))
        new_phsheet.Parameter[DB.BuiltInParameter.SHEET_APPROVED_BY].Set(inpu[3])
        new_phsheet.Parameter[DB.BuiltInParameter.SHEET_DESIGNED_BY].Set(inpu[4])
        new_phsheet.Parameter[DB.BuiltInParameter.SHEET_CHECKED_BY].Set(inpu[5])
        new_phsheet.Parameter[DB.BuiltInParameter.SHEET_DRAWN_BY].Set(inpu[6])
        new_phsheet.Parameter[DB.BuiltInParameter.SHEET_ISSUE_DATE].Set(inpu[7])
    else:
        sheet_index = sheet_num.index(inpu[0])
        sheet = exist_sheets[sheet_index]
        sheet.Name = str(inpu[1])                               
        sheet.LookupParameter(sheet_group_para).Set(str(inpu[2]))
        sheet.Parameter[DB.BuiltInParameter.SHEET_APPROVED_BY].Set(inpu[3])
        sheet.Parameter[DB.BuiltInParameter.SHEET_DESIGNED_BY].Set(inpu[4])
        sheet.Parameter[DB.BuiltInParameter.SHEET_CHECKED_BY].Set(inpu[5])
        sheet.Parameter[DB.BuiltInParameter.SHEET_DRAWN_BY].Set(inpu[6])
        sheet.Parameter[DB.BuiltInParameter.SHEET_ISSUE_DATE].Set(inpu[7])

def write_to_excel():
    """Option to write to excel by reading existing sheets groups from excel"""
    
    sheet_group_para = str(forms.ask_for_string("Sheet Group",prompt='Enter unique sheet group parameter name',title=dest))
    title = ["Sheet Number","Sheet Name",sheet_group_para,"Approved By","Designed By","Reviewed By","Drawn By","Date"]

    try:
        workbook = xlsxwriter.Workbook(dest)
        worksheet = workbook.add_worksheet() 
        # writing title into excel
        for i,v in enumerate(title):
            worksheet.write(0,i,v)
        read_sheets(sheet_group_para)
        row = 1
        zipped_lists = zip(sheet_num,sheet_name,sheet_group,sheet_approved,sheet_designed,sheet_checked,sheet_drawn,sheet_issue)
        sorted_zipped_lists = sorted(zipped_lists)
        for inpu in sorted_zipped_lists:
            worksheet.write(row, 0, inpu[0])
            worksheet.write(row, 1, inpu[1])
            worksheet.write(row, 2, inpu[2])
            worksheet.write(row, 3, inpu[3])
            worksheet.write(row, 4, inpu[4])
            worksheet.write(row, 5, inpu[5])
            worksheet.write(row, 6, inpu[6])
            worksheet.write(row, 7, inpu[7])
            row += 1
        
        column=0
        for col in [sheet_num,sheet_name,sheet_group,sheet_approved,sheet_designed,sheet_checked,sheet_drawn,sheet_issue]:
            width = max_width(col)
            worksheet.set_column(column, column, width) #( first column,last_column,width)
            column += 1

        workbook.close()
        open_excel()

    except Exception as ex:
        error = str(ex)
        if "len() of unsized object" in error:
            forms.alert("{0} parameter has no value".format(sheet_group_para),
                        exitscript=True)
        elif "[Errno 32] The process cannot access the file " in error:
            forms.alert("Close the open excel Sheet_groups and try again",
              exitscript=True)
        elif "'NoneType' object has no attribute 'AsString'" in error:
            forms.alert("Sheet Group parameter not defined",
              exitscript=True)
        else:
            print(traceback.format_exc())

def open_excel():
    """Option to open excel"""
    p = subprocess.Popen(["start","EXCEL.EXE",dest],shell=True)
    p.communicate()

try:
    os.chdir(sys.path[0])
    src = "Sheet_groups.xlsx"
    dest = os.path.join(os.path.expanduser("~/Documents"),src)
    if os.path.exists(dest): # if file already exits in destination no need to copy and overwrite
        pass
    else:
        shutil.copy2(src, dest)
    write_to_excel() # function call

except:
    pass
__doc__="This addin creates renames family types based on parameter value"
__title__="Family\nType Renamer" #Title of the extension
__author__ = "Shahabaz Sha"

# dependencies
from pyrevit import forms
import Autodesk.Revit.DB as DB
import sys
from collections import namedtuple,defaultdict
import operator

xaml_file_name = "ui.xaml"

Name_class = namedtuple('Dummy', ['Name'])
Param_class = namedtuple('Parameters', ['Name',"Index"])

doc =__revit__.ActiveUIDocument.Document

class PrintSheetsWindow(forms.WPFWindow):
    def __init__(self):
        forms.WPFWindow.__init__(self, xaml_file_name)
        self.dict_cat_id = {}
        self.category_cb.ItemsSource = self._get_cat_list()
        self.category_cb.SelectedIndex = 0
        self.rename_button.IsEnabled = False 

    @property
    def selected_category(self):
        return self.category_cb.SelectedItem

    @property
    def selected_family(self):
        return self.family_cb.SelectedItem

    @property
    def selected_param_0(self):
        return self.param_0.SelectedItem

    @property
    def selected_param_1(self):
        return self.param_1.SelectedItem

    @property
    def selected_param_2(self):
        return self.param_2.SelectedItem

    @property
    def selected_param_3(self):
        return self.param_3.SelectedItem

    @property
    def rename_list(self):
        return self.rename_lb.ItemsSource

    @rename_list.setter
    def rename_list(self, value):
        self.rename_lb.ItemsSource = value

    # private utils
    def _get_cat_list(self):
        doc_elements = DB.FilteredElementCollector(doc)\
                        .WhereElementIsElementType()\
                        .ToElements()
        cat_ids = set([ele.Category.Id for ele in doc_elements if ele.Category])
        for i in cat_ids:
            if DB.Category.GetCategory(doc,i):
                self.dict_cat_id[DB.Category.GetCategory(doc,i)] = i
        return sorted(self.dict_cat_id.keys(),key = operator.attrgetter("Name")) # sorting list of classes based on attr

    def _setup_family(self):
        self.family_cb.ItemsSource = sorted([Name_class(i) for i in self.family_ele_dict.keys()],\
                                            key = operator.attrgetter("Name")) # sorting list of classes based on attr
        self.family_cb.SelectedIndex = 0

    def _setup_param(self):
        self.param_0.ItemsSource = self.parameters
        self.param_1.ItemsSource = self.parameters
        self.param_2.ItemsSource = self.parameters
        self.param_3.ItemsSource = self.parameters
        
        self.param_0.SelectedIndex = 1
        self.param_1.SelectedIndex = 0
        self.param_2.SelectedIndex = 0
        self.param_3.SelectedIndex = 0

    # event handlers
    def category_changed(self, sender, args):
        self.cat_id = self.dict_cat_id[self.selected_category]
        elements = DB.FilteredElementCollector(doc)\
                        .OfCategoryId(self.cat_id)\
                        .WhereElementIsElementType()\
                        .ToElements() 
        
        families = [ele.FamilyName for ele in elements]

        self.family_ele_dict = defaultdict(list)
        for k,v in zip(families,elements):
            self.family_ele_dict[k].append(v)

        self._setup_family()
        self.rename_list = [] # clear the list view in GUI when category changed
        self.rename_button.IsEnabled = False 


    def family_changed(self, sender, args):
        if self.selected_family:
            self.rename_list = [] # clear the list view in GUI when category changed
            self.rename_button.IsEnabled = False 
            self.parameters = [Param_class(Name = j.Definition.Name,Index = i+1) 
                                            for i,j in enumerate(self.family_ele_dict[self.selected_family.Name][0].
                                            GetOrderedParameters())] # assuming parameter of one family has same parameters
                                            # i+1 to deal with next line insertion
            self.parameters.insert(0,Param_class(Name = None,Index = 0))
            self._setup_param()


    def get_param_value(self,param_value):
        if param_value:
            storage_type = param_value.StorageType
            if storage_type == DB.StorageType.Double:
                return str(param_value.AsValueString())
            elif storage_type == DB.StorageType.String:
                return str(param_value.AsString())
            elif storage_type == DB.StorageType.Integer:
                return str(param_value.AsInteger())
            elif storage_type == DB.StorageType.ElementId:
                return str(param_value.AsElementId().ToString())
            else:
                return ""
        else:
            return ""

    def rename_format(self,send,args):
        self.name_list = []
        duplicate_counter = 0
        entered = False
        for ele in self.family_ele_dict[self.selected_family.Name]: # iterate through element in selected family type
            if ele.GetParameters(self.parameters[self.selected_param_0.Index].Name):
                param_0 = ele.GetParameters(self.parameters[self.selected_param_0.Index].Name)[0] 
                                                        # using index of parameter list to deal with duplicates 
                                                        # if in future this program extended for instance parameters
            else:
                param_0 = None

            if ele.GetParameters(self.parameters[self.selected_param_1.Index].Name):
                param_1 = ele.GetParameters(self.parameters[self.selected_param_1.Index].Name)[0]
            else:
                param_1 = None

            if ele.GetParameters(self.parameters[self.selected_param_2.Index].Name):
                param_2 = ele.GetParameters(self.parameters[self.selected_param_2.Index].Name)[0]
            else:
                param_2 = None

            if  ele.GetParameters(self.parameters[self.selected_param_3.Index].Name):
                param_3 = ele.GetParameters(self.parameters[self.selected_param_3.Index].Name)[0]
            else:
                param_3 = None
            
            # name formating
            new_name = [self.get_param_value(param_0) + " - " + self.get_param_value(param_1),\
                                                    self.get_param_value(param_2), self.get_param_value(param_3)]
            new_name = " X ".join([i for i in new_name if i!= ""])
            new_name = new_name.replace("None","")
            # string cleanup
            if new_name[-3:] == " - ": 
                new_name = new_name[:-3] # removes trailling -
            if new_name[:3] == " - ": 
                new_name = new_name[3:] # removes leading -
            if new_name[:3] == " X ":
                new_name = new_name[3:] # removes leading X

            if new_name not in self.name_list:
                self.name_list.append(new_name)
            else: 
                if len(new_name):# enter if new_name is not an empty string: for some reason elif "" fails in some cases
                    duplicate_counter += 1
                    new_name = new_name  + " ({0})".format(duplicate_counter)
                    self.name_list.append(new_name)

            if (len(self.name_list) > 50) and not entered:
                if not forms.alert('More than 50 element type found.'
                                    'Try purging {0} to reduce risk of program crashing.\n'
                                    'It is a good idea to have a backup before continuing.\n\n'
                                    'Are sure you want to continue?'
                                    .format(self.selected_category.Name),
                                    title="Continue?",ok=False, yes=True, no=True):
                    self.Close()
                    sys.exit()
                else:
                    entered = True
        
        self.rename_list = [Name_class(Name=i) for i in sorted(self.name_list)]
        self.rename_button.IsEnabled = True 

    def rename(self,send,args):
        renamed = True
        with DB.Transaction(doc, 'Change Name') as t:
            try:
                t.Start()
                for ele,name in zip(self.family_ele_dict[self.selected_family.Name],self.name_list):
                    if name: # sometime name may be empty which can open a can of worms
                        ele.Name = name
                    else:
                        renamed = False
                t.Commit()
            except Exception as e:
                forms.alert(str(e),title="Error",ok = True,yes = False,no = False)
                t.RollBack()
                self.Close()
            else:
                if renamed:
                    forms.alert('All {0} successfully renamed'
                                        .format(self.selected_family.Name),
                                        ok=True, yes=False, no=False)
                else:
                    forms.alert('Some types of  {0} not renamed'
                                        .format(self.selected_family.Name),
                                        ok=True, yes=False, no=False)
# let's show the window (modal)
PrintSheetsWindow().ShowDialog()
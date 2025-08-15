__doc__="This addin finds coordinate of all piles/columns in m"
__title__="Pile/Column\nCoordinates" #Title of the extension
__author__ = "Shahabaz Sha"

from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import HOST_APP
import math
import sys

def rotate(x,y,theta):
    rotated = [math.cos(theta) * x + math.sin(theta) * y,-math.sin(theta)*x + math.cos(theta)*y] # we are multiplying base point coordinates (XYZ)
                                                                                                 # with inverse of rotational matrix to get rotated coordinates or survey point coordinates
    return rotated
def find_cord(x,y,theta,bp_x,bp_y):
    rotated = rotate(x,y,theta)
    bp_cord = [bp_x,bp_y]
    result = [i for i in [rotated[0] + bp_cord[0],rotated[1] + bp_cord[1]]] # then we will add this with base point coordinates to get output. sbz
    return (result[1],result[0])

doc =__revit__.ActiveUIDocument.Document
app = doc.Application
                 
X = []
Y = []

sharedParameterFile = app.OpenSharedParameterFile()
if sharedParameterFile:
    myGroups = sharedParameterFile.Groups
else:
    forms.alert('Shared parameter file doesnot exist',
        ok=True, yes=False, no=False,exitscript= True)

# Creating a dictionary
options_category = {'Structural Columns': DB.BuiltInCategory.OST_StructuralColumns,
    'Foundation':DB.BuiltInCategory.OST_StructuralFoundation
}

selected_switch_category = \
    forms.CommandSwitchWindow.show(sorted(options_category.keys()),
        
        message='Search for tag  in category:')

target_category = options_category[selected_switch_category]

selection = DB.FilteredElementCollector(doc)\
                    .OfCategory(target_category)\
                    .WhereElementIsNotElementType() \
                    .ToElements()

try:
    myGroup = myGroups.Create( "pystructure" ) # create new group
except Exception as e:
    if len(str(e)):
        forms.alert(str(e),title="Error",ok = True,yes = False,no = False)
    else:# Parameter group already exists
        myGroup = myGroups.get_Item("pystructure") # if new group cant be created and it already exist retrieve it.
        #forms.alert("Parameter group already exists",title="Error",ok = True,yes = False,no = False)
else:
    if HOST_APP.is_newer_than(2021):
        option_1 = DB.ExternalDefinitionCreationOptions("North_Coord", DB.SpecTypeId.Length)
        option_2 = DB.ExternalDefinitionCreationOptions("East_Coord", DB.SpecTypeId.Length)
    else:
        option_1 = DB.ExternalDefinitionCreationOptions("North_Coord", DB.ParameterType.Length)
        option_2 = DB.ExternalDefinitionCreationOptions("East_Coord", DB.ParameterType.Length)   

    option_1.UserModifiable = False
    option_1.Description = "Coordinates of piles/column"
    option_2.UserModifiable = False
    option_2.Description = "Coordinates of piles/column"

    myDefinition_ProductDate = myGroup.Definitions.Create(option_1)
    myDefinition_ProductDate = myGroup.Definitions.Create(option_2)

#get the category and build a category set. 
builtInCategory = DB.BuiltInCategory.OST_StructuralFoundation
# create a categroy set incase you need to add to multiple Categories
cats = app.Create.NewCategorySet()
# Add Categories to Category Set. 
cats.Insert(doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_StructuralFoundation))
cats.Insert(doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_StructuralColumns))

#txt parameter name
externalDefinition_1 = myGroup.Definitions.get_Item("North_Coord")
externalDefinition_2 = myGroup.Definitions.get_Item("East_Coord")

# Create shared instance parameter. 
# Start transaction in Revit.
with DB.Transaction(doc, 'Add Parameter') as t:
    try:
        t.Start()
        # Create the new shared parameter 
        newInstanceBinding = app.Create.NewInstanceBinding(cats)
        # insert the new parameter into your project. 
        if HOST_APP.is_newer_than(2021):
            doc.ParameterBindings.Insert(externalDefinition_1, newInstanceBinding, DB.GroupTypeId.Length)
            doc.ParameterBindings.Insert(externalDefinition_2, newInstanceBinding, DB.GroupTypeId.Length) 

        else:
            doc.ParameterBindings.Insert(externalDefinition_1, newInstanceBinding, DB.BuiltInParameterGroup.PG_LENGTH)
            doc.ParameterBindings.Insert(externalDefinition_2, newInstanceBinding, DB.BuiltInParameterGroup.PG_LENGTH) 
 
        # If shared parameter already exist in project, advice user to avoid duplication
        for element in selection:
            params_1 = element.GetParameters("North_Coord")
            params_2 = element.GetParameters("East_Coord")
            if (len(params_1) > 1 or len(params_1) >1) :
                forms.alert('Remove North_Coord & East_Coord from Project parameters and try again',
                    ok=True, yes=False, no=False,exitscript=True)

        # complete transaction
        # set back original shared paramter. 
        t.Commit()
    except Exception as e:
        t.RollBack()
        forms.alert(str(e),title="Error",ok = True,yes = False,no = False)
        sys.exit()

for ele in selection:
    # for foundation and columns
    try:
        x = ele.Location.Point.X
        y = ele.Location.Point.Y
        z = ele.Location.Point.Z
        X.append(x)
        Y.append(y)
    except: # to ignore rafts, pile caps and other unwanted foundations
        X.append("")
        Y.append("")

locations = DB.FilteredElementCollector(doc).OfClass(DB.BasePoint).ToElements()
for loc in locations:
    if loc.IsShared:# this is surveypoint
        sp_nsouth = loc.get_Parameter(DB.BuiltInParameter.BASEPOINT_NORTHSOUTH_PARAM).AsDouble()*.3048
        sp_ewest = loc.get_Parameter(DB.BuiltInParameter.BASEPOINT_EASTWEST_PARAM).AsDouble()*.3048
        sp_elev = loc.get_Parameter(DB.BuiltInParameter.BASEPOINT_ELEVATION_PARAM).AsDouble()*.3048
    else: # this is basepont
        if loc.get_Parameter(DB.BuiltInParameter.BASEPOINT_ANGLETON_PARAM) != None: # To check if the basepoint returned has value
            angle = loc.get_Parameter(DB.BuiltInParameter.BASEPOINT_ANGLETON_PARAM).AsDouble()
            # updating the coordinates required if the basepoint is moved unclipped
            # XYZ in revit is always measured horizintal and vertical to viewer ie from Base point
            bp_nsouth = loc.get_Parameter(DB.BuiltInParameter.BASEPOINT_NORTHSOUTH_PARAM).AsDouble() - rotate(loc.Position.X,loc.Position.Y,angle)[1] 
            bp_ewest = loc.get_Parameter(DB.BuiltInParameter.BASEPOINT_EASTWEST_PARAM).AsDouble() - rotate(loc.Position.X,loc.Position.Y,angle)[0]
            bp_elev = loc.get_Parameter(DB.BuiltInParameter.BASEPOINT_ELEVATION_PARAM).AsDouble()
with DB.Transaction(doc, 'Assign Coords') as t:
    try:
        t.Start()
        for element, x, y in zip(selection,X,Y):
            if x and y: # to ignore data of pile caps and other with no coordinates
                tup = find_cord(x,y,angle,bp_ewest,bp_nsouth)
                north = round(float(tup[0]),3)
                east = round(float(tup[1]),3)
                params_1 = element.GetParameters("North_Coord")
                params_2 = element.GetParameters("East_Coord")
                for param_1,param_2 in zip(params_1,params_2):
                    if param_1.IsShared and param_2.IsShared:
                        param_1.Set(north)
                        param_2.Set(east)
        t.Commit()
    except Exception as err:
        t.RollBack()
        forms.alert('Non shared Parameter named North__Coord/East_Coord already exists',
                    ok=True, yes=False, no=False)
    else:
        forms.alert('Task Succesfully Completed',
            ok=True, yes=False, no=False)
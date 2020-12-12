from pyrevit import revit, DB
from pyrevit import forms

def unit_from_type(display_unit_type):
    if display_unit_type == DB.DisplayUnitType.DUT_MILLIMETERS:
        return "mm" 
    elif display_unit_type == DB.DisplayUnitType.DUT_METERS:
        return "meters"
    elif display_unit_type == DB.DisplayUnitType.DUT_CENTIMETERS:
        return "cm"
    elif display_unit_type == DB.DisplayUnitType.DUT_DECIMETERS:
        return "dm"
    else: # anything other than above is assumed to be in feets.too bold?
        return "feets"

def type_from_unit(unit_type):
    if unit_type == "mm":
        return DB.DisplayUnitType.DUT_MILLIMETERS
    elif unit_type == "meters":
        return  DB.DisplayUnitType.DUT_METERS
    elif unit_type == "cm": 
        return DB.DisplayUnitType.DUT_CENTIMETERS
    elif unit_type == "dm":
        return DB.DisplayUnitType.DUT_DECIMETERS
    else: # anything other than above is assumed to be in feets.so no need for conversion
        return None


def get_type(ele,builtin_enum):
    dut = ele.Parameter[builtin_enum].DisplayUnitType
    return unit_from_type(dut)

def convert_to_internal(value,unit_type):
   dut = type_from_unit(unit_type)
   if dut:
       return DB.UnitUtils.ConvertToInternalUnits(value,dut) # converts 10mm to internal units (feet)
   else:
       return value # already in imperial (internal) units, no need for conversion

def filter_rule(para,param_equality,value):
    param_id = DB.ElementId(para)
    param_prov = DB.ParameterValueProvider(param_id)
        
    value_rule = DB.FilterDoubleRule(param_prov,param_equality(),value ,1e-3/0.3048) # tolerance of 1 mm
    param_filter = DB.ElementParameterFilter(value_rule)
    return param_filter
  
def print_output(num_walls,length,cur_units,equality):
    if num_walls >= 1:
        forms.alert("{} Walls of length{} {} {} selected!!!".format(num_walls,equality,length,cur_units))
    else:
        forms.alert("No other walls of length {} {} m found!!!".format(equality,length))


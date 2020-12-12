from pyrevit import revit,DB
from pyrevit import forms

def formatter_square(string):
    return u'{0}\xb2'.format(string)

def formatter_cube(string):
    return u'{0}\xb3'.format(string)

def unit_from_type(display_unit_type):
    if display_unit_type == DB.DisplayUnitType.DUT_MILLIMETERS:
        return "mm" 
    elif display_unit_type == DB.DisplayUnitType.DUT_METERS:
        return "m"
    elif display_unit_type == DB.DisplayUnitType.DUT_CENTIMETERS:
        return "cm"
    elif display_unit_type == DB.DisplayUnitType.DUT_DECIMETERS:
        return "dm"
    elif display_unit_type == DB.DisplayUnitType.DUT_DECIMAL_FEET:
        return "decimal-feet"
    elif display_unit_type == DB.DisplayUnitType.DUT_FEET_FRACTIONAL_INCHES:
        return "feet-fractional inches"
    elif display_unit_type == DB.DisplayUnitType.DUT_FRACTIONAL_INCHES:
        return "fractional inches"
    elif display_unit_type == DB.DisplayUnitType.DUT_DECIMAL_INCHES:
        return "decimal-inches"
    elif display_unit_type == DB.DisplayUnitType.DUT_CUSTOM:
        return "custom"

    elif display_unit_type == DB.DisplayUnitType.DUT_SQUARE_FEET:
        return formatter_square("ft")   
    elif display_unit_type == DB.DisplayUnitType.DUT_SQUARE_INCHES:
        return formatter_square("in")  
    elif display_unit_type == DB.DisplayUnitType.DUT_SQUARE_METERS:
        return formatter_square("m")  
    elif display_unit_type == DB.DisplayUnitType.DUT_SQUARE_CENTIMETERS:
        return formatter_square("cm") 
    elif display_unit_type == DB.DisplayUnitType.DUT_SQUARE_MILLIMETERS:
        return formatter_square("mm") 
    elif display_unit_type == DB.DisplayUnitType.DUT_SQUARE_MILLIMETERS:
        return "acres"
    elif display_unit_type == DB.DisplayUnitType.DUT_SQUARE_MILLIMETERS:
        return "hectares"

    elif display_unit_type == DB.DisplayUnitType.DUT_CUBIC_FEET:
        return formatter_cube("ft")
    elif display_unit_type == DB.DisplayUnitType.DUT_CUBIC_METERS:
        return formatter_cube("m")
    elif display_unit_type == DB.DisplayUnitType.DUT_CUBIC_INCHES:
        return formatter_cube("in")
    elif display_unit_type == DB.DisplayUnitType.DUT_CUBIC_CENTIMETERS:
        return formatter_cube("cm")
    elif display_unit_type == DB.DisplayUnitType.DUT_CUBIC_MILLIMETERS:
        return formatter_cube("mm")
    elif display_unit_type == DB.DisplayUnitType.DUT_LITERS:
        return "litres"
    elif display_unit_type == DB.DisplayUnitType.DUT_GALLONS_US:
        return "US gallons"
    elif display_unit_type == DB.DisplayUnitType.DUT_CUBIC_YARDS:
        return formatter_cube("yd")
    elif display_unit_type == DB.DisplayUnitType.DUT_UNDEFINED:
        return "undefined"

def conv_unit_type(quant_type):
    if quant_type == "length":
        return DB.UnitType.UT_Length
    elif quant_type == "area":
        return DB.UnitType.UT_Area
    elif quant_type == "volume":
        return DB.UnitType.UT_Volume
        
def total(selection,builtin_enum):
    warning_count = 0 # warning fuse
    total_quant = 0.0

    for ele in selection:
        para = ele.Parameter[builtin_enum]
        if para:
            quant = para.AsDouble() # AsValueString() not recommended
            total_quant+=quant
            dut = para.DisplayUnitType # will be same for all elements
        else:
            warning_count+=1
    if total_quant:
        total_quant = round(DB.UnitUtils.ConvertFromInternalUnits(total_quant,dut),4)
        try:
            formatted_total_quant = str(total_quant) + " " + unit_from_type(dut)
        except: # for none case
            formatted_total_quant = str(total_quant)
        return formatted_total_quant,warning_count
    else:
        return None,None
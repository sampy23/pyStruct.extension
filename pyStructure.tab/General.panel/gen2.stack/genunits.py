from pyrevit import revit,DB
from pyrevit import forms
from pyrevit import HOST_APP

def formatter_square(string):
    return u'{0}\xb2'.format(string)

def formatter_cube(string):
    return u'{0}\xb3'.format(string)

def revit_unit(unit_type,quant_type):
    if HOST_APP.is_newer_than(2021):
        length_metric_units = {DB.UnitTypeId.Meters:'m',
                                DB.UnitTypeId.Centimeters:'cm',
                                DB.UnitTypeId.Decimeters:'dm',
                                 DB.UnitTypeId.Millimeters:'mm'}
        length_imperial_units = {DB.UnitTypeId.Feet:'ft',
                                DB.UnitTypeId.FeetFractionalInches:'ft', # As double value will make all in ft
                                DB.UnitTypeId.Inches:'inches',
                                DB.UnitTypeId.FractionalInches:'inches',
                                DB.UnitTypeId.Custom:'custom'}
        area_metric_units = {   DB.UnitTypeId.SquareMeters:formatter_square("m") ,
                                DB.UnitTypeId.SquareCentimeters:formatter_square("cm"),
                                DB.UnitTypeId.SquareMillimeters:formatter_square("mm")}
        area_imperial_units = {   DB.UnitTypeId.SquareFeet:formatter_square("ft") ,
                                DB.UnitTypeId.SquareInches:formatter_square("in"),}
        volume_metric_units = {   DB.UnitTypeId.CubicMeters:formatter_cube("m") ,
                                DB.UnitTypeId.CubicCentimeters:formatter_cube("cm"),
                                DB.UnitTypeId.CubicMillimeters:formatter_cube("mm"),
                                DB.UnitTypeId.Liters:"L"}
        volume_imperial_units = {   DB.UnitTypeId.CubicFeet:'CF' ,
                                DB.UnitTypeId.CubicInches:formatter_cube("in"),
                                DB.UnitTypeId.CubicYards:"CY",
                               DB.UnitTypeId.UsGallons: "gal"}
    else:
        length_metric_units = {DB.DisplayUnitType.DUT_METERS:'m',
                                DB.DisplayUnitType.DUT_CENTIMETERS:'cm',
                                DB.DisplayUnitType.DUT_DECIMETERS:'dm',
                                DB.DisplayUnitType.DUT_MILLIMETERS:'mm'}
        
        length_imperial_units = {DB.DisplayUnitType.DUT_DECIMAL_FEET:'ft',
                                 DB.DisplayUnitType.DUT_FEET_FRACTIONAL_INCHES:'ft',
                                DB.DisplayUnitType.DUT_DECIMAL_INCHES:"inches",
                                DB.DisplayUnitType.DUT_FRACTIONAL_INCHES:"inches",
                                 DB.DisplayUnitType.DUT_CUSTOM: "custom"}
        area_metric_units = {  DB.DisplayUnitType.DUT_SQUARE_METERS:formatter_square("m") ,
                                DB.DisplayUnitType.DUT_SQUARE_CENTIMETERS:formatter_square("cm"),
                                DB.DisplayUnitType.DUT_SQUARE_MILLIMETERS:formatter_square("mm"),
                                }
        area_imperial_units = { DB.DisplayUnitType.DUT_SQUARE_FEET:formatter_square("ft") ,
                                DB.DisplayUnitType.DUT_SQUARE_INCHES:formatter_square("in"),}
        
        volume_metric_units = {   DB.DisplayUnitType.DUT_CUBIC_METERS:formatter_cube("m") ,
                                DB.DisplayUnitType.DUT_CUBIC_CENTIMETERS:formatter_cube("cm"),
                                DB.DisplayUnitType.DUT_CUBIC_MILLIMETERS:formatter_cube("mm"),
                                DB.DisplayUnitType.DUT_LITERS:"L"}
        volume_imperial_units = {   DB.DisplayUnitType.DUT_CUBIC_FEET:'CF' ,
                                DB.DisplayUnitType.DUT_CUBIC_INCHES:formatter_cube("in"),
                                DB.DisplayUnitType.DUT_CUBIC_YARDS:"CY",
                               DB.DisplayUnitType.DUT_GALLONS_US: "gal"}
        
    if quant_type == 'length':
        length_is_metric = unit_type in list(length_metric_units.keys())
        length_is_imperial = unit_type in list(length_imperial_units.keys())
        if length_is_metric:
            return length_metric_units[unit_type]
        elif length_is_imperial:
            return length_imperial_units[unit_type]
    
    elif quant_type == 'area':
        area_is_metric = unit_type in list(area_metric_units.keys())
        area_is_imperial = unit_type in list(area_imperial_units.keys())
        if area_is_metric:
            return area_metric_units[unit_type]
        elif area_is_imperial:
            return area_imperial_units[unit_type]    

    elif quant_type == 'volume':
        volume_is_metric = unit_type in list(volume_metric_units.keys())
        volume_is_imperial = unit_type in list(volume_imperial_units.keys())
        if volume_is_metric:
            return volume_metric_units[unit_type]
        elif volume_is_imperial:
            return volume_imperial_units[unit_type]  

def conv_unit_type(quant_type):
    if quant_type == "length":
        return DB.UnitType.UT_Length
    elif quant_type == "area":
        return DB.UnitType.UT_Area
    elif quant_type == "volume":
        return DB.UnitType.UT_Volume
        
def total(selection,builtin_enum,unit_type):
    warning_count = 0 # warning fuse
    total_quant = 0.0

    for ele in selection:
        para = ele.Parameter[builtin_enum]
        if para:
            quant = para.AsDouble() # AsValueString() not recommended
            total_quant+=quant
        else:
            warning_count+=1
    if total_quant:
        total_quant = round(DB.UnitUtils.ConvertFromInternalUnits(total_quant,unit_type),4)
        return total_quant,warning_count
    else:
        return None,None
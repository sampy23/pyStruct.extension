__title__ = "Wall Splitting Tool"
__author__ = "Shahabaz Sha"

from pyrevit import revit, DB
from pyrevit import forms

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument


def split_walls(selected_walls):
    """
    Splits selected walls at intermediate levels.
    """

    # Collect and sort all levels by elevation (Z-axis)
    all_levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).ToElements()
    levels_by_elevation = sorted(all_levels, key=lambda lvl: lvl.Elevation)

    # Ensure minimum levels exist
    if len(levels_by_elevation) < 2:
        forms.alert("At least 2 levels needed to split walls", exitscript=True)
        return

    created_segment_count = 0

    # Start Revit transaction
    with DB.Transaction(doc, "Split Walls by Levels") as transaction:
        try:
            transaction.Start()

            for wall in selected_walls:

                # Get wall geometry (must be curve-based)
                wall_location = wall.Location
                if not isinstance(wall_location, DB.LocationCurve):
                    continue

                # -------------------- GET LEVEL CONSTRAINTS --------------------
                top_constraint_param = wall.get_Parameter(DB.BuiltInParameter.WALL_HEIGHT_TYPE)

                base_level_elem = doc.GetElement(wall.LevelId)
                top_level_id = top_constraint_param.AsElementId() if top_constraint_param else None
                top_constraint_level = (
                    doc.GetElement(top_level_id)
                    if top_level_id != DB.ElementId.InvalidElementId else None
                )

                # Skip invalid walls
                if not base_level_elem or not top_constraint_level:
                    continue

                # -------------------- ELEVATIONS --------------------
                z_base = base_level_elem.Elevation
                z_top = top_constraint_level.Elevation

                # -------------------- ORIGINAL OFFSETS --------------------
                base_offset_orig = wall.get_Parameter(
                    DB.BuiltInParameter.WALL_BASE_OFFSET
                ).AsDouble()

                top_offset_orig = wall.get_Parameter(
                    DB.BuiltInParameter.WALL_TOP_OFFSET
                ).AsDouble()

                # -------------------- FIND INTERMEDIATE LEVELS --------------------
                intermediate_levels = [
                    lvl for lvl in levels_by_elevation
                    if z_base < lvl.Elevation < z_top
                ]

                # Skip if no splitting required
                if not intermediate_levels:
                    continue

                # -------------------- PREPARE SPLITTING --------------------
                current_base_level = base_level_elem
                wall_curve = wall_location.Curve

                # Loop through all split levels + final top level
                for target_level in intermediate_levels + [top_constraint_level]:

                    segment_height = target_level.Elevation - current_base_level.Elevation

                    # Skip invalid segments
                    if segment_height <= 0:
                        continue

                    # -------------------- CREATE NEW WALL SEGMENT --------------------
                    segment_wall = DB.Wall.Create(
                        doc,
                        wall_curve,
                        wall.WallType.Id,
                        current_base_level.Id,
                        segment_height,
                        0,
                        wall.Flipped,
                        True
                    )

                    # -------------------- APPLY BASE OFFSET --------------------
                    try:
                        if current_base_level.Id == base_level_elem.Id and base_offset_orig != 0:
                            segment_wall.get_Parameter(
                                DB.BuiltInParameter.WALL_BASE_OFFSET
                            ).Set(base_offset_orig)
                        else:
                            segment_wall.get_Parameter(
                                DB.BuiltInParameter.WALL_BASE_OFFSET
                            ).Set(0)
                    except:
                        pass

                    # -------------------- SET TOP CONSTRAINT --------------------
                    try:
                        segment_wall.get_Parameter(
                            DB.BuiltInParameter.WALL_HEIGHT_TYPE
                        ).Set(target_level.Id)
                    except:
                        pass

                    # -------------------- APPLY TOP OFFSET --------------------
                    try:
                        if target_level.Id == top_constraint_level.Id and top_offset_orig != 0:
                            segment_wall.get_Parameter(
                                DB.BuiltInParameter.WALL_TOP_OFFSET
                            ).Set(top_offset_orig)
                        else:
                            segment_wall.get_Parameter(
                                DB.BuiltInParameter.WALL_TOP_OFFSET
                            ).Set(0)
                    except:
                        pass

                    # Move base upward for next segment
                    current_base_level = target_level
                    created_segment_count += 1

                # Delete original wall after splitting
                doc.Delete(wall.Id)

            # Commit transaction
            transaction.Commit()

            forms.alert(
                "Walls split successfully.\nTotal number of new walls are: {}".format(created_segment_count)
            )

        except Exception as ex:
            if transaction.HasStarted():
                transaction.RollBack()

            forms.alert("Script failed.\n\n{}".format(str(ex)), exitscript=True)


selected_walls = revit.get_selection()

if not selected_walls:
    forms.alert(
        "No walls selected!!! \nPlease select walls and continue..",
        exitscript=True
    )

split_walls(selected_walls)
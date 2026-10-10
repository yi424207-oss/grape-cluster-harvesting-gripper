"""Parametric concept model of a grape cluster support and peduncle shear.

Units: mm. Coordinate Z is vertical. This is a course-design geometry model,
not a tested manufacturing release. Run: python model.py
"""
from pathlib import Path
import cadquery as cq
from cadquery import exporters
from cadquery.occ_impl.shapes import Compound

OUT = Path(__file__).resolve().parent
PARTS = OUT / "parts"
PARTS.mkdir(exist_ok=True)

def box(dx, dy, dz, xyz):
    return cq.Workplane("XY").box(dx, dy, dz).translate(xyz).val()

def cyl(radius, height, xyz):
    return cq.Solid.makeCylinder(radius, height, cq.Vector(*xyz), cq.Vector(0, 0, 1))

def rail(points, radius):
    """Round segmented soft finger with continuous intersecting joints."""
    solids = []
    for a, b in zip(points[:-1], points[1:]):
        v = cq.Vector(*b).sub(cq.Vector(*a))
        solids.append(cq.Solid.makeCylinder(radius, v.Length, cq.Vector(*a), v.normalized()))
    solids.extend(cq.Solid.makeSphere(radius, cq.Vector(*p)) for p in points)
    result = solids[0]
    for s in solids[1:]:
        result = result.fuse(s)
    return result.clean()

# Fixed bracket with four mounting holes through X.
bracket = box(9, 58, 80, (-178, 0, 145))
for yy in (-19, 19):
    for zz in (120, 170):
        hole = cq.Solid.makeCylinder(3.2, 12, cq.Vector(-184, yy, zz), cq.Vector(1,0,0))
        bracket = bracket.cut(hole)

# Central spine and rigid supports; assembly is shown in its closed position.
spine = box(178, 22, 15, (-84.5, 0, 183))
for side in (-1, 1):
    spine = spine.fuse(box(16, 18, 77, (side*119, 0, 140)))
    spine = spine.fuse(box(110, 14, 12, (side*68, 0, 178)))
spine = spine.clean()

# The clamp makes a 17 mm throat for the upper limit of the 5--15 mm stem.
# Separate moving jaw is explicitly modeled, rather than counting the cutter
# as a gripper. Soft pads face the stem from either side.
fixed_jaw = box(29, 13, 22, (0, -18, 147))
moving_jaw = box(29, 13, 22, (0, 18, 147))
pad_fixed = box(24, 2.5, 16, (0, -10.25, 147))
pad_moving = box(24, 2.5, 16, (0, 10.25, 147))
actuator = box(28, 33, 24, (0, 47, 148))
link = cq.Solid.makeCylinder(3, 19, cq.Vector(0,25,147), cq.Vector(0,1,0))

# Two blades at a separate higher station. The blade shapes are conceptual
# envelopes; the cutting edge and motor torque require prototype testing.
blade_fixed = box(30, 18, 2, (0, -19, 165))
blade_move = box(30, 18, 2, (0, 19, 165))
blade_drive = box(28, 33, 22, (0, 46, 171))

# Four compliant fingers act as two opposing half cradles. Each lower hook
# supports a share of fruit weight; no friction-only fruit grip is assumed.
fingers = []
finger_cores = []
for sx in (-1, 1):
    for sy in (-1, 1):
        p = [(sx*120,sy*62,109), (sx*116,sy*82,62),
             (sx*107,sy*79,0), (sx*91,sy*68,-68),
             (sx*63,sy*48,-112), (sx*38,sy*32,-133)]
        outer = rail(p, 12)
        core = rail(p, 10)
        fingers.append(outer.cut(core).clean())
        finger_cores.append(core)

# Link rails can swing with the two fingers on each side. Hinge barrels and
# actuators are schematic mount volumes; fasteners and control are omitted.
carriers = []
for sx in (-1, 1):
    carrier = box(20, 146, 12, (sx*120,0,108))
    carrier = carrier.fuse(cq.Solid.makeCylinder(9, 19, cq.Vector(sx*120,-9.5,109),cq.Vector(0,1,0)))
    carriers.append(carrier.clean())

parts = {
    "01_mount": bracket, "02_frame": spine,
    "03_stem_jaw_fixed": fixed_jaw, "04_stem_jaw_moving": moving_jaw,
    "05_stem_pad_fixed": pad_fixed, "06_stem_pad_moving": pad_moving,
    "07_stem_actuator_envelope": actuator, "08_stem_link": link,
    "09_blade_fixed": blade_fixed, "10_blade_moving": blade_move,
    "11_blade_actuator_envelope": blade_drive,
}
for i, s in enumerate(carriers, 1): parts[f"12_carrier_{i}"] = s
for i, s in enumerate(fingers, 1): parts[f"13_soft_finger_{i}"] = s
for i, s in enumerate(finger_cores, 1): parts[f"14_finger_core_{i}"] = s
for i, side in enumerate((-1,1), 1):
    parts[f"15_cradle_drive_envelope_{i}"] = box(29, 25, 24, (side*146, 0, 118))
    # Split sling under the bunch: the two halves open with their carriers.
    parts[f"16_soft_sling_half_{i}"] = box(65, 78, 4, (side*34, 0, -139))

assembly = cq.Assembly(name="grape_harvesting_end_effector_concept")
for name, shape in parts.items():
    color = (0.14,0.36,0.68)
    if ("soft_finger" in name or "soft_sling" in name or "pad" in name): color=(0.19,0.67,0.61)
    if "blade" in name: color=(0.75,0.78,0.82)
    if "actuator" in name: color=(0.88,0.58,0.20)
    assembly.add(shape, name=name, color=cq.Color(*color))
    exporters.export(shape, str(PARTS / f"{name}.stl"), tolerance=0.3)

assembly.save(str(OUT/"grape_gripper_assembly.step"))
all_solids = Compound.makeCompound(list(parts.values()))
exporters.export(all_solids, str(OUT/"grape_gripper_assembly.stl"), tolerance=0.3)

# OpenSCAD is only used as a reproducible visualization layer for the real
# CAD meshes. The semi-transparent ellipsoid illustrates the design envelope.
lines = ["$fn=48;", "color([0.67,0.83,0.45,0.18]) translate([0,0,-25]) scale([97,85,108]) sphere(1);"]
for name in parts:
    rgb = [0.14,0.36,0.68]
    if "soft_finger" in name or "soft_sling" in name or "pad" in name: rgb=[0.10,0.65,0.57]
    if "blade" in name: rgb=[0.75,0.77,0.80]
    if "actuator" in name: rgb=[0.92,0.56,0.16]
    lines.append(f"color({rgb}) import(\"parts/{name}.stl\");")
(OUT/"visualization.scad").write_text("\n".join(lines)+"\n")
print(f"Wrote {len(parts)} solids to {OUT}")

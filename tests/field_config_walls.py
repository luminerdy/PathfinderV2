"""
Wall-Centered Field Configuration
4 AprilTags, one per wall, centered
"""

from field_config import FieldConfig, WallConfig

# 4-tag wall-centered field (easier to mount than corners)
WALL_CENTERED_6X6 = FieldConfig(
    name="wall_centered_6x6",
    description="6x6 ft field with one tag per wall (centered)",
    size_ft=(6, 6),
    tag_height_in=10,
    tag_size_in=6,
    walls=[
        WallConfig(
            name="north",
            length_ft=6,
            tags=[0],  # Center of north wall
            position="top"
        ),
        WallConfig(
            name="east",
            length_ft=6,
            tags=[1],  # Center of east wall
            position="right"
        ),
        WallConfig(
            name="south",
            length_ft=6,
            tags=[2],  # Center of south wall
            position="bottom"
        ),
        WallConfig(
            name="west",
            length_ft=6,
            tags=[3],  # Center of west wall
            position="left"
        )
    ]
)

# Make this the default
DEFAULT_FIELD = WALL_CENTERED_6X6

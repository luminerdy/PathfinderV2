"""
Test Field Configuration
Define AprilTag layouts for different test scenarios
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict


@dataclass
class WallConfig:
    """Configuration for one wall"""
    name: str           # 'north', 'south', 'east', 'west'
    length_ft: float    # Wall length in feet
    tags: List[int]     # AprilTag IDs on this wall
    position: str       # 'top', 'bottom', 'left', 'right'


@dataclass
class FieldConfig:
    """Test field configuration"""
    name: str
    description: str
    size_ft: Tuple[float, float]  # (width, height) in feet
    tag_height_in: float           # Tag center height in inches
    tag_size_in: float             # Tag size in inches
    walls: List[WallConfig]
    
    def get_all_tags(self) -> List[int]:
        """Get list of all tag IDs in field"""
        tags = []
        for wall in self.walls:
            tags.extend(wall.tags)
        return sorted(tags)
    
    def get_tag_count(self) -> int:
        """Total number of tags"""
        return len(self.get_all_tags())


# Predefined field configurations

WALL_FIELD_6X6 = FieldConfig(
    name="wall_field_6x6",
    description="6x6 ft field with wall-mounted AprilTags at 10 inch height",
    size_ft=(6, 6),
    tag_height_in=10,
    tag_size_in=6,
    walls=[
        WallConfig(
            name="north",
            length_ft=6,
            tags=[1, 2],
            position="top"
        ),
        WallConfig(
            name="east",
            length_ft=6,
            tags=[3],
            position="right"
        ),
        WallConfig(
            name="south",
            length_ft=6,
            tags=[4, 5],
            position="bottom"
        ),
        WallConfig(
            name="west",
            length_ft=6,
            tags=[0],
            position="left"
        )
    ]
)


CORNER_FIELD_6X6 = FieldConfig(
    name="corner_field_6x6",
    description="6x6 ft field with corner-mounted tags",
    size_ft=(6, 6),
    tag_height_in=10,
    tag_size_in=6,
    walls=[
        WallConfig(
            name="northwest",
            length_ft=2,
            tags=[0],
            position="top-left"
        ),
        WallConfig(
            name="northeast",
            length_ft=2,
            tags=[1],
            position="top-right"
        ),
        WallConfig(
            name="southeast",
            length_ft=2,
            tags=[2],
            position="bottom-right"
        ),
        WallConfig(
            name="southwest",
            length_ft=2,
            tags=[3],
            position="bottom-left"
        )
    ]
)


SIMPLE_TEST_FIELD = FieldConfig(
    name="simple_test",
    description="Minimal field for basic testing (3 tags)",
    size_ft=(6, 6),
    tag_height_in=10,
    tag_size_in=6,
    walls=[
        WallConfig(
            name="front",
            length_ft=6,
            tags=[0],
            position="top"
        ),
        WallConfig(
            name="left",
            length_ft=2,
            tags=[1],
            position="left"
        ),
        WallConfig(
            name="right",
            length_ft=2,
            tags=[2],
            position="right"
        )
    ]
)


# Registry of available fields
AVAILABLE_FIELDS = {
    "wall_field_6x6": WALL_FIELD_6X6,
    "corner_field_6x6": CORNER_FIELD_6X6,
    "simple_test": SIMPLE_TEST_FIELD
}


def get_field_config(name: str) -> FieldConfig:
    """
    Get field configuration by name
    
    Args:
        name: Field configuration name
    
    Returns:
        FieldConfig instance
    
    Raises:
        ValueError if field not found
    """
    if name not in AVAILABLE_FIELDS:
        raise ValueError(f"Unknown field: {name}. Available: {list(AVAILABLE_FIELDS.keys())}")
    
    return AVAILABLE_FIELDS[name]


def print_field_info(config: FieldConfig):
    """Print field configuration details"""
    print(f"\n{'='*60}")
    print(f"Field: {config.name}")
    print(f"Description: {config.description}")
    print(f"Size: {config.size_ft[0]}' x {config.size_ft[1]}'")
    print(f"Tag height: {config.tag_height_in}\"")
    print(f"Tag size: {config.tag_size_in}\"")
    print(f"Total tags: {config.get_tag_count()}")
    print(f"\nWalls:")
    for wall in config.walls:
        print(f"  {wall.name:15s} ({wall.length_ft}') - Tags: {wall.tags}")
    print(f"{'='*60}\n")

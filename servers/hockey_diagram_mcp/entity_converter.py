"""
Entity to diagram conversion functions.

Converts extracted entities from natural language into diagram specifications
that can be rendered by the generator.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from entities import (
    ExtractedEntities, Player, Movement, Zone as EntityZone, 
    ArrowType, ZoneType, PassType, MovementType, PlayerRole
)
from coordinate_mapper import (
    coordinate_mapper, Zone as MapperZone, Team,
    get_player_coordinate, get_area_coordinate, 
    get_formation_coordinates, get_drill_positioning,
    get_zone_boundary, validate_coordinate
)
from models import DiagramSpec, PlayerPosition, MovementArrow, TacticalZone, TacticalElement


class EntityToDiagramConverter:
    """
    Converts extracted entities to diagram specifications.
    
    Handles:
    - Player positioning based on formations and roles
    - Movement arrow generation
    - Zone highlighting
    - Tactical element creation
    - Context-aware positioning
    """
    
    def __init__(self):
        self.mapper = coordinate_mapper
    
    def convert_entities_to_spec(
        self, 
        entities: ExtractedEntities,
        view: str = "full",
        title: Optional[str] = None
    ) -> DiagramSpec:
        """
        Convert extracted entities to a complete diagram specification.
        
        Args:
            entities: Extracted entities from natural language
            view: Diagram view (full, offensive, defensive, neutral)
            title: Optional diagram title
            
        Returns:
            Complete diagram specification
        """
        # Determine primary zone context
        primary_zone = self._determine_primary_zone(entities)
        
        # Get formation coordinates if specified
        formation_coords = {}
        if entities.formation:
            formation_coords = self.mapper.get_formation_coordinates(entities.formation)
        
        # Convert players
        player_positions = self._convert_players(
            entities.players, 
            primary_zone, 
            entities.formation,
            formation_coords
        )
        
        # Convert movements
        movement_arrows = self._convert_movements(
            entities.movements,
            player_positions
        )
        
        # Convert zones
        tactical_zones = self._convert_zones(entities.zones)
        
        # Create tactical elements
        tactical_elements = self._create_tactical_elements(entities, player_positions)
        
        # Determine diagram type
        diagram_type = self._determine_diagram_type(entities)
        
        # Create and return specification
        return DiagramSpec(
            players=player_positions,
            movements=movement_arrows,
            zones=tactical_zones,
            elements=tactical_elements,
            view=view,
            title=title or self._generate_title(entities),
            diagram_type=diagram_type,
            output_format="png"
        )
    
    def _determine_primary_zone(self, entities: ExtractedEntities) -> MapperZone:
        """Determine the primary zone context from entities."""
        # Check zones first
        if entities.zones:
            zone_types = [z.zone_type for z in entities.zones]
            if ZoneType.OFFENSIVE in zone_types:
                return MapperZone.OFFENSIVE
            elif ZoneType.DEFENSIVE in zone_types:
                return MapperZone.DEFENSIVE
            elif ZoneType.NEUTRAL in zone_types:
                return MapperZone.NEUTRAL
        
        # Check context clues
        if entities.situation:
            sit_lower = entities.situation.lower()
            if any(word in sit_lower for word in ["offensive", "attacking", "power play", "o-zone"]):
                return MapperZone.OFFENSIVE
            elif any(word in sit_lower for word in ["defensive", "defending", "penalty kill", "d-zone"]):
                return MapperZone.DEFENSIVE
            elif any(word in sit_lower for word in ["neutral", "center", "transition"]):
                return MapperZone.NEUTRAL
        
        # Check formation
        if entities.formation:
            form_lower = entities.formation.lower()
            if "powerplay" in form_lower or "offensive" in form_lower:
                return MapperZone.OFFENSIVE
            elif "penalty_kill" in form_lower or "defensive" in form_lower:
                return MapperZone.DEFENSIVE
        
        # Default based on action
        if entities.action and any(word in entities.action.lower() for word in ["forecheck", "attack"]):
            return MapperZone.OFFENSIVE
        
        return MapperZone.NEUTRAL
    
    def _convert_players(
        self, 
        players: List[Player], 
        primary_zone: MapperZone,
        formation: Optional[str],
        formation_coords: Dict[str, Tuple[float, float]]
    ) -> List[PlayerPosition]:
        """Convert player entities to positioned players."""
        positioned_players = []
        used_positions = set()
        
        for player in players:
            # Get coordinates based on context
            x, y = self._get_player_coordinates(
                player, 
                primary_zone, 
                formation,
                formation_coords,
                used_positions
            )
            
            # Create player position
            player_pos = PlayerPosition(
                position=player.position,
                x=x,
                y=y,
                team=self._determine_team(player),
                has_puck=player.has_puck,
                label=player.label
            )
            
            positioned_players.append(player_pos)
            used_positions.add((x, y))
        
        return positioned_players
    
    def _get_player_coordinates(
        self,
        player: Player,
        zone: MapperZone,
        formation: Optional[str],
        formation_coords: Dict[str, Tuple[float, float]],
        used_positions: set
    ) -> Tuple[float, float]:
        """Get coordinates for a single player."""
        # Try formation-specific coordinates first
        if formation and player.label:
            # Check if player label matches formation position
            if player.label in formation_coords:
                return formation_coords[player.label]
        
        # Try location-based coordinates
        if player.location:
            x, y = self.mapper.convert_role_to_coordinate(
                player.position,
                player.location,
                zone.value
            )
            # Avoid overlapping positions
            offset = 0
            while (x, y) in used_positions and offset < 10:
                offset += 2
                x += offset
                y += offset
            return x, y
        
        # Use role-based coordinates
        role = player.role.value if player.role else "primary"
        return self.mapper.get_player_coordinate(
            player.position,
            zone,
            role,
            formation
        )
    
    def _convert_movements(
        self,
        movements: List[Movement],
        player_positions: List[PlayerPosition]
    ) -> List[MovementArrow]:
        """Convert movement entities to arrows."""
        arrows = []
        
        # Create position lookup
        player_lookup = {
            p.position: (p.x, p.y) for p in player_positions
        }
        
        for movement in movements:
            # Get start position
            start_x, start_y = self._get_movement_start(movement, player_lookup)
            
            # Get end position
            end_x, end_y = self._get_movement_end(movement, player_lookup, start_x, start_y)
            
            # Create arrow
            arrow = MovementArrow(
                start_x=start_x,
                start_y=start_y,
                end_x=end_x,
                end_y=end_y,
                arrow_type=self._convert_arrow_type(movement.arrow_type),
                label=movement.label,
                curved=movement.movement_type == MovementType.CYCLE
            )
            
            arrows.append(arrow)
        
        return arrows
    
    def _get_movement_start(
        self,
        movement: Movement,
        player_lookup: Dict[str, Tuple[float, float]]
    ) -> Tuple[float, float]:
        """Get movement starting position."""
        # Try player position first
        if movement.player and movement.player in player_lookup:
            return player_lookup[movement.player]
        
        # Try from location
        if movement.from_location:
            return self.mapper.get_area_coordinate(movement.from_location)
        
        # Default to center
        return (0, 0)
    
    def _get_movement_end(
        self,
        movement: Movement,
        player_lookup: Dict[str, Tuple[float, float]],
        start_x: float,
        start_y: float
    ) -> Tuple[float, float]:
        """Get movement ending position."""
        # Try to location first
        if movement.to_location:
            return self.mapper.get_area_coordinate(movement.to_location)
        
        # Try target player
        if movement.target_player and movement.target_player in player_lookup:
            return player_lookup[movement.target_player]
        
        # Use direction if available
        if movement.direction:
            return self.mapper.get_relative_position(
                (start_x, start_y),
                movement.direction,
                movement.distance or 20
            )
        
        # Default offset
        return (start_x + 20, start_y)
    
    def _convert_zones(self, zones: List[EntityZone]) -> List[TacticalZone]:
        """Convert zone entities to tactical zones."""
        tactical_zones = []
        
        for zone in zones:
            # Get zone boundaries
            boundary = self.mapper.get_zone_boundary(zone.zone_type.value + "_zone")
            if boundary:
                x, y, width, height = boundary
                
                tactical_zone = TacticalZone(
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    zone_type=zone.zone_type.value,
                    highlight_type=zone.highlight_type,
                    label=zone.label
                )
                
                tactical_zones.append(tactical_zone)
        
        return tactical_zones
    
    def _create_tactical_elements(
        self,
        entities: ExtractedEntities,
        player_positions: List[PlayerPosition]
    ) -> List[TacticalElement]:
        """Create additional tactical elements."""
        elements = []
        
        # Add formation label if present
        if entities.formation:
            elements.append(TacticalElement(
                type="text",
                x=0,
                y=-60,
                text=entities.formation.replace("_", " ").title(),
                size="large"
            ))
        
        # Add situation label if present
        if entities.situation:
            elements.append(TacticalElement(
                type="text",
                x=0,
                y=-50,
                text=entities.situation,
                size="medium"
            ))
        
        # Add pressure indicators
        for player in player_positions:
            if player.has_puck:
                # Add puck indicator
                elements.append(TacticalElement(
                    type="puck",
                    x=player.x,
                    y=player.y + 3
                ))
        
        return elements
    
    def _convert_arrow_type(self, arrow_type: Optional[ArrowType]) -> str:
        """Convert entity arrow type to diagram arrow type."""
        if not arrow_type:
            return "solid"
        
        mapping = {
            ArrowType.SOLID: "solid",
            ArrowType.DASHED: "dashed",
            ArrowType.CURVED: "curved",
            ArrowType.DOTTED: "dashed"
        }
        
        return mapping.get(arrow_type, "solid")
    
    def _determine_team(self, player: Player) -> str:
        """Determine team for player."""
        # Could be enhanced with more logic
        if player.team:
            return player.team.lower()
        
        # Default based on position naming
        if player.label and "opponent" in player.label.lower():
            return "away"
        
        return "home"
    
    def _determine_diagram_type(self, entities: ExtractedEntities) -> str:
        """Determine the type of diagram."""
        if entities.formation:
            if "drill" in entities.formation.lower():
                return "drill"
            elif any(word in entities.formation.lower() for word in ["powerplay", "penalty_kill"]):
                return "system"
        
        if entities.action:
            if "drill" in entities.action.lower():
                return "drill"
        
        return "tactical"
    
    def _generate_title(self, entities: ExtractedEntities) -> str:
        """Generate a title from entities if not provided."""
        parts = []
        
        if entities.formation:
            parts.append(entities.formation.replace("_", " ").title())
        
        if entities.action:
            parts.append(entities.action)
        
        if entities.situation:
            parts.append(f"({entities.situation})")
        
        return " ".join(parts) if parts else "Hockey Tactical Diagram"
    
    def convert_drill_description(
        self,
        drill_type: str,
        player_count: int,
        description: str
    ) -> DiagramSpec:
        """
        Convert a drill description to diagram specification.
        
        Args:
            drill_type: Type of drill
            player_count: Number of players
            description: Drill description
            
        Returns:
            Diagram specification
        """
        # Get drill positioning
        positions = self.mapper.get_drill_positioning(drill_type, player_count)
        
        # Create players
        players = []
        position_names = ["G", "LD", "RD", "C", "LW", "RW"]
        
        for i, (x, y) in enumerate(positions):
            position = position_names[i % len(position_names)]
            player = PlayerPosition(
                position=position,
                x=x,
                y=y,
                team="home",
                label=f"P{i+1}" if i >= 6 else None
            )
            players.append(player)
        
        # Create basic movement patterns based on drill type
        movements = self._generate_drill_movements(drill_type, players)
        
        return DiagramSpec(
            players=players,
            movements=movements,
            zones=[],
            elements=[],
            view="full",
            title=f"{drill_type.replace('_', ' ').title()} - {description}",
            diagram_type="drill"
        )
    
    def _generate_drill_movements(
        self,
        drill_type: str,
        players: List[PlayerPosition]
    ) -> List[MovementArrow]:
        """Generate movement patterns for common drills."""
        movements = []
        
        if drill_type == "triangle_passing" and len(players) >= 3:
            # Create passing triangle
            for i in range(3):
                start = players[i]
                end = players[(i + 1) % 3]
                movements.append(MovementArrow(
                    start_x=start.x,
                    start_y=start.y,
                    end_x=end.x,
                    end_y=end.y,
                    arrow_type="dashed",
                    label="Pass"
                ))
        
        elif drill_type == "2v1_rush" and len(players) >= 4:
            # Attacking movements
            movements.append(MovementArrow(
                start_x=players[0].x,
                start_y=players[0].y,
                end_x=players[0].x + 40,
                end_y=players[0].y,
                arrow_type="solid",
                label="Attack"
            ))
            movements.append(MovementArrow(
                start_x=players[1].x,
                start_y=players[1].y,
                end_x=players[1].x + 40,
                end_y=players[1].y,
                arrow_type="solid"
            ))
        
        return movements


# Create global converter instance
converter = EntityToDiagramConverter()


def convert_entities_to_diagram(
    entities: ExtractedEntities,
    view: str = "full",
    title: Optional[str] = None
) -> DiagramSpec:
    """Convenience function to convert entities to diagram spec."""
    return converter.convert_entities_to_spec(entities, view, title)


def convert_drill_to_diagram(
    drill_type: str,
    player_count: int,
    description: str
) -> DiagramSpec:
    """Convenience function to convert drill to diagram spec."""
    return converter.convert_drill_description(drill_type, player_count, description)
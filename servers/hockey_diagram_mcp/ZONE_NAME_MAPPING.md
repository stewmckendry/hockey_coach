# Hockey Zone Name Mapping

## Current Technical Names → Hockey-Friendly Names

### DEFENSIVE ZONES (Our End)
| Current Name | Hockey Name | Description |
|--------------|-------------|-------------|
| def-left-high | d-corner-left-high | Defensive corner, left side, upper |
| def-center-left-high | d-circle-left-high | Left defensive circle, upper |
| def-center-right-high | d-circle-right-high | Right defensive circle, upper |
| def-left-mid-high | d-behind-net-left | Behind our net, left side |
| def-center-left-mid-high | d-circle-left-center | Left defensive circle, center |
| def-center-right-mid-high | d-circle-right-center | Right defensive circle, center |
| def-left-mid-low | d-behind-net-right | Behind our net, right side |
| def-center-left-mid-low | d-circle-left-low | Left defensive circle, lower |
| def-center-right-mid-low | d-circle-right-low | Right defensive circle, lower |
| def-left-low | d-corner-left-low | Defensive corner, left side, lower |
| def-center-left-low | d-circle-left-boards | Left circle to boards |
| def-center-right-low | d-circle-right-boards | Right circle to boards |

### NEUTRAL ZONES
| Current Name | Hockey Name | Description |
|--------------|-------------|-------------|
| neu-left-high | neutral-left-wing-high | Neutral zone, left wing lane upper |
| neu-right-high | neutral-right-wing-high | Neutral zone, right wing lane upper |
| neu-left-mid-high | neutral-left-center-high | Neutral zone, left center lane |
| neu-right-mid-high | neutral-right-center-high | Neutral zone, right center lane |
| neu-left-mid-low | neutral-left-center-low | Neutral zone, left center lane |
| neu-right-mid-low | neutral-right-center-low | Neutral zone, right center lane |
| neu-left-low | neutral-left-wing-low | Neutral zone, left wing lane lower |
| neu-right-low | neutral-right-wing-low | Neutral zone, right wing lane lower |

### OFFENSIVE ZONES (Their End)
| Current Name | Hockey Name | Description |
|--------------|-------------|-------------|
| off-center-left-high | o-point-left | Left point position |
| off-center-right-high | o-high-slot-high | High slot, upper portion |
| off-right-high | o-corner-right-high | Offensive corner, right side, upper |
| off-center-left-mid-high | o-point-center-left | Point area, center-left |
| off-center-right-mid-high | o-slot-high | Slot area, upper |
| off-right-mid-high | o-behind-net-right | Behind their net, right side |
| off-center-left-mid-low | o-point-center-right | Point area, center-right |
| off-center-right-mid-low | o-slot-low | Slot area, lower |
| off-right-mid-low | o-behind-net-left | Behind their net, left side |
| off-center-left-low | o-point-right | Right point position |
| off-center-right-low | o-low-slot | Low slot/crease area |
| off-right-low | o-corner-left-low | Offensive corner, left side, lower |

## Key Hockey Areas (Combinations of Zones)

- **The Slot**: o-slot-high + o-slot-low
- **High Slot**: o-high-slot-high + o-point-center-left/right
- **Point**: o-point-left + o-point-right + o-point-center-left/right
- **Crease**: o-low-slot (closest to net)
- **Corners**: o-corner-left-low + o-corner-right-high
- **Behind Net**: o-behind-net-left + o-behind-net-right
- **Hashmarks**: Junction between circles and slot
- **Blue Line**: Edge of o-point zones

## Usage in Formations

Instead of:
```
"position": "off-center-right-mid-high"
```

Use:
```
"position": "o-slot-high"
```

This makes formations much more readable and matches coaching terminology!
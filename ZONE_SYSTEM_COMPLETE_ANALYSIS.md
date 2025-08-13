# Hockey Diagram Zone System - Complete Analysis

## Executive Summary

The hockey diagram generator has **TWO zone systems**:
1. **Legacy Named Zones** (31 zones) - Specific hockey positions with overlaps
2. **Zone Grid System** (32 zones) - MECE grid covering entire ice surface

## 1. Zone Grid System (MECE - ✅ Mutually Exclusive, ✅ Collectively Exhaustive)

### Overview
- **Total Zones**: 32
- **Coverage**: 100% of ice surface
- **Overlaps**: None
- **Grid**: 8 columns × 4 rows

### Zone Distribution
- **Defensive zones**: 12 (x < -25)
- **Neutral zones**: 8 (-25 ≤ x ≤ 25)
- **Offensive zones**: 12 (x > 25)

### Zone Naming Convention
Pattern: `{area}-{position}-{height}`
- **area**: def, neu, off
- **position**: left, center-left, center-right, right
- **height**: low, mid-low, mid-high, high

### Complete Zone List with Coordinates

#### Defensive Zones (def-*)
| Zone Name | Center (x, y) | X Bounds | Y Bounds |
|-----------|---------------|----------|----------|
| def-left-low | (-87.5, -31.9) | -100 to -75 | -42.5 to -21.2 |
| def-left-mid-low | (-87.5, -10.6) | -100 to -75 | -21.2 to 0 |
| def-left-mid-high | (-87.5, 10.6) | -100 to -75 | 0 to 21.2 |
| def-left-high | (-87.5, 31.9) | -100 to -75 | 21.2 to 42.5 |
| def-center-left-low | (-62.5, -31.9) | -75 to -50 | -42.5 to -21.2 |
| def-center-left-mid-low | (-62.5, -10.6) | -75 to -50 | -21.2 to 0 |
| def-center-left-mid-high | (-62.5, 10.6) | -75 to -50 | 0 to 21.2 |
| def-center-left-high | (-62.5, 31.9) | -75 to -50 | 21.2 to 42.5 |
| def-center-right-low | (-37.5, -31.9) | -50 to -25 | -42.5 to -21.2 |
| def-center-right-mid-low | (-37.5, -10.6) | -50 to -25 | -21.2 to 0 |
| def-center-right-mid-high | (-37.5, 10.6) | -50 to -25 | 0 to 21.2 |
| def-center-right-high | (-37.5, 31.9) | -50 to -25 | 21.2 to 42.5 |

#### Neutral Zones (neu-*)
| Zone Name | Center (x, y) | X Bounds | Y Bounds |
|-----------|---------------|----------|----------|
| neu-left-low | (-12.5, -31.9) | -25 to 0 | -42.5 to -21.2 |
| neu-left-mid-low | (-12.5, -10.6) | -25 to 0 | -21.2 to 0 |
| neu-left-mid-high | (-12.5, 10.6) | -25 to 0 | 0 to 21.2 |
| neu-left-high | (-12.5, 31.9) | -25 to 0 | 21.2 to 42.5 |
| neu-right-low | (12.5, -31.9) | 0 to 25 | -42.5 to -21.2 |
| neu-right-mid-low | (12.5, -10.6) | 0 to 25 | -21.2 to 0 |
| neu-right-mid-high | (12.5, 10.6) | 0 to 25 | 0 to 21.2 |
| neu-right-high | (12.5, 31.9) | 0 to 25 | 21.2 to 42.5 |

#### Offensive Zones (off-*)
| Zone Name | Center (x, y) | X Bounds | Y Bounds |
|-----------|---------------|----------|----------|
| off-center-left-low | (37.5, -31.9) | 25 to 50 | -42.5 to -21.2 |
| off-center-left-mid-low | (37.5, -10.6) | 25 to 50 | -21.2 to 0 |
| off-center-left-mid-high | (37.5, 10.6) | 25 to 50 | 0 to 21.2 |
| off-center-left-high | (37.5, 31.9) | 25 to 50 | 21.2 to 42.5 |
| off-center-right-low | (62.5, -31.9) | 50 to 75 | -42.5 to -21.2 |
| off-center-right-mid-low | (62.5, -10.6) | 50 to 75 | -21.2 to 0 |
| off-center-right-mid-high | (62.5, 10.6) | 50 to 75 | 0 to 21.2 |
| off-center-right-high | (62.5, 31.9) | 50 to 75 | 21.2 to 42.5 |
| off-right-low | (87.5, -31.9) | 75 to 100 | -42.5 to -21.2 |
| off-right-mid-low | (87.5, -10.6) | 75 to 100 | -21.2 to 0 |
| off-right-mid-high | (87.5, 10.6) | 75 to 100 | 0 to 21.2 |
| off-right-high | (87.5, 31.9) | 75 to 100 | 21.2 to 42.5 |

## 2. Legacy Named Zones (Hockey-Specific Positions)

### Issues with Legacy System
1. **Overlapping zones** (not mutually exclusive):
   - `crease` and `goal_crease` are identical
   - Multiple slot zones overlap
   - Points and circles overlap

2. **Incomplete coverage** (not collectively exhaustive):
   - Missing face-off dots
   - Missing blue line positions
   - Gaps between defined zones

### Legacy Zone List
| Zone Name | Center (x, y) | Description | Issues |
|-----------|---------------|-------------|---------|
| slot | (75, 0) | Prime scoring area | Overlaps with low_slot |
| high_slot | (50, 0) | High slot area | |
| low_slot | (85, 0) | Low slot area | Overlaps with slot |
| crease | (86, 0) | Goal crease | Duplicate of goal_crease |
| goal_crease | (86, 0) | Goal crease | Duplicate of crease |
| left_corner | (85, 35) | Left corner | |
| right_corner | (85, -35) | Right corner | |
| ... | ... | ... | ... |

## 3. Recommendations

### For LLM Usage
1. **Use Zone Grid System** for complete coverage and no ambiguity
2. **Map hockey terms to grid zones**:
   - "slot" → `off-right-mid-low` and `off-right-mid-high`
   - "left corner" → `off-right-low` (left side from offensive perspective)
   - "right corner" → `off-right-high` (right side from offensive perspective)

### Zone Selection Logic for LLM
```python
def select_zone(description):
    # Map common hockey terms to grid zones
    mappings = {
        "slot": "off-right-mid-low",
        "high slot": "off-center-right-mid-low",
        "point": "off-center-left-mid-high",
        "left corner": "off-right-low",
        "right corner": "off-right-high",
        "behind net": "off-right-mid-low",
        "defensive zone": "def-*",
        "neutral zone": "neu-*",
        "offensive zone": "off-*"
    }
    # Use mappings or fall back to grid zone names
```

### Visual Reference
```
    DEFENSIVE          NEUTRAL           OFFENSIVE
    
HIGH  [def-left-high]  [neu-left-high]  [neu-right-high]  [off-center-left-high]  [off-center-right-high]  [off-right-high]
      
MID-H [def-left-mid-h] [neu-left-mid-h] [neu-right-mid-h] [off-center-left-mid-h] [off-center-right-mid-h] [off-right-mid-h]
      
MID-L [def-left-mid-l] [neu-left-mid-l] [neu-right-mid-l] [off-center-left-mid-l] [off-center-right-mid-l] [off-right-mid-l]
      
LOW   [def-left-low]   [neu-left-low]   [neu-right-low]   [off-center-left-low]   [off-center-right-low]   [off-right-low]
      
      ←---------------- -100 to 0 ----------------→←---------------- 0 to 100 ----------------→
```

## 4. Conclusion

The **Zone Grid System** provides:
- ✅ **Mutually Exclusive**: No overlapping zones
- ✅ **Collectively Exhaustive**: 100% ice coverage
- ✅ **Clear naming**: Systematic, predictable names
- ✅ **LLM-friendly**: Unambiguous zone selection

The legacy named zones should be mapped to grid zones for consistency while maintaining hockey-specific terminology for user familiarity.
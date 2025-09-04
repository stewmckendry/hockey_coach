#!/usr/bin/env python3
"""
Updated Neutral Zone Positions based on feedback:
1. Offensive zone is RIGHT (+x), Defensive zone is LEFT (-x)
2. Better naming for offside dots
3. Face-off positions for all dots (home and away)
4. Remove duplicate center ice aliases
5. Better queue position names
6. Add wall and blue line references
"""

# CORRECTED: Offensive zone is RIGHT (+x), Defensive zone is LEFT (-x)
# We attack from left to right

NEUTRAL_POSITIONS_UPDATED = {
    # ==========================================
    # CENTER ICE POSITIONS (keep only 2 aliases)
    # ==========================================
    "center ice": (0, 0),
    "center faceoff": (0, 0),
    
    # Center ice face-off positions - HOME TEAM (slight right offset)
    "center faceoff home center": (1, 0),  # Nudged RIGHT for home team attacking right
    "center faceoff home right wing": (1, -12),
    "center faceoff home left wing": (1, 12),
    "center faceoff home right defense": (10.5, -7.5),  # On circle, supporting attack
    "center faceoff home left defense": (10.5, 7.5),
    
    # Center ice face-off positions - AWAY TEAM (slight left offset)
    "center faceoff away center": (-1, 0),  # Nudged LEFT for away team
    "center faceoff away right wing": (-1, -12),
    "center faceoff away left wing": (-1, 12),
    "center faceoff away right defense": (-10.5, -7.5),
    "center faceoff away left defense": (-10.5, 7.5),
    
    # ==========================================
    # OFFSIDE DOTS - NEAR DEFENSIVE ZONE (left side)
    # ==========================================
    "offside dot defensive left": (-20, 22.5),   # Left side, near defensive zone
    "offside dot defensive right": (-20, -22.5),  # Right side, near defensive zone
    
    # Face-off positions at defensive zone offside dots - HOME TEAM
    "offside defensive left faceoff home center": (-19, 22.5),
    "offside defensive left faceoff home wing outside": (-19, 30),
    "offside defensive left faceoff home wing inside": (-19, 15),
    "offside defensive left faceoff home defense left": (-28, 26),
    "offside defensive left faceoff home defense right": (-11, 19),
    
    "offside defensive right faceoff home center": (-19, -22.5),
    "offside defensive right faceoff home wing outside": (-19, -30),
    "offside defensive right faceoff home wing inside": (-19, -15),
    "offside defensive right faceoff home defense left": (-11, -19),
    "offside defensive right faceoff home defense right": (-28, -26),
    
    # Face-off positions at defensive zone offside dots - AWAY TEAM
    "offside defensive left faceoff away center": (-21, 22.5),
    "offside defensive left faceoff away wing outside": (-21, 30),
    "offside defensive left faceoff away wing inside": (-21, 15),
    "offside defensive left faceoff away defense left": (-30, 26),
    "offside defensive left faceoff away defense right": (-13, 19),
    
    "offside defensive right faceoff away center": (-21, -22.5),
    "offside defensive right faceoff away wing outside": (-21, -30),
    "offside defensive right faceoff away wing inside": (-21, -15),
    "offside defensive right faceoff away defense left": (-13, -19),
    "offside defensive right faceoff away defense right": (-30, -26),
    
    # ==========================================
    # OFFSIDE DOTS - NEAR OFFENSIVE ZONE (right side)
    # ==========================================
    "offside dot offensive left": (20, 22.5),   # Left side, near offensive zone
    "offside dot offensive right": (20, -22.5),  # Right side, near offensive zone
    
    # Face-off positions at offensive zone offside dots - HOME TEAM
    "offside offensive left faceoff home center": (21, 22.5),
    "offside offensive left faceoff home wing outside": (21, 30),
    "offside offensive left faceoff home wing inside": (21, 15),
    "offside offensive left faceoff home defense left": (30, 26),
    "offside offensive left faceoff home defense right": (13, 19),
    
    "offside offensive right faceoff home center": (21, -22.5),
    "offside offensive right faceoff home wing outside": (21, -30),
    "offside offensive right faceoff home wing inside": (21, -15),
    "offside offensive right faceoff home defense left": (13, -19),
    "offside offensive right faceoff home defense right": (30, -26),
    
    # Face-off positions at offensive zone offside dots - AWAY TEAM
    "offside offensive left faceoff away center": (19, 22.5),
    "offside offensive left faceoff away wing outside": (19, 30),
    "offside offensive left faceoff away wing inside": (19, 15),
    "offside offensive left faceoff away defense left": (28, 26),
    "offside offensive left faceoff away defense right": (11, 19),
    
    "offside offensive right faceoff away center": (19, -22.5),
    "offside offensive right faceoff away wing outside": (19, -30),
    "offside offensive right faceoff away wing inside": (19, -15),
    "offside offensive right faceoff away defense left": (11, -19),
    "offside offensive right faceoff away defense right": (28, -26),
    
    # ==========================================
    # BOARD AND WALL POSITIONS
    # ==========================================
    "left boards": (0, 42.5),
    "right boards": (0, -42.5),
    "neutral zone left wall": (12, 38),   # Along boards in neutral zone
    "neutral zone right wall": (12, -38),
    
    # ==========================================
    # BLUE LINE REFERENCES (for neutral zone context)
    # ==========================================
    "defensive blue line center": (-25, 0),  # Left side blue line
    "offensive blue line center": (25, 0),   # Right side blue line
    
    # ==========================================
    # BENCH/QUEUE POSITIONS (renamed for clarity)
    # ==========================================
    "home bench left side": (10, 38),   # Home team bench area
    "home bench right side": (10, -38),
    "away bench left side": (-10, 38),  # Away team bench area
    "away bench right side": (-10, -38),
}

# Summary of changes:
print("""
NEUTRAL ZONE POSITION UPDATES:
========================================

1. ✅ FIXED COORDINATE SYSTEM:
   - Offensive zone = RIGHT (+x)
   - Defensive zone = LEFT (-x)
   - Home team attacks left-to-right

2. ✅ RENAMED OFFSIDE DOTS:
   - "offside dot defensive left/right" (near -25 blue line)
   - "offside dot offensive left/right" (near +25 blue line)

3. ✅ ADDED FACEOFF POSITIONS FOR ALL DOTS:
   - 5 positions per team per dot
   - Both home and away team positions
   - Total: 50 new faceoff positions

4. ✅ REMOVED DUPLICATES:
   - Kept only "center ice" and "center faceoff"
   - Removed: "center", "red line", "center ice faceoff"

5. ✅ RENAMED QUEUE POSITIONS:
   - "home bench left/right side"
   - "away bench left/right side"

6. ✅ ADDED NEW POSITIONS:
   - "neutral zone left/right wall"
   - "defensive/offensive blue line center"

TOTAL POSITIONS: 67 (up from 18)
""")

if __name__ == "__main__":
    # Print in format ready to paste into position_mapper.py
    print("\n# Copy this to position_mapper.py:")
    print("NEUTRAL_POSITIONS = {")
    for name, (x, y) in sorted(NEUTRAL_POSITIONS_UPDATED.items()):
        comment = ""
        if "offside" in name and "faceoff" not in name:
            comment = "  # Offside faceoff dot"
        elif "blue line" in name:
            comment = "  # Blue line reference"
        elif "bench" in name:
            comment = "  # Player bench area"
        print(f'    "{name}": ({x}, {y}),{comment}')
    print("}")
# Multiple level maps for variety
LEVEL_MAPS = [
    # Map 1: Classic Maze
    [
        "WWWWWWWWWWWWWWWW",
        "W..............W",
        "W.1.WWW........W",
        "W...WWW..W.....W",
        "W...WWW..W..W..W",
        "W........W..W..W",
        "W....W......W..W",
        "W..............W",
        "W......WW......W",
        "W...........2..W",
        "W..............W",
        "WWWWWWWWWWWWWWWW"
    ],
    
    # Map 2: Arena
    [
        "WWWWWWWWWWWWWWWW",
        "W..............W",
        "W.1............W",
        "W...WW....WW...W",
        "W...WW....WW...W",
        "W..............W",
        "W......WW......W",
        "W......WW......W",
        "W...WW....WW...W",
        "W...WW....WW...W",
        "W............2.W",
        "WWWWWWWWWWWWWWWW"
    ],
    
    # Map 3: Corridors
    [
        "WWWWWWWWWWWWWWWW",
        "W..............W",
        "W.1..WWWWWWW...W",
        "W....W.........W",
        "W....W.....W...W",
        "W..........W...W",
        "W....WWWWW.W...W",
        "W..........W...W",
        "W..........W...W",
        "W..........W...W",
        "W...........2..W",
        "WWWWWWWWWWWWWWWW"
    ],
    
    # Map 4: Center Box
    [
        "WWWWWWWWWWWWWWWW",
        "W..............W",
        "W.1............W",
        "W..............W",
        "W....WWWWWW....W",
        "W....W....W....W",
        "W....W....W....W",
        "W....WWWWWW....W",
        "W..............W",
        "W..............W",
        "W............2.W",
        "WWWWWWWWWWWWWWWW"
    ],
    
    # Map 5: Cross Pattern
    [
        "WWWWWWWWWWWWWWWW",
        "W..............W",
        "W.1...W....W...W",
        "W.....W....W...W",
        "W.....W....W...W",
        "W.....WWWWWW...W",
        "W..............W",
        "W.WWWWWW.......W",
        "W.W....W.......W",
        "W.W....W.......W",
        "W.W....W.....2.W",
        "WWWWWWWWWWWWWWWW"
    ],
    
    # Map 6: Diagonal
    [
        "WWWWWWWWWWWWWWWW",
        "W..............W",
        "W.1.W..........W",
        "W...WW.........W",
        "W....WW........W",
        "W.....WW.......W",
        "W......WW......W",
        "W.......WW.....W",
        "W........WW....W",
        "W.........WW...W",
        "W..........W.2.W",
        "WWWWWWWWWWWWWWWW"
    ],
]

# Default map (for backward compatibility)
LEVEL_MAP = LEVEL_MAPS[0]

# Original smaller map (commented out)
# LEVEL_MAP = [
#     "WWWWWWWWWW",
#     "W.1......W",
#     "W....W...W",
#     "W........W",
#     "W......W.W",
#     "W.....2..W",
#     "WWWWWWWWWW"
# ]
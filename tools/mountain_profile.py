"""Shared mountain and walkable coast profiles in game units (100 units/metre)."""
import math
HILLS = [
    (800, -2100, 2000, 1700, 1100),
    (-2250, 600, 1100, 1700, 650),
    (2350, 300, 1200, 1800, 950),
    (-2050, -2400, 1400, 1300, 1000),
    (-4200, -4050, 2000, 2100, 2350),
    (2200, -4450, 2600, 1600, 2800),
    (4450, 1400, 1800, 2700, 1850),
    (-2900, 3950, 2500, 1500, 1250),
]
BOUNDS = (-5814, 5814, -5952, 5452)

def height(x, y):
    return sum(a * max(0, 1-((x-cx)/rx)**2-((y-cy)/ry)**2)**2
               for cx, cy, rx, ry, a in HILLS)

def expression(x, y):
    return '+'.join(f'{a}*pow(max(0,1-pow((({x})-({cx}))/{rx},2)-pow((({y})-({cy}))/{ry},2)),2)'
                    for cx, cy, rx, ry, a in HILLS)

def coast_edge(x, y):
    """Signed distance to the nearest coast, in game units."""
    return min(
        6400-abs(x)+280*math.sin(math.radians(y*.08))+160*math.sin(math.radians(y*.21)),
        6200-y+250*math.sin(math.radians(x*.09))+120*math.sin(math.radians(x*.23)),
        6700+y+250*math.sin(math.radians(x*.08))+140*math.sin(math.radians(x*.20)),
    )

def floor_height(x, y):
    """The coast mesh's ground height at a game-space XY point."""
    edge = coast_edge(x, y)
    t = min(1, max(0, (edge-1200)/1200))
    inland = t*t*(3-2*t)
    beach = -140+140*min(1, max(0, edge/600))+.16*min(0, edge)
    return height(x, y)*inland+beach

def coast_edge_expression(x, y):
    return (f'min(min(6400-abs({x})+280*sin(ToRad(({y})*0.08))+'
            f'160*sin(ToRad(({y})*0.21)),6200-({y})+'
            f'250*sin(ToRad(({x})*0.09))+120*sin(ToRad(({x})*0.23))),'
            f'6700+({y})+250*sin(ToRad(({x})*0.08))+'
            f'140*sin(ToRad(({x})*0.20)))')

def floor_expression(x, y):
    edge = coast_edge_expression(x, y)
    t = f'max(0,min(1,(({edge})-1200)/1200))'
    return (f'({expression(x, y)})*pow({t},2)*(3-2*{t})'
            f'-140+140*max(0,min(1,({edge})/600))'
            f'+0.16*min(0,({edge}))')

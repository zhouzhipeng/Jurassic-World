"""Shared mountain profile in game units (100 units/metre); no file writes."""
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

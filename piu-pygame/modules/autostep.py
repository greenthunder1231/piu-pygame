from modules.imports import *

def bracketid(n1: int, n2: int) -> bool:
    if n1 == n2:
        return True
    n1, n2 = (min(n1, n2), max(n1, n2))
    n = (n1, n2)
    validpairs = [
        (0, 2),
        (1, 2),
        (2, 3),
        (2, 4),
        (3, 6),
        (4, 5),
        (5, 7),
        (6, 7),
        (7, 8),
        (7, 9)
    ]
    if not n in validpairs:
        return None
    return validpairs.index(n)

def pairs(*panels) -> list:
    return [(panels[i], panels[i + 1]) for i in range(len(panels) - 1)]

def bracketpriority(*panels: int) -> list | None:
    pans = list(panels)
    final = []
    priority = [
        (1, 2),
        (2, 4),
        (5, 7),
        (7, 8),
        (0, 2),
        (2, 3),
        (6, 7),
        (7, 9),
        (4, 5),
        (3, 6)
    ]
    combinations = pairs(*pans)
    for p in priority:
        i = 0
        while i < len(combinations):
            if combinations[i] == p:
                final.append(combinations[i])
                for j in combinations[i]:
                    pans.remove(j)
                    combinations = pairs(*pans)
            i += 1
    final.extend(pans)
    if len(final) > 2:
        print(f'Panels cannot be bracketed: {final}')
        return None
    final = [(bracketid(*i) if isinstance(i, (list, tuple)) else i) for i in final]
    return final

def easeinout(t: float) -> float:
    if t <= 0:
        return float(0)
    if t >= 1:
        return float(1)
    return 3 * (t ** 2) - 2 * (t ** 3)

def rotatept(p1: tuple, p2: tuple, theta: float) -> tuple:
    x, y = p1
    cx, cy = p2
    rx = (x - cx) * math.cos(theta) - (y - cy) * math.sin(theta) + cx
    ry = (x - cx) * math.sin(theta) + (y - cy) * math.cos(theta) + cy
    return (rx, ry)
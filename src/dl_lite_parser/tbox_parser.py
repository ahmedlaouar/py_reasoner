from dl_lite.axiom import Axiom, Modifier, Side
from dl_lite.tbox import TBox

def process_line(line):
    splitted_line = line.split('<')
    sides = []
    for side in splitted_line:
        modifiers = []
        temp = side
        if "NOT" in temp:
            modifiers.append(Modifier.negation)
            temp = temp.replace("NOT", "")
        if "EXISTS" in temp:
            modifiers.append(Modifier.projection)
            temp = temp.replace("EXISTS", "")
        if "INV" in temp:
            modifiers.append(Modifier.inversion)
            temp = temp.replace("INV", "")
        side_name = temp.strip()
        sides.append(Side(side_name,modifiers.copy()))
    return Axiom(sides[0],sides[1])

def read_tbox(file_path: str):
    tbox = TBox()
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip() == "BEGINTBOX" or line.strip() == "ENDTBOX":
                continue
            axiom = process_line(line) 
            tbox.add_axiom(axiom)
    return tbox
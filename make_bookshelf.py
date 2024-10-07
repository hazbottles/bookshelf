"""
Usage:
  python3 make_bookshelf.py > bookshelf.tex; pdflatex bookshelf.tex
"""
class Panel:
    def __init__(self, width, height, fill=None):
        self.width = width
        self.height = height 
        self.fill = fill
             
    def draw(self, scale):
        drawcmd = r"\filldraw[draw=black,fill={}]".format(self.fill) if self.fill else r"\draw" 
        return r"{} (0,0) rectangle ({},{});".format(drawcmd, self.width/scale, self.height/scale)

class Door:
    def __init__(self, width, height, doornob_side, border=50, doornob_radius=10):
        self.width = width
        self.height = height 
        self.doornob_side = doornob_side
        self.border = border
        self.doornob_radius = doornob_radius
             
    def draw(self, scale):
        w, h, i, r = self.width/scale, self.height/scale, self.border/scale, self.doornob_radius/scale
        res = r"\draw (0,0) rectangle ({},{});".format(w, h) + "\n"
        res += r"\draw ({},{}) rectangle ({},{});".format(i, i, w-i, h-i) + "\n"
        if self.doornob_side == "left":
            res += r"\draw ({}, {}) circle ({});".format(w - i/2, h/2, r)
        elif self.doornob_side == "right":
            res += r"\draw ({}, {}) circle ({});".format(i/2, h/2, r)
        else:
            raise ValueError(self.doornob_side)
        return res

class Shelves:
    def __init__(self, width, height, shelve_spacing, shelve_thick, closed):
        self.width = width
        self.height = height 
        self.shelve_spacing = shelve_spacing
        self.shelve_thick = shelve_thick
        self.closed = closed
             
    def draw(self, scale):
        w, h, st = (
            round(self.width/scale, 2), round(self.height/scale, 2), 
             round(self.shelve_thick/scale, 2),
        )

        sss = self.shelve_spacing
        if isinstance(sss, (int, float)):
            sss = [sss]
         

        res = r"\draw ({}, {}) -- ({}, {});".format(st, 0, st, h) + "\n"
        res += r"\draw ({}, {}) -- ({}, {});".format(w-st, 0, w-st, h) + "\n"
        if self.closed in ["left", "both"]:
            res += r"\draw ({}, {}) -- ({}, {});".format(w, 0, w, h) + "\n"
        if self.closed in ["right", "both"]:
            res += r"\draw ({}, {}) -- ({}, {});".format(0, 0, 0, h) + "\n"

        ss = round(sss[0]/scale, 2)
        ch = ss
        count = 0
        while ch < h:
            res += r"\draw ({},{}) rectangle ({},{});".format(
                st, round(ch-st, 2), round(w-st, 2), round(ch, 2)
            ) + "\n"
            count += 1
            ss = round(sss[min([count, len(sss)-1])]/scale, 2)
            ch += ss

        return res[:-1]


W = 3220
H = 2700


skirting_height = 150
crown_height = 150
base_height = 720
counter_height = 50
counter_overhang = 20
shelve_width = 20
shelving_spacing = [500, 300]
# shelving_height determined by these
base = [  # right to left
    Panel(100, base_height),
    
    Door(600, base_height, "left"),
    Door(450, base_height, "left"),
    Door(450, base_height, "right"),
    Door(450, base_height, "left"),
    Door(450, base_height, "right"),
    Door(600, base_height, "right"),
]
shelving_height = H - base_height - counter_height - crown_height - skirting_height
top = [
    Panel(100, shelving_height),
    # TODO: add option for changing shelf heights
    Shelves(600, shelving_height, shelving_spacing, 20, closed=None),
    Shelves(900, shelving_height, shelving_spacing, 20, closed=None),
    Shelves(900, shelving_height, shelving_spacing, 20, closed=None),
    Shelves(600, shelving_height, shelving_spacing, 20, closed="left"),
]
total_width = sum([b.width for b in base])
rows = [
    [Panel(total_width + counter_overhang, skirting_height, "white"),],
    base,
    [Panel(total_width + counter_overhang, counter_height, "white")],
    top,
    [Panel(total_width, crown_height)],
]

tex = r"""\documentclass{article}
\usepackage{tikz}

\begin{document}

\begin{tikzpicture}[scale=0.4, xscale=-1]
"""

xoffset = yoffset = 0
scale = 100  # hack, 3220 -> 32.2
tex += "    % wall\n"
tex += r"    \draw (0,0) rectangle ({:.2f},{:.2f});".format(W/scale, H/scale) + "\n"
tex += r"    \filldraw[draw=black,fill=gray] ({:.2f},{:.2f}) rectangle ({:.2f},{:.2f});".format(
    total_width/scale, 0, W/scale, H/scale) + "\n"
for i, row in enumerate(rows):
    xoffset = 0
    tex += f"\n    % ROW={i}\n"
    for ii, box in enumerate(row):
        tex += f"    % box={ii}\n"
        tex += "    " + box.draw(scale).replace("\n", "\n    ") + "\n"
        tex += r"    \tikzset{{shift={{({},{})}}}}".format(box.width/scale, 0) + "\n"
        xoffset += box.width/scale
    tex += r"    \tikzset{{shift={{({},{})}}}}".format(-xoffset, box.height/scale) + "\n"


tex+=r"""
\end{tikzpicture}

\end{document}"""
print(tex)
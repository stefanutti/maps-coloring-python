import math
from PIL import Image, ImageDraw
from pathlib import Path

patterns = [
    ["R","G","R","G","R","G"],
    ["R","G","R","G","R","B"],
    ["R","G","R","G","B","G"],
    ["R","G","R","B","R","G"],
    ["R","G","R","B","R","B"],
    ["R","G","R","B","G","B"],
    ["R","G","B","R","G","B"],
    ["R","G","B","R","B","G"],
    ["R","G","B","G","R","G"],
    ["R","G","B","G","R","B"],
    ["R","G","B","G","B","G"],
]

color_map = {
    "R": (220, 50, 47),
    "G": (133, 153, 0),
    "B": (38, 139, 210),
}
all_colors = {"R","G","B"}

cols_per_row=[4,4,3]
cell_w,cell_h=240,220
margin_x,margin_y=50,50

img_w=margin_x*2+max(cols_per_row)*cell_w
img_h=margin_y*2+len(cols_per_row)*cell_h

img=Image.new("RGB",(img_w,img_h),"white")
draw=ImageDraw.Draw(img)

def hex_vertices(cx,cy,r):
    angles=[120,60,0,300,240,180]
    return [(cx+r*math.cos(math.radians(a)), cy-r*math.sin(math.radians(a))) for a in angles]

def draw_hex(cx,cy,r,pattern):
    pts=hex_vertices(cx,cy,r)
    center=(cx,cy)

    edge_pairs=[(0,1),(1,2),(2,3),(4,3),(5,4),(0,5)]
    for (i,j),c in zip(edge_pairs,pattern):
        draw.line([pts[i],pts[j]],fill=color_map[c],width=12)

    vertex_edges={0:(5,0),1:(0,1),2:(1,2),3:(2,3),4:(3,4),5:(4,5)}
    inward_len=35  # longer than before

    for v_idx,(e1,e2) in vertex_edges.items():
        c1,c2=pattern[e1],pattern[e2]
        missing=list(all_colors-{c1,c2})[0]

        x,y=pts[v_idx]
        dx,dy=center[0]-x,center[1]-y
        norm=math.hypot(dx,dy)
        ux,uy=dx/norm,dy/norm

        x2=x+inward_len*ux
        y2=y+inward_len*uy

        draw.line([(x,y),(x2,y2)],fill=color_map[missing],width=8)

    for x,y in pts:
        draw.ellipse((x-7,y-7,x+7,y+7),fill="black")

idx=0
for row,ncols in enumerate(cols_per_row):
    row_w=ncols*cell_w
    x0=(img_w-row_w)//2+cell_w//2
    cy=margin_y+row*cell_h+cell_h//2

    for col in range(ncols):
        cx=x0+col*cell_w
        draw_hex(cx,cy,70,patterns[idx])
        idx+=1

out_png="11_hexagons_longer_inner_segments.png"
img.save(out_png)

# SVG
def svg_hex(cx,cy,r,pattern):
    pts=hex_vertices(cx,cy,r)
    center=(cx,cy)
    edge_pairs=[(0,1),(1,2),(2,3),(4,3),(5,4),(0,5)]
    parts=[]

    for (i,j),c in zip(edge_pairs,pattern):
        x1,y1=pts[i]
        x2,y2=pts[j]
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="rgb{color_map[c]}" stroke-width="12" stroke-linecap="round"/>')

    vertex_edges={0:(5,0),1:(0,1),2:(1,2),3:(2,3),4:(3,4),5:(4,5)}
    inward_len=35

    for v_idx,(e1,e2) in vertex_edges.items():
        c1,c2=pattern[e1],pattern[e2]
        missing=list(all_colors-{c1,c2})[0]

        x,y=pts[v_idx]
        dx,dy=center[0]-x,center[1]-y
        norm=math.hypot(dx,dy)
        ux,uy=dx/norm,dy/norm
        x2=x+inward_len*ux
        y2=y+inward_len*uy

        parts.append(f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="rgb{color_map[missing]}" stroke-width="8" stroke-linecap="round"/>')

    for x,y in pts:
        parts.append(f'<circle cx="{x}" cy="{y}" r="7" fill="black"/>')

    return "\n".join(parts)

svg_parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{img_w}" height="{img_h}" viewBox="0 0 {img_w} {img_h}">',
           '<rect width="100%" height="100%" fill="white"/>']

idx=0
for row,ncols in enumerate(cols_per_row):
    row_w=ncols*cell_w
    x0=(img_w-row_w)//2+cell_w//2
    cy=margin_y+row*cell_h+cell_h//2

    for col in range(ncols):
        cx=x0+col*cell_w
        svg_parts.append(svg_hex(cx,cy,70,patterns[idx]))
        idx+=1

svg_parts.append("</svg>")

out_svg="11_hexagons_longer_inner_segments.svg"
Path(out_svg).write_text("\n".join(svg_parts))

print(out_png)
print(out_svg)
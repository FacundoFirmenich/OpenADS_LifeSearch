"""Vector print projections; counts are checked against the source graph."""
import json
from pathlib import Path

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor, white

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/"paper/figures"
M=json.loads((ROOT/"companion/graph_model.json").read_text())
N={n["id"]:n for n in M["nodes"]}
assert len([n for n in N.values() if n["kind"]=="contrast"])==90
assert sum(n["kind"]=="contrast" and int(n["data"]["summary"]["joint_sign"])!=0 for n in N.values())==16
assert sum(n["kind"]=="anchor" and n["data"]["status"]=="NOT_IN_ARCHIVE" for n in N.values())==2

INK="#102838"; DIM="#395367"; TEAL="#05645e"; ROSE="#934454"; GOLD="#79520b"; BLUE="#325e89"
def text(c,s,x,y,size=10,color=INK,bold=False):
    c.setFillColor(HexColor(color));c.setFont("Helvetica-Bold" if bold else "Helvetica",size)
    c.drawString(x,y,s)
def card(c,x,y,w,h,k,title,lines,theme):
    c.setFillColor(HexColor("#f4f8fa"));c.setStrokeColor(HexColor("#c5d7e0"))
    c.roundRect(x,y,w,h,7,stroke=1,fill=1)
    text(c,k,x+11,y+h-16,8,theme,True)
    text(c,title,x+11,y+h-33,12,INK,True)
    for i,line in enumerate(lines):text(c,line,x+11,y+h-50-12*i,9,DIM)
def bar(c,s,sub,y):
    c.setFillColor(HexColor("#e7f2f4"));c.roundRect(12,y,500,35,6,stroke=0,fill=1)
    text(c,s,23,y+21,10,INK,True);text(c,sub,23,y+9,8,DIM)
def arrow(c,x,y,x2,y2,col=BLUE,dash=False):
    c.setStrokeColor(HexColor(col));c.setFillColor(HexColor(col));c.setLineWidth(1.2)
    if dash:c.setDash(3,2)
    c.line(x,y,x2,y2);c.setDash()
    import math
    a=math.atan2(y2-y,x2-x); p=c.beginPath();p.moveTo(x2,y2)
    for b in (a+.46,a-.46):p.lineTo(x2-5*math.cos(b),y2-5*math.sin(b))
    p.close();c.drawPath(p,stroke=0,fill=1)

def abstract():
    c=Canvas(str(FIG/"visual_abstract.pdf"),pagesize=(524,156),invariant=1);c.setTitle("P02 visual abstract")
    text(c,"What the archive captures — and what the comparisons support",12,140,12,INK,True)
    card(c,12,47,158,78,"PHYSICAL EVIDENCE","15 named studies",["Ocean, chemistry and","access are distinct."],TEAL)
    card(c,183,47,158,78,"ARCHIVE CHECK","2 absent / 13 found",["Enceladus imaging","Europa water-vapour study"],ROSE)
    card(c,354,47,158,78,"TRAJECTORY CHECK","16 directions supported",["0 of 8 reversals supported","in both directions"],BLUE)
    bar(c,"One archive, two different checks","Neither check measures the completeness of the literature or ranks worlds for life.",7)
    c.showPage();c.save()

def epistemic():
    c=Canvas(str(FIG/"epistemic_graph_print.pdf"),pagesize=(524,247),invariant=1);c.setTitle("P02 epistemic graph")
    text(c,"Follow each claim to its evidence and its limit",12,230,13,INK,True)
    card(c,12,150,150,67,"PHYSICAL RECORD","Primary studies",["Named observations"],TEAL)
    card(c,187,150,150,67,"HISTORICAL ARCHIVE","Identity audit",["DOI, bibcode and title"],BLUE)
    card(c,362,150,150,67,"SCOPED RESULT","Two omissions",["Not an estimate of recall"],ROSE)
    card(c,12,64,150,67,"ANALYSIS INPUT","Shared paper draws",["Same paper, same draw"],BLUE)
    card(c,187,64,150,67,"JOINT RULE","AND: two requirements",["Unanimous signs + bands"],GOLD)
    card(c,362,64,150,67,"SCOPED RESULT","16 local directions",["Not a habitability rank"],TEAL)
    arrow(c,162,183,186,183);arrow(c,337,183,361,183)
    arrow(c,162,97,186,97);arrow(c,337,97,361,97)
    arrow(c,261,149,261,132,ROSE,True)
    bar(c,"Keep retrieval error outside the conditional bands","Arrows show operations or conditions, not causal effects or comparable evidence scores.",12)
    c.showPage();c.save()

if __name__=="__main__":
    abstract();epistemic()

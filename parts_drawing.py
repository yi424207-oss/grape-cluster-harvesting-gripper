"""Dimensioned concept sheets tied to the values in model.py (units mm)."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

ROOT=Path(__file__).resolve().parent
fig,axs=plt.subplots(2,2,figsize=(11.7,8.3),dpi=220)
def setup(ax,xlim,ylim,title):
    ax.set_aspect('equal');ax.set_xlim(*xlim);ax.set_ylim(*ylim);ax.axis('off')
    ax.set_title(title,fontsize=11,fontweight='bold',color='#173b5a',pad=8)
def dim(ax,a,b,label,offset=(0,0)):
    a=(a[0]+offset[0],a[1]+offset[1]);b=(b[0]+offset[0],b[1]+offset[1])
    ax.annotate('',a,b,arrowprops=dict(arrowstyle='<->',lw=.8,color='#3b5364'))
    ax.text((a[0]+b[0])/2,(a[1]+b[1])/2,label,fontsize=8,ha='center',va='bottom',color='#253d4d')

ax=axs[0,0];setup(ax,(-45,45),(85,205),'P01 MOUNT PLATE  front view Y-Z')
ax.add_patch(Rectangle((-29,105),58,80,fill=False,lw=2,edgecolor='#205b92'))
for y in (-19,19):
    for z in (120,170):ax.add_patch(Circle((y,z),3.2,fill=False,lw=1.4,edgecolor='#205b92'))
dim(ax,(-29,195),(29,195),'58');dim(ax,(38,105),(38,185),'80')
dim(ax,(-19,98),(19,98),'38 c-c')
ax.text(0,88,'4 x dia. 6.4 through  |  Z pitch 50  |  thickness 9',ha='center',fontsize=8)

ax=axs[0,1];setup(ax,(-62,62),(-45,55),'P03/P04 STEM JAWS  top view X-Y')
for y in (-18,18):
    ax.add_patch(Rectangle((-14.5,y-6.5),29,13,fill=False,lw=2,edgecolor='#205b92'))
for y in (-10.25,10.25):
    ax.add_patch(Rectangle((-12,y-1.25),24,2.5,facecolor='#5bb4a5',alpha=.8))
dim(ax,(-14.5,40),(14.5,40),'29')
dim(ax,(33,-9),(33,9),'18 open gap')
ax.text(0,-37,'Jaw height 22  |  each pad 24 x 2.5 x 16',ha='center',fontsize=8)

ax=axs[1,0];setup(ax,(15,159),(-169,132),'P13/P14 COMPOSITE FINGER  front X-Z')
P=[(120,109),(116,62),(107,0),(91,-68),(63,-112),(38,-133)]
ax.plot(*zip(*P),color='#246aa6',lw=13,solid_capstyle='round')
ax.plot(*zip(*P),color='#53b49f',lw=3,solid_capstyle='round')
for x,z in P:ax.add_patch(Circle((x,z),2.2,color='#173b5a'))
dim(ax,(146,-133),(146,109),'242 Z span')
dim(ax,(38,-153),(120,-153),'82 inward')
ax.text(64,100,'outer R12 / core R10',fontsize=8)
ax.text(38,-164,'Mirrored four times. Coordinates are in model.py.',fontsize=8)

ax=axs[1,1];setup(ax,(-95,95),(-77,82),'P16 SPLIT SLING  top view X-Y')
for sx in (-1,1):
    ax.add_patch(Rectangle((sx*34-32.5,-39),65,78,fill=False,lw=2,edgecolor='#5aa89e'))
ax.plot([0,0],[-56,56],ls='--',lw=.8,color='#71828e')
dim(ax,(-66.5,57),(-1.5,57),'65')
dim(ax,(-78,-39),(-78,39),'78')
dim(ax,(-1.5,-52),(1.5,-52),'3 gap')
ax.text(0,-68,'2 panels  |  thickness 4  |  closed configuration',ha='center',fontsize=8)

fig.suptitle('SELECTED PART DRAWINGS  |  concept dimensions in mm',fontsize=15,fontweight='bold',color='#18344a')
fig.text(.5,.018,'Nominal geometry only. Fits, tolerances, materials and joining methods require prototype verification.',ha='center',fontsize=9,color='#526273')
fig.tight_layout(rect=[0,.04,1,.94]);fig.savefig(ROOT/'selected_parts.png',bbox_inches='tight');plt.close(fig)

styles=getSampleStyleSheet()
story=[Paragraph('Grape end effector  -  concept drawing appendix',styles['Title']),Spacer(1,14)]
for file,width in [('general_arrangement.png',450),('selected_parts.png',450)]:
    from PIL import Image as PIL
    with PIL.open(ROOT/file) as im:ratio=im.height/im.width
    story.append(Image(str(ROOT/file),width=width,height=width*ratio))
    story.append(Spacer(1,14))
SimpleDocTemplate(str(ROOT/'关键零部件尺寸方案图.pdf'),pagesize=A4,leftMargin=62,rightMargin=62,topMargin=58,bottomMargin=58).build(story)
print('Wrote selected parts drawing')

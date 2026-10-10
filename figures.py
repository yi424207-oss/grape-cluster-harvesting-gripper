"""Render the generated solid model and draw dimensioned orthographic sheets."""
from pathlib import Path
import numpy as np
import cadquery as cq
from model import parts
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Ellipse

ROOT=Path(__file__).resolve().parent
PALETTE={'soft':'#4aa897','metal':'#b3bfca','frame':'#2d65a2','drive':'#d99535'}

def category(name):
    if 'soft_finger' in name or 'soft_sling' in name or 'pad' in name: return 'soft'
    if 'blade' in name: return 'metal'
    if 'actuator' in name or 'drive' in name: return 'drive'
    return 'frame'

def get_meshes():
    meshes=[]
    for name,shape in parts.items():
        vertices, triangles=shape.tessellate(2.0,0.4)
        a=np.array([v.toTuple() for v in vertices]); t=np.array(triangles,dtype=int)
        if len(t)>3500: t=t[::max(1,len(t)//3500)]
        meshes.append((name,a[t],category(name)))
    return meshes

def figure_3d(meshes):
    fig=plt.figure(figsize=(10.2,8.2),dpi=210,facecolor='white')
    ax=fig.add_subplot(111,projection='3d',computed_zorder=False)
    # Painter order is a visual aid; STEP remains the authoritative geometry.
    for n,tris,cat in meshes:
        poly=Poly3DCollection(tris,facecolors=PALETTE[cat],edgecolors='none',linewidths=0,alpha=.96)
        ax.add_collection3d(poly)
    ax.set_xlim(-190,175);ax.set_ylim(-135,135);ax.set_zlim(-155,205)
    ax.set_box_aspect((365,270,360),zoom=.85)
    ax.view_init(elev=21,azim=-58)
    for axis in [ax.xaxis,ax.yaxis,ax.zaxis]: axis.pane.fill=False;axis.line.set_color('#dddddd')
    ax.grid(False);ax.set_xticks([]);ax.set_yticks([]);ax.set_zticks([])
    ax.text2D(.04,.94,'GRAPE CLUSTER HARVESTING END EFFECTOR',transform=ax.transAxes,fontweight='bold',fontsize=12,color='#18344a')
    ax.text2D(.04,.90,'Concept assembly - closed pose - millimetres',transform=ax.transAxes,fontsize=9,color='#516372')
    ax.text2D(.03,.08,'Blue  frame & clamp     Teal  compliant supports     Grey  blades     Ochre  actuator envelopes',transform=ax.transAxes,fontsize=8,color='#42586a')
    fig.savefig(ROOT/'assembly_view.png',bbox_inches='tight',pad_inches=.12)
    plt.close(fig)

def outline(ax, dims):
    ax.set_xlim(*dims[0]);ax.set_ylim(*dims[1]);ax.set_aspect('equal');ax.axis('off')
    ax.axhline(0,color='#dae0e6',lw=.5);ax.axvline(0,color='#dae0e6',lw=.5)

def fig_orthographic():
    fig,axes=plt.subplots(1,2,figsize=(11.2,7.2),dpi=210)
    ax=axes[0];outline(ax,((-207,186),(-173,232)))
    # Front projection X/Z: fixture, cross beam, clamps, fingers, sling.
    ax.plot([-183,-183],[105,185],color=PALETTE['frame'],lw=7)
    ax.plot([-170,12],[183,183],color=PALETTE['frame'],lw=12)
    ax.plot([-125,125],[177,177],color=PALETTE['frame'],lw=9)
    for sx in (-1,1):
        ax.plot([sx*120,sx*120],[107,177],color=PALETTE['frame'],lw=9)
        xy=np.array([[sx*120,109],[sx*116,62],[sx*107,0],[sx*91,-68],[sx*63,-112],[sx*38,-133]])
        ax.plot(xy[:,0],xy[:,1],color=PALETTE['soft'],lw=10,solid_capstyle='round')
        ax.plot([sx*1.5,sx*66],[-139,-139],color=PALETTE['soft'],lw=5)
    ax.add_patch(Ellipse((0,-25),194,216,facecolor='#91af40',alpha=.13,edgecolor='#7d9734',lw=1.4))
    ax.add_patch(plt.Rectangle((-15,136),30,22,facecolor=PALETTE['frame']))
    ax.add_patch(plt.Rectangle((-15,164),30,2,facecolor=PALETTE['metal']))
    ax.annotate('',(-110,105),(110,105),arrowprops={'arrowstyle':'<->','color':'#34495b','lw':.9})
    ax.text(0,112,'240 mm carrier span',ha='center',fontsize=9)
    ax.annotate('',(166,-139),(166,183),arrowprops={'arrowstyle':'<->','color':'#34495b','lw':.9})
    ax.text(171,18,'322 mm working height',rotation=90,va='center',fontsize=9)
    ax.text(0,209,'FRONT   X-Z',ha='center',fontweight='bold',fontsize=12)

    ax=axes[1];outline(ax,((-172,172),(-160,170)))
    # Plan X/Y: two carriers and four support fingers. Stem in the centre.
    ax.plot([-130,130],[0,0],color=PALETTE['frame'],lw=10)
    for sx in (-1,1):
        ax.plot([sx*120,sx*120],[-73,73],color=PALETTE['frame'],lw=9)
        for sy in (-1,1):
            ax.plot([sx*120,sx*116,sx*107,sx*91,sx*63,sx*38],
                    [sy*62,sy*82,sy*79,sy*68,sy*48,sy*32],color=PALETTE['soft'],lw=7)
    ax.add_patch(Ellipse((0,0),194,170,fill=False,edgecolor='#7d9734',lw=1.3,ls='--'))
    ax.add_patch(Ellipse((0,0),15,15,fill=False,edgecolor='#34495b',lw=1))
    ax.annotate('',(-97,-119),(97,-119),arrowprops={'arrowstyle':'<->','color':'#34495b','lw':.9})
    ax.text(0,-136,'Fruit envelope: 200 mm max dia.',ha='center',fontsize=9)
    ax.text(0,147,'TOP   X-Y',ha='center',fontweight='bold',fontsize=12)
    fig.suptitle('GENERAL ARRANGEMENT   |   closed position   |   dimensional concept',fontsize=13,fontweight='bold',color='#18344a')
    fig.text(.5,.025,'The 200 mm dotted boundary is a fruit sizing envelope, not a contact-force simulation.',ha='center',fontsize=9,color='#516372')
    fig.tight_layout(rect=[0,.05,1,.95]);fig.savefig(ROOT/'general_arrangement.png',bbox_inches='tight');plt.close(fig)

if __name__=='__main__':
    figure_3d(get_meshes());fig_orthographic();print('Rendered figures')

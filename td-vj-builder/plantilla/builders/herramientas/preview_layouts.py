# preview_layouts.py — render de comprobación FUERA de TD (moderngl + EGL por software, cámaras sintéticas).
# No sustituye a TouchDesigner: solo revisa composición. Requiere: pip install moderngl pillow numpy
import moderngl, numpy as np, re, sys, ast, os
from PIL import Image, ImageDraw
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
OUT=os.path.join(ROOT,"research","previews"); os.makedirs(OUT,exist_ok=True)
W,H=960,540
def cams():
    out=[]
    cols=[(220,80,70),(70,170,220),(240,200,60),(110,200,120),(190,110,220)]
    for i,c in enumerate(cols):
        im=Image.new('RGB',(640,360))
        px=np.zeros((360,640,3),np.uint8)
        y=np.linspace(0,1,360)[:,None]
        for k in range(3): px[:,:,k]=(c[k]*(0.45+0.55*(1-y))).astype(np.uint8)
        im=Image.fromarray(px); d=ImageDraw.Draw(im)
        d.ellipse((260,70,380,190),fill=(245,225,200)); d.rectangle((220,200,420,360),fill=(30,30,40))
        d.text((20,20),"CAM %d"%(i+1),fill=(255,255,255))
        d.rectangle((0,0,639,359),outline=(255,255,255),width=4)
        out.append(np.asarray(im.transpose(Image.FLIP_TOP_BOTTOM)))
    return out
PRE="""#version 430
in vec2 vUV;
uniform sampler2D sTD2DInputs[5];
uniform vec4 uTDOutputInfo;
vec4 TDOutputSwizzle(vec4 c){return c;}
"""
VS="""#version 430
in vec2 p; out vec2 vUV; void main(){vUV=p*0.5+0.5; gl_Position=vec4(p,0,1);}"""
def cfg(path):
    t=ast.parse(open(path).read())
    for n in t.body:
        if isinstance(n,ast.Assign) and getattr(n.targets[0],'id','')=='CONFIG':
            return {k.arg:ast.literal_eval(k.value) for k in n.value.keywords}
ctx=moderngl.create_context(standalone=True,backend='egl')
tex=[]
for a in cams():
    t=ctx.texture((640,360),3,a.tobytes()); t.filter=(moderngl.LINEAR,moderngl.LINEAR); tex.append(t)
def render(name,t,over=None):
    c=cfg(f"{ROOT}/builders/layouts/setup_layout_{name}.py")
    src=open(f"{ROOT}/"+c['shader']).read()
    src=re.sub(r'^\s*#version.*$','',src,flags=re.M)
    prog=ctx.program(vertex_shader=VS,fragment_shader=PRE+src)
    def S(k,v):
        if k in prog:
            try: prog[k].value=v
            except Exception as e: print('set',k,e)
    S('uTime',t);S('uResolution',(W,H));S('uCamCount',5);S('uCamfit',0);S('uCamAspect',16/9);S('uHeroIndex',0)
    S('uTDOutputInfo',(1/W,1/H,W,H))
    for s in list(c['five_slots'])+list(c.get('extras',[])):
        v=s[4]
        if over and s[1] in over: v=over[s[1]]
        S(s[1],int(v) if prog[s[1]].gl_type==0x1404 else float(v)) if s[1] in prog else None
    for col in c.get('colors',[]): S(col[1],col[2])
    for i,x in enumerate(tex): x.use(i)
    prog['sTD2DInputs'].value=list(range(5))
    vb=ctx.buffer(np.array([-1,-1,1,-1,-1,1,1,1],'f4').tobytes())
    vao=ctx.simple_vertex_array(prog,vb,'p')
    fbo=ctx.simple_framebuffer((W,H)); fbo.use(); fbo.clear(0,0,0,1); vao.render(moderngl.TRIANGLE_STRIP)
    return Image.frombytes('RGB',(W,H),fbo.read()).transpose(Image.FLIP_TOP_BOTTOM)
names=["rs_playeras","rs_columnas","rs_luna","rs_late_show","rs_riff","rs_corriente"]
imgs=[]
for n in names:
    im=render("layout_"+n if False else n,1.7); im.save(f"{OUT}/{n}.png"); imgs.append(im)
cw,ch=640,360
sheet=Image.new('RGB',(cw*3,ch*2))
for i,im in enumerate(imgs):
    sheet.paste(im.resize((cw,ch)),((i%3)*cw,(i//3)*ch))
sheet.save(f"{OUT}/contact_sheet.png"); print("ok")

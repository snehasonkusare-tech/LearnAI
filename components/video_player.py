import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import streamlit.components.v1 as components
import json
import re


def clean_text(text: str, limit: int = 200) -> str:
    if not text:
        return ""
    text = re.sub(r'\*{1,2}|_{1,2}', '', text)
    text = re.sub(r'\s+', ' ', text.replace('\n', ' ')).strip()
    return text[:limit]


def parse_nodes(visual: str, chapter_title: str) -> list:
    """Extract node labels from ASCII diagram."""
    found = re.findall(r'\[([^\]]{2,26})\]|\(([^)]{2,26})\)', visual)
    nodes = []
    for f in found:
        label = (f[0] or f[1]).strip()
        if label:
            nodes.append(re.sub(r'\*{1,2}|_{1,2}', '', label).strip())
    nodes = list(dict.fromkeys(nodes))[:7]
    if not nodes:
        nodes = [chapter_title, "Core Process", "Key Output"]
    return nodes


def parse_concepts(key_concepts: list) -> list:
    ICONS = ["💡", "⚡", "🔑", "🎯", "🔄", "📌"]
    cards = []
    for i, c in enumerate(key_concepts[:6]):
        c = re.sub(r'\*{1,2}|_{1,2}', '', c).strip()
        if ': ' in c:
            name, desc = c.split(': ', 1)
        else:
            name, desc = c[:30], c
        cards.append({
            "icon": ICONS[i % len(ICONS)],
            "title": clean_text(name, 24),
            "desc": clean_text(desc, 65)
        })
    return cards


def parse_steps(example: str) -> list:
    steps = []
    EMOJIS = ["🔵", "🟡", "🟢", "🔴", "🟣", "🟠"]
    for line in example.split('\n'):
        line = line.strip()
        if re.match(r'^step\s*\d', line.lower()):
            parts = line.split(':', 1)
            label = clean_text(parts[0], 14) if parts else "Step"
            body = clean_text(parts[1], 55) if len(parts) > 1 else ""
            steps.append({"label": label, "body": body, "icon": EMOJIS[len(steps) % len(EMOJIS)]})
    if not steps:
        for i, line in enumerate([l.strip() for l in example.split('\n') if len(l.strip()) > 15][:5]):
            steps.append({"label": f"Step {i+1}", "body": clean_text(line, 55), "icon": EMOJIS[i % len(EMOJIS)]})
    return steps[:5]


def build_scenes(content: dict, chapter_title: str, topic: str) -> list:
    nodes = parse_nodes(content.get("visual", ""), chapter_title)
    concepts = parse_concepts(content.get("key_concepts", []))
    steps = parse_steps(content.get("example", ""))

    analogy = content.get("analogy", "")
    analogy_short = clean_text(analogy.split('.')[0] if analogy else f"Think of {chapter_title} like a real-world process.", 160)

    takeaway = content.get("key_takeaway", "")
    takeaway_short = clean_text(takeaway, 160) if takeaway else f"You now understand {chapter_title}!"

    exp_sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', content.get("explanation", "")) if len(s.strip()) > 20]
    explain_short = clean_text(exp_sents[0] if exp_sents else f"{chapter_title} is a key concept in {topic}.", 150)

    # Chapter-specific flow diagram data
    flow_data = content.get('flow_diagram', {})
    flow_nodes = flow_data.get('nodes', [])
    flow_conns = flow_data.get('connections', [])
    # Fallback if AI didn't give us flow data
    if not flow_nodes:
        flow_nodes = [
            {"id": i+1, "label": n, "desc": "", "icon": ["📥","⚙️","🔄","📤","✅"][i % 5]}
            for i, n in enumerate(nodes[:5])
        ]
        flow_conns = [{"from": i+1, "to": i+2} for i in range(len(flow_nodes)-1)]

    return [
        {
            "type": "intro",
            "speech": f"Hi! I'm ARIA. Today I'll SHOW you how {chapter_title} works. Watch the diagram!",
            "topic": clean_text(topic, 30),
            "chapter": clean_text(chapter_title, 40),
            "bg": "dark",
            "duration": 4500
        },
        {
            "type": "mindmap",
            "speech": f"Here's the big picture of {chapter_title}. See how everything connects!",
            "center": clean_text(chapter_title, 28),
            "nodes": [c["title"] for c in concepts[:6]] if concepts else nodes[:6],
            "bg": "space",
            "duration": 7000
        },
        {
            "type": "flow",
            "speech": f"This is exactly how {chapter_title} works — watch each step light up!",
            "flowNodes": flow_nodes,
            "connections": flow_conns,
            "bg": "tech",
            "duration": 8000
        },
        {
            "type": "analogy",
            "speech": analogy_short,
            "chapter": clean_text(chapter_title, 28),
            "bg": "story",
            "duration": 6000
        },
        {
            "type": "steps",
            "speech": "Follow along — watch each step light up one by one!",
            "steps": steps,
            "bg": "dark",
            "duration": 8000
        },
        {
            "type": "concepts",
            "speech": "These are the key ideas. Each one is super important — remember them!",
            "cards": concepts[:4] if concepts else [{"icon": "💡", "title": chapter_title, "desc": explain_short}],
            "bg": "tech",
            "duration": 7000
        },
        {
            "type": "celebrate",
            "speech": takeaway_short,
            "chapter": clean_text(chapter_title, 36),
            "bg": "celebration",
            "duration": 6000
        }
    ]


def show_video_player(content: dict, chapter_title: str, topic: str):
    scenes = build_scenes(content, chapter_title, topic)
    scenes_json = json.dumps(scenes, ensure_ascii=False)
    total = len(scenes)

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#06060f;display:flex;flex-direction:column;align-items:center;padding:4px;font-family:'Segoe UI',sans-serif}}
#wrap{{width:100%;max-width:840px;border-radius:18px;overflow:hidden;box-shadow:0 0 50px rgba(0,212,255,0.15)}}
#bar{{height:4px;background:rgba(255,255,255,0.06)}}\n#fill{{height:100%;width:0%;border-radius:2px;transition:width .5s}}
canvas{{display:block;width:100%;height:auto}}
#ctrl{{display:flex;align-items:center;justify-content:space-between;padding:9px 14px;background:#09091a;border-top:1px solid rgba(255,255,255,0.07)}}
.btn{{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.13);border-radius:8px;color:#fff;width:36px;height:36px;font-size:14px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s}}
.btn:hover{{background:rgba(255,255,255,0.18);transform:scale(1.08)}}
.big{{width:42px;height:42px;font-size:16px}}
#dots{{display:flex;gap:5px}}
.dot{{width:7px;height:7px;border-radius:50%;background:rgba(255,255,255,0.2);cursor:pointer;transition:all .3s}}
.dot.on{{border-radius:4px;width:20px}}
#lbl{{font-size:11px;color:#8892a4;letter-spacing:1px;text-transform:uppercase}}
</style></head>
<body>
<div id="wrap">
  <div id="bar"><div id="fill"></div></div>
  <canvas id="c" width="840" height="470"></canvas>
  <div id="ctrl">
    <div style="display:flex;gap:6px;align-items:center">
      <button class="btn" onclick="prev()">&#9664;</button>
      <button class="btn big" id="pb" onclick="togglePlay()">&#9646;&#9646;</button>
      <button class="btn" onclick="nextS()">&#9654;</button>
    </div>
    <div id="dots"></div>
    <div id="lbl">Scene 1 / {total}</div>
  </div>
</div>

<script>
const SC={scenes_json};
const N=SC.length, W=840, H=470;
let cur=0,playing=true,timer=null,af=null;
let gt=0,lt=0,ss=0,trans=0;
let cx2=W*.16, ctx2=W*.16;

const cv=document.getElementById('c');
const c=cv.getContext('2d');

// Palette per background
const PAL={{
  dark:       {{bg:'#06060f',ac:'#00d4ff',sc:'#7b61ff',tc:'#00ff88'}},
  space:      {{bg:'#080618',ac:'#a78bfa',sc:'#00d4ff',tc:'#ff6b9d'}},
  tech:       {{bg:'#060c18',ac:'#00d4ff',sc:'#7b61ff',tc:'#00ff88'}},
  story:      {{bg:'#060f0a',ac:'#00ff88',sc:'#00d4ff',tc:'#ffd700'}},
  celebration:{{bg:'#100a06',ac:'#ffd700',sc:'#ff9500',tc:'#ff6b6b'}}
}};
function P(){{return PAL[SC[cur].bg]||PAL.dark;}}

function h2r(h){{return {{r:parseInt(h.slice(1,3),16),g:parseInt(h.slice(3,5),16),b:parseInt(h.slice(5,7),16)}};}}
function ha(h,a){{const {{r,g,b}}=h2r(h);return `rgba(${{r}},${{g}},${{b}},${{a}})`;}}
function lerp(a,b,t){{return a+(b-a)*t;}}
function eo(t){{return 1-Math.pow(1-t,3);}}
function cl(v,a,b){{return Math.max(a,Math.min(b,v));}}
function prog(){{return cl((performance.now()-ss)/1500,0,1);}}

function rr(x,y,w,h,r,fill,stroke,sw){{
  c.beginPath();
  if(c.roundRect)c.roundRect(x,y,w,h,r);
  else{{c.moveTo(x+r,y);c.lineTo(x+w-r,y);c.quadraticCurveTo(x+w,y,x+w,y+r);c.lineTo(x+w,y+h-r);c.quadraticCurveTo(x+w,y+h,x+w-r,y+h);c.lineTo(x+r,y+h);c.quadraticCurveTo(x,y+h,x,y+h-r);c.lineTo(x,y+r);c.quadraticCurveTo(x,y,x+r,y);c.closePath();}}
  if(fill){{c.fillStyle=fill;c.fill();}}
  if(stroke){{c.strokeStyle=stroke;c.lineWidth=sw||1.5;c.stroke();}}
}}

function wt(text,x,y,mw,lh,ml){{
  const words=text.split(' ');let line='',n=0,cy=y;
  for(let w of words){{
    const t=line+w+' ';
    if(c.measureText(t).width>mw&&line){{if(!ml||n<ml)c.fillText(line.trim(),x,cy);line=w+' ';cy+=lh;n++;if(ml&&n>=ml)break;}}
    else line=t;
  }}
  if(line.trim()&&(!ml||n<ml))c.fillText(line.trim(),x,cy);
  return cy;
}}

// ─── ARROW ─────────────────────────────────────────────
function arrow(x1,y1,x2,y2,col,thick,progress){{
  const dx=x2-x1, dy=y2-y1, len=Math.sqrt(dx*dx+dy*dy);
  const tx=x1+dx*progress, ty=y1+dy*progress;
  c.save();c.strokeStyle=col;c.lineWidth=thick||2;
  c.beginPath();c.moveTo(x1,y1);c.lineTo(tx,ty);c.stroke();
  if(progress>.9){{
    const angle=Math.atan2(dy,dx);
    c.fillStyle=col;c.beginPath();
    c.moveTo(tx,ty);
    c.lineTo(tx-12*Math.cos(angle-0.4),ty-12*Math.sin(angle-0.4));
    c.lineTo(tx-12*Math.cos(angle+0.4),ty-12*Math.sin(angle+0.4));
    c.closePath();c.fill();
  }}
  c.restore();
}}

// ─── BACKGROUNDS ───────────────────────────────────────
function bgDark(p){{
  c.fillStyle=p.bg;c.fillRect(0,0,W,H);
  c.save();c.globalAlpha=0.035;c.strokeStyle=p.ac;c.lineWidth=1;
  const g=50,off=(gt*10)%g;
  for(let x=-g+off%g;x<W;x+=g){{c.beginPath();c.moveTo(x,0);c.lineTo(x,H);c.stroke();}}
  for(let y=0;y<H;y+=g){{c.beginPath();c.moveTo(0,y);c.lineTo(W,y);c.stroke();}}
  c.restore();
  [[.12,.25,160,p.ac,.07],[.88,.72,130,p.sc,.05]].forEach(([ox,oy,or,col,oa])=>{{
    const gd=c.createRadialGradient(ox*W,oy*H,0,ox*W,oy*H,or);
    gd.addColorStop(0,ha(col,oa));gd.addColorStop(1,'transparent');
    c.fillStyle=gd;c.fillRect(0,0,W,H);
  }});
}}
function bgSpace(p){{
  c.fillStyle=p.bg;c.fillRect(0,0,W,H);
  c.save();for(let i=0;i<40;i++){{
    const sx=(i*173+i*i*7)%W,sy=(i*97+i*i*3)%H;
    const a=.2+.25*Math.sin(gt+i*.9);
    c.fillStyle=`rgba(255,255,255,${{a*.5}})`;
    c.beginPath();c.arc(sx,sy,.8+i%2*.5,0,Math.PI*2);c.fill();
  }}c.restore();
  const gd=c.createRadialGradient(W*.6,H*.4,0,W*.6,H*.4,250);
  gd.addColorStop(0,ha(p.ac,.07));gd.addColorStop(1,'transparent');
  c.fillStyle=gd;c.fillRect(0,0,W,H);
}}
function bgTech(p){{
  c.fillStyle=p.bg;c.fillRect(0,0,W,H);
  c.save();c.globalAlpha=.03;c.strokeStyle=p.ac;c.lineWidth=1;
  const g=40,off=(gt*8)%g;
  for(let x=-g+off%g;x<W;x+=g){{c.beginPath();c.moveTo(x,0);c.lineTo(x,H);c.stroke();}}
  for(let y=off;y<H;y+=g){{c.beginPath();c.moveTo(0,y);c.lineTo(W,y);c.stroke();}}
  c.restore();
  [[.1,.2,100,p.ac,.06],[.85,.78,90,p.sc,.05]].forEach(([ox,oy,or,col,oa])=>{{
    const gd=c.createRadialGradient(ox*W,oy*H,0,ox*W,oy*H,or);
    gd.addColorStop(0,ha(col,oa));gd.addColorStop(1,'transparent');c.fillStyle=gd;c.fillRect(0,0,W,H);
  }});
}}
function bgStory(p){{
  const sky=c.createLinearGradient(0,0,0,H);
  sky.addColorStop(0,'#020c16');sky.addColorStop(.55,'#060f0a');sky.addColorStop(1,'#0a1a0a');
  c.fillStyle=sky;c.fillRect(0,0,W,H);
  c.save();for(let i=0;i<30;i++){{
    const sx=(i*157+i*i*11)%W,sy=(i*83+i*i*5)%(H*.5);
    const a=.25+.3*Math.sin(gt+i*.75);
    c.fillStyle=`rgba(255,255,255,${{a*.5}})`;c.beginPath();c.arc(sx,sy,.7+i%2*.5,0,Math.PI*2);c.fill();
  }}c.restore();
  const gnd=c.createLinearGradient(0,H*.7,0,H);
  gnd.addColorStop(0,'#081408');gnd.addColorStop(1,'#040a04');
  c.fillStyle=gnd;c.fillRect(0,H*.7,W,H);
  c.save();c.globalAlpha=.5;
  [[65,H*.7,26,60],[710,H*.7,20,48],[735,H*.7,15,38]].forEach(([tx,ty,tw,th])=>{{
    c.fillStyle='#0c1e0c';c.beginPath();c.moveTo(tx,ty-th);c.lineTo(tx-tw,ty);c.lineTo(tx+tw,ty);c.closePath();c.fill();
  }});c.restore();
}}
function bgCelebration(p){{
  c.fillStyle=p.bg;c.fillRect(0,0,W,H);
  c.save();c.globalAlpha=.09+.04*Math.sin(gt*2);
  const burst=c.createRadialGradient(W/2,H/2,0,W/2,H/2,280);
  burst.addColorStop(0,p.ac);burst.addColorStop(.5,p.sc);burst.addColorStop(1,'transparent');
  c.fillStyle=burst;c.fillRect(0,0,W,H);c.restore();
  const cc=[p.ac,p.sc,'#ff6b6b','#00ff88','#ffd700'];
  c.save();for(let i=0;i<40;i++){{
    const cx=(i*137.5+gt*26*((i%3)-1)*.9)%W,cy=((i*73+gt*36+i*195)%H);
    const a=.4+.3*Math.sin(gt*2+i);
    c.fillStyle=ha(cc[i%cc.length],a*.7);c.save();c.translate(cx%W,cy%H);c.rotate(gt+i);c.fillRect(-4,-4,8,3);c.restore();
  }}c.restore();
}}

// ─── ARIA CHARACTER ─────────────────────────────────────
function drawARIA(x,y,sc2,pose,talk){{
  const p=P();c.save();c.translate(x,y);c.scale(sc2,sc2);
  const br=Math.sin(gt*1.8)*2, mo=Math.sin(talk*8)*.5+.5;

  c.save();c.globalAlpha=.12;c.fillStyle='#000';c.beginPath();c.ellipse(0,130,34,8,0,0,Math.PI*2);c.fill();c.restore();

  // Legs
  [-13,13].forEach((lx,li)=>{{
    const ls=pose==='celebrate'?Math.sin(gt*3+li*Math.PI)*7:0;
    c.save();c.translate(lx,92+br*.3);c.rotate(ls*.05);
    rr(-6,0,12,28,5,ha(p.ac,.6),p.ac,1.5);rr(-7,26,16,7,4,ha(p.sc,.7),p.sc,1);c.restore();
  }});

  // Body
  const bg2=c.createLinearGradient(-26,22,26,80);
  bg2.addColorStop(0,ha(p.ac,.2));bg2.addColorStop(1,ha(p.sc,.13));
  rr(-26,22+br*.3,52,58,10,bg2,p.ac,2);
  c.save();c.globalAlpha=.2;c.strokeStyle=p.ac;c.lineWidth=.8;
  [[0,38],[0,52],[0,64]].forEach(([bx3,by3])=>{{c.beginPath();c.moveTo(-18,by3+br*.2);c.lineTo(18,by3+br*.2);c.stroke();}});
  c.restore();
  const core=c.createRadialGradient(0,52,0,0,52,6);
  core.addColorStop(0,ha(p.ac,.9+.1*Math.sin(gt*3)));core.addColorStop(1,ha(p.ac,.1));
  c.beginPath();c.arc(0,52+br*.2,5,0,Math.PI*2);c.fillStyle=core;c.fill();

  // Arms
  let la=-Math.PI/8+br*.01, ra=Math.PI/8;
  if(pose==='wave')la=-Math.PI/2.4+Math.sin(gt*4)*.22;
  else if(pose==='point')la=-Math.PI/3;
  else if(pose==='celebrate'){{la=-Math.PI/2+Math.sin(gt*3)*.28;ra=-Math.PI/2+Math.sin(gt*3+1)*.28;}}

  c.save();c.translate(-26,36+br*.3);c.rotate(la);
  rr(-5,0,11,34,5,ha(p.ac,.55),p.ac,1.5);
  c.beginPath();c.arc(0,34,6,0,Math.PI*2);c.fillStyle=ha(p.ac,.8);c.fill();c.strokeStyle=p.ac;c.lineWidth=1.5;c.stroke();
  if(pose==='wave'){{c.font='14px serif';c.textAlign='center';c.textBaseline='middle';c.fillText('👋',0,34);}}
  c.restore();

  c.save();c.translate(26,36+br*.3);c.rotate(ra);
  rr(-5,0,11,34,5,ha(p.sc,.55),p.sc,1.5);
  c.beginPath();c.arc(0,34,6,0,Math.PI*2);c.fillStyle=ha(p.sc,.8);c.fill();c.strokeStyle=p.sc;c.lineWidth=1.5;c.stroke();
  if(pose==='point'){{c.font='12px serif';c.textAlign='center';c.textBaseline='middle';c.fillText('👉',0,34);}}
  if(pose==='celebrate'){{c.font='12px serif';c.textAlign='center';c.textBaseline='middle';c.fillText('🎉',0,34);}}
  c.restore();

  // Head
  const hy=-42+br;
  c.save();c.globalAlpha=.1+.04*Math.sin(gt*1.4);
  const aura=c.createRadialGradient(0,hy,0,0,hy,52);
  aura.addColorStop(0,p.ac);aura.addColorStop(1,'transparent');c.fillStyle=aura;c.fillRect(-58,hy-52,116,104);c.restore();
  const hg=c.createRadialGradient(-7,hy-7,4,0,hy,36);
  hg.addColorStop(0,'#1e1e3f');hg.addColorStop(.7,'#0d0d22');hg.addColorStop(1,'#080818');
  c.beginPath();c.arc(0,hy,36,0,Math.PI*2);c.fillStyle=hg;c.fill();c.strokeStyle=p.ac;c.lineWidth=2.5;c.stroke();
  c.save();c.globalAlpha=.16;c.strokeStyle=p.sc;c.lineWidth=1;c.setLineDash([4,6]);
  c.beginPath();c.arc(0,hy,29,0,Math.PI*2);c.stroke();c.setLineDash([]);c.restore();
  const vg=c.createLinearGradient(-22,hy-16,22,hy+8);
  vg.addColorStop(0,ha(p.ac,.2));vg.addColorStop(1,ha(p.ac,.05));
  rr(-22,hy-16,44,26,8,vg,ha(p.ac,.36),1.5);

  // Eyes
  const blink=Math.abs(Math.sin(gt*.33));
  [[-10,hy-5],[10,hy-5]].forEach(([ex,ey],ei)=>{{
    const bh=blink<.05?.1:1;
    c.save();c.translate(0,ey*(1-bh));c.scale(1,bh);
    c.globalAlpha=(.22+.14*Math.sin(gt*2+ei))*bh;
    const eg=c.createRadialGradient(ex,ey/bh,0,ex,ey/bh,11);
    eg.addColorStop(0,p.ac);eg.addColorStop(1,'transparent');
    c.fillStyle=eg;c.beginPath();c.arc(ex,ey/bh,11,0,Math.PI*2);c.fill();
    c.globalAlpha=bh;
    const ec=c.createRadialGradient(ex,ey/bh,0,ex,ey/bh,4.5);
    ec.addColorStop(0,'#ffffff');ec.addColorStop(.4,p.ac);ec.addColorStop(1,ha(p.ac,.3));
    c.beginPath();c.arc(ex,ey/bh,4.5,0,Math.PI*2);c.fillStyle=ec;c.fill();c.restore();
  }});

  // Mouth
  const my=hy+13;
  if(mo>.4&&talk>0){{
    const mh=2.5+mo*5;c.beginPath();c.ellipse(0,my,8,mh,0,0,Math.PI*2);
    c.fillStyle=ha(p.ac,.4);c.fill();c.strokeStyle=p.ac;c.lineWidth=1.5;c.stroke();
  }}else{{
    c.beginPath();c.arc(0,my-2,7,.18,Math.PI-.18);c.strokeStyle=p.ac;c.lineWidth=2;c.stroke();
    c.save();c.globalAlpha=.3;
    [[-13,my+2],[13,my+2]].forEach(([ex,ey])=>{{c.fillStyle=ha('#ff9090',.7);c.beginPath();c.arc(ex,ey,2.5,0,Math.PI*2);c.fill();}});
    c.restore();
  }}

  // Antenna
  const ay=hy-36,as2=Math.sin(gt*1.4)*3;
  c.save();c.strokeStyle=ha(p.ac,.6);c.lineWidth=2;
  c.beginPath();c.moveTo(0,ay);c.lineTo(as2,ay-20);c.stroke();
  const ag=c.createRadialGradient(as2,ay-22,0,as2,ay-22,6);
  ag.addColorStop(0,p.ac);ag.addColorStop(1,ha(p.ac,.2));
  c.beginPath();c.arc(as2,ay-22,5+Math.sin(gt*3),0,Math.PI*2);c.fillStyle=ag;c.fill();c.restore();

  c.save();c.globalAlpha=.6;
  rr(-18,100+br*.3,36,13,6,ha(p.ac,.14),ha(p.ac,.36),1);
  c.font='bold 7px Segoe UI';c.fillStyle=p.ac;c.textAlign='center';c.textBaseline='middle';c.fillText('ARIA',0,106+br*.3);c.restore();
  c.restore();
}}

// ─── SPEECH BUBBLE ──────────────────────────────────────
function drawBubble(bx,by,bw,text,p){{
  if(!text)return;
  c.font='13.5px Segoe UI';
  const pad=14,lh=20,mw=bw-pad*2;
  const words=text.split(' ');let lines=[],line='';
  for(let w of words){{
    const t=line+w+' ';
    if(c.measureText(t).width>mw&&line){{lines.push(line.trim());line=w+' ';}}
    else line=t;
  }}
  if(line.trim())lines.push(line.trim());
  const bh=lines.length*lh+pad*2,ty=by-bh-10;
  c.save();c.globalAlpha=.25;rr(bx+3,ty+3,bw,bh,13,'rgba(0,0,0,.6)');c.restore();
  const bg4=c.createLinearGradient(bx,ty,bx,ty+bh);
  bg4.addColorStop(0,'rgba(10,10,30,.96)');bg4.addColorStop(1,'rgba(6,6,18,.96)');
  rr(bx,ty,bw,bh,13,bg4,ha(p.ac,.45),1.5);
  c.save();c.globalAlpha=.05;rr(bx+5,ty+5,bw-10,bh/2-5,9,ha('#fff',1));c.restore();
  c.save();c.fillStyle='rgba(8,8,22,.96)';c.strokeStyle=ha(p.ac,.45);c.lineWidth=1.5;
  c.beginPath();c.moveTo(bx+35,ty+bh);c.lineTo(bx+26,ty+bh+12);c.lineTo(bx+55,ty+bh);c.closePath();c.fill();c.stroke();c.restore();
  c.font='13.5px Segoe UI';c.fillStyle='#e6ecf5';c.textAlign='left';
  lines.forEach((l,i)=>c.fillText(l,bx+pad,ty+pad+14+i*lh));
  c.save();[0,.35,.7].forEach((d,i)=>{{
    c.globalAlpha=(.35+.35*Math.sin(gt*4+d))*.7;c.fillStyle=p.ac;
    c.beginPath();c.arc(bx+bw-20+i*7,ty+bh-9,2.5,0,Math.PI*2);c.fill();
  }});c.restore();
}}

// ═══════════════════════════════════════════════════════
// ─── DIAGRAM RENDERERS ──────────────────────────────────
// ═══════════════════════════════════════════════════════

// BIG INTRO — pulsing topic card
function diagIntro(scene,p,pr){{
  const a1=eo(cl(pr*3,0,1));
  const cx=W*.63,cy=H*.42;
  c.save();c.globalAlpha=.14*a1+.04*Math.sin(gt*1.5);
  const gd=c.createRadialGradient(cx,cy,0,cx,cy,200);
  gd.addColorStop(0,p.ac);gd.addColorStop(1,'transparent');
  c.fillStyle=gd;c.fillRect(0,0,W,H);c.restore();

  // Orbiting ring
  c.save();c.globalAlpha=.25*a1;c.strokeStyle=p.ac;c.lineWidth=1.5;c.setLineDash([6,10]);c.lineDashOffset=-gt*25;
  c.beginPath();c.arc(cx,cy,90+8*Math.sin(gt),0,Math.PI*2);c.stroke();c.setLineDash([]);c.restore();
  c.save();c.globalAlpha=.14*a1;c.strokeStyle=p.sc;c.lineWidth=1;c.setLineDash([4,14]);c.lineDashOffset=gt*18;
  c.beginPath();c.arc(cx,cy,120+6*Math.cos(gt*.8),0,Math.PI*2);c.stroke();c.setLineDash([]);c.restore();

  // Big emoji
  c.save();c.globalAlpha=a1;
  c.font=`${{Math.round(72*eo(cl(pr*3,0,1)))}}px serif`;c.textAlign='center';c.textBaseline='middle';c.fillText('🧠',cx,cy-18);

  // Topic label
  c.font='bold 11px Segoe UI';c.fillStyle=p.ac;
  ctx2&&1;c.textAlign='center';c.textBaseline='alphabetic';
  c.fillText(scene.topic.toUpperCase(),cx,cy+36);

  // Chapter title
  const fs=scene.chapter.length>22?22:28;
  c.font=`bold ${{fs}}px Segoe UI`;c.fillStyle='#ffffff';
  c.fillText(scene.chapter,cx,cy+68);

  // Subtitle
  c.font='12px Segoe UI';c.fillStyle=ha(p.sc,.8);
  c.fillText('Watch & Learn 👇',cx,cy+92);
  c.restore();
}}

// MIND MAP — radial concept map
function diagMindMap(scene,p,pr){{
  const nodes=scene.nodes||[];if(!nodes.length)return;
  const cx=W*.63,cy=H*.46;
  const COLORS=[p.ac,p.sc,p.tc,'#ff6b9d','#ff9500','#ffd700'];

  // Center glow
  c.save();c.globalAlpha=.1+.04*Math.sin(gt*1.5);
  const cg=c.createRadialGradient(cx,cy,0,cx,cy,100);
  cg.addColorStop(0,p.ac);cg.addColorStop(1,'transparent');c.fillStyle=cg;c.fillRect(0,0,W,H);c.restore();

  // Center node
  const ca=eo(cl(pr*4,0,1));
  c.save();c.globalAlpha=ca;
  const cgrd=c.createRadialGradient(cx,cy,0,cx,cy,44);
  cgrd.addColorStop(0,ha(p.ac,.35));cgrd.addColorStop(1,ha(p.ac,.08));
  c.beginPath();c.arc(cx,cy,44,0,Math.PI*2);c.fillStyle=cgrd;c.fill();
  c.strokeStyle=p.ac;c.lineWidth=2.5;c.stroke();
  c.font='bold 12px Segoe UI';c.fillStyle='#ffffff';c.textAlign='center';c.textBaseline='middle';
  const label=scene.center;
  if(c.measureText(label).width>72){{
    const words=label.split(' ');const mid=Math.ceil(words.length/2);
    c.fillText(words.slice(0,mid).join(' '),cx,cy-8);
    c.fillText(words.slice(mid).join(' '),cx,cy+10);
  }}else c.fillText(label,cx,cy);
  c.restore();

  // Branch nodes
  nodes.forEach((node,i)=>{{
    const delay=0.1+i*.1;
    const na=eo(cl((pr-delay)*4,0,1));if(na<=0)return;
    const totalNodes=nodes.length;
    const angle=(i/totalNodes)*Math.PI*2 - Math.PI/2;
    const dist=130;
    const nx=cx+Math.cos(angle)*dist, ny=cy+Math.sin(angle)*dist;
    const col=COLORS[i%COLORS.length];

    // Branch line (animated)
    c.save();c.globalAlpha=.55*na;c.strokeStyle=col;c.lineWidth=2;c.setLineDash([5,4]);
    const lx=cx+Math.cos(angle)*46, ly=cy+Math.sin(angle)*46;
    arrow(lx,ly,nx,ny,col,1.5,na);
    c.setLineDash([]);c.restore();

    // Node circle
    c.save();c.globalAlpha=na;c.translate(0,(1-na)*10);
    const ng=c.createRadialGradient(nx,ny,0,nx,ny,28);
    ng.addColorStop(0,ha(col,.28));ng.addColorStop(1,ha(col,.06));
    c.beginPath();c.arc(nx,ny,28,0,Math.PI*2);c.fillStyle=ng;c.fill();
    c.strokeStyle=col;c.lineWidth=2;c.stroke();

    // Pulse ring
    const pulse=(gt*.8+i*.4)%1;
    c.save();c.globalAlpha=na*(1-pulse)*.3;c.strokeStyle=col;c.lineWidth=1.5;
    c.beginPath();c.arc(nx,ny,28+pulse*22,0,Math.PI*2);c.stroke();c.restore();

    // Node label
    c.font='bold 11px Segoe UI';c.fillStyle='#ffffff';c.textAlign='center';c.textBaseline='middle';
    const words=node.split(' ');
    if(words.length===1||c.measureText(node).width<48){{
      c.fillText(node.length>10?node.slice(0,9)+'…':node,nx,ny);
    }}else{{
      c.font='bold 10px Segoe UI';
      c.fillText(words[0].slice(0,9),nx,ny-7);
      c.fillText(words.slice(1).join(' ').slice(0,9),nx,ny+7);
    }}
    c.restore();
  }});
}}

// FLOW DIAGRAM — beautiful circles with emoji, bezier arrows, particles
function diagFlow(scene,p,pr){{
  const nodes=scene.flowNodes||[];
  const conns=scene.connections||[];
  if(!nodes.length)return;
  const n=Math.min(nodes.length,5);

  // Beautiful colour palette per node
  const NCOLS=[
    ['#00d4ff','#0077bb'],['#a78bfa','#6d28d9'],
    ['#00ff88','#00996b'],['#ff6b6b','#cc2222'],
    ['#ffd700','#cc8800']
  ];

  const R=42; // node circle radius

  // ── LAYOUT ──────────────────────────────────────────
  const areaX=W*.3, areaW=W*.68-areaX;
  const positions=[];
  if(n<=4){{
    // Single row centred in right area
    const gap=72;
    const totalW=n*(R*2)+(n-1)*gap;
    const sx=areaX+(areaW-totalW)/2+R;
    for(let i=0;i<n;i++) positions.push({{x:sx+i*(R*2+gap),y:H*.46}});
  }}else{{
    // Two rows
    const r1=Math.ceil(n/2), r2=n-r1, gap=68;
    const w1=r1*(R*2)+(r1-1)*gap, sx1=areaX+(areaW-w1)/2+R;
    for(let i=0;i<r1;i++) positions.push({{x:sx1+i*(R*2+gap),y:H*.32}});
    const w2=r2*(R*2)+(r2-1)*gap, sx2=areaX+(areaW-w2)/2+R;
    for(let i=0;i<r2;i++) positions.push({{x:sx2+i*(R*2+gap),y:H*.66}});
  }}

  // ── CONNECTIONS ─────────────────────────────────────
  conns.forEach((conn,ci)=>{{
    const fi=conn.from-1, ti2=conn.to-1;
    const from=positions[fi], to=positions[ti2];
    if(!from||!to)return;
    const cp=eo(cl((pr-.12-ci*.06)*4,0,1));if(cp<=0)return;

    const c1=NCOLS[fi%NCOLS.length][0];
    const c2=NCOLS[ti2%NCOLS.length][0];
    const sameRow=Math.abs(from.y-to.y)<10;

    // Gradient stroke
    const grd=c.createLinearGradient(from.x,from.y,to.x,to.y);
    grd.addColorStop(0,ha(c1,.7));grd.addColorStop(1,ha(c2,.7));

    c.save();c.globalAlpha=cp;c.strokeStyle=grd;c.lineWidth=3;c.lineCap='round';

    let sx2,sy,ex2,ey,cpx1,cpy1,cpx2,cpy2;
    if(sameRow){{
      sx2=from.x+R+3;sy=from.y;ex2=to.x-R-3;ey=to.y;
      cpx1=sx2+(ex2-sx2)*.4;cpy1=sy-30;
      cpx2=sx2+(ex2-sx2)*.6;cpy2=ey-30;
    }}else{{
      sx2=from.x;sy=from.y+R+3;ex2=to.x;ey=to.y-R-3;
      cpx1=sx2;cpy1=(sy+ey)/2;
      cpx2=ex2;cpy2=(sy+ey)/2;
    }}

    c.beginPath();c.moveTo(sx2,sy);c.bezierCurveTo(cpx1,cpy1,cpx2,cpy2,ex2,ey);c.stroke();

    // Arrowhead
    if(cp>.85){{
      const angle=sameRow?0:Math.PI/2;
      const dx2=ex2-cpx2,dy2=ey-cpy2;
      const ang=Math.atan2(dy2,dx2);
      c.fillStyle=ha(c2,.85*cp);
      c.beginPath();c.moveTo(ex2,ey);
      c.lineTo(ex2-13*Math.cos(ang-.4),ey-13*Math.sin(ang-.4));
      c.lineTo(ex2-13*Math.cos(ang+.4),ey-13*Math.sin(ang+.4));
      c.closePath();c.fill();
    }}

    // Animated particles along bezier
    for(let pi=0;pi<3;pi++){{
      const t2=((gt*.45+pi*.33)%1)*cp;
      const mt=1-t2;
      const px=mt*mt*mt*sx2+3*mt*mt*t2*cpx1+3*mt*t2*t2*cpx2+t2*t2*t2*ex2;
      const py=mt*mt*mt*sy+3*mt*mt*t2*cpy1+3*mt*t2*t2*cpy2+t2*t2*t2*ey;
      const pr2=4-pi;
      c.save();c.globalAlpha=(.7-pi*.18)*cp;
      const pg=c.createRadialGradient(px,py,0,px,py,pr2);
      pg.addColorStop(0,ha('#ffffff',.9));pg.addColorStop(1,'transparent');
      c.fillStyle=pg;c.beginPath();c.arc(px,py,pr2,0,Math.PI*2);c.fill();c.restore();
    }}

    c.restore();
  }});

  // ── NODES ────────────────────────────────────────────
  nodes.slice(0,n).forEach((node,i)=>{{
    const np=eo(cl((pr-i*.1)*4,0,1));if(np<=0)return;
    const {{x,y}}=positions[i];
    const [col1,col2]=NCOLS[i%NCOLS.length];
    const pulse=(gt*.65+i*.4)%1;

    c.save();c.globalAlpha=np;c.translate(0,(1-np)*18);

    // Outer pulse ring
    c.save();c.globalAlpha=np*(1-pulse)*.28;c.strokeStyle=col1;c.lineWidth=2.5;
    c.beginPath();c.arc(x,y,R+5+pulse*22,0,Math.PI*2);c.stroke();c.restore();

    // Drop shadow
    c.save();c.globalAlpha=.22*np;
    const sdw=c.createRadialGradient(x+3,y+5,0,x+3,y+5,R+6);
    sdw.addColorStop(0,'rgba(0,0,0,.6)');sdw.addColorStop(1,'transparent');
    c.fillStyle=sdw;c.beginPath();c.arc(x+3,y+5,R+6,0,Math.PI*2);c.fill();c.restore();

    // Circle gradient fill
    const grd=c.createRadialGradient(x-R*.3,y-R*.3,0,x,y,R);
    grd.addColorStop(0,ha(col1,.95));grd.addColorStop(.6,ha(col1,.75));
    grd.addColorStop(1,ha(col2,.9));
    c.beginPath();c.arc(x,y,R,0,Math.PI*2);c.fillStyle=grd;c.fill();

    // Bright border
    c.strokeStyle=col1;c.lineWidth=2.5;c.stroke();

    // Inner shine (top-left gloss)
    c.save();c.globalAlpha=.2;
    const shine=c.createRadialGradient(x-R*.4,y-R*.4,0,x-R*.4,y-R*.4,R*.7);
    shine.addColorStop(0,'#ffffff');shine.addColorStop(1,'transparent');
    c.fillStyle=shine;c.beginPath();c.arc(x,y,R,0,Math.PI*2);c.fill();c.restore();

    // Emoji icon (large, centred)
    c.font=`${{Math.round(26*np)}}px serif`;c.textAlign='center';c.textBaseline='middle';
    c.fillText(node.icon||'●',x,y-3);

    // Number badge (bottom-right)
    c.beginPath();c.arc(x+R*.65,y+R*.65,11,0,Math.PI*2);
    c.fillStyle=col2;c.fill();c.strokeStyle='#ffffff';c.lineWidth=1.5;c.stroke();
    c.font='bold 10px Segoe UI';c.fillStyle='#ffffff';c.textBaseline='middle';c.textAlign='center';
    c.fillText(i+1,x+R*.65,y+R*.65);

    // Label below circle
    c.font='bold 12px Segoe UI';c.fillStyle='#ffffff';c.textBaseline='alphabetic';c.textAlign='center';
    const lbl=node.label||'';
    c.fillText(lbl.length>14?lbl.slice(0,13)+'…':lbl,x,y+R+22);

    // Short description
    if(node.desc){{
      c.font='10px Segoe UI';c.fillStyle=ha(col1,.85);
      const d=node.desc.slice(0,20)+(node.desc.length>20?'…':'');
      c.fillText(d,x,y+R+38);
    }}

    c.restore();
  }});

  // Flow title tag
  c.save();c.globalAlpha=eo(cl(pr*4,0,1));
  rr(areaX,12,160,26,13,ha(p.ac,.12),ha(p.ac,.4),1.5);
  c.font='bold 11px Segoe UI';c.fillStyle=p.ac;c.textAlign='center';c.textBaseline='middle';
  c.fillText('HOW IT WORKS',areaX+80,25);c.restore();
}}

// ANALOGY VISUAL — simple story illustration
function diagAnalogy(scene,p,pr){{
  const a1=eo(cl(pr*3,0,1));
  const cx=W*.64,cy=H*.42;

  c.save();c.globalAlpha=.1*a1;
  const gd=c.createRadialGradient(cx,cy,0,cx,cy,180);
  gd.addColorStop(0,p.ac);gd.addColorStop(1,'transparent');c.fillStyle=gd;c.fillRect(0,0,W,H);c.restore();

  // Big lightbulb visual
  const la=eo(cl(pr*3,0,1));
  c.save();c.globalAlpha=la;
  c.font=`${{Math.round(80*la)}}px serif`;c.textAlign='center';c.textBaseline='middle';c.fillText('💡',cx,cy-40);
  c.restore();

  // "Real life:" label
  c.save();c.globalAlpha=eo(cl((pr-.2)*3,0,1));
  rr(cx-80,cy+12,160,30,15,ha(p.ac,.14),ha(p.ac,.4),1.5);
  c.font='bold 11px Segoe UI';c.fillStyle=p.ac;c.textAlign='center';c.textBaseline='middle';c.fillText('REAL LIFE ANALOGY',cx,cy+27);c.restore();

  // Concept name
  c.save();c.globalAlpha=eo(cl((pr-.35)*3,0,1));
  c.font='bold 20px Segoe UI';c.fillStyle='#ffffff';c.textAlign='center';c.textBaseline='alphabetic';
  c.fillText(scene.chapter||'',cx,cy+68);c.restore();

  // Two-panel: real world ↔ concept
  const ppa=eo(cl((pr-.45)*3,0,1));
  c.save();c.globalAlpha=ppa;
  const pw=130,ph=50,py=cy+82;
  [[cx-pw-8,'Real World','🌍',p.tc],[cx+8,scene.chapter,'⚙️',p.ac]].forEach(([px2,label,icon,col],i)=>{{
    rr(px2,py,pw,ph,10,ha(col,.1),ha(col,.35),1.5);
    c.font='18px serif';c.textAlign='center';c.textBaseline='middle';c.fillText(icon,px2+pw/2,py+20);
    c.font='bold 9px Segoe UI';c.fillStyle='#c9d3e0';c.fillText(label.slice(0,14),px2+pw/2,py+40);
  }});
  // Connector arrow
  if(ppa>.8)arrow(cx-8,py+ph/2,cx+8,py+ph/2,p.ac,2,1);
  c.restore();
}}

// STEPS TIMELINE — horizontal timeline with icons
function diagSteps(scene,p,pr){{
  const steps=scene.steps||[];if(!steps.length)return;
  const n=Math.min(steps.length,5);
  const ox=W*.3, ex=W*.98;
  const lineY=H*.45;
  const spacing=(ex-ox)/(n-1||1);
  const COLORS=[p.ac,p.sc,p.tc,'#ff6b9d','#ff9500'];

  // Timeline base line
  const la=eo(cl(pr*3,0,1));
  c.save();c.globalAlpha=.3*la;c.strokeStyle='#ffffff';c.lineWidth=2;c.setLineDash([6,6]);
  c.beginPath();c.moveTo(ox,lineY);c.lineTo(ex,lineY);c.stroke();c.setLineDash([]);c.restore();

  // Animated progress line
  const lp=eo(cl((pr-.1)*2,0,1));
  c.save();c.globalAlpha=.9;
  const lg=c.createLinearGradient(ox,lineY,ox+(ex-ox)*lp,lineY);
  lg.addColorStop(0,p.ac);lg.addColorStop(1,p.sc);
  c.strokeStyle=lg;c.lineWidth=3;
  c.beginPath();c.moveTo(ox,lineY);c.lineTo(ox+(ex-ox)*lp,lineY);c.stroke();c.restore();

  // Step nodes
  steps.slice(0,n).forEach((step,i)=>{{
    const np=eo(cl((pr-.08-i*.12)*4,0,1));if(np<=0)return;
    const sx=ox+i*spacing, sy=lineY;
    const col=COLORS[i%COLORS.length];
    const isActive=lp>(i/(n-1||1))-.05;

    // Vertical connector
    c.save();c.globalAlpha=.35*np;c.strokeStyle=col;c.lineWidth=1.5;c.setLineDash([3,4]);
    c.beginPath();c.moveTo(sx,sy+(i%2===0?-12:12));c.lineTo(sx,sy+(i%2===0?-55:55));c.stroke();c.setLineDash([]);c.restore();

    // Node circle
    c.save();c.globalAlpha=np;c.translate(0,(1-np)*8);
    if(isActive){{
      const glow=(gt*.8+i*.3)%1;
      c.save();c.globalAlpha=np*(1-glow)*.3;c.strokeStyle=col;c.lineWidth=2;
      c.beginPath();c.arc(sx,sy,20+glow*16,0,Math.PI*2);c.stroke();c.restore();
    }}
    c.beginPath();c.arc(sx,sy,16,0,Math.PI*2);
    const cg=c.createRadialGradient(sx,sy,0,sx,sy,16);
    cg.addColorStop(0,ha(col,isActive?.6:.3));cg.addColorStop(1,ha(col,isActive?.15:.05));
    c.fillStyle=cg;c.fill();c.strokeStyle=col;c.lineWidth=isActive?2.5:1.5;c.stroke();
    c.font='13px serif';c.textAlign='center';c.textBaseline='middle';c.fillText(step.icon||'●',sx,sy);

    // Label card (alternating top/bottom)
    const cardY=i%2===0?sy-58:sy+24;
    const cardW=Math.min(spacing*.9,118);
    rr(sx-cardW/2,cardY,cardW,34,8,ha(col,.1),ha(col,.3),1.5);
    c.font='bold 10px Segoe UI';c.fillStyle=col;c.textAlign='center';c.textBaseline='alphabetic';
    c.fillText(step.label,sx,cardY+14);
    c.font='9px Segoe UI';c.fillStyle='#a8b4c4';
    c.fillText(step.body.slice(0,18)+(step.body.length>18?'…':''),sx,cardY+28);
    c.restore();
  }});

  // Step counter
  const shown=Math.min(n,Math.floor(lp*n+1));
  c.save();c.globalAlpha=la;
  rr(W*.3,H*.82,120,28,14,ha(p.ac,.12),ha(p.ac,.35),1.5);
  c.font='bold 12px Segoe UI';c.fillStyle=p.ac;c.textAlign='center';c.textBaseline='middle';
  c.fillText(`${{shown}} / ${{n}} Steps`,W*.3+60,H*.82+14);c.restore();
}}

// CONCEPT CARDS — 2×2 icon cards
function diagConcepts(scene,p,pr){{
  const cards=scene.cards||[];if(!cards.length)return;
  const n=Math.min(cards.length,4);
  const COLS=[p.ac,p.sc,p.tc,'#ff6b9d'];
  const cw=160,ch=120,gx=16,gy=14;
  const totalW=2*cw+gx, totalH=Math.ceil(n/2)*(ch+gy)-gy;
  const sx=W*.31+(W*.66-totalW)/2, sy=(H-totalH)/2;

  cards.slice(0,n).forEach((card,i)=>{{
    const cp=eo(cl((pr-i*.1)*3,0,1));if(cp<=0)return;
    const col=i%2,row=Math.floor(i/2);
    const cx2=sx+col*(cw+gx), cy2=sy+row*(ch+gy);
    const acc=COLS[i%COLS.length];
    const glow=(gt*.6+i*.4)%1;

    c.save();c.globalAlpha=cp;c.translate(0,(1-cp)*16);

    // Glow
    c.save();c.globalAlpha=cp*(1-glow)*.18;c.strokeStyle=acc;c.lineWidth=2;
    c.beginPath();c.arc(cx2+cw/2,cy2+ch/2,Math.max(cw,ch)/2+glow*20,0,Math.PI*2);c.stroke();c.restore();

    // Card bg
    const bg3=c.createLinearGradient(cx2,cy2,cx2+cw,cy2+ch);
    bg3.addColorStop(0,ha(acc,.14));bg3.addColorStop(1,ha(acc,.05));
    rr(cx2,cy2,cw,ch,14,bg3,acc,2);
    rr(cx2,cy2,cw,6,[14,14,0,0],acc,null);

    // Icon
    c.font=`${{Math.round(36*cp)}}px serif`;c.textAlign='center';c.textBaseline='middle';c.fillText(card.icon||'💡',cx2+cw/2,cy2+36);

    // Title
    c.font='bold 12px Segoe UI';c.fillStyle='#ffffff';c.textAlign='center';c.textBaseline='alphabetic';
    c.fillText(card.title,cx2+cw/2,cy2+66);

    // Divider
    c.save();c.globalAlpha=.25;c.strokeStyle=acc;c.lineWidth=1;
    c.beginPath();c.moveTo(cx2+18,cy2+73);c.lineTo(cx2+cw-18,cy2+73);c.stroke();c.restore();

    // Desc
    c.font='10px Segoe UI';c.fillStyle='#9aa4b4';c.textAlign='center';
    wt(card.desc,cx2+12,cy2+87,cw-24,15,2);
    c.restore();
  }});
}}

// CELEBRATE
function diagCelebrate(scene,p,pr){{
  const a1=eo(cl(pr*2.5,0,1));
  const cx=W*.63,cy=H*.42;
  c.save();c.globalAlpha=a1;
  const gd=c.createRadialGradient(cx,cy,0,cx,cy,180);
  gd.addColorStop(0,ha(p.ac,.15));gd.addColorStop(1,'transparent');c.fillStyle=gd;c.fillRect(0,0,W,H);
  c.font=`${{Math.round(68*a1)}}px serif`;c.textAlign='center';c.textBaseline='middle';c.fillText('🏆',cx,cy-30);
  c.font='bold 22px Segoe UI';c.fillStyle='#ffffff';c.textBaseline='alphabetic';c.fillText('Chapter Complete!',cx,cy+28);
  c.font='13px Segoe UI';c.fillStyle=p.ac;c.fillText(scene.chapter||'',cx,cy+54);
  c.restore();
  // Star burst
  c.save();
  for(let i=0;i<10;i++){{
    const angle=i/10*Math.PI*2+gt*.2;
    const r=110+40*Math.sin(gt*1.4+i);
    const sx2=cx+Math.cos(angle)*r,sy2=cy+Math.sin(angle)*r*.5;
    c.globalAlpha=(.25+.2*Math.sin(gt*3+i))*a1;
    c.font=`${{13+i%4*3}}px serif`;c.textAlign='center';c.textBaseline='middle';
    c.fillText(i%2===0?'⭐':'✨',sx2,sy2);
  }}
  c.restore();
}}

// ─── MAIN RENDER ─────────────────────────────────────────
function render(ts){{
  const dt=(ts-lt)/1e3;lt=ts;gt+=dt;
  const pr=cl((ts-ss)/1500,0,1);
  const scene=SC[cur];const p=P();
  cx2=lerp(cx2,ctx2,.05);
  const talkT=cl((gt-ss/1e3)*.5,0,1)<.95?1:0;

  c.clearRect(0,0,W,H);

  // Background
  switch(scene.bg){{
    case 'dark':bgDark(p);break;case 'space':bgSpace(p);break;
    case 'tech':bgTech(p);break;case 'story':bgStory(p);break;
    case 'celebration':bgCelebration(p);break;default:bgDark(p);
  }}

  // Diagram (right side — most of the screen)
  const dp=cl((ts-ss-400)/2000,0,1);
  c.save();
  switch(scene.type){{
    case 'intro':     diagIntro(scene,p,dp);break;
    case 'mindmap':   diagMindMap(scene,p,dp);break;
    case 'flow':      diagFlow(scene,p,dp);break;
    case 'analogy':   diagAnalogy(scene,p,dp);break;
    case 'steps':     diagSteps(scene,p,dp);break;
    case 'concepts':  diagConcepts(scene,p,dp);break;
    case 'celebrate': diagCelebrate(scene,p,dp);break;
  }}
  c.restore();

  // ARIA (left side)
  drawARIA(cx2,H*.74,.82,scene.pose||'explain',talkT);

  // Speech bubble
  const ba=eo(cl((ts-ss-250)/650,0,1));
  c.save();c.globalAlpha=ba;
  drawBubble(Math.max(cx2-22,14),H*.66,Math.min(W-cx2+16,310),scene.speech||'',p);
  c.restore();

  // Transition fade
  if(trans>0){{c.save();c.globalAlpha=trans;c.fillStyle='#06060f';c.fillRect(0,0,W,H);trans=Math.max(0,trans-.055);c.restore();}}
  af=requestAnimationFrame(render);
}}

// ─── CONTROLS ────────────────────────────────────────────
function goScene(idx){{
  cur=((idx%N)+N)%N;
  ss=performance.now();lt=performance.now();trans=.75;
  const poses=['wave','explain','point','explain','point','explain','celebrate'];
  SC[cur].pose=poses[cur]||'explain';
  ctx2=W*.16+(SC[cur].pose==='point'?12:0);
  updateUI();if(playing)resetTimer();
}}
function nextS(){{goScene(cur+1);}}
function prev(){{goScene(cur-1);}}
function togglePlay(){{
  playing=!playing;
  document.getElementById('pb').innerHTML=playing?'&#9646;&#9646;':'&#9654;';
  if(playing)resetTimer();else clearInterval(timer);
}}
function resetTimer(){{clearInterval(timer);timer=setInterval(nextS,SC[cur].duration||6500);}}
function updateUI(){{
  const p=P(),f=document.getElementById('fill');
  f.style.width=((cur+1)/N*100)+'%';f.style.background=p.ac;
  document.getElementById('lbl').textContent=`Scene ${{cur+1}} / ${{N}}`;
  document.querySelectorAll('.dot').forEach((d,i)=>{{
    d.classList.toggle('on',i===cur);
    d.style.background=i===cur?p.ac:'rgba(255,255,255,.2)';
    d.style.width=i===cur?'20px':'7px';
  }});
}}
function buildDots(){{
  const el=document.getElementById('dots');el.innerHTML='';
  SC.forEach((_,i)=>{{
    const d=document.createElement('div');d.className='dot'+(i===0?' on':'');
    d.onclick=()=>goScene(i);el.appendChild(d);
  }});
}}

buildDots();ctx2=W*.16;cx2=W*.16;
const poses=['wave','explain','point','explain','point','explain','celebrate'];
SC.forEach((s,i)=>s.pose=poses[i]||'explain');
ss=performance.now();lt=performance.now();
updateUI();af=requestAnimationFrame(render);resetTimer();
</script>
</body></html>"""

    components.html(html, height=530, scrolling=False)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import streamlit.components.v1 as components
import json
import re


def clean_text(text: str, limit: int = 250) -> str:
    if not text:
        return ""
    text = re.sub(r'\*{1,2}|_{1,2}', '', text)
    text = re.sub(r'\s+', ' ', text.replace('\n', ' ')).strip()
    return text[:limit]


def build_narrated_scenes(content: dict, chapter_title: str, topic: str) -> list:
    scenes = []

    # Scene 1 — ARIA introduces herself
    scenes.append({
        "type": "intro",
        "speech": f"Hey! I'm ARIA, your AI teacher! Today I'll explain {chapter_title} in a fun and clear way. Let's go!",
        "pose": "wave",
        "bg": "welcome",
        "duration": 5000
    })

    # Scene 2 — Real-life story/analogy
    analogy = content.get("analogy", "")
    if analogy:
        sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', analogy) if len(s.strip()) > 15]
        analogy_text = sents[0] if sents else analogy[:220]
    else:
        analogy_text = f"Let me tell you a little story that makes {chapter_title} super easy to understand!"
    scenes.append({
        "type": "story",
        "speech": clean_text(analogy_text, 220),
        "pose": "explain",
        "bg": "story",
        "duration": 6000
    })

    # Scene 3 — Explanation part 1
    explanation = content.get("explanation", "")
    exp_sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', explanation) if len(s.strip()) > 20]
    if exp_sents:
        scenes.append({
            "type": "explain",
            "speech": clean_text(exp_sents[0], 220),
            "pose": "teach",
            "bg": "classroom",
            "duration": 6500,
            "highlight": clean_text(chapter_title, 32)
        })

    # Scene 4 — Explanation part 2
    if len(exp_sents) > 2:
        scenes.append({
            "type": "explain",
            "speech": clean_text(exp_sents[2], 220),
            "pose": "point",
            "bg": "classroom",
            "duration": 6500,
            "highlight": "Key Point"
        })

    # Scene 5 — Step by step example
    example = content.get("example", "")
    step_lines = []
    for line in example.split('\n'):
        line = line.strip()
        if re.match(r'^step\s*\d', line.lower()):
            parts = line.split(':', 1)
            if len(parts) > 1:
                step_lines.append({"label": clean_text(parts[0], 15), "body": clean_text(parts[1], 85)})
    if step_lines:
        scenes.append({
            "type": "steps",
            "speech": "Now let me walk you through it step by step — follow along with me!",
            "pose": "point",
            "bg": "technical",
            "duration": 7000,
            "steps": step_lines[:4]
        })

    # Scene 6 — Key concepts
    concepts = content.get("key_concepts", [])
    if concepts:
        cards = []
        names = []
        for c in concepts[:4]:
            c = re.sub(r'\*{1,2}|_{1,2}', '', c).strip()
            if ': ' in c:
                name, desc = c.split(': ', 1)
            else:
                name, desc = c[:30], c
            names.append(clean_text(name, 20))
            cards.append({"title": clean_text(name, 26), "desc": clean_text(desc, 72)})
        scenes.append({
            "type": "concepts",
            "speech": f"Here are the key concepts you need to remember: {', '.join(names[:3])}.",
            "pose": "explain",
            "bg": "technical",
            "duration": 7000,
            "cards": cards
        })

    # Scene 7 — Takeaway / celebration
    takeaway = content.get("key_takeaway", "")
    if not takeaway:
        takeaway = f"Amazing! You now understand {chapter_title}. Keep going — you're doing great!"
    scenes.append({
        "type": "celebrate",
        "speech": clean_text(takeaway, 220),
        "pose": "celebrate",
        "bg": "celebration",
        "duration": 6000
    })

    return scenes


def show_video_player(content: dict, chapter_title: str, topic: str):
    scenes = build_narrated_scenes(content, chapter_title, topic)
    scenes_json = json.dumps(scenes, ensure_ascii=False)
    total = len(scenes)
    safe_topic = json.dumps(topic)
    safe_chapter = json.dumps(chapter_title)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#06060f;font-family:'Segoe UI',system-ui,sans-serif;display:flex;flex-direction:column;align-items:center;padding:6px}}
#wrap{{width:100%;max-width:820px;border-radius:20px;overflow:hidden;box-shadow:0 0 60px rgba(0,212,255,0.18)}}
#topbar{{height:4px;background:rgba(255,255,255,0.06)}}
#topfill{{height:100%;width:0%;border-radius:2px;transition:width 0.5s ease}}
canvas{{display:block;width:100%;height:auto;background:#06060f}}
#controls{{display:flex;align-items:center;justify-content:space-between;padding:10px 16px;background:#09091a;border-top:1px solid rgba(255,255,255,0.07)}}
.cbtn{{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.13);border-radius:9px;color:#fff;width:38px;height:38px;font-size:14px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all 0.2s}}
.cbtn:hover{{background:rgba(255,255,255,0.18);transform:scale(1.08)}}
.cbtn.big{{width:44px;height:44px;font-size:16px}}
#dots{{display:flex;gap:5px;align-items:center}}
.dot{{width:7px;height:7px;border-radius:50%;background:rgba(255,255,255,0.2);cursor:pointer;transition:all 0.3s}}
.dot.on{{border-radius:4px;width:20px}}
#lbl{{font-size:11px;color:#8892a4;letter-spacing:1px;text-transform:uppercase}}
</style>
</head>
<body>
<div id="wrap">
  <div id="topbar"><div id="topfill"></div></div>
  <canvas id="c" width="820" height="460"></canvas>
  <div id="controls">
    <div style="display:flex;gap:6px;align-items:center">
      <button class="cbtn" onclick="prev()">&#9664;</button>
      <button class="cbtn big" id="pb" onclick="togglePlay()">&#9646;&#9646;</button>
      <button class="cbtn" onclick="nextScene()">&#9654;</button>
    </div>
    <div id="dots"></div>
    <div id="lbl">Scene 1 / {total}</div>
  </div>
</div>

<script>
const SCENES = {scenes_json};
const TOPIC = {safe_topic};
const CHAPTER = {safe_chapter};
const TOTAL = SCENES.length;
const W = 820, H = 460;

let cur=0, playing=true, timer=null, af=null;
let gt=0, lt=0, slideStart=0, transAlpha=0;
let charX=W*0.17, charTX=W*0.17;

const canvas=document.getElementById('c');
const ctx=canvas.getContext('2d');

const PALETTES={{
  welcome:{{bg:'#06060f',ac:'#00d4ff',sec:'#7b61ff'}},
  story:  {{bg:'#060f0a',ac:'#00ff88',sec:'#00d4ff'}},
  classroom:{{bg:'#0a0618',ac:'#a78bfa',sec:'#00d4ff'}},
  technical:{{bg:'#0a0a18',ac:'#00d4ff',sec:'#7b61ff'}},
  celebration:{{bg:'#0f0a06',ac:'#ffd700',sec:'#ff9500'}}
}};

function pal(){{ return PALETTES[SCENES[cur].bg]||PALETTES.welcome; }}
function h2r(h){{ return {{r:parseInt(h.slice(1,3),16),g:parseInt(h.slice(3,5),16),b:parseInt(h.slice(5,7),16)}}; }}
function ha(h,a){{ const {{r,g,b}}=h2r(h); return `rgba(${{r}},${{g}},${{b}},${{a}})`; }}
function lerp(a,b,t){{ return a+(b-a)*t; }}
function eo(t){{ return 1-Math.pow(1-t,3); }}
function cl(v,a,b){{ return Math.max(a,Math.min(b,v)); }}

function rr(x,y,w,h,r,fill,stroke,sw){{
  ctx.beginPath();
  if(ctx.roundRect)ctx.roundRect(x,y,w,h,typeof r==='number'?r:[r,r,r,r]);
  else{{ctx.moveTo(x+(typeof r==='number'?r:r[0]),y);ctx.lineTo(x+w-(typeof r==='number'?r:r[1]),y);ctx.quadraticCurveTo(x+w,y,x+w,y+(typeof r==='number'?r:r[1]));ctx.lineTo(x+w,y+h-(typeof r==='number'?r:r[2]));ctx.quadraticCurveTo(x+w,y+h,x+w-(typeof r==='number'?r:r[2]),y+h);ctx.lineTo(x+(typeof r==='number'?r:r[3]),y+h);ctx.quadraticCurveTo(x,y+h,x,y+h-(typeof r==='number'?r:r[3]));ctx.lineTo(x,y+(typeof r==='number'?r:r[0]));ctx.quadraticCurveTo(x,y,x+(typeof r==='number'?r:r[0]),y);ctx.closePath();}}
  if(fill){{ctx.fillStyle=fill;ctx.fill();}}
  if(stroke){{ctx.strokeStyle=stroke;ctx.lineWidth=sw||1.5;ctx.stroke();}}
}}

function wt(text,x,y,mw,lh,ml){{
  ctx.save();
  const words=text.split(' ');let line='',n=0,cy=y;
  for(let w of words){{
    const test=line+w+' ';
    if(ctx.measureText(test).width>mw&&line){{
      if(!ml||n<ml)ctx.fillText(line.trim(),x,cy);
      line=w+' ';cy+=lh;n++;
      if(ml&&n>=ml)break;
    }}else line=test;
  }}
  if(line.trim()&&(!ml||n<ml))ctx.fillText(line.trim(),x,cy);
  ctx.restore();
  return cy;
}}

// ─── BACKGROUNDS ────────────────────────────────────────
function bgWelcome(p){{
  ctx.fillStyle=p.bg;ctx.fillRect(0,0,W,H);
  ctx.save();ctx.globalAlpha=0.04;ctx.strokeStyle=p.ac;ctx.lineWidth=1;
  const g=50,off=(gt*12)%g;
  for(let x=-g+off%g;x<W;x+=g){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}}
  for(let y=0;y<H;y+=g){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}}
  ctx.restore();
  [[0.12,0.25,170,p.ac,0.07],[0.88,0.72,140,p.sec,0.06],[0.5,1.1,200,p.ac,0.05]].forEach(([ox,oy,or,col,oa])=>{{
    const gd=ctx.createRadialGradient(ox*W,oy*H,0,ox*W,oy*H,or);
    gd.addColorStop(0,ha(col,oa+0.02*Math.sin(gt*1.2)));gd.addColorStop(1,'transparent');
    ctx.fillStyle=gd;ctx.fillRect(0,0,W,H);
  }});
  ctx.save();
  for(let i=0;i<25;i++){{
    const sx=(i*173+i*i*7)%W,sy=(i*97+i*i*3)%H;
    const a=0.2+0.25*Math.sin(gt*1.3+i*0.9);
    ctx.fillStyle=ha(i%3===0?p.ac:p.sec,a*0.5);
    ctx.beginPath();ctx.arc(sx,sy,1+i%2*0.5,0,Math.PI*2);ctx.fill();
  }}
  ctx.restore();
}}

function bgStory(p){{
  const sky=ctx.createLinearGradient(0,0,0,H);
  sky.addColorStop(0,'#020c16');sky.addColorStop(0.55,'#060f0a');sky.addColorStop(1,'#0a1a0a');
  ctx.fillStyle=sky;ctx.fillRect(0,0,W,H);
  ctx.save();ctx.globalAlpha=0.75;
  const mg=ctx.createRadialGradient(700,65,0,700,65,40);
  mg.addColorStop(0,'#ffffff');mg.addColorStop(0.5,'#c8ffd4');mg.addColorStop(1,'transparent');
  ctx.fillStyle=mg;ctx.beginPath();ctx.arc(700,65,35,0,Math.PI*2);ctx.fill();ctx.restore();
  ctx.save();
  for(let i=0;i<35;i++){{
    const sx=(i*157+i*i*11)%W,sy=(i*83+i*i*5)%(H*0.5);
    const a=0.3+0.35*Math.sin(gt+i*0.75);
    ctx.fillStyle=`rgba(255,255,255,${{a*0.55}})`;
    ctx.beginPath();ctx.arc(sx,sy,0.7+i%2*0.5,0,Math.PI*2);ctx.fill();
  }}
  ctx.restore();
  const gnd=ctx.createLinearGradient(0,H*0.7,0,H);
  gnd.addColorStop(0,'#081408');gnd.addColorStop(1,'#040a04');
  ctx.fillStyle=gnd;ctx.fillRect(0,H*0.7,W,H);
  ctx.save();ctx.globalAlpha=0.55;
  [[65,H*0.7,28,65],[680,H*0.7,22,52],[710,H*0.7,16,42],[745,H*0.7,24,58]].forEach(([tx,ty,tw,th])=>{{
    ctx.fillStyle='#0c1e0c';
    ctx.beginPath();ctx.moveTo(tx,ty-th);ctx.lineTo(tx-tw,ty);ctx.lineTo(tx+tw,ty);ctx.closePath();ctx.fill();
    ctx.fillStyle='#060e06';rr(tx-tw*0.25,ty,tw*0.5,18,3,'#060e06');
  }});
  ctx.restore();
  ctx.save();ctx.globalAlpha=0.25;
  const path=ctx.createLinearGradient(W/2,H*0.7,W/2,H);
  path.addColorStop(0,ha(p.ac,0.5));path.addColorStop(1,'transparent');
  ctx.fillStyle=path;
  ctx.beginPath();ctx.moveTo(W/2-18,H*0.7);ctx.lineTo(W/2-55,H);ctx.lineTo(W/2+55,H);ctx.lineTo(W/2+18,H*0.7);ctx.closePath();ctx.fill();
  ctx.restore();
}}

function bgClassroom(p){{
  ctx.fillStyle=p.bg;ctx.fillRect(0,0,W,H);
  const bx=400,by=35,bw=380,bh=260;
  rr(bx,by,bw,bh,14,ha(p.ac,0.05),ha(p.ac,0.18),1.5);
  ctx.save();ctx.globalAlpha=0.7;
  ctx.font='bold 13px Segoe UI';ctx.fillStyle=p.ac;ctx.textAlign='center';
  ctx.fillText((SCENES[cur].highlight||'KEY CONCEPT').toUpperCase(),bx+bw/2,by+26);ctx.restore();
  ctx.save();ctx.globalAlpha=0.25;ctx.strokeStyle=p.ac;ctx.lineWidth=1;ctx.setLineDash([4,4]);
  ctx.beginPath();ctx.moveTo(bx+18,by+36);ctx.lineTo(bx+bw-18,by+36);ctx.stroke();ctx.setLineDash([]);ctx.restore();
  const wp=cl((gt-slideStart/1000-0.5)*0.28,0,1);
  ctx.save();ctx.globalAlpha=0.45*wp;ctx.font='12px monospace';ctx.fillStyle='#b8c4d4';ctx.textAlign='left';
  ['• Core concept','• Application','• Key formula','• Remember this'].forEach((l,i)=>{{
    if(i/4<wp)ctx.fillText(l,bx+20,by+62+i*32);
  }});
  ctx.restore();
  ctx.save();ctx.globalAlpha=0.12;ctx.strokeStyle='#ffffff';ctx.lineWidth=1.5;
  ctx.beginPath();ctx.moveTo(0,H*0.78);ctx.lineTo(W*0.44,H*0.78);ctx.stroke();ctx.restore();
  ctx.save();ctx.globalAlpha=0.03;ctx.strokeStyle=p.ac;ctx.lineWidth=1;
  for(let x=0;x<W;x+=50){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}}
  for(let y=0;y<H;y+=50){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}}
  ctx.restore();
}}

function bgTechnical(p){{
  ctx.fillStyle=p.bg;ctx.fillRect(0,0,W,H);
  ctx.save();ctx.globalAlpha=0.04;ctx.strokeStyle=p.ac;ctx.lineWidth=1;
  const gs=40,off=(gt*8)%gs;
  for(let x=-gs+off%gs;x<W;x+=gs){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}}
  for(let y=off;y<H;y+=gs){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}}
  ctx.restore();
  ctx.save();
  for(let i=0;i<7;i++){{
    const nx=580+Math.cos(gt*0.28+i*1.0)*110,ny=210+Math.sin(gt*0.35+i*1.0)*75;
    const nr=14+i*4;
    ctx.globalAlpha=0.06+0.02*Math.sin(gt+i);
    ctx.strokeStyle=i%2===0?p.ac:p.sec;ctx.lineWidth=1.5;
    ctx.beginPath();
    for(let j=0;j<6;j++){{const a=j/6*Math.PI*2-Math.PI/6;j===0?ctx.moveTo(nx+Math.cos(a)*nr,ny+Math.sin(a)*nr):ctx.lineTo(nx+Math.cos(a)*nr,ny+Math.sin(a)*nr);}}
    ctx.closePath();ctx.stroke();
  }}
  ctx.restore();
  [[0.1,0.2,110,p.ac,0.06],[0.85,0.78,95,p.sec,0.05]].forEach(([ox,oy,or,col,oa])=>{{
    const gd=ctx.createRadialGradient(ox*W,oy*H,0,ox*W,oy*H,or);
    gd.addColorStop(0,ha(col,oa));gd.addColorStop(1,'transparent');
    ctx.fillStyle=gd;ctx.fillRect(0,0,W,H);
  }});
}}

function bgCelebration(p){{
  ctx.fillStyle=p.bg;ctx.fillRect(0,0,W,H);
  ctx.save();ctx.globalAlpha=0.1+0.04*Math.sin(gt*2);
  const burst=ctx.createRadialGradient(W/2,H/2,0,W/2,H/2,300);
  burst.addColorStop(0,p.ac);burst.addColorStop(0.5,p.sec);burst.addColorStop(1,'transparent');
  ctx.fillStyle=burst;ctx.fillRect(0,0,W,H);ctx.restore();
  const cc=[p.ac,p.sec,'#ff6b6b','#00ff88','#ffd700','#ff9500'];
  ctx.save();
  for(let i=0;i<45;i++){{
    const cx2=(i*137.5+gt*28*((i%3)-1)*0.9)%W;
    const cy2=((i*73+gt*38+i*195)%H);
    const a=0.4+0.3*Math.sin(gt*2+i);
    ctx.fillStyle=ha(cc[i%cc.length],a*0.7);
    ctx.save();ctx.translate(cx2%W,cy2%H);ctx.rotate(gt+i);
    ctx.fillRect(-4,-4,8,3);ctx.restore();
  }}
  ctx.restore();
  ctx.save();
  for(let i=0;i<10;i++){{
    const angle=i/10*Math.PI*2+gt*0.18;
    const r=140+45*Math.sin(gt*1.4+i);
    const sx=W/2+Math.cos(angle)*r,sy=H/2+Math.sin(angle)*r*0.5;
    ctx.globalAlpha=0.3+0.2*Math.sin(gt*3+i);
    ctx.font=`${{14+i%4*3}}px serif`;ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(i%2===0?'⭐':'✨',sx,sy);
  }}
  ctx.restore();
}}

// ─── ARIA CHARACTER ─────────────────────────────────────
function drawARIA(x,y,sc,pose,talk){{
  const p=pal();
  ctx.save();ctx.translate(x,y);ctx.scale(sc,sc);
  const br=Math.sin(gt*1.8)*2;
  const mo=Math.sin(talk*8)*0.5+0.5;

  // Shadow
  ctx.save();ctx.globalAlpha=0.15;ctx.fillStyle='#000000';
  ctx.beginPath();ctx.ellipse(0,128,36,9,0,0,Math.PI*2);ctx.fill();ctx.restore();

  // Legs
  [-14,14].forEach((lx,li)=>{{
    const ls=pose==='celebrate'?Math.sin(gt*3+li*Math.PI)*7:0;
    ctx.save();ctx.translate(lx,90+br*0.3);ctx.rotate(ls*0.05);
    rr(-6,0,13,30,5,ha(p.ac,0.65),p.ac,1.5);
    rr(-8,27,18,8,4,ha(p.sec,0.75),p.sec,1);
    ctx.restore();
  }});

  // Body
  const bg2=ctx.createLinearGradient(-28,22,28,82);
  bg2.addColorStop(0,ha(p.ac,0.22));bg2.addColorStop(1,ha(p.sec,0.14));
  rr(-28,22+br*0.3,56,60,10,bg2,p.ac,2);
  ctx.save();ctx.globalAlpha=0.12+0.05*Math.sin(gt*2);
  const bg3=ctx.createRadialGradient(0,50,0,0,50,50);
  bg3.addColorStop(0,p.ac);bg3.addColorStop(1,'transparent');
  ctx.fillStyle=bg3;ctx.fillRect(-35,18,70,70);ctx.restore();
  ctx.save();ctx.globalAlpha=0.22;ctx.strokeStyle=p.ac;ctx.lineWidth=0.8;
  [[0,38],[0,52],[0,65]].forEach(([bx3,by3])=>{{ctx.beginPath();ctx.moveTo(-20,by3+br*0.2);ctx.lineTo(20,by3+br*0.2);ctx.stroke();}});
  ctx.beginPath();ctx.moveTo(-8,38+br*0.2);ctx.lineTo(-8,65+br*0.2);ctx.stroke();
  ctx.beginPath();ctx.moveTo(8,38+br*0.2);ctx.lineTo(8,65+br*0.2);ctx.stroke();ctx.restore();
  const core=ctx.createRadialGradient(0,52,0,0,52,7);
  core.addColorStop(0,ha(p.ac,0.9+0.1*Math.sin(gt*3)));core.addColorStop(1,ha(p.ac,0.1));
  ctx.beginPath();ctx.arc(0,52+br*0.2,5.5,0,Math.PI*2);ctx.fillStyle=core;ctx.fill();

  // Arms
  let la=-Math.PI/8+br*0.01, ra=Math.PI/8;
  if(pose==='wave'){{la=-Math.PI/2.4+Math.sin(gt*4)*0.22;}}
  else if(pose==='point'){{la=-Math.PI/3;}}
  else if(pose==='celebrate'){{la=-Math.PI/2+Math.sin(gt*3)*0.28;ra=-Math.PI/2+Math.sin(gt*3+1)*0.28;}}

  ctx.save();ctx.translate(-28,36+br*0.3);ctx.rotate(la);
  rr(-6,0,12,36,5,ha(p.ac,0.55),p.ac,1.5);
  ctx.beginPath();ctx.arc(0,36,7,0,Math.PI*2);ctx.fillStyle=ha(p.ac,0.8);ctx.fill();ctx.strokeStyle=p.ac;ctx.lineWidth=1.5;ctx.stroke();
  if(pose==='wave'){{ctx.font='16px serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('👋',0,36);}}
  ctx.restore();

  ctx.save();ctx.translate(28,36+br*0.3);ctx.rotate(ra);
  rr(-6,0,12,36,5,ha(p.sec,0.55),p.sec,1.5);
  ctx.beginPath();ctx.arc(0,36,7,0,Math.PI*2);ctx.fillStyle=ha(p.sec,0.8);ctx.fill();ctx.strokeStyle=p.sec;ctx.lineWidth=1.5;ctx.stroke();
  if(pose==='point'){{ctx.font='14px serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('👉',0,36);}}
  if(pose==='celebrate'){{ctx.font='14px serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('🎉',0,36);}}
  ctx.restore();

  // Head
  const hy=-42+br;
  ctx.save();ctx.globalAlpha=0.11+0.04*Math.sin(gt*1.4);
  const aura=ctx.createRadialGradient(0,hy,0,0,hy,55);
  aura.addColorStop(0,p.ac);aura.addColorStop(1,'transparent');
  ctx.fillStyle=aura;ctx.fillRect(-60,hy-55,120,110);ctx.restore();
  const hg=ctx.createRadialGradient(-8,hy-8,4,0,hy,38);
  hg.addColorStop(0,'#1e1e3f');hg.addColorStop(0.7,'#0d0d22');hg.addColorStop(1,'#080818');
  ctx.beginPath();ctx.arc(0,hy,37,0,Math.PI*2);ctx.fillStyle=hg;ctx.fill();
  ctx.strokeStyle=p.ac;ctx.lineWidth=2.5;ctx.stroke();
  ctx.save();ctx.globalAlpha=0.18;ctx.strokeStyle=p.sec;ctx.lineWidth=1;ctx.setLineDash([4,6]);
  ctx.beginPath();ctx.arc(0,hy,30,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);ctx.restore();
  const vg=ctx.createLinearGradient(-23,hy-17,23,hy+8);
  vg.addColorStop(0,ha(p.ac,0.22));vg.addColorStop(1,ha(p.ac,0.05));
  rr(-23,hy-17,46,27,8,vg,ha(p.ac,0.38),1.5);
  ctx.save();ctx.globalAlpha=0.1;rr(-19,hy-14,18,8,4,ha('#ffffff',0.5));ctx.restore();

  // Eyes
  const blink=Math.abs(Math.sin(gt*0.33));
  [[-11,hy-5],[11,hy-5]].forEach(([ex,ey],ei)=>{{
    const bh2=blink<0.05?0.1:1;
    ctx.save();ctx.translate(0,ey*(1-bh2));ctx.scale(1,bh2);
    ctx.globalAlpha=(0.25+0.15*Math.sin(gt*2+ei))*bh2;
    const eg=ctx.createRadialGradient(ex,ey/bh2,0,ex,ey/bh2,12);
    eg.addColorStop(0,p.ac);eg.addColorStop(1,'transparent');
    ctx.fillStyle=eg;ctx.beginPath();ctx.arc(ex,ey/bh2,12,0,Math.PI*2);ctx.fill();
    ctx.globalAlpha=bh2;
    const ec=ctx.createRadialGradient(ex,ey/bh2,0,ex,ey/bh2,5);
    ec.addColorStop(0,'#ffffff');ec.addColorStop(0.4,p.ac);ec.addColorStop(1,ha(p.ac,0.3));
    ctx.beginPath();ctx.arc(ex,ey/bh2,5,0,Math.PI*2);ctx.fillStyle=ec;ctx.fill();
    ctx.restore();
  }});

  // Mouth
  const my=hy+13;
  if(mo>0.4&&talk>0){{
    const mh=2.5+mo*5;
    ctx.beginPath();ctx.ellipse(0,my,9,mh,0,0,Math.PI*2);
    ctx.fillStyle=ha(p.ac,0.4);ctx.fill();ctx.strokeStyle=p.ac;ctx.lineWidth=1.5;ctx.stroke();
    ctx.save();ctx.globalAlpha=0.45*mo;
    const mg2=ctx.createRadialGradient(0,my,0,0,my,9);
    mg2.addColorStop(0,ha('#ffffff',0.8));mg2.addColorStop(1,'transparent');
    ctx.fillStyle=mg2;ctx.beginPath();ctx.ellipse(0,my,9,mh,0,0,Math.PI*2);ctx.fill();ctx.restore();
  }}else{{
    ctx.beginPath();ctx.arc(0,my-2,8,0.18,Math.PI-0.18);
    ctx.strokeStyle=p.ac;ctx.lineWidth=2;ctx.stroke();
    ctx.save();ctx.globalAlpha=0.35;
    [[-15,my+2],[15,my+2]].forEach(([cx2,cy2])=>{{ctx.fillStyle=ha('#ff9090',0.7);ctx.beginPath();ctx.arc(cx2,cy2,3,0,Math.PI*2);ctx.fill();}});
    ctx.restore();
  }}

  // Antenna
  const ay=hy-37,as2=Math.sin(gt*1.4)*3;
  ctx.save();ctx.strokeStyle=ha(p.ac,0.6);ctx.lineWidth=2;
  ctx.beginPath();ctx.moveTo(0,ay);ctx.lineTo(as2,ay-22);ctx.stroke();
  const ag=ctx.createRadialGradient(as2,ay-24,0,as2,ay-24,7);
  ag.addColorStop(0,p.ac);ag.addColorStop(1,ha(p.ac,0.2));
  ctx.beginPath();ctx.arc(as2,ay-24,5+Math.sin(gt*3),0,Math.PI*2);ctx.fillStyle=ag;ctx.fill();ctx.restore();

  // Name tag
  ctx.save();ctx.globalAlpha=0.65;
  rr(-20,100+br*0.3,40,14,7,ha(p.ac,0.15),ha(p.ac,0.38),1);
  ctx.font='bold 8px Segoe UI';ctx.fillStyle=p.ac;ctx.textAlign='center';ctx.textBaseline='middle';
  ctx.fillText('ARIA',0,107+br*0.3);ctx.restore();

  ctx.restore();
}}

// ─── SPEECH BUBBLE ──────────────────────────────────────
function drawBubble(bx,by,bw,text,p){{
  if(!text)return;
  ctx.font='14.5px Segoe UI';
  const pad=16,lh=21,mw=bw-pad*2;
  const words=text.split(' ');let lines=[],line='';
  for(let w of words){{
    const test=line+w+' ';
    if(ctx.measureText(test).width>mw&&line){{lines.push(line.trim());line=w+' ';}}
    else line=test;
  }}
  if(line.trim())lines.push(line.trim());
  const bh=lines.length*lh+pad*2,ty=by-bh-12;

  ctx.save();ctx.globalAlpha=0.28;rr(bx+4,ty+4,bw,bh,14,'rgba(0,0,0,0.6)');ctx.restore();
  const bg4=ctx.createLinearGradient(bx,ty,bx,ty+bh);
  bg4.addColorStop(0,'rgba(10,10,30,0.96)');bg4.addColorStop(1,'rgba(6,6,18,0.96)');
  rr(bx,ty,bw,bh,14,bg4,ha(p.ac,0.48),2);
  ctx.save();ctx.globalAlpha=0.06;rr(bx+6,ty+6,bw-12,bh/2-6,10,ha('#ffffff',1));ctx.restore();

  // Tail
  ctx.save();ctx.fillStyle='rgba(8,8,22,0.96)';ctx.strokeStyle=ha(p.ac,0.48);ctx.lineWidth=2;
  ctx.beginPath();ctx.moveTo(bx+38,ty+bh);ctx.lineTo(bx+28,ty+bh+14);ctx.lineTo(bx+60,ty+bh);ctx.closePath();
  ctx.fill();ctx.stroke();ctx.restore();

  ctx.font='14.5px Segoe UI';ctx.fillStyle='#e6ecf5';ctx.textAlign='left';
  lines.forEach((l,i)=>ctx.fillText(l,bx+pad,ty+pad+15+i*lh));

  // Talking dots
  ctx.save();ctx.textAlign='left';
  [0,0.35,0.7].forEach((d,i)=>{{
    ctx.globalAlpha=(0.4+0.4*Math.sin(gt*4+d))*0.7;
    ctx.fillStyle=p.ac;ctx.beginPath();ctx.arc(bx+bw-22+i*7,ty+bh-10,3,0,Math.PI*2);ctx.fill();
  }});
  ctx.restore();
}}

// ─── SCENE CONTENT (right side) ─────────────────────────
function drawContent(scene,p,prog){{
  const ox=310;
  if(scene.type==='intro'||scene.type==='story'){{
    const a=eo(cl(prog*2.5,0,1));
    ctx.save();ctx.globalAlpha=a;
    ctx.font=`${{Math.round(72*eo(cl(prog*3,0,1)))}}px serif`;
    ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(scene.type==='intro'?'🤖':'💡',W*0.77,H*0.33);
    const gd=ctx.createRadialGradient(W*0.77,H*0.33,0,W*0.77,H*0.33,80);
    gd.addColorStop(0,ha(p.ac,0.12));gd.addColorStop(1,'transparent');
    ctx.fillStyle=gd;ctx.fillRect(0,0,W,H);
    ctx.font='bold 26px Segoe UI';ctx.fillStyle='#ffffff';ctx.textBaseline='alphabetic';
    ctx.fillText(scene.type==='intro'?TOPIC:CHAPTER,W*0.77,H*0.58);
    ctx.font='13px Segoe UI';ctx.fillStyle=p.ac;
    ctx.fillText(scene.type==='intro'?'Your AI Teacher':'Real Life Story',W*0.77,H*0.68);
    ctx.restore();

  }}else if(scene.type==='explain'){{
    const cp=eo(cl(prog*3,0,1));
    const cx=ox,cy=42,cw=W-ox-28,ch=H-72;
    ctx.save();ctx.globalAlpha=cp;
    rr(cx,cy,cw,ch,16,ha(p.ac,0.05),ha(p.ac,0.17),1.5);
    rr(cx,cy,cw,38,16,ha(p.ac,0.14));
    ctx.font='bold 12px Segoe UI';ctx.fillStyle=p.ac;ctx.textAlign='center';
    ctx.fillText((scene.highlight||'EXPLANATION').toUpperCase(),cx+cw/2,cy+23);
    ctx.font='14px Segoe UI';ctx.fillStyle='#c9d3e0';ctx.textAlign='left';
    const words2=scene.speech.split(' ');let line2='',ln=0,lx=cx+16,ly=cy+60;
    for(let i=0;i<Math.floor(words2.length*cl(prog*2.2,0,1));i++){{
      const test=line2+words2[i]+' ';
      if(ctx.measureText(test).width>cw-32&&line2){{
        ctx.fillText(line2.trim(),lx,ly+ln*23);line2=words2[i]+' ';ln++;
        if(ly+ln*23>cy+ch-18)break;
      }}else line2=test;
    }}
    if(line2.trim())ctx.fillText(line2.trim(),lx,ly+ln*23);
    ctx.restore();

  }}else if(scene.type==='steps'){{
    const steps=scene.steps||[];
    steps.forEach((step,i)=>{{
      const sp=eo(cl((prog-i*0.14)*3,0,1));
      if(sp<=0)return;
      const sy2=35+i*96,sx=ox;
      ctx.save();ctx.globalAlpha=sp;
      rr(sx,sy2,W-sx-22,80,12,ha(p.ac,0.07),ha(p.ac,0.2),1.5);
      ctx.beginPath();ctx.arc(sx+24,sy2+40,16,0,Math.PI*2);
      const cg=ctx.createRadialGradient(sx+24,sy2+40,0,sx+24,sy2+40,16);
      cg.addColorStop(0,ha(p.ac,0.4));cg.addColorStop(1,ha(p.ac,0.1));
      ctx.fillStyle=cg;ctx.fill();ctx.strokeStyle=p.ac;ctx.lineWidth=2;ctx.stroke();
      ctx.font='bold 12px Segoe UI';ctx.fillStyle='#ffffff';ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillText(i+1,sx+24,sy2+40);ctx.textBaseline='alphabetic';
      ctx.font='bold 12px Segoe UI';ctx.fillStyle=p.ac;ctx.textAlign='left';
      ctx.fillText(step.label||`Step ${{i+1}}`,sx+48,sy2+28);
      ctx.font='12px Segoe UI';ctx.fillStyle='#c9d3e0';
      wt(step.body||'',sx+48,sy2+46,W-sx-72,18,2);
      ctx.restore();
    }});

  }}else if(scene.type==='concepts'){{
    const cards=scene.cards||[];
    const cw=(W-ox-28)/2-8;
    cards.forEach((card,i)=>{{
      const cp2=eo(cl((prog-i*0.1)*3,0,1));if(cp2<=0)return;
      const col=i%2,row=Math.floor(i/2);
      const cx=ox+col*(cw+16),cy=38+row*145;
      ctx.save();ctx.globalAlpha=cp2;ctx.translate(0,(1-cp2)*18);
      const ac2=i%2===0?p.ac:p.sec;
      rr(cx,cy,cw,128,12,ha(ac2,0.08),ha(ac2,0.28),2);
      rr(cx,cy,cw,5,[12,12,0,0],ac2,null);
      ctx.font=`${{Math.round(28*cp2)}}px serif`;ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillText(['💡','⚡','🔑','🎯'][i%4],cx+cw/2,cy+40);
      ctx.font='bold 12px Segoe UI';ctx.fillStyle='#ffffff';ctx.textAlign='center';ctx.textBaseline='alphabetic';
      ctx.fillText(card.title,cx+cw/2,cy+72);
      ctx.font='11px Segoe UI';ctx.fillStyle='#a8b4c4';
      wt(card.desc,cx+10,cy+90,cw-20,17,2);
      ctx.restore();
    }});

  }}else if(scene.type==='celebrate'){{
    const ap=eo(cl(prog*2.2,0,1));
    const bx=ox+10,by=55,bw2=W-ox-38,bh2=160;
    ctx.save();ctx.globalAlpha=ap;
    const bg5=ctx.createRadialGradient(bx+bw2/2,by+bh2/2,0,bx+bw2/2,by+bh2/2,160);
    bg5.addColorStop(0,ha(p.ac,0.13));bg5.addColorStop(1,'transparent');
    ctx.fillStyle=bg5;ctx.fillRect(0,0,W,H);
    rr(bx,by,bw2,bh2,20,ha(p.ac,0.09),ha(p.ac,0.38),2.5);
    ctx.font=`${{Math.round(52*ap)}}px serif`;ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText('🏆',bx+bw2/2,by+58);
    ctx.font='bold 19px Segoe UI';ctx.fillStyle='#ffffff';ctx.textBaseline='alphabetic';
    ctx.fillText('Chapter Complete!',bx+bw2/2,by+105);
    ctx.font='13px Segoe UI';ctx.fillStyle=p.ac;
    ctx.fillText(CHAPTER,bx+bw2/2,by+130);
    ctx.restore();
  }}
}}

// ─── RENDER LOOP ────────────────────────────────────────
function render(ts){{
  const dt=(ts-lt)/1000;lt=ts;gt+=dt;
  const prog=cl((ts-slideStart)/1500,0,1);
  const scene=SCENES[cur];const p=pal();
  charX=lerp(charX,charTX,0.05);
  const talkT=cl((gt-slideStart/1000)*0.5,0,1)<0.95?1:0;

  ctx.clearRect(0,0,W,H);
  switch(scene.bg){{
    case 'welcome':bgWelcome(p);break;case 'story':bgStory(p);break;
    case 'classroom':bgClassroom(p);break;case 'technical':bgTechnical(p);break;
    case 'celebration':bgCelebration(p);break;default:bgWelcome(p);
  }}
  const cp=cl((ts-slideStart-550)/2000,0,1);
  drawContent(scene,p,cp);
  drawARIA(charX,H*0.74,0.87,scene.pose||'explain',talkT);
  const ba=eo(cl((ts-slideStart-280)/700,0,1));
  ctx.save();ctx.globalAlpha=ba;
  drawBubble(Math.max(charX-25,18),H*0.67,Math.min(W-charX+20,380),scene.speech||'',p);
  ctx.restore();
  if(transAlpha>0){{
    ctx.save();ctx.globalAlpha=transAlpha;ctx.fillStyle='#06060f';ctx.fillRect(0,0,W,H);
    transAlpha=Math.max(0,transAlpha-0.055);ctx.restore();
  }}
  af=requestAnimationFrame(render);
}}

// ─── CONTROLS ───────────────────────────────────────────
function goScene(idx){{
  cur=((idx%TOTAL)+TOTAL)%TOTAL;
  slideStart=performance.now();lt=performance.now();transAlpha=0.75;
  charTX=W*0.17+(SCENES[cur].pose==='point'?14:0);
  updateUI();if(playing)resetTimer();
}}
function nextScene(){{goScene(cur+1);}}
function prev(){{goScene(cur-1);}}
function togglePlay(){{
  playing=!playing;
  document.getElementById('pb').innerHTML=playing?'&#9646;&#9646;':'&#9654;';
  if(playing)resetTimer();else clearInterval(timer);
}}
function resetTimer(){{
  clearInterval(timer);
  timer=setInterval(nextScene,SCENES[cur].duration||6000);
}}
function updateUI(){{
  const p=pal();
  const tf=document.getElementById('topfill');
  tf.style.width=((cur+1)/TOTAL*100)+'%';tf.style.background=p.ac;
  document.getElementById('lbl').textContent=`Scene ${{cur+1}} / ${{TOTAL}}`;
  document.querySelectorAll('.dot').forEach((d,i)=>{{
    d.classList.toggle('on',i===cur);
    d.style.background=i===cur?p.ac:'rgba(255,255,255,0.2)';
    d.style.width=i===cur?'20px':'7px';
  }});
}}
function buildDots(){{
  const el=document.getElementById('dots');el.innerHTML='';
  SCENES.forEach((_,i)=>{{
    const d=document.createElement('div');d.className='dot'+(i===0?' on':'');
    d.onclick=()=>goScene(i);el.appendChild(d);
  }});
}}

buildDots();charTX=W*0.17;charX=W*0.17;
slideStart=performance.now();lt=performance.now();
updateUI();af=requestAnimationFrame(render);resetTimer();
</script>
</body></html>"""

    components.html(html, height=530, scrolling=False)

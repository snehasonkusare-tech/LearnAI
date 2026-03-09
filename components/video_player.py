import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import streamlit.components.v1 as components
import json
import re

def clean(text: str, limit: int = 300) -> str:
    if not text:
        return ""
    text = re.sub(r'\*{1,2}|_{1,2}', '', text)
    text = text.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
    text = re.sub(r'\s+', ' ', text.replace('\n', ' ')).strip()
    return text[:limit]

def build_slides(content: dict, chapter_title: str, topic: str) -> list:
    explanation = content.get("explanation", "")
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', explanation) if len(s.strip()) > 20]

    analogy = content.get("analogy", "")
    analogy_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', analogy) if len(s.strip()) > 15]

    example = content.get("example", "")
    step_lines = []
    for line in example.split('\n'):
        line = line.strip()
        if re.match(r'^step\s*\d', line.lower()):
            parts = line.split(':', 1)
            label = parts[0].strip() if parts else line
            body = parts[1].strip() if len(parts) > 1 else ""
            step_lines.append({"label": clean(label, 20), "body": clean(body, 90)})
    if not step_lines:
        for s in [s.strip() for s in example.split('\n') if len(s.strip()) > 15][:5]:
            step_lines.append({"label": "Step", "body": clean(s, 90)})

    key_concepts = content.get("key_concepts", [])
    cards = []
    for c in key_concepts[:4]:
        c = re.sub(r'\*{1,2}|_{1,2}', '', c).strip()
        if ": " in c:
            t, d = c.split(": ", 1)
        else:
            t, d = "Concept", c
        cards.append({"title": clean(t, 28), "desc": clean(d, 90)})

    mistakes_text = content.get("common_mistakes", "")
    mistake_lines = [s.strip() for s in mistakes_text.split('\n') if len(s.strip()) > 15][:3]
    if not mistake_lines:
        mistake_lines = [clean(mistakes_text, 150)]

    takeaway = content.get("key_takeaway", "")
    takeaway_short = clean(" ".join([s.strip() for s in re.split(r'(?<=[.!?])\s+', takeaway) if len(s.strip()) > 10][:2]), 200)

    visual = content.get("visual", "")
    nodes = []
    for line in visual.split('\n'):
        found = re.findall(r'\[([^\]]{2,28})\]|\(([^)]{2,28})\)', line)
        for f in found:
            label = (f[0] or f[1]).strip()
            if label:
                nodes.append(clean(label, 22))
    nodes = list(dict.fromkeys(nodes))[:7]
    if not nodes:
        nodes = [clean(chapter_title, 22), "Process", "Output"]

    slides = [
        {"type": "title",     "title": clean(chapter_title, 55), "topic": clean(topic, 35), "desc": clean(sentences[0] if sentences else "", 130)},
        {"type": "explain",   "title": clean(chapter_title, 45), "lines": [clean(s, 130) for s in sentences[:5]], "topic": clean(topic, 30)},
        {"type": "flowchart", "title": "How It Works", "nodes": nodes, "topic": clean(topic, 30)},
        {"type": "analogy",   "title": "Real Life Analogy", "lines": [clean(s, 130) for s in analogy_sentences[:4]]},
        {"type": "steps",     "title": "Step by Step", "steps": step_lines[:5]},
        {"type": "concepts",  "title": "Key Concepts", "cards": cards},
        {"type": "mistakes",  "title": "Common Mistakes", "items": [clean(m, 110) for m in mistake_lines]},
        {"type": "takeaway",  "title": "Key Takeaway", "body": takeaway_short, "topic": clean(topic, 30), "chapter": clean(chapter_title, 40)},
    ]
    return slides


def show_video_player(content: dict, chapter_title: str, topic: str):
    slides = build_slides(content, chapter_title, topic)
    slides_json = json.dumps(slides, ensure_ascii=False)
    total = len(slides)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#06060f;font-family:'Segoe UI',system-ui,sans-serif;display:flex;flex-direction:column;align-items:center;padding:6px}}
#player{{width:100%;max-width:800px;border-radius:20px;overflow:hidden;box-shadow:0 0 80px rgba(0,212,255,0.18)}}
#topbar{{height:4px;background:rgba(255,255,255,0.06)}}
#topfill{{height:100%;width:0%;border-radius:2px;transition:width 0.6s ease}}
canvas{{display:block;width:100%;height:auto;background:#06060f}}
#controls{{display:flex;align-items:center;justify-content:space-between;padding:10px 16px;background:#09091a;border-top:1px solid rgba(255,255,255,0.07)}}
.cbtn{{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.13);border-radius:9px;color:#fff;width:38px;height:38px;font-size:14px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all 0.2s}}
.cbtn:hover{{background:rgba(255,255,255,0.18);transform:scale(1.08)}}
.cbtn.big{{width:44px;height:44px;font-size:16px}}
#dots{{display:flex;gap:5px;align-items:center}}
.dot{{width:7px;height:7px;border-radius:50%;background:rgba(255,255,255,0.2);cursor:pointer;transition:all 0.3s}}
.dot.on{{border-radius:4px;width:22px}}
#ctr{{font-size:12px;color:#8892a4;min-width:36px;text-align:right}}
</style>
</head>
<body>
<div id="player">
  <div id="topbar"><div id="topfill"></div></div>
  <canvas id="c" width="800" height="430"></canvas>
  <div id="controls">
    <div style="display:flex;gap:6px;align-items:center">
      <button class="cbtn" onclick="prev()">◀</button>
      <button class="cbtn big" id="pb" onclick="togglePlay()">⏸</button>
      <button class="cbtn" onclick="nextSlide()">▶</button>
    </div>
    <div id="dots"></div>
    <div id="ctr">1/{total}</div>
  </div>
</div>

<script>
const slides = {slides_json};
const TOTAL = slides.length;
let cur = 0, playing = true, timer = null, animFrame = null;
let t = 0;
const DURATION = 8000;

const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
const W = 800, H = 430;

const PALETTES = [
  {{bg:'#06060f', accent:'#00d4ff', secondary:'#7b61ff'}},
  {{bg:'#0a0618', accent:'#a78bfa', secondary:'#00d4ff'}},
  {{bg:'#060f0a', accent:'#00ff88', secondary:'#00d4ff'}},
  {{bg:'#0f0a06', accent:'#ff9500', secondary:'#ff6b6b'}},
  {{bg:'#0a0a18', accent:'#ffd700', secondary:'#ff9500'}},
  {{bg:'#0c0618', accent:'#ff6b9d', secondary:'#a78bfa'}},
  {{bg:'#0f0606', accent:'#ff6b6b', secondary:'#ffd700'}},
  {{bg:'#06060f', accent:'#00d4ff', secondary:'#00ff88'}},
];
function pal(i){{ return PALETTES[i % PALETTES.length]; }}

function lerp(a,b,t){{ return a+(b-a)*t; }}
function easeOut(t){{ return 1-Math.pow(1-t,3); }}
function clamp(v,a,b){{ return Math.max(a,Math.min(b,v)); }}

function wrapText(ctx, text, x, y, maxW, lineH){{
  const words = text.split(' ');
  let line = '', cy = y;
  for(let w of words){{
    const test = line + w + ' ';
    if(ctx.measureText(test).width > maxW && line){{
      ctx.fillText(line.trim(), x, cy);
      line = w + ' '; cy += lineH;
    }} else line = test;
  }}
  if(line.trim()) ctx.fillText(line.trim(), x, cy);
  return cy;
}}

function roundRect(ctx, x, y, w, h, r, fill, stroke, sw){{
  ctx.beginPath();
  ctx.roundRect(x,y,w,h,r);
  if(fill){{ ctx.fillStyle=fill; ctx.fill(); }}
  if(stroke){{ ctx.strokeStyle=stroke; ctx.lineWidth=sw||1.5; ctx.stroke(); }}
}}

function hexA(hex, a){{
  const r=parseInt(hex.slice(1,3),16), g=parseInt(hex.slice(3,5),16), b=parseInt(hex.slice(5,7),16);
  return `rgba(${{r}},${{g}},${{b}},${{a}})`;
}}

function drawBg(p, t){{
  ctx.fillStyle = p.bg;
  ctx.fillRect(0,0,W,H);

  ctx.save();
  ctx.globalAlpha = 0.04;
  ctx.strokeStyle = p.accent;
  ctx.lineWidth = 1;
  const gridSize = 50;
  const offset = (t * 20) % gridSize;
  for(let x = -gridSize+offset%gridSize; x < W; x+=gridSize){{
    ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke();
  }}
  for(let y = 0; y < H; y+=gridSize){{
    ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke();
  }}
  ctx.restore();

  const orbs = [
    {{x:0.15, y:0.2, r:180, col:p.accent}},
    {{x:0.85, y:0.75, r:150, col:p.secondary}},
    {{x:0.5, y:1.1, r:200, col:p.accent}},
  ];
  orbs.forEach((o,i)=>{{
    const pulse = 0.08 + 0.03*Math.sin(t*1.5+i*2);
    const grd = ctx.createRadialGradient(o.x*W, o.y*H, 0, o.x*W, o.y*H, o.r);
    grd.addColorStop(0, hexA(o.col, pulse));
    grd.addColorStop(1, 'transparent');
    ctx.fillStyle = grd;
    ctx.fillRect(0,0,W,H);
  }});

  ctx.save();
  for(let i=0;i<12;i++){{
    const px = (W*0.1 + W*0.8*((i*137.5+t*8)%W)/W);
    const py = (H - (H*(((i*73+t*15+i*200)%H))/H) + H) % H;
    const alpha = 0.3 + 0.2*Math.sin(t*2+i);
    ctx.fillStyle = hexA(i%2===0?p.accent:p.secondary, alpha*0.6);
    ctx.beginPath();
    ctx.arc(px%W, py%H, 1.5+i%2, 0, Math.PI*2);
    ctx.fill();
  }}
  ctx.restore();
}}

function drawTitle(s, p, progress){{
  const a  = easeOut(clamp(progress*3,0,1));
  const a2 = easeOut(clamp((progress-0.15)*3,0,1));
  const a3 = easeOut(clamp((progress-0.3)*3,0,1));
  const a4 = easeOut(clamp((progress-0.45)*3,0,1));

  ctx.save();
  ctx.globalAlpha = 0.12 * a;
  const grd = ctx.createRadialGradient(W/2, H*0.38, 0, W/2, H*0.38, 220);
  grd.addColorStop(0, p.accent); grd.addColorStop(1, 'transparent');
  ctx.fillStyle = grd;
  ctx.beginPath(); ctx.arc(W/2, H*0.38, 220, 0, Math.PI*2); ctx.fill();
  ctx.restore();

  ctx.save();
  ctx.globalAlpha = 0.25 * a;
  ctx.strokeStyle = p.accent; ctx.lineWidth = 2;
  ctx.setLineDash([8,12]); ctx.lineDashOffset = -t * 30;
  ctx.beginPath(); ctx.arc(W/2, H*0.38, 160 + 10*Math.sin(t), 0, Math.PI*2); ctx.stroke();
  ctx.setLineDash([]); ctx.restore();

  ctx.save();
  ctx.globalAlpha = 0.12 * a;
  ctx.strokeStyle = p.secondary; ctx.lineWidth = 1.5;
  ctx.setLineDash([4,16]); ctx.lineDashOffset = t * 20;
  ctx.beginPath(); ctx.arc(W/2, H*0.38, 200 + 8*Math.cos(t*0.8), 0, Math.PI*2); ctx.stroke();
  ctx.setLineDash([]); ctx.restore();

  ctx.save();
  ctx.globalAlpha = a * 0.9;
  ctx.font = `${{Math.round(72*a)}}px serif`;
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('🧠', W/2, H*0.35 - 10*(1-a));
  ctx.restore();

  ctx.save();
  ctx.globalAlpha = a2;
  ctx.font = '600 13px Segoe UI'; ctx.fillStyle = p.accent;
  ctx.textAlign = 'center';
  ctx.fillText(s.topic.toUpperCase(), W/2, H*0.55 - 8*(1-a2));
  ctx.restore();

  ctx.save();
  ctx.globalAlpha = a3;
  ctx.textAlign = 'center'; ctx.fillStyle = '#ffffff';
  const titleSize = s.title.length > 30 ? 28 : 34;
  ctx.font = `800 ${{titleSize}}px Segoe UI`;
  ctx.fillText(s.title, W/2, H*0.66 - 12*(1-a3));
  ctx.restore();

  ctx.save();
  ctx.globalAlpha = a4 * 0.75;
  ctx.font = '14px Segoe UI'; ctx.fillStyle = '#c9d3e0'; ctx.textAlign = 'center';
  wrapText(ctx, s.desc, W/2 - 220, H*0.77, 440, 22);
  ctx.restore();

  ctx.save();
  ctx.globalAlpha = a4;
  const lineW = 80 * a4;
  const grd2 = ctx.createLinearGradient(W/2-lineW, 0, W/2+lineW, 0);
  grd2.addColorStop(0, 'transparent'); grd2.addColorStop(0.5, p.accent); grd2.addColorStop(1, 'transparent');
  ctx.strokeStyle = grd2; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(W/2-lineW, H*0.88); ctx.lineTo(W/2+lineW, H*0.88); ctx.stroke();
  ctx.restore();
}}

function drawExplain(s, p, progress){{
  const headA = easeOut(clamp(progress*4,0,1));

  ctx.save(); ctx.globalAlpha = 0.06;
  roundRect(ctx, 30, 30, 6, H-60, 3, p.accent); ctx.restore();

  ctx.save(); ctx.globalAlpha = headA;
  roundRect(ctx, 50, 35, 130, 26, 13, hexA(p.accent,0.15), p.accent, 1);
  ctx.font = '700 11px Segoe UI'; ctx.fillStyle = p.accent; ctx.textAlign = 'center';
  ctx.fillText('EXPLANATION', 115, 52); ctx.restore();

  ctx.save(); ctx.globalAlpha = headA;
  ctx.font = `700 26px Segoe UI`; ctx.fillStyle = '#ffffff'; ctx.textAlign = 'left';
  ctx.fillText(s.title, 50, 92); ctx.restore();

  ctx.save(); ctx.globalAlpha = headA * 0.6;
  ctx.strokeStyle = p.accent; ctx.lineWidth = 2;
  const underW = Math.min(ctx.measureText(s.title).width, W-100) * headA;
  ctx.beginPath(); ctx.moveTo(50, 100); ctx.lineTo(50+underW, 100); ctx.stroke(); ctx.restore();

  const linesPerSlide = s.lines || [];
  linesPerSlide.forEach((line, i) => {{
    const lineProgress = easeOut(clamp((progress - 0.15 - i*0.12)*5, 0, 1));
    if(lineProgress <= 0) return;
    const y = 135 + i * 58;

    ctx.save(); ctx.globalAlpha = lineProgress;
    const grd = ctx.createRadialGradient(58, y+8, 0, 58, y+8, 14);
    grd.addColorStop(0, hexA(p.accent, 0.3)); grd.addColorStop(1, 'transparent');
    ctx.fillStyle = grd;
    ctx.beginPath(); ctx.arc(58, y+8, 14, 0, Math.PI*2); ctx.fill();
    ctx.font = '700 11px Segoe UI'; ctx.fillStyle = p.accent; ctx.textAlign = 'center';
    ctx.fillText((i+1)+'', 58, y+13); ctx.restore();

    ctx.save(); ctx.globalAlpha = lineProgress * 0.9;
    ctx.font = '14.5px Segoe UI'; ctx.fillStyle = '#dde4ee'; ctx.textAlign = 'left';
    wrapText(ctx, line, 84, y+2, W-140, 20); ctx.restore();

    if(i < linesPerSlide.length-1){{
      ctx.save(); ctx.globalAlpha = lineProgress * 0.08;
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(50, y+46); ctx.lineTo(W-50, y+46); ctx.stroke(); ctx.restore();
    }}
  }});
}}

function drawFlowchart(s, p, progress){{
  const nodes = s.nodes || [];
  if(!nodes.length) return;
  const headA = easeOut(clamp(progress*4, 0, 1));

  ctx.save(); ctx.globalAlpha = headA;
  roundRect(ctx, W/2-65, 28, 130, 26, 13, hexA(p.accent,0.15), p.accent, 1);
  ctx.font = '700 11px Segoe UI'; ctx.fillStyle = p.accent; ctx.textAlign = 'center';
  ctx.fillText('HOW IT WORKS', W/2, 45);
  ctx.font = '700 24px Segoe UI'; ctx.fillStyle = '#ffffff';
  ctx.fillText(s.title, W/2, 88); ctx.restore();

  const n = nodes.length;
  const nodeW = 130, nodeH = 42;
  const cols = Math.min(n, 3);
  const startX = W/2 - ((cols-1) * 180)/2;
  const positions = [];
  for(let i=0;i<n;i++){{
    const row = Math.floor(i/3);
    const col = row%2===0 ? i%3 : 2-(i%3);
    positions.push({{x: startX + col*180, y: 130 + row*100}});
  }}

  for(let i=0;i<n-1;i++){{
    const cp = easeOut(clamp((progress - 0.1 - i*0.08)*6, 0, 1));
    if(cp <= 0) continue;
    const from = positions[i], to = positions[i+1];
    ctx.save(); ctx.globalAlpha = 0.5 * cp;
    ctx.strokeStyle = p.accent; ctx.lineWidth = 2; ctx.setLineDash([6,4]);
    const fx=from.x, fy=from.y+nodeH/2, tx=to.x, ty=to.y+nodeH/2;
    ctx.beginPath(); ctx.moveTo(fx, fy);
    if(from.x === to.x) ctx.lineTo(fx, lerp(fy,ty,cp));
    else if(from.y === to.y) ctx.lineTo(lerp(fx,tx,cp), fy);
    else {{ ctx.lineTo(fx, fy+(ty-fy)*cp*0.5); ctx.lineTo(lerp(fx,tx,cp), fy+(ty-fy)*cp*0.5); }}
    ctx.stroke(); ctx.setLineDash([]);
    if(cp > 0.9){{
      ctx.globalAlpha = cp; ctx.fillStyle = p.accent;
      ctx.beginPath(); ctx.moveTo(tx,ty); ctx.lineTo(tx-6,ty-5); ctx.lineTo(tx-6,ty+5); ctx.fill();
    }}
    ctx.restore();
  }}

  nodes.forEach((node, i) => {{
    const np = easeOut(clamp((progress - i*0.09)*5, 0, 1));
    if(np <= 0) return;
    const {{x, y}} = positions[i];
    const scale = 0.6 + 0.4*np;
    const nx = x - (nodeW*scale)/2;
    const isFirst = i===0, isLast = i===n-1;
    const ac = isFirst ? p.accent : isLast ? p.secondary : hexA(p.accent, 0.5);

    ctx.save(); ctx.globalAlpha = np;
    ctx.translate(x, y+nodeH/2); ctx.scale(scale,scale); ctx.translate(-x,-(y+nodeH/2));

    const grd = ctx.createRadialGradient(x,y+nodeH/2,0,x,y+nodeH/2,70);
    grd.addColorStop(0, hexA(i===0?p.accent:p.secondary, 0.2)); grd.addColorStop(1,'transparent');
    ctx.fillStyle=grd; ctx.beginPath(); ctx.arc(x,y+nodeH/2,70,0,Math.PI*2); ctx.fill();

    roundRect(ctx, nx, y, nodeW*scale, nodeH*scale, 10,
      hexA(isFirst||isLast?(isFirst?p.accent:p.secondary):p.accent, 0.15),
      ac, isFirst||isLast?2:1.5);

    ctx.font='700 10px Segoe UI'; ctx.fillStyle=hexA(i===0?p.accent:p.secondary,0.8);
    ctx.textAlign='left'; ctx.fillText((i+1)+'', nx+10, y+15);

    ctx.font=`${{isFirst||isLast?'700':'600'}} 12px Segoe UI`;
    ctx.fillStyle=isFirst||isLast?'#ffffff':'#dde4ee';
    ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText(node.length>18?node.slice(0,17)+'…':node, x, y+nodeH/2);
    ctx.textBaseline='alphabetic'; ctx.restore();
  }});
}}

function drawAnalogy(s, p, progress){{
  const headA = easeOut(clamp(progress*4,0,1));
  const emojiA = easeOut(clamp((progress-0.05)*5,0,1));

  ctx.save(); ctx.globalAlpha = emojiA;
  const grd = ctx.createRadialGradient(200,H/2,0,200,H/2,140);
  grd.addColorStop(0, hexA(p.accent,0.12)); grd.addColorStop(1,'transparent');
  ctx.fillStyle=grd; ctx.fillRect(0,0,W,H);
  ctx.strokeStyle=hexA(p.accent, 0.2+0.1*Math.sin(t*2)); ctx.lineWidth=2;
  ctx.setLineDash([8,10]);
  ctx.beginPath(); ctx.arc(200,H/2,110+5*Math.sin(t),0,Math.PI*2); ctx.stroke();
  ctx.setLineDash([]);
  ctx.font=`${{Math.round(80*emojiA)}}px serif`;
  ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText('💡', 200, H/2-10); ctx.restore();

  const RX = 360;
  ctx.save(); ctx.globalAlpha = headA;
  roundRect(ctx, RX, 35, 150, 26, 13, hexA(p.accent,0.15), p.accent, 1);
  ctx.font='700 11px Segoe UI'; ctx.fillStyle=p.accent; ctx.textAlign='center';
  ctx.fillText('REAL LIFE ANALOGY', RX+75, 52); ctx.restore();

  ctx.save(); ctx.globalAlpha=headA;
  ctx.font='700 26px Segoe UI'; ctx.fillStyle=p.accent; ctx.textAlign='left';
  ctx.fillText(s.title, RX, 90); ctx.restore();

  (s.lines||[]).forEach((line,i)=>{{
    const la = easeOut(clamp((progress-0.2-i*0.1)*5,0,1));
    if(la<=0) return;
    const y = 120 + i*72;
    ctx.save(); ctx.globalAlpha=la;
    roundRect(ctx, RX-4, y-8, W-RX-40, 62, 8,
      hexA(i===0?p.accent:p.secondary,0.07),
      hexA(i===0?p.accent:p.secondary,0.25), 1);
    ctx.font=`700 24px serif`; ctx.fillStyle=hexA(p.accent,0.3); ctx.textAlign='left';
    ctx.fillText('"', RX+6, y+12);
    ctx.font='13.5px Segoe UI'; ctx.fillStyle='#dde4ee';
    wrapText(ctx, line, RX+22, y+8, W-RX-75, 19); ctx.restore();
  }});
}}

function drawSteps(s, p, progress){{
  const headA = easeOut(clamp(progress*4,0,1));
  const steps = s.steps||[];

  ctx.save(); ctx.globalAlpha=headA;
  roundRect(ctx, 50, 30, 140, 26, 13, hexA(p.accent,0.15), p.accent, 1);
  ctx.font='700 11px Segoe UI'; ctx.fillStyle=p.accent; ctx.textAlign='center';
  ctx.fillText('STEP BY STEP', 120, 47);
  ctx.font='700 24px Segoe UI'; ctx.fillStyle='#ffffff'; ctx.textAlign='left';
  ctx.fillText(s.title, 50, 87); ctx.restore();

  const timelineA = easeOut(clamp((progress-0.1)*4,0,1));
  ctx.save(); ctx.globalAlpha=0.25*timelineA;
  const grad = ctx.createLinearGradient(78,110,78,H-30);
  grad.addColorStop(0,p.accent); grad.addColorStop(1,'transparent');
  ctx.strokeStyle=grad; ctx.lineWidth=2; ctx.setLineDash([4,4]);
  ctx.beginPath(); ctx.moveTo(78,110); ctx.lineTo(78,H-30); ctx.stroke();
  ctx.setLineDash([]); ctx.restore();

  steps.forEach((step,i)=>{{
    const sp = easeOut(clamp((progress-0.15-i*0.11)*6,0,1));
    if(sp<=0) return;
    const y = 112 + i*64;
    ctx.save(); ctx.globalAlpha=sp; ctx.translate(-(1-sp)*20,0);

    const circGrd = ctx.createRadialGradient(78,y+14,0,78,y+14,18);
    circGrd.addColorStop(0,hexA(p.accent,0.8)); circGrd.addColorStop(1,hexA(p.accent,0.1));
    ctx.fillStyle=circGrd; ctx.beginPath(); ctx.arc(78,y+14,14,0,Math.PI*2); ctx.fill();
    ctx.strokeStyle=p.accent; ctx.lineWidth=2; ctx.stroke();
    ctx.font='700 13px Segoe UI'; ctx.fillStyle='#ffffff';
    ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText(''+(i+1),78,y+14); ctx.textBaseline='alphabetic';

    roundRect(ctx, 106, y, W-160, 54, 8, hexA(p.accent,0.07), hexA(p.accent,0.2), 1.2);

    ctx.font='700 13px Segoe UI'; ctx.fillStyle=p.accent; ctx.textAlign='left';
    ctx.fillText(step.label||('Step '+(i+1)), 120, y+18);
    ctx.font='13px Segoe UI'; ctx.fillStyle='#c9d3e0';
    wrapText(ctx, step.body||'', 120, y+34, W-200, 18); ctx.restore();
  }});
}}

function drawConcepts(s, p, progress){{
  const headA = easeOut(clamp(progress*4,0,1));
  const cards = s.cards||[];

  ctx.save(); ctx.globalAlpha=headA;
  roundRect(ctx, W/2-65, 28, 130, 26, 13, hexA(p.accent,0.15), p.accent, 1);
  ctx.font='700 11px Segoe UI'; ctx.fillStyle=p.accent; ctx.textAlign='center';
  ctx.fillText('KEY CONCEPTS', W/2, 45);
  ctx.font='700 24px Segoe UI'; ctx.fillStyle='#ffffff';
  ctx.fillText(s.title, W/2, 85); ctx.restore();

  const cols=2, cardW=320, cardH=140, gapX=30, gapY=20;
  const startX=(W-cols*cardW-(cols-1)*gapX)/2;
  const accentColors=[p.accent,p.secondary,p.accent,p.secondary];

  cards.forEach((card,i)=>{{
    const cp = easeOut(clamp((progress-0.15-i*0.08)*5,0,1));
    if(cp<=0) return;
    const col=i%cols, row=Math.floor(i/cols);
    const cx=startX+col*(cardW+gapX), cy=108+row*(cardH+gapY);
    const ac=accentColors[i];

    ctx.save(); ctx.globalAlpha=cp; ctx.translate(0,(1-cp)*15);
    const grd=ctx.createRadialGradient(cx+cardW/2,cy+cardH/2,0,cx+cardW/2,cy+cardH/2,cardW/2);
    grd.addColorStop(0,hexA(ac,0.12)); grd.addColorStop(1,'transparent');
    ctx.fillStyle=grd; ctx.fillRect(cx-20,cy-20,cardW+40,cardH+40);

    roundRect(ctx, cx, cy, cardW, cardH, 14, hexA(ac,0.08), ac, 1.5);
    roundRect(ctx, cx, cy, cardW, 5, [14,14,0,0], ac, null);

    const circX=cx+28, circY=cy+35;
    ctx.fillStyle=hexA(ac,0.2); ctx.beginPath(); ctx.arc(circX,circY,16,0,Math.PI*2); ctx.fill();
    ctx.strokeStyle=ac; ctx.lineWidth=1.5; ctx.stroke();
    ctx.font='700 13px Segoe UI'; ctx.fillStyle=ac;
    ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText(''+(i+1),circX,circY); ctx.textBaseline='alphabetic';

    ctx.font='700 14px Segoe UI'; ctx.fillStyle='#ffffff'; ctx.textAlign='left';
    ctx.fillText(card.title, cx+52, cy+30);
    ctx.strokeStyle=hexA(ac,0.4); ctx.lineWidth=1.5;
    ctx.beginPath(); ctx.moveTo(cx+52,cy+38); ctx.lineTo(cx+cardW-16,cy+38); ctx.stroke();
    ctx.font='13px Segoe UI'; ctx.fillStyle='#b8c4d4';
    wrapText(ctx, card.desc, cx+16, cy+58, cardW-32, 19); ctx.restore();
  }});
}}

function drawMistakes(s, p, progress){{
  const headA = easeOut(clamp(progress*4,0,1));
  const items = s.items||[];
  const red = '#ff6b6b';

  ctx.save(); ctx.globalAlpha=headA;
  roundRect(ctx, W/2-75, 28, 150, 26, 13, 'rgba(255,107,107,0.15)', red, 1);
  ctx.font='700 11px Segoe UI'; ctx.fillStyle=red; ctx.textAlign='center';
  ctx.fillText('⚠ COMMON MISTAKES', W/2, 45);
  ctx.font='700 24px Segoe UI'; ctx.fillStyle='#ffffff';
  ctx.fillText(s.title, W/2, 85); ctx.restore();

  ctx.save(); ctx.globalAlpha=0.06*headA;
  const grd=ctx.createLinearGradient(0,0,W,0);
  grd.addColorStop(0,'transparent'); grd.addColorStop(0.5,red); grd.addColorStop(1,'transparent');
  ctx.fillStyle=grd; ctx.fillRect(0,0,W,H); ctx.restore();

  const icons=['⚠️','❌','🚫'];
  items.forEach((item,i)=>{{
    const ip = easeOut(clamp((progress-0.2-i*0.12)*5,0,1));
    if(ip<=0) return;
    const y = 115 + i*100;
    ctx.save(); ctx.globalAlpha=ip; ctx.translate((1-ip)*25,0);

    roundRect(ctx, 50, y, W-100, 84, 12, 'rgba(255,107,107,0.06)',
      `rgba(255,107,107,${{0.3*ip}})`, 1.5);

    const grd2=ctx.createRadialGradient(82,y+42,0,82,y+42,22);
    grd2.addColorStop(0,'rgba(255,107,107,0.3)'); grd2.addColorStop(1,'transparent');
    ctx.fillStyle=grd2; ctx.beginPath(); ctx.arc(82,y+42,22,0,Math.PI*2); ctx.fill();
    ctx.font='26px serif'; ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText(icons[i%icons.length],82,y+42); ctx.textBaseline='alphabetic';

    ctx.font='700 12px Segoe UI'; ctx.fillStyle=red; ctx.textAlign='left';
    ctx.fillText('MISTAKE '+(i+1),116,y+22);
    ctx.font='13.5px Segoe UI'; ctx.fillStyle='#d0d8e4';
    wrapText(ctx, item, 116, y+38, W-185, 19); ctx.restore();
  }});
}}

function drawTakeaway(s, p, progress){{
  const a1=easeOut(clamp(progress*4,0,1));
  const a2=easeOut(clamp((progress-0.15)*4,0,1));
  const a3=easeOut(clamp((progress-0.3)*4,0,1));
  const a4=easeOut(clamp((progress-0.5)*4,0,1));

  ctx.save(); ctx.globalAlpha=0.18*a1;
  const grd=ctx.createRadialGradient(W/2,H*0.4,0,W/2,H*0.4,300);
  grd.addColorStop(0,p.accent); grd.addColorStop(1,'transparent');
  ctx.fillStyle=grd; ctx.fillRect(0,0,W,H); ctx.restore();

  ctx.save(); ctx.globalAlpha=0.15*a1;
  ctx.strokeStyle=p.accent; ctx.lineWidth=1.5;
  ctx.translate(W/2,H*0.38); ctx.rotate(t*0.3);
  for(let i=0;i<8;i++){{
    const angle=(i/8)*Math.PI*2;
    ctx.beginPath();
    ctx.moveTo(Math.cos(angle)*80,Math.sin(angle)*80);
    ctx.lineTo(Math.cos(angle)*110,Math.sin(angle)*110);
    ctx.stroke();
  }}
  ctx.restore();

  ctx.save(); ctx.globalAlpha=a1;
  ctx.font=`${{Math.round(64*a1)}}px serif`;
  ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText('⭐',W/2,H*0.28); ctx.restore();

  ctx.save(); ctx.globalAlpha=a2;
  roundRect(ctx, W/2-65, H*0.42, 130, 26, 13, hexA(p.accent,0.15), p.accent, 1);
  ctx.font='700 11px Segoe UI'; ctx.fillStyle=p.accent; ctx.textAlign='center';
  ctx.fillText('KEY TAKEAWAY', W/2, H*0.42+17); ctx.restore();

  ctx.save(); ctx.globalAlpha=a3*0.9;
  ctx.font='15px Segoe UI'; ctx.fillStyle='#dde4ee'; ctx.textAlign='center';
  const bodyY=H*0.54;
  const words=s.body.split(' ');
  let line='', cy=bodyY;
  for(let w of words){{
    const test=line+w+' ';
    if(ctx.measureText(test).width>600&&line){{
      ctx.fillText(line.trim(),W/2,cy); line=w+' '; cy+=24;
    }} else line=test;
  }}
  if(line.trim()) ctx.fillText(line.trim(),W/2,cy);
  ctx.restore();

  ctx.save(); ctx.globalAlpha=a4;
  const badgeW=260, badgeH=38;
  const bx=W/2-badgeW/2, by=H*0.82;
  const grd2=ctx.createLinearGradient(bx,by,bx+badgeW,by);
  grd2.addColorStop(0,hexA(p.accent,0.3));
  grd2.addColorStop(0.5,hexA(p.secondary,0.3));
  grd2.addColorStop(1,hexA(p.accent,0.3));
  roundRect(ctx, bx, by, badgeW, badgeH, 19, grd2, p.accent, 1.5);
  ctx.font='700 13px Segoe UI'; ctx.fillStyle='#ffffff';
  ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText('✓ '+s.chapter+' Complete', W/2, by+badgeH/2);
  ctx.textBaseline='alphabetic'; ctx.restore();
}}

let lastTime=0, slideStartTime=0, transitionAlpha=1;

function render(timestamp){{
  const dt=(timestamp-lastTime)/1000;
  lastTime=timestamp; t+=dt;
  const slideProgress=clamp((timestamp-slideStartTime)/1500,0,1);
  const s=slides[cur], p=pal(cur);
  ctx.clearRect(0,0,W,H);
  drawBg(p,t);
  ctx.save(); ctx.globalAlpha=transitionAlpha;
  switch(s.type){{
    case 'title':     drawTitle(s,p,slideProgress); break;
    case 'explain':   drawExplain(s,p,slideProgress); break;
    case 'flowchart': drawFlowchart(s,p,slideProgress); break;
    case 'analogy':   drawAnalogy(s,p,slideProgress); break;
    case 'steps':     drawSteps(s,p,slideProgress); break;
    case 'concepts':  drawConcepts(s,p,slideProgress); break;
    case 'mistakes':  drawMistakes(s,p,slideProgress); break;
    case 'takeaway':  drawTakeaway(s,p,slideProgress); break;
  }}
  ctx.restore();
  animFrame=requestAnimationFrame(render);
}}

function goSlide(idx){{
  cur=((idx%TOTAL)+TOTAL)%TOTAL;
  slideStartTime=performance.now();
  document.getElementById('ctr').textContent=(cur+1)+'/'+TOTAL;
  const accent=pal(cur).accent;
  document.getElementById('topfill').style.width=(((cur+1)/TOTAL)*100)+'%';
  document.getElementById('topfill').style.background=accent;
  document.querySelectorAll('.dot').forEach((d,i)=>{{
    d.classList.toggle('on',i===cur);
    d.style.background=i===cur?accent:'rgba(255,255,255,0.2)';
  }});
  if(playing) resetTimer();
}}

function nextSlide(){{ goSlide(cur+1); }}
function prev(){{ goSlide(cur-1); }}
function togglePlay(){{
  playing=!playing;
  document.getElementById('pb').textContent=playing?'⏸':'▶';
  if(playing) resetTimer(); else clearInterval(timer);
}}
function resetTimer(){{ clearInterval(timer); timer=setInterval(nextSlide,DURATION); }}

function buildDots(){{
  const el=document.getElementById('dots'); el.innerHTML='';
  slides.forEach((_,i)=>{{
    const d=document.createElement('div');
    d.className='dot'+(i===0?' on':'');
    d.onclick=()=>goSlide(i); el.appendChild(d);
  }});
}}

buildDots();
document.getElementById('topfill').style.background=pal(0).accent;
document.getElementById('topfill').style.width=(100/TOTAL)+'%';
document.querySelectorAll('.dot')[0].style.background=pal(0).accent;
slideStartTime=performance.now(); lastTime=performance.now();
animFrame=requestAnimationFrame(render);
resetTimer();
</script>
</body></html>"""

    components.html(html, height=510, scrolling=False)
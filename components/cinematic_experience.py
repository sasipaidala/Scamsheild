"""Scroll-driven cinematic hero for ScamShield's public landing page.

The scene is self-contained in an iframe and uses a Canvas 2D renderer as a
lightweight fallback, avoiding a mandatory WebGL or CDN dependency.
"""

from __future__ import annotations

import base64

import streamlit as st


_CINEMATIC_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{color-scheme:dark;--bg:#070b0a;--panel:#0d1411;--line:#1e3428;--green:#39ff88;--mint:#b7ffd1;--muted:#8ba899;--white:#f0fff6}
*{box-sizing:border-box}html{scroll-behavior:smooth;scrollbar-color:#245b3d #070b0a}body{margin:0;background:var(--bg);color:var(--white);font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;overflow-x:hidden}
.scene-wrap{height:210vh;position:relative;background:radial-gradient(ellipse at 50% 25%,#13271d 0%,#09110d 37%,#070b0a 76%)}
canvas{position:sticky;top:0;width:100%;height:100vh;display:block;max-height:100vh}
.hud{position:fixed;z-index:3;top:22px;left:clamp(18px,4vw,52px);right:clamp(18px,4vw,52px);display:flex;align-items:center;justify-content:space-between;pointer-events:none;text-transform:uppercase;letter-spacing:.14em;font:600 10px/1.4 ui-monospace,SFMono-Regular,monospace;color:#a7c7b3}
.brand{display:flex;align-items:center;gap:10px;color:#f0fff6;font-size:12px;letter-spacing:.1em}.mark{width:28px;height:28px;border:1px solid #39ff8877;display:grid;place-items:center;color:var(--green);box-shadow:0 0 22px #39ff8820;border-radius:8px}.hud-right{display:flex;gap:18px;align-items:center}.live{color:var(--green)}
.overlay{position:sticky;top:0;z-index:2;height:100vh;margin-top:-100vh;margin-bottom:0;display:flex;align-items:center;justify-content:center;pointer-events:none;padding:88px 24px 58px;text-align:center;overflow:hidden}.copy{max-width:780px;width:100%;transition:opacity .15s linear,transform .15s linear;text-shadow:0 2px 24px rgba(0,0,0,.55)}.eyebrow{font:700 10px/1.4 ui-monospace,monospace;letter-spacing:.22em;color:var(--green);text-transform:uppercase;margin-bottom:22px}.title{font-size:clamp(36px,7vw,84px);line-height:.98;letter-spacing:-.065em;font-weight:750;margin:0 auto 22px;text-wrap:balance}.title em{font-style:normal;color:var(--green);text-shadow:0 0 35px #39ff8833}.desc{max-width:570px;margin:0 auto;color:#a9beb1;font-size:clamp(13px,1.55vw,17px);line-height:1.8}.scroll-cue{margin-top:38px;color:#a5c4b0;font:600 10px/1.4 ui-monospace,monospace;letter-spacing:.17em;text-transform:uppercase}.scroll-cue span{display:block;color:var(--green);font-size:19px;margin-top:8px;animation:bob 1.5s ease-in-out infinite}
.bottom{position:absolute;z-index:3;left:clamp(18px,4vw,52px);right:clamp(18px,4vw,52px);bottom:24px;display:flex;justify-content:space-between;gap:16px;color:#799786;font:600 9px/1.5 ui-monospace,monospace;letter-spacing:.13em;text-transform:uppercase}.progress{position:fixed;z-index:4;left:0;top:0;height:2px;width:0;background:var(--green);box-shadow:0 0 14px #39ff88;}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(5px)}}
@media(max-width:560px){.overlay{padding:76px 18px 54px}.hud{top:14px}.hud-right .location{display:none}.title{font-size:clamp(34px,11vw,54px)}.desc{font-size:13px}.bottom{bottom:14px;font-size:8px}.scene-wrap{height:190vh}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.scroll-cue span{animation:none}}
</style></head><body>
<div class="progress" id="progress"></div>
<div class="hud"><div class="brand"><span class="mark">S/</span> SCAMSHIELD <span style="color:#39ff88">AI</span></div><div class="hud-right"><span class="location">DIGITAL THREAT LAB</span><span class="live">● SYSTEM READY</span></div></div>
<section class="scene-wrap" id="journey" aria-label="Scroll-driven ScamShield cinematic introduction">
<canvas id="scene" aria-label="An animated crystal inside a geometric security cage transitions into a network of evidence signals"></canvas>
<div class="overlay"><div class="copy" id="copy"><div class="eyebrow" id="eyebrow">ACT I · SIGNAL DETECTED</div><h1 class="title" id="title">Every threat leaves<br><em>a signal.</em></h1><p class="desc" id="desc">Behind every suspicious link or message is a trail of clues. Follow the evidence. Understand the risk. Make the next move with clarity.</p><div class="scroll-cue" id="cue">SCROLL TO ENTER THE INVESTIGATION<span>↓</span></div></div></div>
<div class="bottom"><span id="stage">01 / 03 · CONTAINED SIGNAL</span><span>SCROLL-DRIVEN EXPERIENCE</span></div>
</section>
<script>
(()=>{
const canvas=document.getElementById('scene'),ctx=canvas.getContext('2d',{alpha:false});
const progress=document.getElementById('progress'),copy=document.getElementById('copy');
const eyebrow=document.getElementById('eyebrow'),title=document.getElementById('title'),desc=document.getElementById('desc'),cue=document.getElementById('cue'),stage=document.getElementById('stage');
const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
let w=0,h=0,dpr=1,scrollP=0,lastStage=-1,stars=[],lastT=0;
function resize(){dpr=Math.min(window.devicePixelRatio||1,1.7);w=canvas.clientWidth;h=canvas.clientHeight;canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);stars=Array.from({length:Math.min(170,Math.floor(w*h/6500))},()=>({x:Math.random(),y:Math.random(),z:Math.random(),r:.3+Math.random()*1.2,s:.15+Math.random()*.7}));draw(0)}
function line(a,b,c,d,alpha=1,width=1){ctx.strokeStyle=`rgba(57,255,136,${alpha})`;ctx.lineWidth=width;ctx.beginPath();ctx.moveTo(a,b);ctx.lineTo(c,d);ctx.stroke()}
function glow(x,y,r,color='57,255,136',a=.5){const g=ctx.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,`rgba(${color},${a})`);g.addColorStop(1,`rgba(${color},0)`);ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill()}
function poly(points,alpha=.8,width=1.1){ctx.strokeStyle=`rgba(104,255,166,${alpha})`;ctx.lineWidth=width;ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.closePath();ctx.stroke()}
function draw(t){const W=w,H=h,cx=W*.5,cy=H*.48;ctx.fillStyle='#070b0a';ctx.fillRect(0,0,W,H);
const bg=ctx.createRadialGradient(cx,cy,0,cx,cy,Math.max(W,H)*.75);bg.addColorStop(0,'#13281d');bg.addColorStop(.48,'#0a130e');bg.addColorStop(1,'#070b0a');ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);
// Sparse atmospheric particles drift toward the focus, never forming a galaxy.
stars.forEach((s,i)=>{let yy=(s.y+(reduce?0:t*.000012*s.s+scrollP*.15))%1;let xx=s.x;let dx=(xx-.5),dy=(yy-.46);if(scrollP>.34){xx=.5+dx*(1+scrollP*2.5);yy=.46+dy*(1+scrollP*2.5)}const x=xx*W,y=yy*H;ctx.fillStyle=`rgba(183,255,209,${.18+s.z*.55})`;ctx.fillRect(x,y,s.r,s.r);});
const zoom=1+scrollP*2.3,rot=t*(reduce?0:.00018)+scrollP*.7;
// A contained, faceted crystal suspended in a precision security cage.
const radius=Math.min(W,H)*(.135+scrollP*.018),crystalScale=Math.max(.16,1-scrollP*1.55);
ctx.save();ctx.translate(cx,cy);ctx.rotate(rot*.35);const cage=Math.min(W,H)*(.25+scrollP*.07);
for(let j=0;j<3;j++){ctx.save();ctx.rotate(j*Math.PI/3+rot*.18);ctx.strokeStyle=`rgba(57,255,136,${.38-scrollP*.15})`;ctx.lineWidth=1;ctx.strokeRect(-cage,-cage,cage*2,cage*2);line(-cage,-cage,cage,cage,.28);line(-cage,cage,cage,-cage,.28);ctx.restore()}
for(let i=0;i<12;i++){const a=i*Math.PI/6+rot*.4;const x=Math.cos(a)*cage,y=Math.sin(a)*cage;glow(x,y,7,'57,255,136',.42);ctx.fillStyle='#b7ffd1';ctx.fillRect(x-1,y-1,2,2)}
ctx.restore();
// Crystal facets gradually open into a deep evidence tunnel as the scroll camera advances.
ctx.save();ctx.translate(cx,cy);ctx.rotate(rot);ctx.scale(crystalScale,crystalScale);const r=radius;
const p=[[0,-r],[r*.62,-r*.32],[r*.52,r*.62],[0,r],[ -r*.52,r*.62],[-r*.62,-r*.32],[0,0]];
glow(0,0,r*1.9,'57,255,136',.16*(1-scrollP*.55));poly(p.slice(0,6),.9,1.5);[[0,1,6],[1,2,6],[2,3,6],[3,4,6],[4,5,6],[5,0,6]].forEach((ids,i)=>{ctx.fillStyle=`rgba(${i%2?'57,255,136':'183,255,209'},${.018+scrollP*.018})`;ctx.beginPath();ids.forEach((id,j)=>j?ctx.lineTo(p[id][0],p[id][1]):ctx.moveTo(p[id][0],p[id][1]));ctx.closePath();ctx.fill();poly(ids.map(id=>p[id]),.42,.8)});ctx.restore();
// Scroll past the cage: a converging network tunnel and evidence nodes replace the crystal.
if(scrollP>.28){const q=(scrollP-.28)/.72;ctx.save();ctx.globalAlpha=Math.min(1,q*1.5);const vanY=cy;for(let i=0;i<13;i++){const z=(i/13+((t*.00006)%1));const spread=(Math.min(W,H)*(.04+z*.62))*(.5+q);const yy=vanY+(z-.5)*H*.85;line(cx-spread,yy,cx+spread,yy,.08+z*.18);line(cx,vanY,cx-spread,yy,.10+z*.22);line(cx,vanY,cx+spread,yy,.10+z*.22)}
const nodes=[];for(let i=0;i<9;i++){const a=i/9*Math.PI*2+t*.00012;const rr=Math.min(W,H)*(.11+((i%3)*.075)+q*.18);nodes.push([cx+Math.cos(a)*rr,cy+Math.sin(a)*rr*.58])}nodes.forEach((p,i)=>{const n=nodes[(i+1)%nodes.length];line(p[0],p[1],n[0],n[1],.26);glow(p[0],p[1],14,'57,255,136',.28);ctx.fillStyle='#b7ffd1';ctx.beginPath();ctx.arc(p[0],p[1],2.2,0,Math.PI*2);ctx.fill()});glow(cx,cy,Math.min(W,H)*.18,'57,255,136',.14);ctx.restore()}
// Frame edges and scanlines add restrained cinematic texture.
ctx.fillStyle='rgba(150,255,192,.025)';for(let y=0;y<H;y+=4)ctx.fillRect(0,y,W,1);
const vignette=ctx.createRadialGradient(cx,cy,Math.min(W,H)*.22,cx,cy,Math.max(W,H)*.7);vignette.addColorStop(0,'rgba(0,0,0,0)');vignette.addColorStop(1,'rgba(0,0,0,.66)');ctx.fillStyle=vignette;ctx.fillRect(0,0,W,H);
}
function update(){const max=Math.max(1,document.documentElement.scrollHeight-innerHeight);scrollP=Math.min(1,Math.max(0,window.scrollY/max));progress.style.width=(scrollP*100)+'%';const stageNow=scrollP<.33?0:scrollP<.68?1:2;if(stageNow!==lastStage){lastStage=stageNow;if(stageNow===0){eyebrow.textContent='ACT I · SIGNAL DETECTED';title.innerHTML='Every threat leaves<br><em>a signal.</em>';desc.textContent='Behind every suspicious link or message is a trail of clues. Follow the evidence. Understand the risk. Make the next move with clarity.';cue.style.display='block';stage.textContent='01 / 03 · CONTAINED SIGNAL'}else if(stageNow===1){eyebrow.textContent='ACT II · INVESTIGATE THE BREACH';title.innerHTML='Look closer.<br><em>Connect the clues.</em>';desc.textContent='Move beyond appearances. Inspect structure, trace indicators, and separate technical evidence from assumptions.';cue.style.display='block';stage.textContent='02 / 03 · EVIDENCE MAPPING'}else{eyebrow.textContent='ACT III · DEFENSE IN MOTION';title.innerHTML='Turn signals<br>into <em>safer decisions.</em>';desc.textContent='ScamShield brings explainable analysis into one workspace—showing what was detected, what remains unknown, and what to do next.';cue.style.display='none';stage.textContent='03 / 03 · DEFENSE READY'}}}
function frame(t){if(!reduce)draw(t);requestAnimationFrame(frame)}window.addEventListener('scroll',update,{passive:true});window.addEventListener('resize',()=>{resize();update()});resize();update();if(reduce)draw(0);else requestAnimationFrame(frame);
})();
</script></body></html>'''


def render_cinematic_experience() -> None:
    """Render a responsive scroll-controlled scene without external assets."""
    encoded_html = base64.b64encode(_CINEMATIC_HTML.encode("utf-8")).decode("ascii")
    st.iframe(
        f"data:text/html;base64,{encoded_html}",
        height=760,
    )

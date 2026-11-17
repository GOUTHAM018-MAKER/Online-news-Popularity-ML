'use strict';
const {summary:s,predictions:rows}=window.PROJECT_DATA;

// --- Scroll animations ---
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target); } });
}, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
document.querySelectorAll('section, figure, .table-wrap, blockquote, .hero').forEach(el => { el.classList.add('fade-in'); observer.observe(el); });

// --- Sticky header shadow ---
const header = document.querySelector('header');
if (header) { window.addEventListener('scroll', () => { header.classList.toggle('scrolled', window.scrollY > 10); }, { passive: true }); }

// --- Active nav link highlight ---
const navLinks = document.querySelectorAll('nav .section-links a');
const sections = [...navLinks].map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
const navObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      navLinks.forEach(a => a.classList.remove('active'));
      const link = document.querySelector(`nav .section-links a[href="#${e.target.id}"]`);
      if (link) link.classList.add('active');
    }
  });
}, { threshold: 0.15, rootMargin: '-80px 0px -60% 0px' });
sections.forEach(s => navObserver.observe(s));
const fmt=n=>Number(n).toLocaleString('en-US',{maximumFractionDigits:0});
const pct=n=>(100*n).toFixed(1)+'%';
const model=document.querySelector('#model'),channel=document.querySelector('#channel'),budget=document.querySelector('#budget'),threshold=document.querySelector('#threshold'),caseView=document.querySelector('#case-view');
for(const m of s.metrics){const o=new Option(m.model,m.model);o.selected=m.model===s.winner;model.add(o)}
for(const c of [...new Set(rows.map(r=>r.channel))].sort())channel.add(new Option(c,c));
const canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d');
// Evaluation labels never enter the sorting rule. Baseline ties use random expectation.
function evaluateSelection(data,name,budgetPercent,popularAt){
 const ranked=[...data].sort((a,b)=>b[name]-a[name]||a.row_id-b.row_id);
 const n=ranked.length,k=Math.min(n,Math.max(1,Math.ceil(n*budgetPercent/100)));
 const total=ranked.filter(r=>r.shares>=popularAt).length,base=n?total/n:0;
 const random=name==='Median baseline';
 const hit=random?k*base:ranked.slice(0,k).filter(r=>r.shares>=popularAt).length;
 const precision=k?hit/k:0,recall=total?hit/total:0;
 return {ranked,n,k,total,base,hit,precision,recall,lift:base?precision/base:null,random};
}
function stat(label,value,detail){const el=document.createElement('div');el.className='stat';const strong=document.createElement('strong');strong.textContent=value;const text=document.createElement('div');text.textContent=label;const small=document.createElement('span');small.textContent=detail;el.append(strong,text,small);return el}
function update(){
 const cutoff=Number(threshold.value),subset=rows.filter(r=>channel.value==='all'||r.channel===channel.value);
 const q=evaluateSelection(subset,model.value,Number(budget.value),cutoff);
 document.querySelector('#budget-label').textContent=budget.value+'%';
 const readout=document.querySelector('#readout');readout.replaceChildren();
 readout.append(stat('Articles promoted',fmt(q.k),`out of ${fmt(q.n)} candidates`),stat('Precision',q.n?pct(q.precision):'—','promoted articles that are popular'),stat('Recall',q.total?pct(q.recall):'—','popular articles captured'),stat('Lift over random',q.lift===null?'—':q.lift.toFixed(2)+'×',`random precision: ${pct(q.base)}`));
 const hitText=q.random?q.hit.toFixed(1)+' expected':fmt(q.hit);
 document.querySelector('#interpretation').textContent=!q.n?'No articles match this channel.':!q.total?`No articles in this channel reached ${fmt(cutoff)} shares; recall and lift are undefined.`:q.random?`The median baseline gives every article the same prediction. Random tie-breaking would capture ${hitText} popular articles on average, with no advantage over random selection.`:`Of ${fmt(q.k)} promoted articles, ${hitText} reached ${fmt(cutoff)} shares. The shortlist misses ${fmt(q.total-q.hit)} popular articles. Random selection of the same size would find ${(q.k*q.base).toFixed(1)} on average.`;
 const w=canvas.clientWidth,h=canvas.clientHeight,dpr=window.devicePixelRatio||1;canvas.width=w*dpr;canvas.height=h*dpr;ctx.scale(dpr,dpr);ctx.clearRect(0,0,w,h);
 const p={l:82,r:20,t:18,b:50},x=v=>p.l+v*(w-p.l-p.r),y=v=>h-p.b-v*(h-p.t-p.b);
 ctx.font="12px 'Inter', system-ui, sans-serif";ctx.fillStyle='#64748b';ctx.strokeStyle='#e2e8f0';
 for(let i=0;i<=4;i++){const v=i/4;ctx.beginPath();ctx.moveTo(x(v),y(0));ctx.lineTo(x(v),y(1));ctx.moveTo(x(0),y(v));ctx.lineTo(x(1),y(v));ctx.stroke();ctx.fillText((v*100)+'%',x(v)-9,h-p.b+19);ctx.save();ctx.textAlign='right';ctx.fillText((v*100)+'%',p.l-10,y(v)+4);ctx.restore()}
 function line(points,color,dash=[]){ctx.strokeStyle=color;ctx.lineWidth=2;ctx.setLineDash(dash);ctx.beginPath();points.forEach(([a,b],i)=>i?ctx.lineTo(x(a),y(b)):ctx.moveTo(x(a),y(b)));ctx.stroke();ctx.setLineDash([])}
 if(q.n&&q.total){
  line([[0,0],[q.base,1],[1,1]],'#bd822b',[3,4]);
  line([[0,0],[1,1]],'#85908a',[6,5]);
  let cumulative=0;const points=[[0,0]];
  q.ranked.forEach((r,i)=>{cumulative+=r.shares>=cutoff?1:0;points.push([(i+1)/q.n,q.random?(i+1)/q.n:cumulative/q.total])});
  line(points,'#0d9488');line([[q.k/q.n,0],[q.k/q.n,q.recall]],'#28615b',[3,4]);ctx.fillStyle='#0d9488';ctx.beginPath();ctx.arc(x(q.k/q.n),y(q.recall),5,0,Math.PI*2);ctx.fill();
 }
 ctx.fillStyle='#64748b';ctx.fillText('Articles promoted (%)',w/2-65,h-6);ctx.save();ctx.translate(17,h/2+70);ctx.rotate(-Math.PI/2);ctx.fillText('Popular articles captured (%)',0,0);ctx.restore();
 const body=document.querySelector('#cases');body.replaceChildren();
 if(q.random){const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=6;td.textContent='No unique shortlist: the baseline has identical predictions for every article. Metrics show expected random tie-breaking.';tr.append(td);body.append(tr)}
 else{
  const cases=caseView.value==='missed'?q.ranked.slice(q.k).filter(r=>r.shares>=cutoff).sort((a,b)=>b.shares-a.shares).slice(0,8):q.ranked.slice(0,q.k).slice(0,8);
  for(const r of cases){const tr=document.createElement('tr');for(const val of [r.row_id,r.date,r.channel,fmt(r[model.value]),fmt(r.shares),caseView.value==='missed'?'Missed popular article':r.shares>=cutoff?'Popular · hit':'Below threshold']){const td=document.createElement('td');td.textContent=val;tr.append(td)}body.append(tr)}
  if(!cases.length){const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=6;td.textContent='No articles in this view.';tr.append(td);body.append(tr)}
 }
 canvas.setAttribute('aria-label',`Popularity gains curve for ${model.value}. Budget ${budget.value}%. Precision ${pct(q.precision)}. Recall ${q.total?pct(q.recall):'undefined'}. Lift ${q.lift===null?'undefined':q.lift.toFixed(2)}. ${document.querySelector('#interpretation').textContent}`);
}
[model,channel,budget,threshold,caseView].forEach(e=>e.addEventListener('input',update));window.addEventListener('resize',update);update();
if(location.hostname.endsWith('.github.io')){const owner=location.hostname.split('.')[0],project=location.pathname.split('/').filter(Boolean)[0]||owner+'.github.io';for(const id of ['#repository','#repository-2']){const repo=document.querySelector(id);if(repo){repo.href=`https://github.com/${owner}/${project}`;repo.textContent='View source repository ↗'}}}

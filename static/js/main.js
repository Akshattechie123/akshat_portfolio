(()=>{
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches,mobile=innerWidth<820;
const g=window.gsap;if(g&&window.ScrollTrigger)g.registerPlugin(ScrollTrigger);

/* Loader (one orchestrated entrance) */
const loader=$('#loader');
function intro(){
  if(!g||reduce){loader.remove();return}
  g.timeline().to('#loader i',{width:'100%',duration:.9,ease:'power2.inOut'})
   .to(loader,{yPercent:-100,duration:.7,ease:'power4.inOut'}).add(()=>loader.remove())
   .from('.hero h1, .page h1',{y:60,opacity:0,duration:.9,ease:'power3.out'},'-=.3')
   .from('.hero .lead,.hero .row,.hero .social',{y:24,opacity:0,stagger:.12},'-=.5');
}
addEventListener('load',intro);

/* Scroll reveals */
if(g&&!reduce){
  $$('.wrap h2,.glass:not(.tilt),.grid4>*,.grid3>*,.skill,.timeline li').forEach(el=>{
    g.fromTo(el,{opacity:0,y:30},{opacity:1,y:0,duration:.7,scrollTrigger:{trigger:el,start:'top 90%'}})});
}
/* Skill bars + counters */
$$('.meter i').forEach(b=>ScrollTrigger&&ScrollTrigger.create({trigger:b,start:'top 95%',once:true,onEnter:()=>g.to(b,{width:b.dataset.w+'%',duration:1.2,ease:'power2.out'})}));
$$('.count').forEach(c=>ScrollTrigger&&ScrollTrigger.create({trigger:c,start:'top 95%',once:true,onEnter:()=>{const o={v:0};g.to(o,{v:+c.dataset.n,duration:1.6,onUpdate:()=>c.textContent=Math.round(o.v)})}}));

/* Cursor, magnetic buttons, tilt */
const cur=$('#cursor');
addEventListener('pointermove',e=>{cur.style.left=e.clientX+'px';cur.style.top=e.clientY+'px';mx=e.clientX/innerWidth*2-1;my=-(e.clientY/innerHeight*2-1)});
$$('a,button,.pick span').forEach(el=>{el.addEventListener('mouseenter',()=>cur.classList.add('big'));el.addEventListener('mouseleave',()=>cur.classList.remove('big'))});
if(g&&!reduce&&matchMedia('(hover:hover)').matches){
  $$('.mag').forEach(b=>{b.addEventListener('pointermove',e=>{const r=b.getBoundingClientRect();g.to(b,{x:(e.clientX-r.left-r.width/2)*.25,y:(e.clientY-r.top-r.height/2)*.35,duration:.3})});b.addEventListener('pointerleave',()=>g.to(b,{x:0,y:0,duration:.5,ease:'elastic.out(1,.4)'}))});
  $$('.tilt').forEach(c=>{c.addEventListener('pointermove',e=>{const r=c.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;g.to(c,{rotateY:x*10,rotateX:-y*10,transformPerspective:800,duration:.3})});c.addEventListener('pointerleave',()=>g.to(c,{rotateX:0,rotateY:0,duration:.6}))});
}

/* Mobile menu */
const burger=$('.burger'),nav=$('.nav nav');
burger.addEventListener('click',()=>{const o=nav.classList.toggle('open');burger.setAttribute('aria-expanded',o)});

/* Page transitions */
$$('a[href^="/"]').forEach(a=>a.addEventListener('click',e=>{
  if(e.metaKey||e.ctrlKey||a.target||reduce||!g)return;e.preventDefault();
  g.to('#wipe',{yPercent:-101,startAt:{yPercent:0,y:'101%'},duration:.5,ease:'power3.in',onComplete:()=>location.href=a.href});
}));

/* Three.js: wireframe spheres following the cursor */
let mx=0,my=0;
const cv=$('#gl');
if(cv&&window.THREE&&!reduce){
  const r=new THREE.WebGLRenderer({canvas:cv,alpha:true,antialias:!mobile});r.setPixelRatio(Math.min(devicePixelRatio,mobile?1:2));
  const sc=new THREE.Scene(),cam=new THREE.PerspectiveCamera(60,1,.1,100);cam.position.z=14;
  const cols=[0x22d3ee,0x8b5cf6,0x3b82f6],N=mobile?6:14,S=[];
  for(let i=0;i<N;i++){
    const m=new THREE.Mesh(new THREE.IcosahedronGeometry(.5+Math.random()*1.4,1),new THREE.MeshBasicMaterial({color:cols[i%3],wireframe:true,transparent:true,opacity:.35}));
    m.position.set((Math.random()-.5)*26,(Math.random()-.5)*16,(Math.random()-.5)*8);m.userData={s:.002+Math.random()*.004,d:Math.random()*2+.5};sc.add(m);S.push(m)}
  function size(){r.setSize(innerWidth,innerHeight,false);cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix()}size();addEventListener('resize',size);
  let sy=0;addEventListener('scroll',()=>sy=scrollY/innerHeight);
  (function loop(t){requestAnimationFrame(loop);
    S.forEach((m,i)=>{m.rotation.x+=m.userData.s;m.rotation.y+=m.userData.s*1.4;m.position.y+=Math.sin(t*.0006*m.userData.d+i)*.004});
    cam.position.x+=(mx*2.5-cam.position.x)*.04;cam.position.y+=(my*1.5-sy*1.2-cam.position.y)*.04;cam.lookAt(0,0,0);r.render(sc,cam)})(0);
}

/* Websites filter */
$$('.filters button').forEach(b=>b.addEventListener('click',()=>{
  $$('.filters button').forEach(x=>x.classList.toggle('on',x===b));
  $$('[data-cat]').forEach(c=>{const show=b.dataset.f==='all'||c.dataset.cat===b.dataset.f;c.style.display=show?'':'none'})}));

/* PDF modal */
const pm=$('#pdfmodal');
if(pm){$$('.pdf').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();$('iframe',pm).src=a.dataset.pdf;pm.hidden=false}));
  $('button',pm).addEventListener('click',()=>{pm.hidden=true;$('iframe',pm).src=''})}

/* AJAX forms (+ multi-step) */
$$('form[data-ajax]').forEach(f=>{
  const err=$('.err',f),box=f.parentElement,done=$('.done',box),steps=$$('.step',f);let i=0;
  const next=$('.next',f),back=$('.back',f),send=$('.send',f),bar=$('.progress i',box);
  function show(n){i=n;steps.forEach((s,k)=>s.classList.toggle('on',k===n));
    if(steps.length){bar.style.width=(n+1)/steps.length*100+'%';back.hidden=n===0;next.hidden=n===steps.length-1;send.hidden=n!==steps.length-1;if(n===steps.length-1)summary()}}
  function summary(){const d=new FormData(f),L={full_name:'Name',email:'Email',title:'Project',project_type:'Type',budget:'Budget',timeline:'Timeline',goal:'Goal'};
    $('.summary',f).textContent=Object.entries(L).map(([k,l])=>d.get(k)?`${l}: ${d.get(k)}`:'').filter(Boolean).join('\n')+(d.getAll('feature_chips').length?'\nFeatures: '+d.getAll('feature_chips').join(', '):'')}
  if(steps.length){next.addEventListener('click',()=>{const bad=$$('[required]',steps[i]).find(x=>!x.checkValidity());if(bad){bad.reportValidity();return}err.textContent='';show(i+1)});back.addEventListener('click',()=>show(i-1));show(0)}
  f.addEventListener('submit',async e=>{e.preventDefault();
    const bad=$$('[required]',f).find(x=>!x.checkValidity());if(bad){const k=steps.findIndex(s=>s.contains(bad));if(k>-1)show(k);bad.reportValidity();return}
    const btn=$('button:not([type=button])',f);btn.disabled=true;const old=btn.textContent;btn.textContent='Sending...';err.textContent='';
    try{const res=await fetch(f.action,{method:'POST',body:new FormData(f),headers:{'X-Requested-With':'fetch'}});const j=await res.json();
      if(j.ok){f.hidden=true;$('.progress',box)&&($('.progress',box).hidden=true);done.hidden=false}
      else err.textContent=j.error||Object.values(j.errors||{})[0]||'Could not send. Please try again.'}
    catch{err.textContent='Network error. Please try again.'}
    btn.disabled=false;btn.textContent=old});
});
})();

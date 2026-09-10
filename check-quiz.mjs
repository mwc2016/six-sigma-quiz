// Run: node check-quiz.mjs. No browser or test dependencies.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync('index.html','utf8');
assert.equal(html,fs.readFileSync('dist/index.html','utf8'),'Published static output must match source');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
const prefix=script.slice(0,script.indexOf('    const LEGACY_KEY'));
const data=vm.runInNewContext(prefix+'; JSON.stringify({sets,bank});');
const {sets,bank}=JSON.parse(data);
assert.deepEqual(sets.map(s=>s.questions.length),[100,150,150,150,150,150]);
const questions=sets.flatMap(s=>s.questions);
const norm=q=>q.toLowerCase().replace(/[^a-z0-9]/g,'');
assert.equal(new Set(questions.map(q=>norm(q.q))).size,850,'No duplicate question text');
assert.equal(new Set(questions.map(q=>q.id)).size,850);
// Each numerical problem family is confined to one tab. Different numbers alone
// cannot disguise duplicate question templates across tabs.
const owners=new Map();
sets.forEach((s,i)=>s.questions.forEach(q=>{
  const shape=norm(q.q.replace(/[−-]?\d+(?:\.\d+)?/g,'#'));
  if(owners.has(shape)) assert.equal(owners.get(shape),i,'Repeated problem template in different tabs');
  owners.set(shape,i);
  assert.equal(q.o.length,4); assert.equal(new Set(q.o).size,4);
  assert.ok(q.q && q.e && Number.isInteger(q.a) && q.a>=0 && q.a<4);
  if(i){assert.ok(bank.sources[q.source]); assert.match(q.scope,/^[1-5]\.\d+\.\d+$/);}
}));
// A second calculation pass, separate from the builder. These expected values
// correspond to the fixed data in the five cases of each documented family.
const {sqrt,exp,ceil,pow}=Math;
const choose=(n,r)=>{let x=1;for(let i=1;i<=r;i++)x=x*(n-i+1)/i;return x;};
const expected=[
 k=>[10*k+4,10*k+7,8,k+2,k+2,5*(k+1)/k,26+k,k/5,sqrt(k*k+(k+1)**2),10,60*k/(k+3),80+3*k,.4+.08*k,100*(k+2)/(40+10*k),100*(k+3)/(100+20*k),2,Math.min(20-k,10+k)/6,(24+6*k)/18,(8-k)/6,k/2,2+k,6.4+1.6*k,pow(.9,k+2),1-pow(.95,k+3),exp(-k/2),3+3*k,exp(-4/(k+2)),50,(28+k)/100,(k+4)/(30+5*k)],
 k=>[2,1.96*(k+2)/5,26.85+k,44.4+k,ceil(pow(1.96*(k+3),2)),100*k,k,9+3*k,4+2*k,23+2*k,sqrt(2*k*k+2*k+1),k*k+4*k+5,90-5*k,k,.05/(k+2),2+2*k,4*k,k*k/5,k+2,k+1,28+5*k,4+k,.8,13+4*k,5+k,28+4*k,2+k,1/(.8-.1*k),k+1,pow(.5+.05*k,2)],
 k=>[3*pow(2,k+1),k+4,pow(2,k+1),pow(2,k+3),pow(2,k+2),9*k+2,choose(k+3,2),choose(k+3,3),1+2*(k+1)+choose(k+1,2),pow(2,k+3)-1,10+2*k,2+k,2+2*k,120+10*k,.5,70+5*k,6+k,8+k,2+k,25,8+2*k,k+1,4+k,6+2*k,3+k,4+k,80+15*k,32*k,3+3*k,sqrt(18/(k+2))],
 k=>[51.5+2.5*k,58,40+k+.577*(k+2),2.114*(k+2),.223*(10+k),(k+1)/1.128,30+2.5*k,5+k,2.089*(k+1),80+k-1.427*(k+1),(10+k)/(500+100*k),.04+3*sqrt(.0384/(100*k)),0,3*k,5*k+3*sqrt(4.75*k),.05/k,.02,(100+20*k)/(50+5*k),2+3*sqrt(2/(k+3)),4-3*sqrt(4/(10+k)),52+1.2*k,(k+1)/3,1+2*k,100/k,10/k,8+8*k,.5,14+k,k+3,2],
 k=>[4+k,15+3*k,25+5*k,10,3600/(30+k),ceil(3+k/2),(200+10*k)/3,(10+5*k)/(500+100*k),1e6*(20+4*k)/(4000+400*k),95,72+1.8*k,ceil((20+5*k)*.22),100*(30+3*k)/(60+5*k),20,140+20*k,400+100*k,5+k,100+50*k,(1200+100*k)/1.1-1000,(1000+200*k)/1.21,30000+3000*k,700+20*k,1050+30*k,64+32*k,36+36*k,65+5*k,6+k,100*(5+k)/(10+k),20+10*k,200+30*k]
];
for(let tab=1;tab<6;tab++)for(const q of sets[tab].questions){
 const [,family,caseNo]=q.id.match(/S\d+-(\d+)-(\d+)/);
 const value=expected[tab-1](+caseNo)[+family-1];
 assert.ok(Math.abs(Number(q.o[q.a])-value)<=.000051,`${q.id}: key ${q.o[q.a]} vs independent value ${value}`);
 assert.ok(q.e.endsWith(`Result: ${q.o[q.a]}.`),q.id+' explanation/key mismatch');
}

// Minimal event/DOM stand-in to exercise the actual page controller and timer.
class Element {
 constructor(tag='div'){this.tagName=tag;this.children=[];this.attrs={};this.listeners={};this.dataset={};this.className='';this.textContent='';this.hidden=true;this.value=0;this._html='';this.classList={add:(...x)=>{},remove:(...x)=>{},toggle:()=>{}};}
 set innerHTML(s){this._html=s;this.children=[];if(this.tagName==='fieldset'){
  this.options=[...s.matchAll(/<input id="([^"]+)" type="radio" name="([^"]+)" value="(\d)"([^>]*)>/g)].map(m=>{
   const input=new Element('input');input.id=m[1];input.name=m[2];input.type='radio';input.value=m[3];input.checked=m[4].includes('checked');input.parent=this;
   const label=new Element('label');input.label=label;return input;
  }); this.feedback=new Element('p');}}
 get innerHTML(){return this._html;}
 append(x){this.children.push(x);}
 setAttribute(k,v){this.attrs[k]=v;}
 addEventListener(k,fn){(this.listeners[k]??=[]).push(fn);}
 emit(k,event={}){for(const fn of this.listeners[k]||[])fn(event);}
 focus(){}
 closest(s){return s==='fieldset'?this.parent:this.label;}
 querySelector(s){if(s==='input:checked')return this.options.find(x=>x.checked)||null;if(s==='.feedback')return this.feedback;return null;}
 querySelectorAll(s){return s==='label'?this.options.map(x=>x.label):[];}
}
function app(saved=new Map(),badStorage=false){
 let now=0,focused=true;const elements=new Map();const doc=new Element();const win=new Element();
 const element=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
 doc.visibilityState='visible';doc.hasFocus=()=>focused;doc.createElement=tag=>new Element(tag);
 doc.querySelector=s=>s.startsWith('#question-')?element('#quiz').children.find(x=>x.id===s.slice(1)):element(s);
 win.scrollTo=()=>{};
 let interval;
 const ctx=vm.createContext({document:doc,window:win,performance:{now:()=>now},setInterval:fn=>{interval=fn;},localStorage:{
 getItem:k=>{if(badStorage)throw Error('disabled');return saved.get(k)??null;},
 setItem:(k,v)=>{if(badStorage)throw Error('full');saved.set(k,v);},removeItem:k=>saved.delete(k)
 },console});
 vm.runInContext(script,ctx);
 return {ctx,saved,doc,win,element,eval:s=>vm.runInContext(s,ctx),advance:ms=>{now+=ms;},tick:()=>interval(),focus:state=>{focused=state;win.emit(state?'focus':'blur');}};
}
const legacy='lean-six-sigma-black-belt-progress-v1';
const saved=new Map([[legacy,JSON.stringify({answers:{'DEF-01':0},randomMode:false})]]);
let app1=app(saved);
assert.equal(app1.element('#quiz').children.filter(x=>x.tagName==='fieldset').length,100);
assert.equal(app1.eval('answers["DEF-01"]'),0,'Legacy answers preserved');
app1.advance(4200);app1.tick();assert.equal(app1.element('#timer').textContent,'00:00:04');
app1.focus(false);app1.advance(9000);app1.tick();assert.equal(app1.eval('currentElapsed()'),4200,'Blur pauses');
app1.focus(true);app1.advance(800);app1.doc.visibilityState='hidden';app1.doc.emit('visibilitychange');
app1.advance(100000);app1.tick();assert.equal(app1.eval('currentElapsed()'),5000,'Hidden/minimized time excluded');
app1.doc.visibilityState='visible';app1.doc.emit('visibilitychange');app1.advance(2000);
app1.eval('selectSet(1)');assert.equal(app1.element('#quiz').children.filter(x=>x.tagName==='fieldset').length,150);
assert.equal(app1.eval('currentElapsed()'),0);app1.advance(3500);app1.tick();
const id=sets[1].questions[0].id;
app1.eval(`answers[${JSON.stringify(id)}] = 2; saveProgress();`);
app1.element('#randomButton').emit('click');assert.equal(app1.eval('randomMode'),true);
assert.equal(app1.eval('new Set(questionOrder.map(q=>q.id)).size'),150);
app1.eval('selectSet(0)');assert.equal(app1.eval('currentElapsed()'),7000,'Set time restored');
app1.eval('selectSet(1)');assert.equal(app1.eval('currentElapsed()'),3500);assert.equal(app1.eval(`answers[${JSON.stringify(id)}]`),2);
assert.equal(app1.eval('randomMode'),true,'Per-set random order restored');
app1.element('#restartTimer').emit('click');assert.equal(app1.eval('currentElapsed()'),0);
assert.equal(app1.eval(`answers[${JSON.stringify(id)}]`),2,'Timer restart preserves answers');
app1.advance(2000);app1.win.emit('pagehide');app1.advance(999999);app1.tick();
assert.equal(app1.eval('currentElapsed()'),2000,'Page close does not add offline time');
let app2=app(saved);assert.equal(app2.eval('activeSet'),1);assert.equal(app2.eval('currentElapsed()'),2000,'Reload restores only accrued time');
app2.element('#resetButton').emit('click');assert.equal(app2.eval('Object.keys(answers).length'),0);assert.equal(app2.eval('currentElapsed()'),2000,'Answer reset preserves time');
app2.eval('selectSet(0)');assert.equal(app2.eval('answers["DEF-01"]'),0,'Reset is isolated to its set');
app2.element('#verifyButton').emit('click');assert.match(app2.element('#scoreText').textContent,/1\/1 correct/);
app2.eval('selectSet(5)');
// Exercise answer entry and verification for every possible correct-answer position.
for(const pos of [0,1,2,3]){
 const q=sets[5].questions.find(q=>q.a===pos);
 const field=app2.element('#quiz').children.find(x=>x.id===`question-${q.id}`);
 const input=field.options[pos];input.checked=true;app2.element('#quiz').emit('change',{target:input});
}
app2.element('#verifyButton').emit('click');assert.match(app2.element('#scoreText').textContent,/4\/4 correct/);
app2.element('#setTabs').children[5].emit('keydown',{key:'Home',preventDefault(){}});assert.equal(app2.eval('activeSet'),0);
app2.element('#setTabs').children[0].emit('keydown',{key:'End',preventDefault(){}});assert.equal(app2.eval('activeSet'),5);
app2.doc.emit('freeze');app2.advance(5000);app2.tick();const stopped=app2.eval('currentElapsed()');
app2.doc.emit('resume');app2.advance(1000);assert.equal(app2.eval('currentElapsed()'),stopped+1000);
// A paused page must not overwrite time saved by another browser window.
const shared=new Map();const first=app(shared);
first.advance(3000);first.focus(false);
const second=app(shared);second.advance(2000);second.focus(false);
first.advance(5000);first.tick();first.focus(true);
assert.equal(first.eval('currentElapsed()'),5000,'Focus reloads time from another window');
assert.equal(app(new Map(),true).element('#storageWarning').hidden,false,'Storage failure is visible');
const corrupt=new Map([[legacy,'{broken'],['lean-six-sigma-time-v2-original','-100']]);
assert.equal(app(corrupt).eval('currentElapsed()'),0,'Invalid saved timer cannot produce negative time');
console.log('PASS: 850 questions; 750 independently recalculated keys; distinct cross-tab templates; source/output match; legacy progress, six sets, answers, grading, shuffle, keyboard, timer lifecycle, restart, persistence, and storage failures.');

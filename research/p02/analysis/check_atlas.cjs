/* Runtime interaction checks with linkedom (QA only; delivered HTML has no dependencies). */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const {parseHTML}=require(process.env.P02_DOM_MODULE||'linkedom');
const dir=path.resolve(__dirname,'../companion');
function load(name,hash=''){
 const contents=fs.readFileSync(path.join(dir,name),'utf8');
 const {window,document}=parseHTML(contents);
 const proto=Object.getPrototypeOf(document.createElement('select'));
 const desc=Object.getOwnPropertyDescriptor(proto,'value');
 if(desc&&!desc.set)Object.defineProperty(proto,'value',{configurable:true,get(){return this._testValue??desc.get.call(this)??'';},
    set(v){this._testValue=String(v);}});
 const scripts=[...document.querySelectorAll('script')];
 assert.equal(scripts.length,2);
 const M=JSON.parse(scripts[0].textContent);
 const location={hash,href:'file://'+path.join(dir,name)+hash}, reports=[],exports=[];
 const fakeURL={createObjectURL:b=>{exports.push(b);return 'blob:test'},revokeObjectURL(){}};
 const ctx={window,document,Node:window.Node,location,history:{replaceState(a,b,h){location.hash=h}},
            navigator:{clipboard:{writeText:t=>{reports.push(t);return Promise.resolve();}}},Blob,URL:fakeURL,setTimeout,
            Option:function(t,v){const n=document.createElement('option');n.textContent=t;n.value=v;return n;}};
 vm.runInNewContext(scripts[1].textContent,ctx,{filename:name});
 const $=id=>document.getElementById(id);
 return {document,window,$,ctx,M,exports,location,event:(id,name)=>$(id).dispatchEvent(new window.Event(name))};
}
const a=load('epistemic_graph.html','#g_trend');
assert.equal(a.document.body.dataset.ready,'true');
assert.match(a.$('card').textContent,/Direction gate/);
assert.equal(a.$('card').querySelectorAll('input[type="checkbox"]').length,2);
assert.equal(a.$('matrixSection').hidden,true);
a.event('trace','click');assert.equal(a.$('trace').getAttribute('aria-pressed'),'true');
assert.match(a.$('diagram').textContent,/Unanimous point sign/);
a.event('next','click');assert.match(a.$('note').textContent,/Stop 2/);
const supergraph=load('supergraph.html','#cell_titan_venus_2010_2023_trend_ols');
assert.equal(supergraph.document.body.dataset.ready,'true');
assert.equal(supergraph.$('matrix').querySelectorAll('tbody tr').length,90);
assert.match(supergraph.$('card').textContent,/All 14 year exclusions/);
assert.equal(supergraph.$('card').querySelector('.specs').querySelectorAll('tbody tr').length,24);
assert.match(supergraph.$('card').textContent,/Joint sign: B > A/);
assert.match(supergraph.$('card').textContent,/Compare this pair across both estimators and all windows/);
const y=supergraph.$('card').querySelector('select[aria-label="Select an omitted year"]');
y.value='2010';y.dispatchEvent(new supergraph.window.Event('change'));
assert.match(supergraph.$('card').textContent,/Without 2010: observed range/);
const s=supergraph.$('card').querySelector('select');
s.value='global';s.dispatchEvent(new supergraph.window.Event('change'));
assert.equal(supergraph.$('card').querySelector('.specs').querySelectorAll('tbody tr').length,24);
supergraph.$('search').value='Porco';supergraph.event('search','input');
assert.match(supergraph.$('catalog').textContent,/Two named omissions/);
supergraph.event('export','click');assert.equal(supergraph.exports.length,1);
const scope=load('supergraph.html','#anchor_E01');assert.match(scope.$('card').textContent,/NOT_IN_ARCHIVE/);
assert.equal(scope.$('card').querySelector('a').href,'https://doi.org/10.1126/science.1123013');
assert.equal(supergraph.M.nodes.filter(n=>n.kind==='anchor').length,15);
console.log(JSON.stringify({mode:'DOM execution (not screenshot QA)',article:'PASS',supergraph:'PASS',
  nodes:supergraph.M.nodes.length,cells:90,archives:15,
  checks:['deep-links','AND controls','upstream trace','tour','90-row matrix','two resampling regimes','year influence','search','export','DOI links']},null,2));

const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(require('node:path').join(__dirname,'../ui/index.html'),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
const model=script.split('/* BEGIN INVARIANT MODEL */')[1].split('/* END INVARIANT MODEL */')[0];
const invariantRecord=vm.runInNewContext(model+'\ninvariantRecord');
let count=0;function check(x){assert.ok(x);count++}
for(const L of [.125,1,2,10,100,1e50])for(const k of [.25,.5,1,2,4,10]){const r=invariantRecord('A',L,k,['proportion','unboundedness','scale']);check(r.status==='finite model evaluated');check(r.midpoint===L/2&&r.scaled_extent===L/k&&r.scaled_midpoint===L/k/2);check(r.relative_midpoint===.5);check(r.checks.unboundedness.status==='conditional theorem');check(r.extent===L&&r.divisor===k)}
for(const L of [0,-1,null,Infinity,NaN])check(invariantRecord('A',L,2,[]).status!=='finite model evaluated');
for(const k of [0,-1,Infinity,NaN])check(invariantRecord('B',10,k,[]).status!=='finite model evaluated');
check(invariantRecord('B',10,2,['scale']).keep.join()==='scale');check(Object.keys(invariantRecord('B',10,2,[]).checks).length===0);check(invariantRecord('A',Number.MAX_VALUE,.5,[]).status==='Scaled values exceed numeric range.');check(invariantRecord('A',Number.MIN_VALUE,2,[]).status==='Scaled values exceed numeric range.');
console.log(count+' model assertions passed');

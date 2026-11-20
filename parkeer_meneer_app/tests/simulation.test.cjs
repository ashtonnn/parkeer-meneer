// Cityverse / Parkeer Meneer – offline regressietest zonder externe packages.
// Uitvoeren in de root van de repository: node parkeer_meneer_app/tests/simulation.test.cjs
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');

const html=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8');
const scripts=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m=>m[1]).filter(Boolean);
assert(scripts.length>=2,'JavaScript ontbreekt in index.html');
for(const script of scripts){new vm.Script(script);}
assert(!html.includes('id="view3d"'),'Het oude 3D-experiment mag niet zichtbaar zijn in de hoofdapp');
assert(html.includes('id="csvDownload"'),'CSV-export ontbreekt');
assert(html.includes('id="forecastSummary"'),'Analysekaart ontbreekt');
assert(html.includes('loadBgtForStreet()'),'BGT koppeling ontbreekt');

const main=scripts.find(x=>x.includes('function hash(s)'));
const start=main.indexOf('function hash(s)');
const stop=main.indexOf('function chips()',start);
assert(start>=0&&stop>start,'Pure simulatiefuncties zijn niet te vinden');
const pure=main.slice(start,stop);
const cities=['Kralingse Zoom','Weena','Coolsingel','Meent','Kruisplein'];
let checks=0;
const reports=[];
for(const name of cities){
 const context=vm.createContext({chosen:{name},seed:0,console});
 vm.runInContext(pure,context,{timeout:1500});
 context.seed=context.hash(name);
 const signature=[];
 for(let step=0;step<96;step++){
  const h=Math.floor(step/4),m=(step%4)*15;
  const bays=context.stateAt(h,m),c=context.counts(bays);
  assert.equal(bays.length,24,name+': 24 voorbeeldplekken nodig');
  assert.equal(c.accessible,2,name+': twee illustratieve toegankelijke plaatsen');
  assert.equal(c.taken+c.free+c.accessible,24,name+': onjuiste som');
  assert(bays.every(b=>!(b.accessible&&b.occupied)),name+': toegankelijke demo-plek bezet');
  const forecast=context.forecastAt(step);
  assert(Number.isFinite(forecast)&&forecast>=0&&forecast<=100,name+': ongeldige voorspelling');
  assert.equal(context.occupancyAt(step),100*c.taken/c.regular);
  signature.push(c.taken);checks++;
 }
 assert(new Set(signature).size>1,name+': bezetting verandert niet in de tijd');
 const recheck=context.stateAt(12,0).map(b=>Number(b.occupied));
 assert.deepEqual(recheck,context.stateAt(12,0).map(b=>Number(b.occupied)),name+': data niet reproduceerbaar');
 const result=context.backtestForecast();
 assert.equal(result.n,89);
 assert(result.mae>=0&&result.baseline>=0&&Number.isFinite(result.mae));
 reports.push({straat:name,modelMaePp:Number(result.mae.toFixed(1)),nulmetingMaePp:Number(result.baseline.toFixed(1))});
}
console.log('Geslaagd: '+checks+' 15-minutenmomenten over '+cities.length+' straten. Alle scripts syntactisch geldig.');
console.table(reports);
console.log('Let op: test met synthetische gegevens; browser, Render en externe PDOK/WFS worden hiermee NIET geverifieerd.');

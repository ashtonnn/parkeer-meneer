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

// Controleer dat schooldata niet als echte live sensorbezetting wordt verkocht.
const backend=fs.readFileSync(path.join(__dirname,'..','app.py'),'utf8');
assert(backend.includes('@app.get("/api/parking")'),'Rotterdam WFS endpoint ontbreekt');
assert(backend.includes('"source_url":WFS'),'Herkomst van gemeentelijke parkeerobjecten ontbreekt');
assert(backend.includes('"feature_count":len(features)'),'Aantal werkelijk verwerkte gemeentelijke objecten ontbreekt');
assert(backend.includes('"occupancy":"not_available"'),'Gemeentelijke locaties mogen geen live bezetting suggereren');
assert(backend.includes('"mode":"unavailable"'),'WFS fallback ontbreekt');
assert(backend.includes('@app.get("/api/school/bgt")'),'School BGT endpoint ontbreekt');
assert(backend.includes('"occupancy":"synthetic_not_from_bgt"'),'BGT mag geen sensordata claimen');
assert(!html.includes('id="bgtLayerToggle"'),'Verwijderde technische BGT-toggle staat nog in de gebruikersinterface');

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
 // Test de echte exportfunctie met een nagemaakte browseromgeving.
 let capturedCsv='',downloadedName='',clicks=0;
 context.Blob=class {constructor(parts){capturedCsv=parts.join('');}};
 context.URL={createObjectURL(){return 'blob:test'},revokeObjectURL(){}};
 context.document={
   body:{appendChild(){}},
   createElement(){return {href:'',set download(x){downloadedName=x},click(){clicks++},remove(){}};}
 };
 context.setTimeout=(fn)=>fn();
 context.exportSimulation();
 assert.equal(clicks,1,name+': CSV is niet geactiveerd');
 assert.equal(capturedCsv.split('\r\n').length,2305,name+': export moet 2304 fictieve records plus kop bevatten');
 assert(downloadedName.endsWith('.csv'),name+': CSV bestandsnaam ontbreekt');
 const result=context.backtestForecast();
 assert.equal(result.n,89);
 assert(result.mae>=0&&result.baseline>=0&&Number.isFinite(result.mae));
 reports.push({straat:name,modelMaePp:Number(result.mae.toFixed(1)),nulmetingMaePp:Number(result.baseline.toFixed(1))});
}
console.log('Geslaagd: '+checks+' 15-minutenmomenten, vijf CSV-exporten met 2304 regels, alle scripts syntactisch geldig.');
console.table(reports);
console.log('Let op: test met synthetische gegevens; browser, Render en externe PDOK/WFS worden hiermee NIET geverifieerd.');

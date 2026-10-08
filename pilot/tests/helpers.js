const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
function load(...files) {
 const context = vm.createContext({console, DATA:{triage:JSON.parse(fs.readFileSync(path.join(__dirname,'../kilder/safety-triage-rules-v2.json'),'utf8')),tiltaksgrunnlag:{fakta:[]},pilot3:{}}});
 for (const file of files) vm.runInContext(fs.readFileSync(path.join(__dirname,'../src',file),'utf8'),context,{filename:file});
 return context;
}
const actions=[{id:'housing',title:'Kontakt om bolig',priority:0,relevantFacts:['bolignod','boligstabilitet'],conditions:[{key:'bolignod',value:'nei'}],contactId:'nav',sourceIds:['nav-housing'],prepare:['Beskriv behovet ditt.']},{id:'expenses',title:'Kontakt om nødvendige utgifter',priority:1,relevantFacts:['betalingsvansker','behovstid'],conditions:[{key:'betalingsvansker',value:'ja'}],contactId:'nav',sourceIds:['nav-expenses'],prepare:['Beskriv hva du mangler.']}];
const contacts={nav:{id:'nav',label:'NAV',url:'https://www.nav.no/sok-nav-kontor',access:'UNKNOWN',hours:null,alternative:null}};
function state() {return {facts:{bolignod:'nei',betalingsvansker:'ja',boligstabilitet:'',behovstid:''},factsRevision:1,contextRevision:0,confirmedRevision:1,confirmedContextRevision:0,currentSafetyInput:'',safety:{input:null,level:null,suppressed:false},acknowledgements:{facts:true,draft:true,limits:true},contentVersion:'test-v1',locationContext:{area:'',bydel:'Ukjent'},progressByAction:{},planBasis:{},policyReady:true};}
module.exports={load,actions,contacts,state};

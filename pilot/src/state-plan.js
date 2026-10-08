/* Candidate state is independent of DOM, wall clock and the experimental runtime. */
const SESSION_FORMAT_VERSION = 'navigator-pilot3-session-v3';
const FACT_VALUES = {
 bolignod:['','ja','nei','ukjent','vil_ikke_oppgi'],
 betalingsvansker:['','ja','nei','ukjent','vil_ikke_oppgi'],
 boligstabilitet:['','stabil','midlertidig','ukjent','vil_ikke_oppgi'],
 behovstid:['','i_dag','snart','ukjent','vil_ikke_oppgi'],
 inntektssituasjon:['','lav','ordinar','ukjent','vil_ikke_oppgi'],
 gjeld:['','ja','nei','ukjent','vil_ikke_oppgi'],
 flyttebehov:['','ja','nei','ukjent','vil_ikke_oppgi'],
 varsel:['','ja','nei','ukjent','vil_ikke_oppgi'],
 andre_voksne_i_husstand:['','ja','nei','ukjent','vil_ikke_oppgi'],
 barn_i_husstand:['','ja','nei','ukjent','vil_ikke_oppgi'],
 brutto_husstandsinntekt:['','under_20000','20000_35000','35000_50000','50000_70000','over_70000','ukjent','vil_ikke_oppgi']
};
const PROGRESS_STATUSES=['IKKE_STARTET','KONTAKTET','VENTER','GJORT'];
function cloneJson(value){return JSON.parse(JSON.stringify(value));}
function stableJson(value){
 if(Array.isArray(value)) return '['+value.map(stableJson).join(',')+']';
 if(value && typeof value==='object') return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+stableJson(value[k])).join(',')+'}';
 return JSON.stringify(value);
}
function initialState(contentVersion){return {
 facts:Object.fromEntries(Object.keys(FACT_VALUES).map(k=>[k,''])), factsRevision:0,contextRevision:0,
 confirmedRevision:null,confirmedContextRevision:null,acknowledgements:{facts:false,draft:false,limits:false},
 currentSafetyInput:'',safety:{input:null,level:null,suppressed:false,failed:false},
 locationContext:{area:'',bydel:'Ukjent'},progressByAction:{},planBasis:{},legacyUnknownKeys:[],
 selection:{factKeys:[],actionIds:[],explicitActionIds:[]},migration:null,contentVersion,policyReady:true
};}
function factAnswerState(state,key){
 const value=(state.facts||{})[key];
 if(value===undefined||value==='')return 'UNANSWERED';
 if(value==='ukjent'&&(state.legacyUnknownKeys||[]).includes(key))return 'LEGACY_UNSPECIFIED';
 if(value==='ukjent')return 'UNKNOWN';
 if(value==='vil_ikke_oppgi')return 'WITHHELD';
 return 'ANSWERED';
}
function updateFact(state,key,value){
 if(!Object.hasOwn(FACT_VALUES,key)||!FACT_VALUES[key].includes(value))throw new Error('Ugyldig svar.');
 if(state.facts[key]!==value){state.facts[key]=value;state.factsRevision++;
 state.legacyUnknownKeys=(state.legacyUnknownKeys||[]).filter(k=>k!==key);}
 return state;
}
function actionBasis(action,state){return stableJson({actionId:action.id,contentVersion:state.contentVersion,
 sourceIds:action.sourceIds||[],relevantFacts:Object.fromEntries((action.relevantFacts||[]).map(k=>[k,state.facts[k]||''])),
 locationContext:action.usesLocation?state.locationContext:null});}
function safetyInputStatus(state){
 if(state.safety && state.safety.failed)return 'FAILED';
 if(!String(state.currentSafetyInput||'').trim())return 'NOT_PROVIDED';
 return state.safety && state.safety.input===state.currentSafetyInput?'EVALUATED':'CHANGED';
}
function gateForState(state){
 if(state.acuteLatched||(state.safety&&(state.safety.suppressed||state.safety.level==='ACUTE_RISK_NOW')))return 'ACUTE_HELP';
 if(state.error||safetyInputStatus(state)==='FAILED')return 'ERROR';
 if(state.policyReady!==true)return 'BLOCKED';
 if(!Object.values(state.facts||{}).some(v=>v!==''))return 'EMPTY';
 if(!Object.values(state.acknowledgements||{}).every(Boolean)||Object.keys(state.acknowledgements||{}).length!==3)return 'BLOCKED';
 if(state.confirmedRevision===null||state.confirmedContextRevision===null)return 'BLOCKED';
 return safetyInputStatus(state)==='EVALUATED'?'CURRENT':'CONTACT_ONLY';
}
function evaluateSafetyInput(state,input){
 state.currentSafetyInput=String(input);
 try{
  const hits=matchSignals(state.currentSafetyInput);const level=collapse(hits);
  state.acuteLatched=!!(state.acuteLatched||state.safety.suppressed||level==='ACUTE_RISK_NOW');
  state.safety={input:state.currentSafetyInput,level,suppressed:state.acuteLatched,failed:false};
 }catch(error){state.safety={input:null,level:null,suppressed:!!state.acuteLatched,failed:true};}
 return state;
}
function confirmState(state,actions,contacts){
 const ack=state.acknowledgements||{};
 if(!['facts','draft','limits'].every(k=>ack[k]===true)||!Object.values(state.facts).some(Boolean))return false;
 state.confirmedRevision=state.factsRevision;state.confirmedContextRevision=state.contextRevision;
 state.planBasis=Object.fromEntries(actions.map(a=>[a.id,actionBasis(a,state)]));
 return true;
}
function derivePlan(state,actions,contacts){
 let status=gateForState(state);
 const changedActionIds=actions.filter(a=>state.planBasis&&state.planBasis[a.id]&&state.planBasis[a.id]!==actionBasis(a,state)).map(a=>a.id);
 if(['CURRENT','CONTACT_ONLY'].includes(status)&&(changedActionIds.length||state.confirmedRevision!==state.factsRevision||state.confirmedContextRevision!==state.contextRevision))status='NEEDS_UPDATE';
 const active=['CURRENT','CONTACT_ONLY','NEEDS_UPDATE'].includes(status);
 const matching=actions.filter(a=>!(a.conditions||[]).length||(a.conditions||[]).some(c=>state.facts[c.key]===c.value));
 const hasSpecific=matching.some(a=>!a.fallback);
 const items=active?matching.filter(a=>!hasSpecific||!a.fallback).map(a=>{
  const basis=actionBasis(a,state);const raw=(state.progressByAction||{})[a.id];const changed=changedActionIds.includes(a.id);
  const progress=raw&&raw.basis===basis&&!changed?cloneJson(raw):{status:'IKKE_STARTET',history:raw?cloneJson(raw):null};
  return {...cloneJson(a),contact:cloneJson(contacts[a.contactId]||{label:'Kontakt er ikke avklart',access:'UNKNOWN'}),basis,currentBasis:!changed,progress};
 }).sort((a,b)=>a.priority-b.priority||a.id.localeCompare(b.id)):[];
 const clarificationQuestions=[];
 if(active&&state.facts.betalingsvansker==='ja'&&factAnswerState(state,'behovstid')==='UNANSWERED')clarificationQuestions.push({key:'behovstid',question:'Gjelder det noe du trenger i dag?'});
 const limitations=['Dette er kontaktinformasjon i et utkast. NAV vurderer behov og rettigheter individuelt.','Lokal åpningstid og tilgang er ikke kontrollert. Se den offisielle kontaktinngangen.'];
 if(status==='CONTACT_ONLY')limitations.unshift('Ingen vurdert situasjonstekst. Forslagene er begrenset til kontakt og forberedelse.');
 if(status==='CURRENT')limitations.unshift('Tekstsjekken er begrenset og kan overse fare. Den bekrefter ikke at situasjonen er trygg.');
 return {status,current:status==='CURRENT',navigable:active,actions:items,primaryAction:items[0]||null,secondaryActions:items.slice(1),
 clarificationQuestions,changedActionIds,basisRevision:stableJson({version:state.contentVersion,bases:actions.map(a=>actionBasis(a,state))}),limitations};
}
function questionDefinitions(state){
 const common=[{value:'ukjent',label:'Vet ikke'},{value:'vil_ikke_oppgi',label:'Vil ikke oppgi'}];
 const qs=[{key:'bolignod',label:'Har du et trygt sted å sove og være det neste døgnet?',help:'Du kan svare uten å vite hvilken tjeneste du trenger.',options:[{value:'ja',label:'Ja, jeg har et sted å være'},{value:'nei',label:'Nei, jeg mangler et sted å være det neste døgnet'},...common]},
 {key:'betalingsvansker',label:'Mangler du penger til nødvendige utgifter akkurat nå?',help:'For eksempel mat, husleie eller strøm. Svaret er ikke en søknad.',options:[{value:'ja',label:'Ja, jeg får ikke dekket det jeg trenger'},{value:'nei',label:'Nei, det viktigste er dekket'},...common]}];
 if(state.facts.bolignod==='ja')qs.push({key:'boligstabilitet',label:'Er stedet du bor stabilt eller midlertidig?',help:'Valgfritt. Et midlertidig opphold utelukker ikke at du kan spørre om hjelp.',optional:true,options:[{value:'stabil',label:'Jeg kan bli boende'},{value:'midlertidig',label:'Midlertidig, for eksempel hos venner eller familie'},...common]});
 if(state.facts.betalingsvansker==='ja')qs.push({key:'behovstid',label:'Gjelder det noe du trenger i dag?',help:'Valgfritt. Dette hjelper deg å forklare hvor mye det haster.',optional:true,options:[{value:'i_dag',label:'Ja, jeg trenger hjelp i dag'},{value:'snart',label:'Det gjelder de neste dagene'},...common]});
 return qs;
}
function generalHelp(){return [{label:'Finn NAV-kontor',url:'https://www.nav.no/sok-nav-kontor'},
 {label:'113 ved akutt fare for liv og helse',url:'tel:113'},
 {label:'Legevakt 116 117',url:'tel:116117'}];}
const LEGACY_FACT_KEYS=['inntektssituasjon','betalingsvansker','gjeld','flyttebehov','bolignod','varsel'];
const ACTION_IDS=['housing','expenses','general','midlertidig-botilbud','varsel-avklaring','bostotte','sosialhjelp','gjeldsradgivning','boligformidling','depositum'];
function isRecord(x){return !!x&&typeof x==='object'&&!Array.isArray(x);}
function onlyKeys(x,keys){return isRecord(x)&&Object.keys(x).every(k=>keys.includes(k));}
function validLocation(x){return onlyKeys(x,['area','bydel'])&&['','Trondheim','Annen kommune'].includes(x.area)&&['','Ukjent','Lerkendal','Heimdal','Ostbyen','Midtbyen'].includes(x.bydel);}
function validFacts(x,keys){return onlyKeys(x,keys)&&keys.every(k=>Object.hasOwn(x,k)&&FACT_VALUES[k].includes(x[k]));}
function validSelection(x){return onlyKeys(x,['factKeys','actionIds','explicitActionIds'])&&['factKeys','actionIds','explicitActionIds'].every(k=>Array.isArray(x[k])&&x[k].length<=50&&x[k].every(v=>typeof v==='string'&&(k==='factKeys'?Object.keys(FACT_VALUES):ACTION_IDS).includes(v))&&new Set(x[k]).size===x[k].length);}
function validProgress(x){
 if(!isRecord(x)||Object.keys(x).length>20)return false;
 return Object.entries(x).every(([id,row])=>ACTION_IDS.includes(id)&&onlyKeys(row,['status','contentVersion','basis','markedAt','invalidatedAt','history'])&&PROGRESS_STATUSES.includes(row.status)
 &&(row.contentVersion===undefined||typeof row.contentVersion==='string'&&row.contentVersion.length<=128)
 &&['markedAt','invalidatedAt'].every(k=>row[k]===undefined||typeof row[k]==='string'&&row[k].length<=64)
 &&(row.history===undefined||row.history===null)
 &&(row.basis===undefined||typeof row.basis==='string'&&row.basis.length<=8192||validLegacyBasis(row.basis)));
}
function validLegacyBasis(basis){
 return onlyKeys(basis,['facts','locationContext','actionId','contentVersion','relevantFacts'])
 &&(basis.locationContext===undefined||validLocation(basis.locationContext))
 &&['facts','relevantFacts'].every(k=>basis[k]===undefined||onlyKeys(basis[k],Object.keys(FACT_VALUES))&&Object.entries(basis[k]).every(([key,value])=>FACT_VALUES[key].includes(value)))
 &&(basis.actionId===undefined||ACTION_IDS.includes(basis.actionId))
 &&(basis.contentVersion===undefined||typeof basis.contentVersion==='string'&&basis.contentVersion.length<=128);
}
function exportSession(state){return JSON.stringify({formatVersion:SESSION_FORMAT_VERSION,contentVersion:state.contentVersion,
 facts:state.facts,legacyUnknownKeys:state.legacyUnknownKeys||[],locationContext:state.locationContext,
 progressByAction:state.progressByAction,selection:state.selection,
 acuteLatched:!!(state.acuteLatched||state.safety.suppressed),migration:state.migration||null},null,2);}
function importSession(text,currentState,contentVersion){
 const fail=()=>({ok:false,error:'Filen er ugyldig, for stor eller har et format som ikke støttes. Ingen svar er endret.'});
 try{
  if(typeof text!=='string'||encodeURIComponent(text).replace(/%[0-9A-F]{2}/g,'x').length>65536)return fail();
  const raw=JSON.parse(text);const version=raw.formatVersion;
  const legacy=version==='navigator-pilot3-session-v1'||version==='navigator-pilot3-session-v2';
  if(!legacy&&version!==SESSION_FORMAT_VERSION)return fail();
  const keys=legacy?['formatVersion','contentVersion','facts','locationContext','progressByAction']:['formatVersion','contentVersion','facts','legacyUnknownKeys','locationContext','progressByAction','selection','acuteLatched','migration'];
  if(!onlyKeys(raw,keys)||!keys.every(k=>Object.hasOwn(raw,k))||typeof raw.contentVersion!=='string'||!raw.contentVersion||raw.contentVersion.length>128)return fail();
  const factKeys=version.endsWith('v1')?LEGACY_FACT_KEYS:legacy?[...LEGACY_FACT_KEYS,'andre_voksne_i_husstand','barn_i_husstand','brutto_husstandsinntekt']:Object.keys(FACT_VALUES);
  if(!validFacts(raw.facts,factKeys)||!validLocation(raw.locationContext)||!validProgress(raw.progressByAction))return fail();
  if(!legacy&&(!validSelection(raw.selection)||typeof raw.acuteLatched!=='boolean'||!Array.isArray(raw.legacyUnknownKeys)||raw.legacyUnknownKeys.length>factKeys.length||!raw.legacyUnknownKeys.every(k=>factKeys.includes(k)&&raw.facts[k]==='ukjent')))return fail();
  if(!legacy&&raw.migration!==null&&(!onlyKeys(raw.migration,['fromFormat','legacyPaymentAnswer'])||raw.migration.fromFormat!=='navigator-pilot3-session-v1'||!FACT_VALUES.betalingsvansker.includes(raw.migration.legacyPaymentAnswer)))return fail();
  const next=initialState(contentVersion);Object.assign(next.facts,raw.facts);next.locationContext=cloneJson(raw.locationContext);next.progressByAction=cloneJson(raw.progressByAction);
  for(const row of Object.values(next.progressByAction))if(isRecord(row.basis))row.basis=stableJson(row.basis);
  next.legacyUnknownKeys=legacy?LEGACY_FACT_KEYS.filter(k=>raw.facts[k]==='ukjent'):cloneJson(raw.legacyUnknownKeys);
  if(version.endsWith('v1')){next.migration={fromFormat:version,legacyPaymentAnswer:raw.facts.betalingsvansker};next.facts.betalingsvansker='';next.legacyUnknownKeys=next.legacyUnknownKeys.filter(k=>k!=='betalingsvansker');}
  if(!legacy){next.selection=cloneJson(raw.selection);next.migration=cloneJson(raw.migration);}
  next.acuteLatched=!!(currentState.acuteLatched||currentState.safety.suppressed||raw.acuteLatched);
  next.factsRevision=1;return {ok:true,next,preview:{format:version,answers:Object.values(next.facts).filter(Boolean).length,legacy,needsReview:true}};
 }catch(error){return fail();}
}
function createImportCoordinator(){let epoch=0;return {begin(){return ++epoch;},isCurrent(token){return token===epoch;},cancel(){epoch++;}};}
function createSessionController(initial){
 let state=initial,previous=null;
 return {get(){return state;},changed(){previous=null;},replace(next){previous=null;state=next;},
 reset(version){previous=cloneJson(state);const latch=!!(state.acuteLatched||state.safety.suppressed);state=initialState(version);state.acuteLatched=latch;},
 undo(){if(!previous)return false;state=previous;previous=null;return true;}};
}

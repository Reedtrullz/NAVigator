const STATUS_TEXT={EMPTY:'Svar på et behov for å komme videre',CONTACT_ONLY:'Kontaktforslag med begrenset grunnlag',CURRENT:'Oppdatert til svarene dine',NEEDS_UPDATE:'Svarene er endret – se gjennom på nytt',ACUTE_HELP:'Se hjelp ved fare nå',BLOCKED:'Bekreft grunnlaget for å gå videre',ERROR:'Tekstsjekken feilet – forslagene er satt på vent'};
function renderQuestion(q,state){return '<fieldset id="group-'+esc(q.key)+'"><legend>'+esc(q.label)+'</legend><p id="help-'+esc(q.key)+'" class="muted">'+esc(q.help)+'</p>'+q.options.map(o=>'<label class="choice" for="answer-'+esc(q.key)+'-'+esc(o.value)+'"><input type="radio" id="answer-'+esc(q.key)+'-'+esc(o.value)+'" name="'+esc(q.key)+'" value="'+esc(o.value)+'" aria-describedby="help-'+esc(q.key)+'"'+(state.facts[q.key]===o.value?' checked':'')+'><span>'+esc(o.label)+'</span></label>').join('')+'<button class="text-button" type="button" data-clear="'+esc(q.key)+'">Fjern dette svaret</button></fieldset>';}
function sourceDetails(item,sources){return '<details><summary>Hvorfor denne kontakten? Se kilder og begrensninger</summary><p>'+esc(item.statement||'Forslaget følger behovet du har oppgitt.')+'</p>'+(item.sourceIds||[]).map(id=>{
 const s=sources.find(s=>s.id===id);if(!s)return '<p>Kilden er ikke avklart.</p>';
 return '<p><a href="'+esc(s.url)+'" rel="noreferrer">'+esc(s.title)+'</a><br><span class="muted">Hentet '+esc(s.retrievedAt)+'. '+(s.reviewedAt?'Faglig kontrollert '+esc(s.reviewedAt)+'.':'Faglig kontroll av denne kandidaten gjenstår.')+'</span></p>';
 }).join('')+'</details>';}
function renderContactCard(item,sources){
 const c=item.contact;const progress=item.progress||{status:'IKKE_STARTET'};
 return '<article class="contact-card" data-action="'+esc(item.id)+'"><p class="eyebrow">'+(item.priority===0?'Start med dette':'En kontakt å vurdere')+'</p><h2>'+esc(item.title)+'</h2><p>'+esc(c.label)+'</p>'+
 (c.url?'<a class="button-link" href="'+esc(c.url)+'" rel="noreferrer">Finn kontaktinformasjon hos NAV</a>':'<p>Kontaktvei er ikke avklart.</p>')+
 '<p class="access-note">Lokal åpningstid og tilgang er ikke kontrollert. Kontakt utenfor åpningstid er ikke avklart her; se den offisielle kontaktoversikten.</p><h3>Dette kan du si eller forberede</h3><ul>'+(item.prepare||[]).slice(0,3).map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul><p class="muted">NAV vurderer behov og rettigheter individuelt. Dette er et kontaktforslag.</p>'+
 (!item.currentBasis?'<p class="notice">Grunnlaget for dette kortet er endret. Bekreft svarene før du bruker det videre.</p>':'')+
 '<label for="progress-'+esc(item.id)+'">Din fremdrift</label><select id="progress-'+esc(item.id)+'" data-progress="'+esc(item.id)+'"'+(!item.currentBasis?' disabled':'')+'>'+[['IKKE_STARTET','Ikke startet'],['KONTAKTET','Jeg har tatt kontakt'],['VENTER','Jeg venter på svar'],['GJORT','Ferdig med dette steget']].map(([v,t])=>'<option value="'+v+'"'+(progress.status===v?' selected':'')+'>'+t+'</option>').join('')+'</select>'+
 (progress.history?'<p class="muted">Tidligere fremdrift er bevart i arbeidsfilen. Den gjaldt et annet grunnlag.</p>':'')+sourceDetails(item,sources)+'</article>';
}
function initPilot(){
 const byId=id=>document.getElementById(id);const actions=DATA.content.actions,contacts=DATA.content.contacts;
 const controller=createSessionController(initialState(DATA.content.content_version));const imports=createImportCoordinator();
 let pendingImport=null,selectionInitialized=false;const state=()=>controller.get();
 const announce=text=>{byId('statusLive').textContent=text;};
 const focus=id=>byId(id).focus();
 const model=()=>derivePlan(state(),actions,contacts);
 function showStage(stage,moveFocus=true){
  ['start','needs','next','take'].forEach(s=>{byId(s+'Section').hidden=s!==stage;});
  byId('workflow').hidden=stage==='start';
  document.querySelectorAll('[data-stage]').forEach(el=>{if(el.dataset.stage===stage)el.setAttribute('aria-current','step');else el.removeAttribute('aria-current');});
  if(moveFocus)focus(stage+'Heading');
 }
 function saveChange(){controller.changed();byId('fileState').textContent='Endringer finnes bare i denne åpne siden.';byId('undoReset').hidden=true;}
 function renderQuestions(all=false){
  const qs=questionDefinitions(state());if(all)byId('primaryQuestions').innerHTML=qs.slice(0,2).map(q=>renderQuestion(q,state())).join('');
  const id=document.activeElement&&document.activeElement.id;
  byId('followupQuestions').innerHTML=qs.slice(2).map(q=>renderQuestion(q,state())).join('');
  if(id&&byId(id))byId(id).focus({preventScroll:true});
 }
 function renderReview(){
  const s=state();const facts=Object.keys(s.facts).filter(k=>s.facts[k]);
  byId('answerReview').innerHTML=facts.length?'<ul>'+facts.map(k=>'<li>'+esc(FACT_LABELS[k])+': <strong>'+esc(factLabel(s,k))+'</strong></li>').join('')+'</ul>':'<p>Ingen svar ennå. Ett svar er nok til å se gjennom.</p>';
  byId('answerCount').textContent=facts.length?facts.length+' svar lagt til':'Ingen svar ennå';
  ['facts','draft','limits'].forEach(k=>{byId('ack-'+k).checked=s.acknowledgements[k];});
 }
 function renderPlan(){
  const v=model();byId('planStatus').textContent=STATUS_TEXT[v.status];byId('planStatus').dataset.status=v.status;
  byId('planLimitations').innerHTML=v.limitations.map(x=>'<p>'+esc(x)+'</p>').join('');
  byId('planActions').innerHTML=v.actions.map(a=>renderContactCard(a,DATA.content.sources)).join('');
  byId('updatePlan').hidden=v.status!=='NEEDS_UPDATE';byId('takeNext').hidden=!v.navigable;
  byId('planBlocked').hidden=!['EMPTY','BLOCKED','ERROR','ACUTE_HELP'].includes(v.status);
  byId('planBlocked').textContent=v.status==='ACUTE_HELP'?'Teksten kan tyde på fare. Vanlige kontaktforslag er satt på vent. Bruk hjelpen nedenfor. Tekstsjekken erstatter ikke en vurdering fra mennesker.':v.status==='ERROR'?'Tekstsjekken kunne ikke fullføres. Kontroller teksten og prøv igjen, eller bruk generell kontaktinformasjon.':'Du kan gå tilbake til behovene dine og se gjennom svarene. Generell hjelp er tilgjengelig nedenfor.';
  byId('changedCards').textContent=v.changedActionIds.length?'Berørte kontakter: '+v.changedActionIds.map(id=>(actions.find(a=>a.id===id)||{}).title).join(', '):'';
 }
 function renderSelection(){
  const activeId=document.activeElement&&document.activeElement.id;
  const s=state(),v=model();
  byId('factSelection').innerHTML=Object.keys(s.facts).filter(k=>s.facts[k]).map(k=>'<label class="choice"><input type="checkbox" id="selection-fact-'+esc(k)+'" data-fact-selection="'+esc(k)+'"'+(s.selection.factKeys.includes(k)?' checked':'')+'><span>'+esc(FACT_LABELS[k])+': '+esc(factLabel(s,k))+'</span></label>').join('')||'<p>Ingen opplysninger valgt.</p>';
  byId('actionSelection').innerHTML=v.actions.filter(a=>a.currentBasis).map(a=>{
   const missing=(a.relevantFacts||[]).some(k=>s.facts[k]&&!s.selection.factKeys.includes(k));
   return '<label class="choice"><input type="checkbox" id="selection-action-'+esc(a.id)+'" data-action-selection="'+esc(a.id)+'"'+(s.selection.actionIds.includes(a.id)?' checked':'')+'><span>'+esc(a.title)+'</span></label>'+(missing?'<label class="choice opt-in"><input type="checkbox" id="selection-explicit-'+esc(a.id)+'" data-explicit-selection="'+esc(a.id)+'"'+(s.selection.explicitActionIds.includes(a.id)?' checked':'')+'><span>Ta med dette kontaktforslaget selv om jeg har utelatt behovet det bygger på. Forslaget kan røpe hva jeg trenger hjelp til.</span></label>':'');
  }).join('')||'<p>Ingen gjeldende kontaktforslag å velge.</p>';
  renderNote();
  if(activeId&&byId(activeId))byId(activeId).focus({preventScroll:true});
 }
 function renderNote(){const projected=projectSummary(state(),model(),state().selection);byId('notePreview').innerHTML=summaryPrintHtml(projected);}
 function renderAll(){renderQuestions(true);renderReview();renderPlan();renderSelection();byId('triageInput').value=state().currentSafetyInput||'';}
 function showError(text){byId('formError').hidden=false;byId('formError').innerHTML=esc(text)+' <a href="#group-bolignod">Gå til spørsmålene</a>';focus('formError');announce('Se gjennom meldingen før du går videre.');}
 function makeDownload(text,name,type){
  const blob=new Blob([text],{type});const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download=name;document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  announce('Nedlasting startet. Kontroller at filen finnes på enheten din.');
 }
 document.querySelectorAll('[data-stage]').forEach(el=>el.addEventListener('click',event=>{event.preventDefault();renderPlan();renderSelection();showStage(el.dataset.stage);}));
 byId('startQuestions').addEventListener('click',()=>showStage('needs'));
 byId('needsSection').addEventListener('change',event=>{
  const el=event.target;saveChange();
  if(el.type==='radio'){updateFact(state(),el.name,el.value);renderQuestions();renderReview();renderPlan();renderSelection();announce('Svaret er oppdatert.');}
  if(el.dataset.ack){state().acknowledgements[el.dataset.ack]=el.checked;renderPlan();}
 });
 byId('needsSection').addEventListener('click',event=>{const el=event.target.closest('[data-clear]');if(!el)return;saveChange();updateFact(state(),el.dataset.clear,'');renderQuestions(true);renderReview();renderPlan();renderSelection();focus('needsHeading');announce('Svaret er fjernet.');});
 byId('triageInput').addEventListener('input',()=>{saveChange();evaluateSafetyInput(state(),byId('triageInput').value);renderPlan();renderNote();if(state().acuteLatched)announce('Se hjelp ved fare i neste steg.');});
 byId('showPlan').addEventListener('click',()=>{
  byId('formError').hidden=true;evaluateSafetyInput(state(),byId('triageInput').value);
  if(!state().acuteLatched&&!confirmState(state(),actions,contacts)){showError('Velg minst ett svar og de tre bekreftelsene. Du kan velge «Vet ikke» eller «Vil ikke oppgi».');return;}
  if(!selectionInitialized){state().selection.factKeys=Object.keys(state().facts).filter(k=>state().facts[k]&&factAnswerState(state(),k)!=='WITHHELD');state().selection.actionIds=model().actions.map(a=>a.id);selectionInitialized=true;}
  renderPlan();renderSelection();showStage('next');announce('Neste steg er vist.');
 });
 byId('updatePlan').addEventListener('click',()=>showStage('needs'));
 byId('takeNext').addEventListener('click',()=>{renderSelection();showStage('take');announce('Velg hva notatet skal inneholde.');});
 byId('planActions').addEventListener('change',event=>{const id=event.target.dataset.progress;if(!id)return;const item=model().actions.find(a=>a.id===id);if(!item||!item.currentBasis||!PROGRESS_STATUSES.includes(event.target.value))return;saveChange();state().progressByAction[id]={status:event.target.value,basis:item.basis,contentVersion:state().contentVersion};announce('Din fremdrift er oppdatert.');});
 byId('takeSection').addEventListener('change',event=>{
  const el=event.target;const kind=el.dataset.factSelection?'factKeys':el.dataset.actionSelection?'actionIds':el.dataset.explicitSelection?'explicitActionIds':null;if(!kind)return;
  saveChange();const id=el.dataset.factSelection||el.dataset.actionSelection||el.dataset.explicitSelection;
  state().selection[kind]=state().selection[kind].filter(k=>k!==id);if(el.checked)state().selection[kind].push(id);
  renderSelection();announce('Innholdet i notatet er oppdatert.');
 });
 const projection=()=>projectSummary(state(),model(),state().selection);
 byId('downloadNote').addEventListener('click',()=>makeDownload(summaryText(projection()),'NAVigator-motenotat.txt','text/plain;charset=utf-8'));
 byId('copyNote').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(summaryText(projection()));announce('Notatet er kopiert.');}catch(error){announce('Kopiering støttes ikke her. Last ned notatet som tekst.');}});
 byId('printNote').addEventListener('click',()=>{renderNote();window.print();});
 byId('saveWork').addEventListener('click',()=>{makeDownload(exportSession(state()),'NAVigator-arbeidsfil.json','application/json');byId('fileState').textContent='Nedlasting av arbeidsfil er startet. Kontroller filen; siden lagrer ikke automatisk.';});
 byId('importFile').addEventListener('change',async event=>{
  const token=imports.begin();pendingImport=null;byId('importPreview').hidden=true;const file=event.target.files[0];if(!file)return;
  if(file.size>65536){announce('Filen er for stor. Ingen svar er endret.');return;}
  try{
   const text=await file.text();if(!imports.isCurrent(token))return;
   const result=importSession(text,state(),DATA.content.content_version);if(!result.ok){announce(result.error);return;}
   pendingImport=result;byId('importDescription').textContent=result.preview.answers+' svar vil erstatte svarene på siden. Forslag må bekreftes på nytt.'+(result.preview.legacy?' Eldre uklare svar er merket; endret betalingsspørsmål må besvares på nytt ved v1-import.':'');
   byId('importPreview').hidden=false;focus('applyImport');announce('Se gjennom før du erstatter svarene.');
  }catch(error){if(imports.isCurrent(token))announce('Filen kunne ikke leses. Ingen svar er endret.');}
 });
 byId('applyImport').addEventListener('click',()=>{if(!pendingImport)return;
  // Preserve any danger observed while a file preview was open.
  pendingImport.next.acuteLatched=!!(pendingImport.next.acuteLatched||state().acuteLatched||state().safety.suppressed);
  controller.replace(pendingImport.next);pendingImport=null;imports.cancel();selectionInitialized=true;byId('importPreview').hidden=true;renderAll();showStage('needs');saveChange();announce('Svarene er åpnet. Se gjennom og bekreft grunnlaget.');});
 byId('cancelImport').addEventListener('click',()=>{pendingImport=null;imports.cancel();byId('importPreview').hidden=true;announce('Import avbrutt. Svarene er beholdt.');});
 byId('reset').addEventListener('click',()=>{controller.reset(DATA.content.content_version);imports.cancel();pendingImport=null;selectionInitialized=false;byId('importPreview').hidden=true;renderAll();byId('undoReset').hidden=false;byId('fileState').textContent='Svarene er nullstilt. Du kan angre frem til neste endring.';showStage('start');announce('Svarene er nullstilt. Angre er tilgjengelig.');});
 byId('undoReset').addEventListener('click',()=>{if(controller.undo()){selectionInitialized=true;renderAll();byId('undoReset').hidden=true;showStage('needs');announce('Svarene er gjenopprettet.');}});
 // Only warn for user-entered state; no automatic persistence or telemetry.
 window.addEventListener('beforeunload',event=>{if(Object.values(state().facts).some(Boolean)||state().currentSafetyInput){event.preventDefault();event.returnValue='';}});
 renderAll();showStage('start',false);
}
if(typeof document!=='undefined')initPilot();

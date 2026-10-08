const FACT_LABELS={bolignod:'Sted å være det neste døgnet',betalingsvansker:'Nødvendige utgifter',boligstabilitet:'Bosituasjon',behovstid:'Når hjelpen trengs',inntektssituasjon:'Inntektssituasjon',gjeld:'Gjeld',flyttebehov:'Behov for å flytte',varsel:'Varsel om boligen',andre_voksne_i_husstand:'Andre voksne i husstanden',barn_i_husstand:'Barn i husstanden',brutto_husstandsinntekt:'Samlet bruttoinntekt'};
function factLabel(state,key){
 const q=questionDefinitions(state).find(q=>q.key===key);const value=state.facts[key];
 if(factAnswerState(state,key)==='LEGACY_UNSPECIFIED')return 'Eldre svar: vet ikke / ønsket ikke å svare. Betydningen er ikke avklart.';
 const generic={ukjent:'Vet ikke',vil_ikke_oppgi:'Vil ikke oppgi',ja:'Ja',nei:'Nei',lav:'Lav',ordinar:'Ordinær',under_20000:'Under 20 000 kr', '20000_35000':'20 000–35 000 kr','35000_50000':'35 000–50 000 kr','50000_70000':'50 000–70 000 kr',over_70000:'Over 70 000 kr'};
 return q?(q.options.find(o=>o.value===value)||{}).label||generic[value]||value:generic[value]||value;
}
function projectSummary(state,model,selection){
 const factKeys=new Set(selection.factKeys||[]);const chosen=new Set(selection.actionIds||[]);const explicit=new Set(selection.explicitActionIds||[]);
 const userFacts=[...factKeys].filter(k=>Object.hasOwn(FACT_LABELS,k)&&factAnswerState(state,k)!=='UNANSWERED').map(k=>({key:k,label:FACT_LABELS[k],answer:factLabel(state,k),answerState:factAnswerState(state,k),source:'brukeren'}));
 const actions=(model.actions||[]).filter(a=>chosen.has(a.id)&&a.currentBasis&&((a.relevantFacts||[]).every(k=>!state.facts[k]||factKeys.has(k))||explicit.has(a.id))).map(a=>({id:a.id,title:a.title,contact:a.contact,prepare:a.prepare||[],sourceIds:a.sourceIds||[],source:'produktforslag',explicit:explicit.has(a.id)}));
 // Questions are general and never reproduce unselected answers or safety text.
 return {userFacts,actions,questions:actions.length?['Hva er riktig kontaktvei og neste steg for meg?']:[],limitations:[...model.limitations]};
}
function summaryText(p){
 const block=(title,rows)=>title+'\n'+(rows.length?rows.map(x=>'• '+x).join('\n'):'Ingen valgt.')+'\n';
 return ['Møtenotat – NAVigator (utkast)',block('Opplysninger fra deg',p.userFacts.map(f=>f.label+': '+f.answer)),
 block('Kontaktforslag fra NAVigator',p.actions.flatMap(a=>[a.title,a.contact.label+(a.contact.url?' – '+a.contact.url:''),...a.prepare])),
 block('Spørsmål å ta med',p.questions),block('Begrensninger',p.limitations)].join('\n');
}
function summaryPrintHtml(p){
 const list=rows=>rows.length?'<ul>'+rows.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>':'<p>Ingen valgt.</p>';
 return '<article class="meeting-note"><h2>Møtenotat – NAVigator (utkast)</h2><h3>Opplysninger fra deg</h3>'+list(p.userFacts.map(f=>f.label+': '+f.answer))+
 '<h3>Kontaktforslag fra NAVigator</h3>'+list(p.actions.flatMap(a=>[a.title,a.contact.label+(a.contact.url?' – '+a.contact.url:''),...a.prepare]))+
 '<h3>Spørsmål å ta med</h3>'+list(p.questions)+'<h3>Begrensninger</h3>'+list(p.limitations)+'</article>';
}

const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const Ajv=require('ajv');const root=path.resolve(__dirname,'..');
const content=JSON.parse(fs.readFileSync(path.join(root,'data/pilot3-tiltak-vnext.json')));
const context=vm.createContext({DATA:{content,triage:JSON.parse(fs.readFileSync(path.join(root,'kilder/safety-triage-rules-v2.json')))}});
for(const f of ['safety.js','state-plan.js','summary.js'])vm.runInContext(fs.readFileSync(path.join(root,'src',f),'utf8'),context);
const s=context.initialState(content.content_version);s.facts.bolignod='nei';s.acknowledgements={facts:true,draft:true,limits:true};context.confirmState(s,content.actions,content.contacts);
assert.equal(context.derivePlan(s,content.actions,content.contacts).status,'CONTACT_ONLY');
let item=context.derivePlan(s,content.actions,content.contacts).primaryAction;context.recordProgress(s,item,'KONTAKTET');context.updateFact(s,'boligstabilitet','midlertidig');s.acknowledgements.facts=true;context.confirmState(s,content.actions,content.contacts);item=context.derivePlan(s,content.actions,content.contacts).primaryAction;context.recordProgress(s,item,'VENTER');
const exported=JSON.parse(context.exportSession(s));assert.equal(exported.progressByAction.housing.history[0].status,'KONTAKTET');const schema=JSON.parse(fs.readFileSync(path.join(root,'data/session-v3.schema.json')));const ajv=new Ajv({strict:false,allErrors:true});assert.ok(ajv.validate(schema,exported),JSON.stringify(ajv.errors));
const roundtrip=context.importSession(JSON.stringify(exported),s,content.content_version);assert.ok(roundtrip.ok);assert.equal(roundtrip.next.confirmedRevision,null);
if(process.argv[2]){const html=fs.readFileSync(process.argv[2],'utf8');const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];new vm.Script(script);assert.equal((html.match(/role="status"/g)||[]).length,1);assert.ok(!html.includes('__DATA_JSON__'));}
console.log('GENERATED CONTRACT OK; exported session matches v3 schema');

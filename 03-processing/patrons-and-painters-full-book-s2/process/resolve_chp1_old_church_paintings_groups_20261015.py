from __future__ import annotations
import argparse, csv, hashlib, io, json, os, shutil, subprocess, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
T=ROOT/'04-knowledge'/'tables'
C=T/'entity-candidates.csv'; M=T/'mentions.csv'; S=T/'book-statements.jsonl'; G=T/'segments.jsonl'; V=T/'s2-coverage.csv'
SEG='chp-1:01_CHP-1_sec_i:l35-36'; ST='st-chp1-l150-152-old-church-art'; SRC=ROOT/'02-sources'/'02-Markdown'/'01_CHP-1_sec_i.md'
EXPECTED={C:'fb5851ca9d3c11fb521b18c1041e85116067f9fc08ad9455ecfdc3c16576b0e2',M:'8beb012f2e38373a470c7a0476af9a0f1da5d6dafee896d18315f3a7cd1d686d',S:'cc968ba9b29b2091dbdc32553b27a01d04d4bb21fcd3b86d72e0572fed469e97',G:'ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036',V:'1352b756f0f0310c00d21bfc3bfe194b5a347d291b699db78b5c85fa6e636a4d',SRC:'fb6198d0392e70a23a2d9ed05c0d432d4466de4ba75cc96762e3b4e45a204c40'}
BACKUPS={p:p.with_name(p.name+'.bak-s2-chp1-old-church-groups-20261015') for p in (C,M,S)}

def h(b): return hashlib.sha256(b).hexdigest()
def pc(b):
 r=csv.DictReader(io.StringIO(b.decode('utf-8-sig'),newline='')); return list(r.fieldnames or []),list(r)
def cr(headers,row):
 b=io.StringIO(newline=''); csv.DictWriter(b,fieldnames=headers,lineterminator='\n',extrasaction='ignore').writerow(row); return b.getvalue().encode()
def add(b,x): return b+(b'' if b.endswith((b'\n',b'\r')) else b'\n')+x

def build():
 if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!='c65900801de1cb3af9089345250774161d67f5c9': raise SystemExit('HEAD changed')
 for p,d in EXPECTED.items():
  if h(p.read_bytes())!=d: raise SystemExit(f'hash changed: {p.relative_to(ROOT)}')
 cb,mb,sb=C.read_bytes(),M.read_bytes(),S.read_bytes(); ch,cs=pc(cb); mh,ms=pc(mb)
 if len(cs)!=12250 or len(ms)!=26438: raise SystemExit('table counts changed')
 if {'cand-12273','cand-12274'} & {r['candidate_id'] for r in cs} or {'m-chp1-seci-best-modern-paintings-group','m-chp1-seci-oldest-churches-group'} & {r['mention_id'] for r in ms}: raise SystemExit('new ID already exists')
 seg=next((json.loads(x) for x in G.read_text(encoding='utf-8-sig').splitlines() if x and json.loads(x)['segment_id']==SEG),None)
 if not seg or h(SRC.read_bytes())!=seg['asset_sha256']: raise SystemExit('S0 asset/segment mismatch')
 lines=SRC.read_text(encoding='utf-8-sig').splitlines(); text='\n'.join(lines[int(seg['line_start'])-1:int(seg['line_end'])])
 if h(text.encode())!=seg['sha256']: raise SystemExit('S0 segment hash mismatch')
 cov=next((r for r in csv.DictReader(V.open(encoding='utf-8-sig',newline='')) if r['segment_id']==SEG),None)
 if not cov or cov.get('disposition')!='reviewed' or cov.get('migration_status')!='complete': raise SystemExit('S2 coverage changed')
 phrases=[('most of the best modern paintings','m-chp1-seci-best-modern-paintings-group','cand-12273'),('oldest churches','m-chp1-seci-oldest-churches-group','cand-12274')]
 new_mentions=[]
 for surface,mid,cid in phrases:
  if text.count(surface)!=1: raise SystemExit(f'source phrase mismatch: {surface}')
  start=text.index(surface); end=start+len(surface)
  if any(r['segment_id']==SEG and start<int(r['end_char']) and end>int(r['start_char']) for r in ms): raise SystemExit(f'mention overlap: {surface}')
  new_mentions.append({'mention_id':mid,'segment_id':SEG,'candidate_id':cid,'surface_form':surface,'start_char':str(start),'end_char':str(end),'note':'Source-defined, unenumerated group; Haskell presents this as a hypothetical observation around 1620.'})
 ss=sb.splitlines(keepends=True); idx=None; row=None
 for i,line in enumerate(ss):
  if line.strip():
   x=json.loads(line)
   if x.get('statement_id')==ST: idx,row=i,x; break
 if row is None or row.get('segment_id')!=SEG or row.get('subject_candidate_id') not in (None,'') or row.get('object_candidate_id') not in (None,''): raise SystemExit('statement changed')
 q=row.get('qualifiers',{})
 if q.get('relation_candidate') is not True or q.get('source_line_start')!=150: raise SystemExit('statement classification/source anchor changed')
 candidates=[
  {'candidate_id':'cand-12273','index_entry_id':'','canonical_name':'Most highly regarded modern paintings in Rome around 1620 (source-defined work group)','index_page_range':'','suggested_type':'work','status':'open','index_source_file':'','sub_entry':'','detail':'Haskell conjectures that a well-informed traveler around 1620 would have found most of Rome’s best modern paintings in the oldest churches. The paintings are not named or enumerated; the group boundary follows the source’s comparative wording.','exclude_reason':'','candidate_origin':'body-mention','candidate_source_ref':f'{SEG}#L150'},
  {'candidate_id':'cand-12274','index_entry_id':'','canonical_name':'Oldest churches in Rome around 1620 (source-defined place group)','index_page_range':'','suggested_type':'place','status':'open','index_source_file':'','sub_entry':'','detail':'The source refers collectively to Rome’s oldest churches as the locations of most of its best modern paintings around 1620. No church is identified by name in this claim; retain the group and hypothetical framing.','exclude_reason':'','candidate_origin':'body-mention','candidate_source_ref':f'{SEG}#L150'}]
 u=dict(row); u['subject_candidate_id']='cand-12273'; u['object_candidate_id']='cand-12274'; uq=dict(q); uq.pop('open_endpoint_reason',None); uq['relation_candidate_note']='The unnamed paintings and oldest churches are represented as source-defined work and place groups. Rome remains the contextual place; Haskell frames the claim as a hypothetical observation around 1620, not an inventory.'; u['qualifiers']=uq
 for x in candidates: cb=add(cb,cr(ch,x))
 for x in new_mentions: mb=add(mb,cr(mh,x))
 ending=b'\r\n' if ss[idx].endswith(b'\r\n') else b'\n'; ss[idx]=json.dumps(u,ensure_ascii=False,separators=(',',':')).encode()+ending; sb=b''.join(ss)
 _,c2=pc(cb); _,m2=pc(mb); s2=[json.loads(x) for x in sb.splitlines() if x.strip()]
 if len(c2)!=12252 or len(m2)!=26440 or len(s2)!=15111: raise SystemExit('projected counts mismatch')
 return {C:cb,M:mb,S:sb}

def apply(updates):
 if any(p.exists() for p in BACKUPS.values()): raise SystemExit('recovery backup exists')
 for p,d in EXPECTED.items():
  if h(p.read_bytes())!=d: raise SystemExit(f'file changed after preview: {p}')
 for p,b in BACKUPS.items(): shutil.copy2(p,b)
 temps={}; done=[]
 try:
  for p,data in updates.items():
   with tempfile.NamedTemporaryFile('wb',dir=p.parent,delete=False) as f: t=Path(f.name); f.write(data); f.flush(); os.fsync(f.fileno())
   temps[p]=t
  for p,t in temps.items(): os.replace(t,p); done.append(p)
 except Exception:
  for p in reversed(done): shutil.copy2(BACKUPS[p],p)
  raise
 finally:
  for t in temps.values():
   if t.exists(): t.unlink()

def main():
 p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True); g.add_argument('--preview',action='store_true'); g.add_argument('--apply',action='store_true'); a=p.parse_args(); updates=build()
 print('st-chp1-l150-152-old-church-art: open endpoints -> cand-12273 paintings / cand-12274 churches; hypothetical framing retained')
 print('projected candidates=12252 mentions=26440 statements=15111')
 for f,b in updates.items(): print(f'{f.relative_to(ROOT)}: {h(f.read_bytes())} -> {h(b)}')
 if a.preview: print('preview only; no files or backups written'); return
 apply(updates); print('applied with recovery backups')
if __name__=='__main__': main()

from __future__ import annotations
import argparse, csv, difflib, io, json, re
from collections import defaultdict
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = 'patrons-and-painters-full-book-s2'
TABLES = ROOT / '04-knowledge' / 'tables'
ALIGNMENT = TABLES / 'alignment.csv'
CANDIDATES = TABLES / 'entity-candidates.csv'
MENTIONS = TABLES / 'mentions.csv'
MANIFEST = TABLES / 'ku-manifest.csv'
ACCEPTED = ROOT / '04-knowledge' / 'accepted.yml'
CARD_REL = '04-knowledge/units/institutions/spain-polity.md'
CARD = ROOT / CARD_REL
PROCESS = ROOT / '03-processing' / TASK / 'process' / 'knowledge.md'
RESULT = ROOT / '04-knowledge' / 'results' / f'{TASK}.md'
KU_ID = 'units/institutions/spain-polity'
GROUP = 'sg3-institution-spain-polity'
DATE = '2026-10-17'
S3_ANCHOR = 's3-spain-polity-crosschapter-20261017'
S4_ANCHOR = 's4-spain-polity-registration-20261017'
CITATION = 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)'

SOURCES = [
 ('第2章；印刷页28；Markdown L4–7', 'Haskell称对 Spain 的战争威胁将牵涉 Italy；不推定战争已经发生。', 'threatened war with Spain', '02_CHP-2_sec_iv.md', 'line 4; print p.28'),
 ('第3章；印刷页73；Markdown L104', 'Haskell称 Cardinal Ludovisi 曾为 Spain 的利益行事。', 'had acted in the interests of Spain', '03_CHP-3_sec_ii.md', 'line 104; print p.73'),
 ('第5章；印刷页136；Markdown L43', 'Haskell称 Cerquozzi 的事业与 Spain 及其在 Rome 的支持者密切相关。', 'career was closely linked to Spain', '05_CHP-5_sec_iii.md', 'line 43; print p.136'),
 ('第5章；印刷页137；Markdown L71–73', 'Haskell称 Cerquozzi 的重要赞助人处于 Spanish sphere of influence，并列举 Spanish affiliations / cause 语境。', 'within the Spanish sphere of influence', '05_CHP-5_sec_iii.md', 'lines 71–73; print p.137'),
 ('第7章；印刷页189；Markdown L256–257', 'Haskell提到 France 与 Spain 之间的 hostilities，并称 Spain 仍关注意大利画家及其作品。', 'Spain however retained a welcome interest in Italian painters and their works', '07_CHP-7_sec_i.md', 'lines 256–257; print p.189'),
 ('第8章；印刷页204；Markdown L20–21', 'Haskell将 Spain 的衰落列为十八世纪初影响意大利城市文化地位的背景之一。', 'the decline of Spain', '08_CHP-8_sec_i.md', 'lines 20–21; print p.204'),
 ('第8章；印刷页209；Markdown L63–65', 'Haskell称 Antonio Ruffo 在 Spanish rule 下参与 Messina 有限的政治活动。', 'under Spanish rule', '08_CHP-8_sec_i.md', 'lines 63–65; print p.209'),
 ('第9章；印刷页246；Markdown L24', 'Haskell称威尼斯政府促使 Tiepolo 前往 Madrid 是对 Spain 的绥靖姿态。', 'a gesture of appeasement towards Spain', '09_CHP-9_intro.md', 'line 24; print p.246'),
 ('第10章；印刷页276；Markdown L7–8', 'Haskell把 later Spain 列为与 Venice 有某种相近政体的国家之一。', 'notably Southern Germany and, later, Spain', '10_CHP-10_intro.md', 'lines 7–8; print p.276'),
]

def read(path): return path.read_text(encoding='utf-8-sig')
def write(path, text):
    old = path.read_bytes() if path.exists() else b''
    bom = b'\xef\xbb\xbf' if old.startswith(b'\xef\xbb\xbf') else b''
    path.write_bytes(bom + text.encode('utf-8'))
def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)
def csv_text(fields, rows):
    out = io.StringIO(newline='')
    w = csv.DictWriter(out, fieldnames=fields, lineterminator='\n')
    w.writeheader(); w.writerows(rows)
    return out.getvalue()
def show_diff(label, old, new):
    print(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='a/'+label, tofile='b/'+label)), end='')
def group_of(row):
    m = re.search(r'group=([^;]+)', row.get('resolution_note',''))
    return m.group(1) if m else 'candidate:'+row['candidate_id']
def update_alignment(rows, cid, decision, ku_id, group, note):
    found = [r for r in rows if r.get('candidate_id') == cid and not r.get('external_source')]
    if len(found) != 1: raise ValueError(f'{cid}: expected one candidate alignment, found {len(found)}')
    r = found[0]
    prior = r.get('resolution_note','')
    r['decision'] = decision
    r['ku_id'] = ku_id
    r['process_ref'] = 'S3-S4-full-book-2026-10-17'
    r['resolution_note'] = note + '; prior S3 resolution retained: ' + prior
def update_mention(rows, mid, cid, note):
    found = [r for r in rows if r.get('mention_id') == mid]
    if len(found) != 1: raise ValueError(f'{mid}: expected one mention, found {len(found)}')
    found[0]['candidate_id'] = cid
    found[0]['note'] = note
def add_accepted(text):
    lines = text.splitlines()
    target = '- ' + CARD_REL
    if target in lines: raise ValueError('accepted.yml already contains card')
    end = next((i for i,line in enumerate(lines) if line.startswith('claims:')), len(lines))
    entries = [(i,line[2:]) for i,line in enumerate(lines[:end]) if line.startswith('- 04-knowledge/units/')]
    at = next((i for i,path in entries if path > CARD_REL), end)
    lines.insert(at, target)
    return '\n'.join(lines) + '\n'
def make_card():
    sources = []
    for location,summary,quote,filename,span in SOURCES:
        source_file = '02-sources/02-Markdown/' + filename
        sources.append({'citation': CITATION, 'location': location, 'sentence_summary': summary,
          'original_quotes': [{'source_span': span, 'text': quote}],
          'evidence_ref': {'doc_id':'patrons-and-painters','source_file':source_file,'source_span':span}})
    front = {'title':'西班牙政治实体（Spain as a polity）','name_en':'Spain as a polity','type':'institution',
      'evidence_status':'source_backed','sources':sources,'created':DATE,'updated':DATE,
      'process_ref':f'03-processing/{TASK}/process/knowledge.md#{S4_ANCHOR}'}
    fm = yaml.safe_dump(front, allow_unicode=True, sort_keys=False, width=1000)
    refs = [
      '[S1：第2章，印刷页28](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md#L4)',
      '[S2：第3章，印刷页73](../../../02-sources/02-Markdown/03_CHP-3_sec_ii.md#L104)',
      '[S3：第5章，印刷页136](../../../02-sources/02-Markdown/05_CHP-5_sec_iii.md#L43)',
      '[S4：第5章，印刷页137](../../../02-sources/02-Markdown/05_CHP-5_sec_iii.md#L71)',
      '[S5：第7章，印刷页189](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md#L256)',
      '[S6：第8章，印刷页204](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md#L20)',
      '[S7：第8章，印刷页209](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md#L63)',
      '[S8：第9章，印刷页246](../../../02-sources/02-Markdown/09_CHP-9_intro.md#L24)',
      '[S9：第10章，印刷页276](../../../02-sources/02-Markdown/10_CHP-10_intro.md#L7)']
    ref_text = '；'.join(refs)
    body = f'''## 内容

### 描述

**中文：** 本卡记录 Haskell 跨章叙述中作为国家／政治实体出现的 Spain。第2章把 Spain 放在战争威胁语境中；第3章称 Ludovisi 为 Spain 的利益行事；第5章把 Cerquozzi 的事业与 Spain 及其在 Rome 的支持者联系起来；第7章称 Spain 仍关注意大利画家及其作品；第8章提及 Spain 的衰落与 Naples 的 Spanish rule；第9章把威尼斯政府促使 Tiepolo 前往 Madrid 称为对 Spain 的绥靖；第10章又把 Spain 列为与 Venice 政体有相似之处的国家。各章指向同一政治实体，同时保留原文角色与限定。第2章的战争威胁不表示战事已经发生。{ref_text}

**English:** This unit records Spain as a state or political entity in Haskell’s cross-chapter account. Chapter 2 places Spain in a threatened-war context; Chapter 3 says Ludovisi acted in Spain’s interests; Chapter 5 links Cerquozzi’s career with Spain and its supporters in Rome; Chapter 7 says Spain retained an interest in Italian painters and their works; Chapter 8 refers to Spain’s decline and Spanish rule in Naples; Chapter 9 calls the Venetian government’s mission sending Tiepolo to Madrid an act of appeasement towards Spain; and Chapter 10 lists Spain among countries with regimes somewhat similar to Venice. These passages refer to the same political entity while retaining each source context and qualification. The threatened war in Chapter 2 does not establish that hostilities occurred. {ref_text}

### 书内指称与范围

| 语境（中文） | Context (English) | 证据 / Evidence |
|---|---|---|
| 机构性质：Haskell 所称的国家／政治实体 Spain；本卡不补定各时期的边界、政体沿革或法律制度。 | Institutional nature: the state or political entity called Spain by Haskell; this unit does not supply period borders, constitutional history, or legal institutions. | {refs[0]}（S1）；{refs[7]}（S8）；{refs[8]}（S9） |
| 跨章称谓：war with Spain、interests of Spain、Spain and her supporters、Spain’s interest in Italian painters、Spanish rule、appeasement towards Spain 等措辞按各自语境指向同一政治实体。 | Cross-chapter wording about war, interests, supporters, painters, Spanish rule, and appeasement refers to the same political entity in the respective source contexts. | {refs[0]}（S1）；{refs[1]}（S2）；{refs[2]}（S3）；{refs[4]}（S5）；{refs[6]}（S7）；{refs[7]}（S8） |
| 身份边界：地理地点 Spain 单独归入 place；Spanish Crown、Spanish monarchy、Spanish Empire 保持不同候选；未具名 Spaniards 与意大利境内未具名 Spanish political power 不自动等同于 Spain。 | Identity boundary: geographic Spain is a separate place; the Spanish Crown, Spanish monarchy, and Spanish Empire remain distinct candidates; unnamed Spaniards and unnamed Spanish political power in Italy are not automatically equated with Spain. | {refs[2]}（S3）；{refs[3]}（S4）；{refs[6]}（S7）；{refs[8]}（S9） |

## 关系与证据

目前没有新增 S6 正式关系。相关书内关系候选仍按各自断言、方向和限定留待 S6 裁决；本卡登记身份不自动建立战争、统治、赞助、委托或外交关系。
'''
    return '---\n' + fm + '---\n\n' + body

def counts_for(alignment, candidates, manifest):
    types = {r['candidate_id']:(r.get('suggested_type') or 'untyped') for r in candidates}
    rows = [r for r in alignment if r.get('candidate_id') in types and not r.get('external_source')]
    grouped = defaultdict(list)
    by = defaultdict(lambda: defaultdict(int))
    for r in rows:
        typ = types[r['candidate_id']]
        by[typ][r['decision']] += 1
        if r['decision'] == 'new': grouped[(typ,group_of(r))].append(r)
    regg = regm = pendg = pendm = 0
    for (typ,g), members in grouped.items():
        registered = all(r.get('ku_id') for r in members)
        if registered:
            regg += 1; regm += len(members); by[typ]['registered_groups'] += 1; by[typ]['registered_members'] += len(members)
        else:
            pendg += 1; pendm += len(members); by[typ]['pending_groups'] += 1; by[typ]['pending_members'] += len(members)
    result = {'candidate_count':len(rows),'same':sum(r['decision']=='same' for r in rows),
      'new':sum(r['decision']=='new' for r in rows),'conflict':sum(r['decision']=='conflict' for r in rows),
      'excluded':sum(r['decision']=='excluded' for r in rows),'undecided':sum(r['decision']=='undecided' for r in rows),
      'new_groups':len(grouped),'registered_groups':regg,'registered_members':regm,
      'pending_groups':pendg,'pending_members':pendm,'ku_count':len(manifest)}
    return result, by

def replace_once(text, old, new):
    if text.count(old) != 1: raise ValueError('expected one exact statistics string: '+old[:120])
    return text.replace(old,new,1)
def update_summaries(result, knowledge, c, by):
    status_old = ('**当前状态：全书 S2 语义处理已完成，尚未独立语义验收；S3 已记录全部候选的现行决定与去向，冲突及待证对象仍未解决；S4 KU 登记处理中。** 12,407 个候选决定行中，same=1,892（指向1,040个既有 KU）、new=4,967（4,784个身份组）、conflict=8、excluded=100、undecided=5,440。S4 已登记707组、映射869条成员候选；尚待登记4,077组、4,098条映射。')
    status_new = (f'**当前状态：全书 S2 语义处理已完成，尚未独立语义验收；S3 已记录全部候选的现行决定与去向，冲突及待证对象仍未解决；S4 KU 登记处理中。** {c["candidate_count"]:,} 个候选决定行中，same={c["same"]:,}（指向1,040个既有 KU）、new={c["new"]:,}（{c["new_groups"]:,}个身份组）、conflict={c["conflict"]}、excluded={c["excluded"]:,}、undecided={c["undecided"]:,}。S4 已登记{c["registered_groups"]:,}组、映射{c["registered_members"]:,}条成员候选；尚待登记{c["pending_groups"]:,}组、{c["pending_members"]:,}条映射。')
    result = replace_once(result,status_old,status_new)
    result = replace_once(result,'| [KU 登记](../tables/ku-manifest.csv) | 1,726 KU；新组登记与待登记分类型统计见下表 |',f'| [KU 登记](../tables/ku-manifest.csv) | {c["ku_count"]:,} KU；新组登记与待登记分类型统计见下表 |')
    result = replace_once(result,'| same | 1,892 | 指向 1,040 个既有 KU |',f'| same | {c["same"]:,} | 指向 1,040 个既有 KU |')
    result = replace_once(result,'| new | 4,967 | 按 4,784 个当前身份组进入 S4；每组登记一个 KU |',f'| new | {c["new"]:,} | 按 {c["new_groups"]:,} 个当前身份组进入 S4；每组登记一个 KU |')
    result = replace_once(result,'| **合计** | **12,407** | 每个候选一条当前决定记录 |',f'| **合计** | **{c["candidate_count"]:,}** | 每个候选一条当前决定记录 |')
    knowledge = replace_once(knowledge,'| institution | 497 | 180 | 193 / 196 | 0 | 0 | 121 | 20 / 23 | 173 / 173 |',f'| institution | 497 | {by["institution"]["same"]} | {by["institution"]["registered_groups"]+by["institution"]["pending_groups"]} / {by["institution"]["new"]} | 0 | 0 | 121 | {by["institution"]["registered_groups"]} / {by["institution"]["registered_members"]} | {by["institution"]["pending_groups"]} / {by["institution"]["pending_members"]} |')
    knowledge = replace_once(knowledge,'| place | 1,109 | 225 | 560 / 568 | 0 | 0 | 316 | 40 / 48 | 520 / 520 |',f'| place | 1,109 | {by["place"]["same"]} | {by["place"]["registered_groups"]+by["place"]["pending_groups"]} / {by["place"]["new"]} | 0 | 0 | 316 | {by["place"]["registered_groups"]} / {by["place"]["registered_members"]} | {by["place"]["pending_groups"]} / {by["place"]["pending_members"]} |')
    knowledge = replace_once(knowledge,'| **合计** | **12,407** | **1,892** | **4,784 / 4,967** | **8** | **100** | **5,440** | **707 / 869** | **4,077 / 4,098** |',f'| **合计** | **{c["candidate_count"]:,}** | **{c["same"]:,}** | **{c["new_groups"]:,} / {c["new"]:,}** | **{c["conflict"]}** | **{c["excluded"]:,}** | **{c["undecided"]:,}** | **{c["registered_groups"]:,} / {c["registered_members"]:,}** | **{c["pending_groups"]:,} / {c["pending_members"]:,}** |')
    summary_old = ('5,441 项 `undecided` 各自保留对象、版本、身份、类型或来源锚点不足的理由与后续去向；其中 622 项仍为未分类类型，等待类型证据，不强塞入现有类。所有 12,407 个候选各有且仅有一条 `external_source` 为空的当前决定；235 条外部身份记录另行保留。same 的 1,886 条候选指向 1,040 个既有 KU；4,972 条 new 候选组成 4,789 个类型内身份组。S4 按整组登记，当前没有组内部分登记或类型不符映射；未登记组保留在 S4 待办中。此处收口的是 S3 决定与可追溯去向，冲突和待证身份问题本身未解决。')
    summary_new = (f'{c["undecided"]:,} 项 `undecided` 各自保留对象、版本、身份、类型或来源锚点不足的理由与后续去向；其中 622 项仍为未分类类型，等待类型证据，不强塞入现有类。所有 {c["candidate_count"]:,} 个候选各有且仅有一条 `external_source` 为空的当前决定；235 条外部身份记录另行保留。same 的 {c["same"]:,} 条候选指向 1,040 个既有 KU；new 候选组成 {c["new_groups"]:,} 个类型内身份组，共 {c["new"]:,} 条映射。S4 按整组登记，当前没有组内部分登记或类型不符映射；未登记组保留在 S4 待办中。此处收口的是 S3 决定与可追溯去向，冲突和待证身份问题本身未解决。')
    knowledge = replace_once(knowledge,summary_old,summary_new)
    return result,knowledge

def main():
    ap=argparse.ArgumentParser()
    mode=ap.add_mutually_exclusive_group(required=True); mode.add_argument('--dry-run',action='store_true'); mode.add_argument('--apply',action='store_true')
    args=ap.parse_args()
    for path in (CARD,):
        if path.exists(): raise ValueError('card already exists: '+str(path))
    if S3_ANCHOR in read(PROCESS) or S4_ANCHOR in read(PROCESS): raise ValueError('process anchors already exist')
    if CARD_REL in read(ACCEPTED): raise ValueError('accepted.yml already contains card')
    af,ar=read_csv(ALIGNMENT); mf,mr=read_csv(MENTIONS); kf,kr=read_csv(MANIFEST); _,cr=read_csv(CANDIDATES)
    cby={r['candidate_id']:r for r in cr}
    for cid,typ in {'cand-4591':'institution','cand-8123':'institution','cand-8833':'institution','cand-10409':'place'}.items():
        if cid not in cby or cby[cid].get('suggested_type')!=typ: raise ValueError('candidate type mismatch: '+cid)
    place_rows=[r for r in ar if r.get('candidate_id') in {'cand-5120','cand-5667'} and not r.get('external_source')]
    if len(place_rows)!=2 or any(r.get('decision')!='same' or r.get('ku_id')!='units/places/spain' for r in place_rows): raise ValueError('existing place alignments changed')
    if any(r.get('ku_id')==KU_ID for r in kr): raise ValueError('manifest already has KU')
    update_alignment(ar,'cand-4591','new',KU_ID,GROUP,'group='+GROUP+'; source_ref=chp-2:02_CHP-2_sec_iv:l3-4#L4; cross_chapter_refs=chapters 2,3,5,7,8,9,10; S3: same polity named as Spain across political contexts, not the geographic place; the threatened-war sentence does not assert hostilities; keep Crown, monarchy, Empire and unnamed Spaniards separate')
    update_alignment(ar,'cand-8123','new',KU_ID,GROUP,'group='+GROUP+'; source_ref=chp-9:09_CHP-9_intro:l18-25#L24; S3: Spain as political object of appeasement is same polity as cand-4591 and cand-8833; no particular official or negotiation is inferred')
    update_alignment(ar,'cand-8833','new',KU_ID,GROUP,'group='+GROUP+'; source_ref=chp-10:10_CHP-10_intro:l3-13#L7; S3: country Spain in similar-regime comparison is same polity as cand-4591 and cand-8123; no particular monarch, court or commission is inferred')
    update_alignment(ar,'cand-10409','same','units/places/spain','sg3-place-cand-5120','group=sg3-place-cand-5120; source_ref=chp-14:14_CHP-14_intro:l126-137#L131; S3 correction: Tiepolo destination in chp-14 p.359 and presence in chp-15 p.361 are the geographic Spain already represented by units/places/spain; no city, employer or date is inferred')
    update_mention(mr,'m-chp2-seciv-l31-43-0046','cand-5120',"Destination of Francesco's departure after giving the palace to Taddeo; geographic Spain, not the political entity. S3 correction from cand-4591 after checking the source sentence.")
    update_mention(mr,'m-chp5-sec-iii-l36-43-039','cand-4591',"Spain in the statement that Cerquozzi's career was linked to Spain and her supporters in Rome; political-entity context, not a travel destination. S3 correction from geographic cand-5120 after checking the source sentence.")
    row={'ku_id':KU_ID,'type':'institution','canonical_name':'西班牙政治实体（Spain as a polity）','name_en':'Spain as a polity','source_task':TASK,'card_path':CARD_REL}
    pos=next((i for i,r in enumerate(kr) if r['ku_id']>KU_ID),len(kr)); kr.insert(pos,row)
    accepted_new=add_accepted(read(ACCEPTED)); card_new=make_card()
    c,by=counts_for(ar,cr,kr)
    expected=(1893,4966,4781,708,872,4073,4094,1727)
    actual=(c['same'],c['new'],c['new_groups'],c['registered_groups'],c['registered_members'],c['pending_groups'],c['pending_members'],c['ku_count'])
    if actual!=expected: raise ValueError(f'count mismatch expected={expected} actual={actual}')
    result,knowledge=update_summaries(read(RESULT),read(PROCESS),c,by)
    process_entry=f'''

<a id="{S3_ANCHOR}"></a>

### S3 institution/place：Spain 跨章政治实体与地理地点裁决（{DATE}）

- cand-4591（第2章 p.28）、cand-8123（第9章 p.246）、cand-8833（第10章 p.276）由三个单候选 new 组并为一个机构身份组 {GROUP}。第2、3、5、7、8、9、10章反复以 Spain / Spanish rule 指同一国家政治实体；战争威胁、Ludovisi为其利益行事、Spain及其在Rome的支持者、对意大利画家的兴趣、Naples的Spanish rule、对Spain的绥靖及相似政体语境分别保留为原书表述，不推导政体沿革、精确边界或未记载外交事实。原单候选组名与裁决说明逐条留在alignment历史注释中。
- 地理组复核：cand-10409（第14章 p.359，并见第15章 p.361）从 new 改为 same → units/places/spain；其含义是 Tiepolo 前往／身处 Spain 这一地理地点，与 cand-5120 及已复用同一 place KU 的 cand-5667 相同。旧单候选组与原决定理由留在alignment历史注释中。
- 修正两条提及映射：m-chp2-seciv-l31-43-0046 的 Spain 是 Francesco 离开的目的地，改映射 cand-5120；m-chp5-sec-iii-l36-43-039 的 Spain 与其在 Rome 的支持者相连，是政治实体语境，改映射 cand-4591。未改变相应书内断言或候选关系。
- 边界：cand-5511 Spanish Crown、cand-7478 Spanish Empire、cand-9147 Spanish monarchy 与 cand-4592 threatened-war event 仍是各自不同的 new 组；cand-6622 “Spanish political power in Italy”继续 undecided，因“the Spaniards / Spanish cause”不足以单独判定为国家、军政群体或具体机构。未具名 Spanish collective、Spanish Embassy 与有关人物／事件候选仍保持各自现行决定；未把这些对象并入本卡。

<a id="{S4_ANCHOR}"></a>

### S4 institution：Spain 政治实体身份组登记（{DATE}）

cand-4591、cand-8123、cand-8833 均映射至[西班牙政治实体（Spain as a polity）](../../../04-knowledge/units/institutions/spain-polity.md)（{KU_ID}）。卡片只记录 Haskell 的跨章政治实体指称；地理地点 Spain 仍指向既有 units/places/spain，未使用外部身份标识或声称外部验证。

直接关系端点候选 st-chp4-sec-ii-p117-spanish-french-quarrels、st-chp4-sec-ii-p117-spanish-backing、st-chp6-p156-lorenzo-connections-with-spain-grow-closer、st-chp7-p189-i28、st-chp8-p203-naples-families-and-school 留待 S6；本轮没有新增 relations.csv 正式边。其余含 Spain 语境的 statement 仍按各自已有端点、语气与候选关系状态处理，不因本次身份登记自动升级。

- 当前S3统计：same={c['same']:,}，new={c['new']:,}／{c['new_groups']:,}组，conflict={c['conflict']}，excluded={c['excluded']:,}，undecided={c['undecided']:,}。
- S4 累计：已登记{c['registered_groups']:,}组／{c['registered_members']:,}条成员映射；待登记{c['pending_groups']:,}组／{c['pending_members']:,}条映射；KU={c['ku_count']:,}。机构类型为 {by['institution']['registered_groups']}/{by['institution']['registered_members']} 已登记、{by['institution']['pending_groups']}/{by['institution']['pending_members']} 待登记；地点类型为 {by['place']['registered_groups']}/{by['place']['registered_members']} 已登记、{by['place']['pending_groups']}/{by['place']['pending_members']} 待登记。
'''
    if S3_ANCHOR in knowledge or S4_ANCHOR in knowledge: raise ValueError('process anchors exist')
    knowledge_new=knowledge+process_entry
    result_entry=f'''

### S3/S4 institution/place：Spain 跨章政治实体与地点身份裁决（{DATE}）

- cand-4591、cand-8123、cand-8833 合并为一个新的 Spain 政治实体身份组并登记至[西班牙政治实体 KU](../units/institutions/spain-polity.md)；cand-10409 改为 same，复用既有 units/places/spain。
- 两条提及映射已校正：第2章 p.46 的目的地映射到地理 Spain；第5章 p.136 的 Spain 及其在 Rome 的支持者语境映射到政治实体。
- Spanish Crown、Spanish Empire、Spanish monarchy、未具名 Spaniards／Spanish political power 及 threatened-war event 保持各自新建或待证去向，不与本卡混同。直接 S2 关系候选仍待 S6，无新增正式关系或外部身份记录。
- 更新后 S3：same={c['same']:,}；new={c['new']:,}/{c['new_groups']:,}组；conflict={c['conflict']}；excluded={c['excluded']:,}；undecided={c['undecided']:,}。S4 已登记 {c['registered_groups']:,}组/{c['registered_members']:,}条映射，待登记 {c['pending_groups']:,}组/{c['pending_members']:,}条映射；KU={c['ku_count']:,}。
'''
    if '### S3/S4 institution/place：Spain 跨章政治实体与地点身份裁决' in result: raise ValueError('result entry exists')
    result_new=result+result_entry
    changes={
      ALIGNMENT:(read(ALIGNMENT),csv_text(af,ar)), MENTIONS:(read(MENTIONS),csv_text(mf,mr)),
      MANIFEST:(read(MANIFEST),csv_text(kf,kr)), ACCEPTED:(read(ACCEPTED),accepted_new),
      CARD:('',card_new), PROCESS:(read(PROCESS),knowledge_new), RESULT:(read(RESULT),result_new)}
    for p,(old,new) in changes.items():
        if old!=new: show_diff(p.relative_to(ROOT).as_posix(),old,new)
    print(json.dumps({'mode':'apply' if args.apply else 'dry-run','candidate_decisions':{k:c[k] for k in ['same','new','conflict','excluded','undecided']},'new_groups':c['new_groups'],'registered_groups':c['registered_groups'],'registered_members':c['registered_members'],'pending_groups':c['pending_groups'],'pending_members':c['pending_members'],'ku_count':c['ku_count'],'files_to_write':sum(old!=new for old,new in changes.values())},ensure_ascii=False))
    if args.apply:
        for p,(old,new) in changes.items():
            if old!=new: write(p,new)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
#!/usr/bin/env python3
"""Apply the source-read B577 decisions; default is an evidence/diff dry-run."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from adjudicate_s2_current_review_b576_order_1960_2059_20261103 import (
    atomic_write, canonical_hash, csv_bytes, jsonl_bytes, read_csv, read_jsonl,
    read_text, sha, text_bytes,
)

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge/tables'
PROCESS = Path(__file__).resolve().parent
RECOVERY = ROOT / '06-runtime/recovery/s2-b577-order-2060-2159'
PLAN = RECOVERY / 'review-plan.json'
STAGE = '2026-11-03-s2-current-review-b577-order-2060-2159'
KNOWLEDGE = 's3-s6-camassei-work-types-guido-career-20261103'
KREF = '03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#' + KNOWLEDGE
SREF = 'stages.md#' + STAGE
BATCH = 'S2-B577-CH2-2060-2159'
SOURCE = ROOT / '02-sources/02-Markdown/02_CHP-2_sec_iv.md'
PDF = ROOT / '02-sources/01-book/CHP-2.pdf'
HISTORY = PROCESS / 's2-history-9622-review-events.csv'
EXPECTED_SOURCE = '9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf'
EXPECTED_PDF = '317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e'
EXPECTED_HISTORY = '75ab12df478a816035929353565b0301d55959c6bb13d9b511af072c4c931c89'

# Explicit claim-level selections after reading printed pp.48-51, not all segment mentions.
MAPPINGS = {
    2061:[296,1479,407,240], 2064:[4651,239], 2065:[4651,1017],
    2068:[290,4655], 2069:[290,4654,1017,4223], 2070:[290,293], 2071:[1017,4223],
    2072:[291,4655], 2073:[291,4654,1017,4223], 2074:[291,293],
    2075:[293,4650,1017], 2076:[291,4654],
    2081:[291,12301,4652,4653], 2082:[290,1017,4490,12303],
    2083:[290,4656,12303,1017,4490], 2087:[961,291,198], 2088:[958,961,291],
    2089:[291,398,2088], 2093:[398,12305], 2094:[4651,398,291],
    2095:[290,398], 2096:[291,767], 2097:[291,959,961],
    2098:[209,767,291], 2099:[209,767,4657,4492,4491],
    2100:[767,209,4657,4492,4491], 2101:[767,291],
    2102:[290,2350,398], 2103:[4664,2350], 2104:[4664,291,2350,398],
    2105:[2350,4662,398], 2106:[2350,4663,398], 2107:[2350,4661,398],
    2108:[4651,12304,4288], 2109:[290,1017,394],
    2110:[290,4658,11478,394], 2111:[290,4660,1455],
    2112:[239,290,209], 2113:[398,2542,1135,394],
    2114:[1856,291,2542,1135,398], 2115:[4651,4659,398], 2116:[1588,4659,398],
    2117:[484,932], 2118:[4651,484,398], 2119:[105,484,4665],
    2120:[4651,484,198], 2121:[484,4666,398], 2122:[4666],
    2123:[484,4452], 2124:[484], 2125:[484,485,240], 2126:[484,486,240],
    2127:[4667,486,209], 2128:[485,486], 2129:[485,11888],
    2131:[486,209,4189], 2132:[486,198], 2133:[485,486,11889],
    2134:[199,2318,713], 2135:[2318,4003,4668,240],
    2136:[4672,4003], 2137:[4003,4672,4669], 2138:[4003,4672,4673],
    2139:[4003,4672,2318], 2140:[4003,4672,198,4654],
    2141:[4003,4672], 2142:[4003,4670,2098,4671],
    2143:[4674,4669,4003,4672,198], 2144:[4003,4672], 2145:[4669,4672],
    2146:[4676,198], 2147:[4676,4692,4003], 2148:[4003],
    2150:[4003], 2151:[4677,4692,4003], 2152:[4677,198],
    2153:[4672,4681,4682,4683,4684], 2154:[2318],
    2155:[2318,4003], 2156:[2318,4003], 2157:[2318,4003],
    2158:[4675,4672], 2159:[4675,198],
}
PENDING = {
    2065:'正文称来自Ferrara，注1说明Bologna起源与Ferrara支系；保留两层出处，不裁成唯一家族起源。',
    2071:'Ferrara是城市地点；政治归属转移的行动主体／政体端点未确定，不能把城市当作政体。',
    2075:'支持对象是未单独识别的继承主张；Cesare只是主张人，不是被支持主张这一宾语。',
    2083:'特设外交职位缺正式名称，现有term类型尚待裁决；不把职位等同任职人或外交事件。',
    2093:'其他装饰者为未具名群体，成员与类型边界仍待决。',
    2108:'历任教皇为未具名集合，购画与聘用两类行为分别保留，集合身份仍待决。',
    2110:'Dosso Dossis指作品而非购入画家；具体作品组及Ducal collection范围未明。',
    2127:'Apollo是画中神话形象而非Urban VIII本人，现有person类型边界未决；只保留图像比附。',
    2131:'his只指poet-Pope，ancestors是未具名祖先群体；不能把教皇本人当作祖先或画中Heroes。',
    2134:'St Peter’s明确为场所线索，泛称Churches索引候选的具体空间身份仍留S3。',
    2138:'Roman theologians是未具名选择者群体，不指定个人，也不并入artist’s advisers。',
    2143:'artist’s advisers的群体身份与类型未定，且被转化对象是经文解释，不是作品被物理改动。',
}
NOTES = {
    2061:'Bernini接替Maderno、Borromini协助及原方案延续分别保留；复用已纠正的Maderno人物身份。',
    2064:'ready to advise仅为可咨询状态；未指明的教皇联系留作叙述，不声称实际咨询发生。',
    2076:'成功的教会生涯是作者概述，不能直接推出member_of；rel-2456降为pending。',
    2081:'外交使节活动影响品味／政治同情是Haskell的因果解释，保留为非正式边断言。',
    2087:'肖像形容和时代比较保留Haskell评价，不生成肖像—人物／家族的新事实关系。',
    2089:'relative because限定清苦程度而非解释清苦的成因；保留多年居住大宫殿的反衬。',
    2100:'保留作者对浪漫化处理及Urban perhaps hoped的推测，不提升为已证实的委托意图。',
    2101:'对Claude画风契合Guido趣味的作者解释，不是无条件品味关系。',
    2103:'信件责任者由Haskell叙述支持；不补日期、收信人或手稿档号，rel-2415范围不变。',
    2105:'Giovanni—Amphitrite场景创作关系；现有rel-2413范围不变。',
    2106:'Giovanni—Europa场景创作关系；现有rel-2414范围不变。',
    2107:'Giovanni—Proserpina场景创作关系；现有rel-2412范围不变。',
    2109:'deliberate trickery／despoiling保留为Haskell归责，不与1608年购画事实混写。',
    2113:'1611和1612保留为作品组的两个年份，不一一分配给Tassi和Gentileschi；Scipione为宫殿业主语境。',
    2114:'记录Haskell否定Passeri归属，不写成Guido委托这些壁画。',
    2115:'卖方Bentivoglio、买方Lante、资产palace三角色分开。',
    2116:'Mazarin为买方、Lante为前业主／出让方、palace为资产。',
    2117:'follower不证明亲授师生关系；保留Umbrian与作者风格归类。',
    2119:'Filippo推荐Camassei，受推荐者Marchese未具名，不擅认Taddeo。',
    2120:'Bentivoglio为推荐方、Camassei为被推荐画家、Barberini为接收方。',
    2125:'God creating the Angels是受派绘制的作品，不是Camassei本人；不推定授予人。',
    2126:'Parnassus是独立天顶画，不是Camassei本人或Parnassus概念。',
    2128:'两幅画共有的风格／接受描述，不建立两作品互为关系。',
    2129:'作品与divine sanction概念分开；图像解释保留Haskell主体和原文支持范围。',
    2133:'两幅已纠正作品与未具名后续装饰方案分开；不提前认同Cortona单幅画或Bracciolini程序。',
    2136:'未曾表现的主张指Divine Wisdom题材概念；不是宣称作品实体首次出现。',
    2137:'作品、智慧概念和Wisdom of Solomon文献分开；rel-2495范围不变，未读原典。',
    2139:'almost inconceivable是Haskell判断，不是否定Sacchi作者身份的既成事实。',
    2140:'保留未具名解释者及政治神学引文，不记为Barberini实际神授权力的正式事实。',
    2141:'work与term分开，既有rel-2497主题边范围不变。',
    2142:'保留作者与Raphael壁画的雄心比较，不制造两个作品组间的事实边。',
    2144:'p.50句子续至p.51，沿用continuation入口，不将女像、概念或太阳混同。',
    2145:'Haskell转述经文劝诫；rel-2496范围不变，未声称独立核对经文章节。',
    2151:'laurel—friezes与主画的局部语境分开，现有rel-2274范围不变。',
    2153:'Wisdom发令，Love与Fear为执行者，Lust与Wrath为受控激情；不配成一对一关系。',
    2155:'技法和色彩是作者视觉描述，不转成画家—作品事实边。',
    2156:'无同时代可比对象是Haskell比较评价，不是独立事实证明。',
    2157:'urgency、passion与sublimity保留作者批评语气，不泛化为人物客观属性。',
}
NONRELATION = {2064,2076,2081,2087,2089,2100,2101,2109,2113,2117,2136,2139,2140,2142,2155,2156,2157}


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def cid(n):
    return f'cand-{n:04d}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    require(sha(SOURCE.read_bytes()) == EXPECTED_SOURCE, 'Source version changed')
    require(sha(PDF.read_bytes()) == EXPECTED_PDF, 'PDF version changed')
    require(sha(HISTORY.read_bytes()) == EXPECTED_HISTORY, 'H9622 ledger changed')
    statements, st_raw, _, _ = read_jsonl(TABLES/'book-statements.jsonl')
    roster, rf, rr_raw, reol, rbom = read_csv(PROCESS/'s2-current-review-roster.csv')
    mentions, mf, mr_raw, meol, mbom = read_csv(TABLES/'mentions.csv')
    candidates, cf, cr_raw, ceol, cbom = read_csv(TABLES/'entity-candidates.csv')
    alignment, af, ar_raw, aeol, abom = read_csv(TABLES/'alignment.csv')
    relations, relf, rel_raw, releol, relbom = read_csv(TABLES/'relations.csv')
    backlog, bf, br_raw, beol, bbom = read_csv(TABLES/'candidate-backlog.csv')
    segments, _, _, _ = read_jsonl(TABLES/'segments.jsonl')
    sb = {s['statement_id']:s for s in statements}
    old_statements = copy.deepcopy(sb)
    rb = {r['statement_id']:r for r in roster}
    sg = {s['segment_id']:s for s in segments}
    cb = {c['candidate_id']:c for c in candidates}
    window = {int(r['current_order']):r for r in roster if 2060 <= int(r['current_order']) <= 2159}
    require(len(statements) == len(roster) == 15518 and len(mentions) == 27357, 'Batch baseline counts changed')
    require(len(window) == 100, 'Window is not 100 IDs')
    pending = {n for n,r in window.items() if r['current_review_status'] == 'reviewed_current_pending'}
    require(pending == set(MAPPINGS) and len(pending) == 83, 'Per-ID pending plan no longer matches input')
    require(set(PENDING) <= pending, 'Retained decisions not in pending window')
    source_lines = SOURCE.read_text(encoding='utf-8-sig').splitlines()
    segment_text = {sid:'\n'.join(source_lines[int(s['line_start'])-1:int(s['line_end'])])
                    for sid,s in sg.items() if s['source_file'] == SOURCE.relative_to(ROOT).as_posix()}
    def mention_groups():
        out = defaultdict(list)
        for m in mentions:
            out[m['segment_id']].append(m)
        return {key:sorted(value,key=lambda x:x['mention_id']) for key,value in out.items()}
    before_mentions = mention_groups()
    for row in window.values():
        sid = row['statement_id'];st = sb[sid];seg = sg[st['segment_id']]
        require(canonical_hash(st) == row['current_statement_sha256'], f'Stale statement {sid}')
        require(seg['sha256'] == row['segment_sha256'] and seg['asset_sha256'] == row['source_asset_sha256'], f'Stale source {sid}')
        mm = before_mentions.get(st['segment_id'],[])
        require(canonical_hash(mm) == row['current_segment_mentions_sha256'] and len(mm) == int(row['current_segment_mention_count']), f'Stale mentions {sid}')
    def at(n):
        return sb[window[n]['statement_id']]
    for n,cs in MAPPINGS.items():
        at(n)['qualifiers']['mentioned_candidate_ids'] = list(map(cid,cs))
        if n in NONRELATION:
            q = at(n)['qualifiers']
            q['relation_candidate'] = False
            q['relation_candidate_note'] = 'B577: source-attributed assessment/readiness/context, not an independently asserted formal relation. ' + NOTES[n]

    at(2064)['predicate'] = 'advisory_readiness_and_papal_connections_described'
    at(2064)['qualifiers']['qualification'] = 'Ready to advise records availability, not an actual consultation; the unnamed seventeenth-century popes remain a source-described group.'
    at(2065)['qualifiers']['qualification'] = 'Main text: came from Ferrara. Printed p.48 note 1 (Markdown L210): family originated in Bologna, while an important branch had long been settled in Ferrara. Do not flatten these statements into one origin or a proven branch identity.'
    at(2071)['subject_candidate_id'] = None
    at(2071)['qualifiers']['geographic_context_candidate_id'] = cid(1017)
    at(2071)['qualifiers']['open_endpoint_reason'] = 'The geographic city is not an identified political transferor or polity. Keep that institutional/political endpoint open.'
    at(2075)['object_candidate_id'] = None
    at(2075)['qualifiers']['claimant_candidate_id'] = cid(4650)
    at(2075)['qualifiers']['geographic_context_candidate_id'] = cid(1017)
    at(2075)['qualifiers']['open_endpoint_reason'] = 'The supported succession claim is not the person Cesare; no independently identified proposition endpoint is supplied.'
    at(2076)['object_candidate_id'] = None
    at(2076)['predicate'] = 'ecclesiastical_career_characterized_by_author'
    at(2076)['qualifiers']['institutional_context_candidate_id'] = cid(4654)
    at(2081)['object_candidate_id'] = None
    at(2081)['qualifiers']['causal_context_candidate_id'] = cid(12301)
    at(2081)['qualifiers']['qualification'] = 'Haskell attributes changes in tastes and political sympathies to the diplomatic missions; these effects are not an identified object endpoint.'
    at(2082)['qualifiers']['departure_place_candidate_id'] = cid(1017)
    at(2082)['qualifiers']['destination_place_candidate_id'] = cid(4490)
    at(2082)['qualifiers']['post_candidate_id'] = cid(12303)
    at(2089)['predicate'] = 'austerity_characterization_qualified_by_author'
    at(2089)['qualifiers']['claim'] = 'Haskell qualifies his description of Guido’s austerity as relative, since Guido lived for a number of years in the great Borghese palace on the Quirinal.'
    at(2089)['qualifiers']['qualification'] = 'The grand residence qualifies the extent of austerity; it is not given as the cause of an austere lifestyle. No exact residence dates are supplied.'
    at(2093)['qualifiers']['source_line_start'] = 66
    at(2093)['original_quote'] = 'the great Borghese palace on the Quirinal, decorated by Guido Reni, Tassi, Gentileschi and others'
    at(2094)['qualifiers']['seller_candidate_id'] = cid(4651)
    at(2094)['qualifiers']['transferred_property_candidate_id'] = cid(398)
    at(2097)['qualifiers']['included_work_candidate_ids'] = [cid(959),cid(961)]
    at(2098)['qualifiers']['work_scope'] = 'Two unnamed pictures of fanciful and genre scenes; this is an artist-commission report, not identity confirmation of individual extant versions.'
    at(2099)['qualifiers']['work_scope'] = 'Two further commissioned views; the named sites/properties are subjects, not the pictures themselves. Do not equate city, fortifications, country house and painting.'
    at(2100)['qualifiers']['qualification'] = 'Both the romantic/literal contrast and Urban perhaps hoped are Haskell’s interpretation; no direct statement of Urban’s intention is supplied.'
    at(2101)['qualifiers']['claim'] = 'Haskell interprets the appeal of this aspect of Claude’s painting to Cardinal Guido Bentivoglio in terms of Guido’s love of colour and poetry.'
    at(2109)['qualifiers']['text_layer'] = 'authorial evaluation of the reported removal of artworks'
    at(2110)['qualifiers']['artist_of_procured_works_candidate_id'] = cid(4658)
    at(2110)['qualifiers']['collection_context_candidate_id'] = cid(11478)
    at(2110)['qualifiers']['open_endpoint_reason'] = 'Dosso Dossis denotes paintings by Dosso Dossi, not a purchased person; the particular painting-group asset remains unidentified.'
    at(2111)['qualifiers']['qualification'] = 'Responsibility for decorating unspecified palaces, not architectural authorship, ownership or a named modern office; Gregory XV supplies the papal-period context.'
    at(2112)['qualifiers']['qualification'] = 'Taddeo turned to Enzo under Urban VIII; no separately specified commission or payment is inferred.'
    at(2113)['qualifiers']['qualification'] = 'The two years apply to the fresco group collectively; do not assign one year to each artist. Scipione is the palace owner at that period, not automatically the owner of every movable artwork.'
    at(2114)['qualifiers']['text_layer'] = 'Haskell’s rejection of Passeri’s patron attribution'
    at(2115)['qualifiers'].update(seller_candidate_id=cid(4651),buyer_candidate_id=cid(4659),transferred_property_candidate_id=cid(398))
    at(2116)['qualifiers'].update(seller_candidate_id=cid(4659),buyer_candidate_id=cid(1588),transferred_property_candidate_id=cid(398))
    at(2117)['qualifiers']['qualification'] = 'Follower is Haskell’s characterization; this wording does not establish personal instruction or a documented teacher-pupil relationship.'
    at(2118)['qualifiers']['residence_place_candidate_id'] = cid(398)
    at(2119)['qualifiers']['qualification'] = 'The Marchese is unnamed in this passage; do not infer Taddeo or another patron from adjacent narrative.'
    at(2120)['qualifiers'].update(recommending_family_candidate_id=cid(4651),recommended_artist_candidate_id=cid(484),recipient_candidate_id=cid(198))
    for n in [2125,2126]:
        at(n)['qualifiers']['qualification'] = 'Assigned ceiling-painting project in the Barberini palace; the commissioner is not identified. The title candidate is a work, not the artist; assignment does not alone prove completion.'
    at(2127)['qualifiers']['qualification'] = 'Apollo is a depicted mythological figure, not the historical pope. The person type of that figure remains unresolved; preserve the source’s iconographic identification only.'
    at(2131)['object_candidate_id'] = None
    at(2131)['qualifiers']['pope_context_candidate_id'] = cid(209)
    at(2131)['qualifiers']['open_endpoint_reason'] = 'The possessive his refers to the poet-Pope, while the unnamed ancestors and depicted Heroes are distinct groups; the Pope is not their substitute endpoint.'
    at(2133)['qualifiers']['qualification'] = 'Some themes are said to foreshadow an unnamed larger decorative scheme. Do not identify that group with Cortona’s individual fresco or Bracciolini’s programme merely from later context.'
    at(2136)['subject_candidate_id'] = cid(4672)
    at(2136)['qualifiers']['work_context_candidate_id'] = cid(4003)
    at(2138)['qualifiers']['open_endpoint_reason'] = 'No individual theologian or formal group is identified. This group is not automatically the artist’s advisers.'
    at(2140)['qualifiers']['explanation_author'] = 'unidentified in Haskell’s quoted explanation'
    at(2143)['object_candidate_id'] = cid(4669)
    at(2143)['qualifiers']['work_context_candidate_id'] = cid(4003)
    at(2143)['qualifiers']['open_endpoint_reason'] = 'The transformation concerns the interpretation of biblical text, not a physical alteration of the fresco; the advisers remain an unidentified group distinct from the Roman theologians.'
    at(2153)['object_candidate_id'] = None
    q = at(2153)['qualifiers']
    q.pop('other_personification_candidate_ids',None)
    q.update(ordering_personification_candidate_id=cid(4672),ordered_personification_candidate_ids=[cid(4681),cid(4682)],controlled_passion_candidate_ids=[cid(4683),cid(4684)])
    q['qualification'] = 'Wisdom orders Love and Fear collectively to control Lust and Wrath; the source does not pair one agent with one passion. No binary Wisdom-to-Love factual edge is created.'

    # Correct two exact index subentries; the creator and the depicted works are different objects.
    for n,title in [(485,'God creating the Angels'),(486,'Parnassus')]:
        c = cb[cid(n)]
        require(c['canonical_name'] == 'Camassei, Andrea' and c['sub_entry'] == title and c['suggested_type'] == 'person', 'Camassei candidate baseline changed')
        c['canonical_name'] = title
        c['suggested_type'] = 'work'
        c['detail'] = f'B577: printed p.50 explicitly distinguishes Andrea Camassei from the two ceiling frescoes {title!r} and the other named subject. The original index headword Camassei, Andrea and subentry are retained by index_entry_id/sub_entry; do not align the work to the creator.'
        c['candidate_source_ref'] = 'chp-2:02_CHP-2_sec_iv:l79-89#L83-84'
        alns = [a for a in alignment if a['candidate_id'] == cid(n)]
        require(len(alns) == 1 and alns[0]['decision'] == 'same' and alns[0]['ku_id'] == 'units/persons/andrea-camassei','Camassei alignment baseline changed')
        a = alns[0];a['legacy_ku_id'] = a['ku_id'];a['ku_id'] = '';a['decision'] = 'new';a['process_ref'] = KREF
        a['resolution_note'] = f'B577 corrects prior {a["alignment_id"]}:same->units/persons/andrea-camassei. The index subentry {title!r}, p.50 L83-84, denotes an individual ceiling fresco by Camassei, not the person. Full current KU-manifest comparison found no matching work. new is book-internal/source-scoped; S4 registration and external work/version verification remain pending. No KU created.'
        require(not any(b['candidate_id'] == cid(n) for b in backlog),'Work backlog already exists')
        b = {field:'' for field in bf}
        b.update(backlog_id=f'bl-{100+n-485:04d}',canonical_name=title,suggested_type='work',status='undecided',source_id='haskell-1980-rev-ed',source_ref='chp-2:02_CHP-2_sec_iv:l79-89#L83-84',statement_id=at(2125 if n==485 else 2126)['statement_id'],endpoint_role='ceiling fresco assigned to Camassei, distinct from creator',candidate_id=cid(n),decision_note='S1 type corrected to work and erroneous S3 same-to-creator withdrawn; S3 new, S4 KU registration pending. No formal work relation until a valid work endpoint exists.',process_ref=KREF)
        backlog.append(b)

    # Correct overly broad mentions without changing S0. Add missing, source-exact concept/scheme anchors.
    segid = 'chp-2:02_CHP-2_sec_iv:l79-89';txt = segment_text[segid]
    for m in mentions:
        if m['mention_id'] == 'm-chp2-seciv-l79-89-0028':
            require(m['surface_form']=='his ancestors' and m['candidate_id']==cid(209),'Ancestor mention baseline changed')
            m['surface_form']='his';m['end_char']=str(int(m['start_char'])+3)
            m['note']='B577: only the possessive his refers to the poet-Pope; the unnamed ancestors are not Urban VIII himself.'
        if m['mention_id'] == 'm-s2-chp2-surface-b0dcd7e8da3b23dc':
            require(m['surface_form']=='subject' and m['candidate_id']==cid(840),'Subject mention baseline changed')
            m['candidate_id']=cid(4672)
            m['note']='B577: subject refers to the Divine Wisdom iconographic theme here, not the Contracts index subentry subject.'
    for mid,candidate,surface in [('m-s2-b577-divine-sanction',11888,'the divine sanction given to the sovereigns of this world'),('m-s2-b577-larger-scheme',11889,'the much larger scheme of decoration that was to follow'),('m-s2-b577-advisers-fresco-context',4003,'the fresco')]:
        require(not any(m['mention_id']==mid for m in mentions),'New mention ID already exists')
        require(txt.count(surface)==1,'Exact new source span not unique: '+surface)
        start=txt.index(surface);m={field:'' for field in mf}
        m.update(mention_id=mid,segment_id=segid,candidate_id=cid(candidate),surface_form=surface,start_char=str(start),end_char=str(start+len(surface)),note='B577 source-exact p.50 L84 anchor; interpretation/source-defined scheme remains bounded by Haskell’s wording.')
        mentions.append(m)
    after_mentions=mention_groups()
    for n in MAPPINGS:
        s=at(n);available={m['candidate_id'] for m in after_mentions[s['segment_id']]}
        require(set(s['qualifiers']['mentioned_candidate_ids'])<=available,f'Claim maps candidate without local source span: {n}')
    for segid in {r['segment_id'] for r in window.values()}:
        for m in after_mentions[segid]:
            require(segment_text[segid][int(m['start_char']):int(m['end_char'])]==m['surface_form'],'Bad exact mention '+m['mention_id'])

    # One formal membership inference is not sufficiently supported by the source career summary.
    rel = next(r for r in relations if r['relation_id']=='rel-2456')
    require(rel['status']=='formal' and rel['predicate']=='member_of','Membership relation baseline changed')
    old_rel=copy.deepcopy(rel)
    rel['status']='pending'
    rel['scope']='Haskell所述成功的教会生涯是宽泛职业概述；尚不能由该句独立确认具体成员隶属关系。'
    rel['note']='B577撤回formal推断：p.48 L59的career in the Church不同于entered the Church，不能借其他人物用例升级为member_of。原formal裁决保留于过程记录；待具体成员／任职证据核平。'+KREF

    changed = {sid:s for sid,s in sb.items() if s != old_statements[sid]}
    before_counts=Counter(r['current_review_status'] for r in roster)
    decision_rows=[]
    for n,row in window.items():
        sid=row['statement_id'];prior=row['review_evidence_ref']
        if n in PENDING:
            state='pending';note=PENDING[n];outcome='current_pending_retained_after_role_or_type_repair'
        elif n in MAPPINGS:
            state='pass';note=NOTES.get(n,'按此claim独立核对候选、具体角色、时间与语气；没有复制整个segment的mention集合。');outcome='current_semantic_pass_after_source_mapping_or_role_repair'
        else:
            require(row['current_review_status']=='reviewed_current_pass','Unclassified original row')
            state='pass';note='既有PASS的statement、source、segment与mention指纹核平后复用。';outcome='reused_current_pass_after_B577_fingerprint_check'
        row['current_review_status']='reviewed_current_'+state
        row['review_batch_id']=BATCH;row['review_outcome']=outcome;row['review_evidence_ref']=SREF
        row['follow_up_note']=f'B577: {note} Prior current evidence: {prior}.\n'+row['follow_up_note']
        mids=','.join(at(n)['qualifiers'].get('mentioned_candidate_ids',[]))
        decision_rows.append(f'| {n} | `{sid}` | {state.upper()} | {mids} | {note} |')
    upstream=next(r for r in roster if int(r['current_order'])==2166)
    upstream['follow_up_note']='B577 upstream: cand-0485/cand-0486 are corrected work candidates, S3 new pending registration; this row’s own current review remains unchanged for the next window.\n'+upstream['follow_up_note']
    for row in roster:
        sid=row['statement_id'];s=sb[sid]
        if sid in changed:
            ch=canonical_hash(s);row['current_statement_sha256']=ch
            if int(row.get('history_9622_event_count') or 0)>0:
                row['history_9622_current_statement_match']='exact' if ch==row['history_9622_latest_statement_sha256'] else 'changed'
                row['prior_review_match']='exact_object_and_source_segment' if row['history_9622_current_statement_match']=='exact' and row['history_9622_source_match']=='true' else 'historical_object_or_source_differs'
    # Refresh exact current mention fingerprints for the source segment changed above.
    changed_segment='chp-2:02_CHP-2_sec_iv:l79-89'
    for row in roster:
        if row['segment_id']==changed_segment:
            mm=after_mentions[changed_segment];row['current_segment_mention_count']=str(len(mm));row['current_segment_mentions_sha256']=canonical_hash(mm)
    after_counts=Counter(r['current_review_status'] for r in roster)
    promoted=len(MAPPINGS)-len(PENDING)
    require(after_counts['reviewed_current_pass']==before_counts['reviewed_current_pass']+promoted,'PASS delta mismatch')
    require(len(statements)==15518 and len(mentions)==27360 and len(backlog)==101,'Post counts inconsistent')
    window_counts=Counter(r['current_review_status'] for r in window.values())
    require(window_counts==Counter({'reviewed_current_pass':88,'reviewed_current_pending':12}),'Unexpected batch decisions')

    # Render neither a global rebuild nor a KU creation here. Card relation projections follow a reviewed preview.
    outputs={
        TABLES/'book-statements.jsonl':jsonl_bytes(st_raw,changed),
        PROCESS/'s2-current-review-roster.csv':csv_bytes(roster,rf,reol,rbom),
        TABLES/'mentions.csv':csv_bytes(mentions,mf,meol,mbom),
        TABLES/'entity-candidates.csv':csv_bytes(candidates,cf,ceol,cbom),
        TABLES/'alignment.csv':csv_bytes(alignment,af,aeol,abom),
        TABLES/'relations.csv':csv_bytes(relations,relf,releol,relbom),
        TABLES/'candidate-backlog.csv':csv_bytes(backlog,bf,beol,bbom),
    }
    old_bytes={p:p.read_bytes() for p in outputs}
    relation_counts=Counter(r['status'] for r in relations)
    knowledge_record=f'''\n\n<a id="{KNOWLEDGE}"></a>
### 2026-11-03 B577：Camassei作品身份与Guido关系定向修正

S1/S3：沿用候选保存的C.csv#9/#10锚点，实际核读Camassei主项下的God creating the Angels、Parnassus两个子项。印刷p.50、Markdown L83–84明确称two ceiling frescoes，且将画家、两件作品及Barberini宫殿分开。cand-0485/cand-0486原误标person，aln-0820/aln-0821误same至units/persons/andrea-camassei。两项改为work，保留索引锚点；在全量KU清单中未找到同粒度作品，S3改new、ku_id清空、旧KU移至legacy_ku_id。该比较是书内对象身份判断，不是外部作品版本验证；本批不新建KU。两项分别进入bl-0100/bl-0101，status=undecided，待S4登记，相关新作品关系仍不formal。受影响的2166号statement保持原复核状态，留下一窗口。

S2：逐页核读CHP-2.pdf物理33–36页（印刷48–51）。his ancestors缩为his的教皇指代，祖先群体不冒充Urban VIII；subject从Contracts子项改映Wisdom题材；新增divine sanction、later larger scheme及adviser句中的fresco上下文精确span。修正Guido austerity的因果误读；保留角色、作者评价、意图和图像解释各自范围。

S6：rel-2456由formal退回pending。原记录为{json.dumps(old_rel,ensure_ascii=False)}。p.48的successful career in the Church是职业概述，不可直接套用其他人物entered the Church的member_of用例。本批不裁定Guido不存在成员身份，只撤回该句对该条正式边的充分支持。其他关系逐条保留，Giovanni三场景creator_of、书信authored_by、Sacchi主题与经文来源等已有正式边范围均不变。该条关系的两端卡须随后按既有renderer预览并定向同步。

逐ID裁决及版本证据见[本批S2过程](stages.md#{STAGE})。本批为主审修复与自查，不称独立语义接收。
'''
    stage_record=f'''\n\n<a id="{STAGE}"></a>
### 2026-11-03 S2 当前版逐ID语义复核 B577（2060–2159）

连续100条：17条既有PASS核对当前statement／来源资产／S0段／mention-set指纹后复用；83条pending逐条对照印刷p.48–51与原页，本次{promoted}条转PASS、12条保留pending。statement修订{len(changed)}条；未新增statement；mention新增3条并修正2条，现有提及逐项按segment切片断言surface form。

来源版本：CHP-2.pdf SHA-256={EXPECTED_PDF}；sec_iv Markdown SHA-256={EXPECTED_SOURCE}。原始PDF和S0不改写。H9622历史事件账本9,622条、SHA-256={EXPECTED_HISTORY}，只刷新roster当前版本指纹，不改历史事件、review hash、来源版本或原裁决。

S1/S3纠正两幅Camassei天顶画误作画家的身份；S6撤回仅由宽泛career概述推导的rel-2456 formal状态。比较、角色与历史裁决见[知识过程](knowledge.md#{KNOWLEDGE})。没有由本批创建KU或新增formal边。

| 顺位 | statement ID | 当前决定 | claim-specific candidates | 判读与范围 |
|---:|---|---|---|---|
'''+'\n'.join(decision_rows)+f'''

批后：statement {len(statements):,}；mention {len(mentions):,}；PASS {after_counts['reviewed_current_pass']:,}（{after_counts['reviewed_current_pass']/len(roster)*100:.2f}%）；pending {after_counts['reviewed_current_pending']:,}。本窗口88 PASS／12 pending。关系表{dict(relation_counts)}；backlog 101项，其中新增2项明确undecided。下一连续窗口2160–2259。本批未构成全书独立语义接收。

工具与可恢复写入：[B577脚本](adjudicate_s2_current_review_b577_order_2060_2159_20261103.py)先产生含逐ID差异、输入／输出哈希与来源指纹的review-plan.json；apply仅接受该计划且输入未漂移，写前保留原始字节备份，非目标JSONL行保持逐字节不变。后续审计及定向卡片同步结果另在本节追加。
'''
    for path,addition in [(PROCESS/'stages.md',stage_record),(PROCESS/'knowledge.md',knowledge_record)]:
        text,eol,bom,raw=read_text(path);old_bytes[path]=raw;require(f'id="{STAGE if path.name=="stages.md" else KNOWLEDGE}"' not in text,'Batch record already present')
        outputs[path]=text_bytes(text.rstrip()+'\n'+addition,eol,bom)
    result_path=ROOT/'04-knowledge/results/patrons-and-painters-full-book-s2.md'
    rt,eol,bom,raw=read_text(result_path);old_bytes[result_path]=raw
    line=f'**后续顺序（逐阶段执行）：** **S1 → S2 → S3 → S4 → S5 → S6 → S7。** S1索引、图版、书目及候选来源映射复核已完成。B577修正Camassei两幅天顶画错标人物及错误same映射，S3改为new待S4；rel-2456因career概述不足以支撑member_of，由formal退回pending。当前S2为{len(statements):,}条statement、{len(mentions):,}条mention；当前逐ID清单PASS {after_counts["reviewed_current_pass"]:,}（{after_counts["reviewed_current_pass"]/len(roster)*100:.2f}%）、pending {after_counts["reviewed_current_pending"]:,}，尚未全书独立语义接收。H9622历史事件账本9,622行不改写。B577连续2060–2159共100条：17条既有PASS复用、{promoted}条pending转PASS、12条保留pending。下一连续窗口2160–2259。S3–S6逐类收口，S7待前序阶段收口后开展。详见[本批过程](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md#{STAGE})与[身份／关系修正](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{KNOWLEDGE})。'
    rt,count=re.subn(r'(?m)^\*\*后续顺序（逐阶段执行）：\*\*[^\r\n]*',lambda m:line,rt,count=1);require(count==1,'Current result summary missing')
    outputs[result_path]=text_bytes(rt,eol,bom)
    rs_path=PROCESS.parent/'results/stages.md';rs,eol,bom,raw=read_text(rs_path);old_bytes[rs_path]=raw
    outputs[rs_path]=text_bytes(rs.rstrip()+f'\n\n### 2026-11-03 B577当前结果\n\n连续2060–2159的100条完成本轮处置：88 PASS、12 pending，含{promoted}条pending转PASS。Camassei两件作品候选与其作者分开；2条新增mention及2条span／指代修正；rel-2456 formal退回pending。全书{len(statements):,} statements、{len(mentions):,} mentions，PASS {after_counts["reviewed_current_pass"]:,}、pending {after_counts["reviewed_current_pending"]:,}。下一窗口2160–2259；非独立接收。详见[过程](../process/stages.md#{STAGE})与[当前交接结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。\n',eol,bom)

    summary={'batch':BATCH,'window':[2060,2159],'window_before':{'pass':17,'pending':83},'window_after':{'pass':88,'pending':12},'promoted':promoted,'statements_changed':len(changed),'mentions_added':3,'mentions_corrected':2,'candidates_retyped':2,'alignments_same_to_new':2,'relation_formal_to_pending':['rel-2456'],'backlog_added':['bl-0100','bl-0101'],'global_after':dict(after_counts),'mentions_after':len(mentions)}
    plan={'summary':summary,'source_sha256':EXPECTED_SOURCE,'pdf_sha256':EXPECTED_PDF,'history_sha256':EXPECTED_HISTORY,
          'inputs':{p.relative_to(ROOT).as_posix():sha(raw) for p,raw in old_bytes.items()},
          'outputs':{p.relative_to(ROOT).as_posix():sha(raw) for p,raw in outputs.items()},
          'statement_diffs':[{'order':rb[sid]['current_order'],'statement_id':sid,'before':old_statements[sid],'after':st} for sid,st in changed.items()],
          'retained_pending':PENDING,'mapping_candidates':MAPPINGS}
    RECOVERY.mkdir(parents=True,exist_ok=True)
    if not args.apply:
        PLAN.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'mode':'dry-run','plan':str(PLAN),**summary},ensure_ascii=False))
        return
    require(PLAN.exists(),'Run the evidence/diff dry-run first')
    require(json.loads(PLAN.read_text(encoding='utf-8'))==json.loads(json.dumps(plan,ensure_ascii=False)),'Dry-run plan or current input changed; inspect before re-planning')
    for p,raw in old_bytes.items():
        require(p.read_bytes()==raw,'Input drift before apply: '+str(p))
    for p,raw in old_bytes.items():
        dest=RECOVERY/'before'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
        require(not dest.exists(),'Recovery copy already exists; inspect prior apply')
        dest.write_bytes(raw)
    written=[]
    try:
        for p,raw in outputs.items():
            require(p.read_bytes()==old_bytes[p],'Concurrent input change: '+str(p))
            atomic_write(p,raw);written.append(p)
        for p,raw in outputs.items():require(p.read_bytes()==raw,'Write verification failed: '+str(p))
    except Exception:
        for p in reversed(written):atomic_write(p,old_bytes[p])
        raise
    require(sha(HISTORY.read_bytes())==EXPECTED_HISTORY,'History changed during apply')
    (RECOVERY/'applied.json').write_text(json.dumps({'summary':summary,'applied_outputs':plan['outputs']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'mode':'applied',**summary},ensure_ascii=False))


if __name__=='__main__':
    main()

#!/usr/bin/env python3
"""Apply the source-read B578 decisions; default is an evidence/diff dry-run."""
from __future__ import annotations

import argparse
import copy
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from adjudicate_s2_current_review_b576_order_1960_2059_20261103 import (
    atomic_write, canonical_hash, csv_bytes, jsonl_bytes, read_csv, read_jsonl,
    read_text, sha, text_bytes,
)

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge/tables'
PROCESS = Path(__file__).resolve().parent
RECOVERY = ROOT / '06-runtime/recovery/s2-b578-order-2160-2259'
PLAN = RECOVERY / 'review-plan.json'
STAGE = '2026-11-03-s2-current-review-b578-order-2160-2259'
BATCH = 'S2-B578-CH2-2160-2259'
SREF = 'stages.md#' + STAGE
SOURCE = ROOT / '02-sources/02-Markdown/02_CHP-2_sec_iv.md'
PDF = ROOT / '02-sources/01-book/CHP-2.pdf'
HISTORY = PROCESS / 's2-history-9622-review-events.csv'
EXPECTED_SOURCE = '9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf'
EXPECTED_PDF = '317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e'
EXPECTED_HISTORY = '75ab12df478a816035929353565b0301d55959c6bb13d9b511af072c4c931c89'

# Claim-level references selected from the printed pages, not every mention in each segment.
MAPPINGS = {
    2160:[4003,4672,4678,4679,4680], 2161:[4003,4675],
    2162:[4003,187,198,199], 2163:[209,440,4686,198],
    2164:[484,11890], 2165:[484,4685], 2166:[484,4685,4691],
    2167:[199,350], 2168:[350,4689,4688,240], 2169:[350],
    2170:[350,4687,4685], 2171:[11889,4685,4003],
    2172:[4003,4490], 2173:[4687,198], 2174:[4685],
    2175:[4685,484,240], 2176:[4690,350,209], 2177:[239,484],
    2178:[198], 2179:[440,209,4653], 2180:[440],
    2181:[440,198], 2182:[4686,4687,440,350,198],
    2183:[440,209], 2184:[4695,198,440],
    2185:[440,209,4693,4694,31], 2186:[440,4693],
    2187:[4694,31], 2188:[440,209,4695], 2189:[4695],
    2190:[440,4796], 2191:[186,12479,4702], 2192:[186,3405],
    2193:[4721,4687,2318], 2194:[440,4696,4702,4703],
    2195:[4686,4687,440,350], 2196:[440,4490],
    2197:[440,209,186], 2198:[440,4702,4703],
    2199:[440,4697,198], 2200:[4722,4687,2318],
    2201:[4697,4700], 2202:[4697,4698], 2203:[209,440],
    2204:[4687,4704,4705,4706,4707,4708,4709,4710,4711,4712,4713],
    2205:[4720,187], 2206:[4726,239,4490],
    2207:[4687,198,4714,4715], 2208:[4687,209,4717,4718,4719],
    2209:[4687,4723], 2210:[4687], 2211:[4687], 2212:[4687],
    2213:[4687,4724,209], 2214:[1687], 2215:[1687,4725],
    2216:[1687,4687,2260,2561], 2217:[4728,4727],
    2218:[4729,4348], 2219:[4686], 2220:[4003,4687,4730],
    2221:[350,4687], 2222:[350,4687], 2223:[4730,4731],
    2224:[4732,4736], 2225:[4686,350,440],
    2226:[203,4733,2293,1631,1295,4653],
    2227:[932,4687], 2228:[932,4687], 2229:[203,7],
    2230:[203,2208,350], 2231:[203,4735,350,7],
    2232:[2208,7,2209,203], 2233:[2208,350,209],
    2234:[2208,203], 2235:[2208,209,12480], 2236:[2208,4734],
    2237:[2208], 2238:[2208], 2239:[2208,350], 2240:[],
    2241:[187], 2242:[187,11892], 2243:[187,4739,4740],
    2244:[187,11892], 2245:[4738,187], 2246:[187,209],
    2247:[4737,187], 2248:[187,203], 2249:[203],
    2250:[203,350], 2251:[203,2208,350], 2252:[203,11894],
    2253:[2323,187], 2254:[2323,2098], 2255:[187,203,209,4490],
    2256:[187], 2257:[187,198], 2258:[187,2670],
    2259:[209,4741,4648,1833],
}

PENDING = {
    2176:'原文支持 Cortona 获教皇的 Jesuit advisers 支持，但 cand-4690 所指未具正式组织身份、成员也未具名，类型边界未决；不并入 Society of Jesus。',
    2206:'原文把 Hercules 作为壁画中的寓意图像人物，指向 Taddeo 的罗马治理；cand-4726 的类型仍不能忠实表达图像角色，不能把 Hercules 当作 Taddeo 或历史人物，留待 S3 类型裁决。',
}

NOTES = {
    2160:'Eternity、Sanctity、Purity 是画中 Wisdom 的拟人属性；“and so on”表示例举不尽。',
    2161:'作品、女性形象和胸前显现的太阳分开；保留已有太阳主题边 rel-2272。',
    2162:'Antonio 是 Francesco 的弟弟及该壁画在 Barberini 家族中的唯一公开支持者；不把两人合并。',
    2163:'Bracciolini 是受召拟定家族颂扬方案的诗人；program 与作品、家族和作者分别映射。',
    2164:'“minor commissions”组与此前小房间的两幅已命名壁画分开；为其补入精确原文提及。',
    2165:'“relative failure”由持续获得小型委托限定，不写成职业失败或停止受聘。',
    2166:'小房间、主接待厅和Camassei分别保留；这是 Haskell 对适配度的判断。',
    2167:'Cardinal Francesco 对 Cortona 的支持按原文报告，不扩成具体作品委托。',
    2168:'chapel 是 Barberini 宫内空间，frescoes 是作品；未补出具体壁画标题。',
    2169:'“position firmly established”是作者对地位的总结，不构成可单独识别的对象关系。',
    2170:'将 Cortona、主厅穹顶作品、主厅空间和约 1632 年开工及六七年工期分开记录。',
    2171:'较大的装饰工程在主接待厅开始；不把该厅等同先前小房间或 Camassei 的画。',
    2172:'作品受欢迎是 Haskell 的叙述，范围限定为罗马某些圈子。',
    2173:'“为家族抱负作世俗记录”是设计意图，不推成已实现的政治成果。',
    2174:'“grandiose / most spectacular”保留为 Haskell 对方案的比较评价。',
    2175:'计划把主厅委给 Camassei；计划不等于最终执行。',
    2177:'protégé 表示保护／扶持语境，不单凭此词建立亲授师生关系。',
    2179:'秘书服务与同行赴巴黎分别保留；巴黎在下一 S0 句段续出，按 continuation 指针核读印刷 pp.51–52。',
    2180:'mean character、bad poet 是 Haskell 的评价，不转成外部事实属性。',
    2181:'保留 Haskell 对奉承动机的归因，不声称当事人自述。',
    2182:'方案作者 Bracciolini、执行者 Cortona、作品和受颂家族各自区分。',
    2184:'信件投向 Barberini 家族但未列出个人收件人；不推定由Urban单独收信。',
    2185:'“left him”指 Maffeo；1605 年离开事件与 Clement VIII 之死作为同段时间语境分开。',
    2186:'1623 年后悔针对先前离开 Maffeo 的行为；保留 Haskell 的心理叙述。',
    2187:'仅记录 Clement VIII 于1605年死亡，不添加死因或其他背景。',
    2188:'引文中的“Urban”由上下文指 Urban VIII；以 Bracciolini 的求情为信件语境。',
    2189:'“no one”没有可识别收件人；记录作者对请求未获认真对待的概述。',
    2190:'出版在前、荣誉随后；不把时间相继改写为出版直接导致授勋，也不猜授予者。',
    2191:'新候选 cand-12479 表示主教辖区／教座，和同名城市 cand-4702 区分；其 S3 身份仍 undecided。',
    2192:'重复核读 Capuchin 身份与既有 rel-2285 一致；不新增重复正式边。',
    2193:'Bees 是 Cortona 穹顶的主题，Sacchi 是被比较的前作作者；rel-2275 范围不变。',
    2194:'投诉信与1623年求情信分开；地点为 Sinigaglia，未补收件人或馆藏。',
    2195:'Bracciolini 与 Cortona 共同规划天顶装饰；planning 不等于对每项图像解释的共同作者身份。',
    2197:'任命秘书的行动者、受任人及 Antonio 分开；既有 rel-2286 的任职边未改变。',
    2198:'Sinigaglia 和亚得里亚海岸是地点说明；不把“little port”当作新的地点对象。',
    2199:'诗组及其献给家族成员的范围保留；不虚构具体诗名或成员名单。',
    2200:'Laurel 主题与作品分开，Sacchi 只作为前作对照；rel-2276 范围不变。',
    2201:'“conversion of Bulgaria”是诗组题材；不宣称本句独立证明历史转换事件细节。',
    2202:'“capture of La Rochelle”是诗组题材；不把诗作与历史事件合并。',
    2203:'“not entirely forgiven”是 Haskell 对 Urban 与 Bracciolini 关系的叙述。',
    2204:'逐一保留 Providence、Present、Future、Time、Fates、Virtues、Immortality、Faith、Hope、Charity 的图像角色，不把寓意直接写成现实人物。',
    2205:'Abundance=Cardinal Antonio 是被报告的图像解释；“granaries he built”不指向未识别的具体粮仓。',
    2207:'Religion 与 Rome 是寓意形象，Barberini family 是受颂对象；不映射为现实宗教机构。',
    2208:'原文说四项副题材但只列举三项；只映射 fight against Vices、learning、plenty，不补第四项。',
    2209:'“opens a new chapter”是 Haskell 的艺术史评价，不等同一个新组织或创作事件。',
    2212:'painted frame“appears”被有意越界，保留视觉解释，不说物理画框损坏。',
    2213:'巨人群带来冲突印象；访客卷入教皇对邪恶的战争是修辞，不是实际战争事件。',
    2214:'这是 Haskell 注释转述 Montagu 的学术解释，不当作普遍规律。',
    2215:'Four Ages 是至少一位未具名观察者的可能读法，保留“可能”和转述层级。',
    2216:'区分 Montagu、Rosichino、Girolamo Teti 三层学术归述及其不同读法。',
    2217:'仅记录注释指向 Vitzthum 1961 文献；不把引文指针当作该文支持的独立证据。',
    2218:'Borghese 与 Ludovisi 是家族赞助语境，不改成某两位未具名枢机个人。',
    2219:'主题新颖性是对17世纪教皇赞助语境的比较判断；Papal court 候选不是 papal patronage 本身，故撤掉错配对象。',
    2220:'原文的主语是 Sacchi 与 Cortona 两幅穹顶画；分别映射 cand-4003/cand-4687，宾语为新宫廷 cand-4730，不能把 Bracciolini 的单个方案当作宫廷兴趣。',
    2221:'总体清晰与隐晦典故是对 Cortona 天顶画的双重视觉评价。',
    2222:'显示效果与文学兴趣是 Haskell 对 Cortona 综合能力的解释。',
    2223:'宫廷兴趣与文艺复兴人文主义者作比较，不构成二者身份或机构隶属。',
    2224:'“well over a century”描述艺术综合被宫廷画家群体采用的持续期；不虚构固定组织成员。',
    2225:'方案将王侯奉承推至作者所见极端；不额外添加未被本句指称的家族候选。',
    2226:'Francesco 受 Rubens 周期影响是 Haskell 的高可能判断；Rubens 为作者，cand-4733 的确切作品身份仍未证实。',
    2227:'Domenichino 明确依据 hearsay；只记录他对教皇穹顶适宜性的判断。',
    2228:'“few to quarrel”是 Haskell 对 Domenichino 读法的评价，不代表独立统计现代学者。',
    2229:'Francesco 对学院的控制按 Haskell 原文记录，不补控制开始或结束年份。',
    2230:'employment 及 pupilage 有原文支持，但“many obligations”未列具体教堂或作品。',
    2231:'资助对象是 Accademia 教堂重建，Cortona 是建筑工程作者；不误写成资助 Cortona 本人。',
    2232:'Romanelli 在1638年获任 Accademia di S. Luca Principe，且是按 Francesco 命令；职务与人物分开。',
    2233:'“aimed to supplant”是未实现的个人抱负，不写成实际继任。',
    2234:'教堂与祭坛／穹顶画为未逐一具名的委托范围；不虚构单件作品。',
    2235:'新增 cand-12480 只指来源中未具名的单一侄辈；身份与跨章对应保持 S3 undecided，不猜 Francesco 或 Antonio。',
    2236:'tapestry works 保留为 Romanelli 管理的作坊／生产机构候选；具体组织边界未获原文说明。',
    2237:'疲软、乏力而非真正古典是 Haskell 对 Romanelli 绘画变化的评价。',
    2238:'可靠与获得年金荣誉均按作者概述记录，不补金额和授予人。',
    2239:'色彩和手法继承及缺少才气是作者比较；“follower”不单独证明正式师承。',
    2240:'这是作者关于气质与审美的概括性判断；无具名实体端点，不另造候选。',
    2241:'贪婪与野心是 Haskell 对 Antonio 资格的讽刺评价，不写成客观资格清单。',
    2242:'收入缓和贪欲是作者的心理解释；收入来源组与逐项官职分开。',
    2243:'Cardinals Borghese/Ludovisi 只按姓氏候选保留；收入比较为 Haskell 的不确定判断。',
    2245:'将1627年枢机任命事件、Antonio本人及19岁年龄分开。',
    2246:'“youngest of the Pope’s nephews”是排行描述，不代表他是 Urban VIII 唯一侄辈。',
    2247:'Conclave elder members 是未具名群体；记录其震惊反应，不推定人员名单。',
    2248:'Antonio 为 Francesco 的弟弟；不将兄弟身份与作者的艺术评价合并。',
    2250:'Francesco 选择 Cortona 为喜爱画家，richly coloured/extrovert 保留为作者描述。',
    2251:'Francesco 选择 Romanelli 为喜爱画家；Cortona 是其师／风格参照，不能合并成同一画家。',
    2252:'“half the scholars”是夸张性范围，保留未具名学者群，不按字面折半。',
    2253:'Sacchi 主要依靠 Antonio 支持，保留“almost entirely”，不提升为唯一资助者。',
    2254:'Sacchi 对 Raphael 的敬仰和不愿竞争是作者心理描述，不表示真实师生关系。',
    2255:'Francesco 与 Urban VIII 被说成阻挠 Antonio 抱负；被送离罗马的频率仅为“as often as possible”。',
    2256:'外貌与风度照录作者描写，不把 dandy/bon vivant 提升为独立身份。',
    2257:'Antonio 分享 Barberini 家族对学问和艺术的兴趣；家族集体与个人分开。',
    2258:'1631年 devolution 是 Antonio 开始介入艺术赞助的机会语境，不等于某幅画已被购得。',
    2259:'原文用“city”称指，但后续明确为等待并入教皇国的政治领土；保留 city=place、Urbino state=institution、Papal States=institution 三层，不声称已完成并入。',
}

NEW_MENTIONS = [
    ('m-s2-b578-minor-commissions','chp-2:02_CHP-2_sec_iv:l91-94',11890,'minor commissions','P.51 exact source phrase for Camassei’s unnamed commission group.'),
    ('m-s2-b578-vaster-setting','chp-2:02_CHP-2_sec_iv:l91-94',11889,'decoration of a much vaster setting','P.51 exact source phrase for the larger decorative scheme/setting.'),
    ('m-s2-b578-bracciolini-departure','chp-2:02_CHP-2_sec_iv:l96-104',4693,'hurriedly left him','P.52 exact departure phrase; “him” resolves to Maffeo in the claim context.'),
    ('m-s2-b578-clement-death','chp-2:02_CHP-2_sec_iv:l96-104',4694,'Clement VIII died in 1605','P.52 exact date-bearing event phrase.'),
    ('m-s2-b578-sinigaglia-see','chp-2:02_CHP-2_sec_iv:l96-104',12479,'Bishop of Sinigaglia','P.52 exact office/see phrase; the named ecclesiastical see is distinct from the city candidate.'),
    ('m-s2-b578-rubens-cycle-creator','chp-2:02_CHP-2_sec_iv:l106-112',2293,'Rubens','P.53 exact creator mention for the cycle; work identity remains source-scoped.'),
    ('m-s2-b578-antonio-cardinalate','chp-2:02_CHP-2_sec_iv:l114-125',4738,'was made Cardinal in 1627','P.54 exact appointment-event phrase.'),
    ('m-s2-b578-urbino-devolution','chp-2:02_CHP-2_sec_iv:l114-125',2670,'devolution of Urbino to the papacy','P.54 exact event phrase; not a specific artwork acquisition.'),
]

EXPECTED_PRIOR_PASS = {2164,2171,2244,2249}
def require(ok, message):
    if not ok:
        raise SystemExit(message)


def cid(n):
    return f'cand-{n:04d}'


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--apply',action='store_true')
    args=ap.parse_args()
    require(sha(SOURCE.read_bytes())==EXPECTED_SOURCE,'Source Markdown version changed')
    require(sha(PDF.read_bytes())==EXPECTED_PDF,'Authority PDF version changed')
    require(sha(HISTORY.read_bytes())==EXPECTED_HISTORY,'Immutable H9622 ledger changed')
    statements,st_raw,_,_=read_jsonl(TABLES/'book-statements.jsonl')
    roster,rf,rr_raw,reol,rbom=read_csv(PROCESS/'s2-current-review-roster.csv')
    mentions,mf,mr_raw,meol,mbom=read_csv(TABLES/'mentions.csv')
    candidates,cf,cr_raw,ceol,cbom=read_csv(TABLES/'entity-candidates.csv')
    alignment,af,ar_raw,aeol,abom=read_csv(TABLES/'alignment.csv')
    relations,relf,rel_raw,releol,relbom=read_csv(TABLES/'relations.csv')
    segments,_,_,_=read_jsonl(TABLES/'segments.jsonl')
    sb={s['statement_id']:s for s in statements}; old_statements=copy.deepcopy(sb)
    rb={r['statement_id']:r for r in roster}
    window={int(r['current_order']):r for r in roster if 2160<=int(r['current_order'])<=2259}
    require(len(statements)==len(roster)==15518 and len(mentions)==27360,'B578 baseline counts changed')
    require(set(MAPPINGS)==set(window),'B578 mapping IDs do not cover exactly the current window')
    require(len(window)==100,'B578 window is not 100 IDs')
    before_pass={n for n,r in window.items() if r['current_review_status']=='reviewed_current_pass'}
    before_pending={n for n,r in window.items() if r['current_review_status']=='reviewed_current_pending'}
    require(before_pass==EXPECTED_PRIOR_PASS and len(before_pending)==96,'B578 prior review outcomes changed')
    require(set(PENDING)<=before_pending,'A retained pending row was not pending before this batch')
    cm={c['candidate_id']:c for c in candidates}
    require('cand-12479' not in cm and 'cand-12480' not in cm,'New candidate IDs already exist')
    require(not any(a['candidate_id'] in {'cand-12479','cand-12480'} for a in alignment),'New candidate already has alignment row')
    source_lines=SOURCE.read_text(encoding='utf-8-sig').splitlines()
    sg={s['segment_id']:s for s in segments}
    relevant_segments={sb[r['statement_id']]['segment_id'] for r in window.values()}
    st_text={sid:'\n'.join(source_lines[int(sg[sid]['line_start'])-1:int(sg[sid]['line_end'])]) for sid in relevant_segments}
    for n,row in window.items():
        st=sb[row['statement_id']]; seg=sg[st['segment_id']]
        require(canonical_hash(st)==row['current_statement_sha256'],f'Stale statement at order {n}')
        require(seg['sha256']==row['segment_sha256'] and seg['asset_sha256']==row['source_asset_sha256'],f'Stale source at order {n}')
    def grouped(ms):
        out=defaultdict(list)
        for m in ms: out[m['segment_id']].append(m)
        return {k:sorted(v,key=lambda x:x['mention_id']) for k,v in out.items()}
    before_groups=grouped(mentions)
    for row in window.values():
        st=sb[row['statement_id']]; mm=before_groups.get(st['segment_id'],[])
        require(canonical_hash(mm)==row['current_segment_mentions_sha256'] and len(mm)==int(row['current_segment_mention_count']),f'Stale mention set for {st["statement_id"]}')
    for n,row in window.items():
        if n not in EXPECTED_PRIOR_PASS:
            continue
        require(row['history_9622_source_match']=='true' and row['history_9622_current_statement_match']=='exact',f'Prior PASS provenance is not exact at {n}')

    # Exact source spans added because the claim-level candidates had no local mention anchor.
    existing_mids={m['mention_id'] for m in mentions}
    paris=next((m for m in mentions if m['segment_id']=='chp-2:02_CHP-2_sec_iv:l96-104' and m['surface_form']=='Paris'),None)
    require(paris is not None and paris['candidate_id']==cid(4653),'Paris continuation mention is missing or mapped differently; reuse must be reviewed')
    nephew=next((m for m in mentions if m['mention_id']=='m-chp2-seciv-l106-112-0042'),None)
    require(nephew is not None and nephew['segment_id']=='chp-2:02_CHP-2_sec_iv:l106-112' and nephew['surface_form']=='his nephew' and nephew['candidate_id']==cid(203),'Existing nephew mention changed; inspect identity correction before apply')
    nephew['candidate_id']=cid(12480)
    nephew['note']='Haskell identifies one unnamed nephew of Urban VIII; the source does not establish that he is Francesco Barberini.'
    for mid,sid,num,surface,note in NEW_MENTIONS:
        require(mid not in existing_mids,f'Mention ID already exists: {mid}')
        txt=st_text[sid]
        require(txt.count(surface)==1,f'New source phrase is not unique in {sid}: {surface!r}')
        start=txt.index(surface); m={f:'' for f in mf}
        m.update(mention_id=mid,segment_id=sid,candidate_id=cid(num),surface_form=surface,start_char=str(start),end_char=str(start+len(surface)),note=note)
        mentions.append(m); existing_mids.add(mid)

    # Two source-defined endpoints are now explicit; their cross-chapter S3 identity remains open.
    candidate_rows=[]
    c1={f:'' for f in cf}
    c1.update(candidate_id='cand-12479',canonical_name='Bishopric of Sinigaglia (episcopal see named by Haskell)',suggested_type='institution',status='open',detail='Haskell describes Antonio Barberini (Urban VIII’s brother) as becoming Bishop of Sinigaglia in 1627. This candidate denotes the named see/jurisdiction, not the city cand-4702. No cross-chapter identity or current KU has been established.',candidate_origin='body-mention',candidate_source_ref='chp-2:02_CHP-2_sec_iv:l96-104#L99')
    c2={f:'' for f in cf}
    c2.update(candidate_id='cand-12480',canonical_name='Unidentified nephew of Urban VIII (Romanelli admirer, p.53)',suggested_type='person',status='open',detail='Haskell says Romanelli won few admirers other than Pope Urban VIII and his nephew. The nephew is not named; do not infer Francesco, Antonio, Taddeo, or another person from adjacent passages.',candidate_origin='body-mention',candidate_source_ref='chp-2:02_CHP-2_sec_iv:l106-112#L112')
    candidate_rows.extend([c1,c2]); candidates.extend(candidate_rows)
    a1={f:'' for f in af}
    a1.update(alignment_id='aln-12808',candidate_id='cand-12479',decision='undecided',process_ref=SREF,resolution_note='source_ref=chp-2:02_CHP-2_sec_iv:l96-104#L99; Haskell names the bishopric/see of Sinigaglia, distinct from city cand-4702. No cross-chapter identity or matching KU has been established; keep S3 undecided.')
    a2={f:'' for f in af}
    a2.update(alignment_id='aln-12809',candidate_id='cand-12480',decision='undecided',process_ref=SREF,resolution_note='source_ref=chp-2:02_CHP-2_sec_iv:l106-112#L112; the text identifies one unnamed nephew but not his identity. Compare with source candidates cand-4497 and cand-10739, but do not merge with those references or with Francesco, Antonio, or Taddeo without evidence; keep S3 undecided.')
    alignment.extend([a1,a2])

    def at(n): return sb[window[n]['statement_id']]
    for n,nums in MAPPINGS.items():
        q=at(n).setdefault('qualifiers',{})
        q['mentioned_candidate_ids']=[cid(i) for i in nums]
    # Cross-page sentence continuation: Paris belongs to the next segment named in the statement.
    require(at(2179)['qualifiers'].get('continuation_resolved_by_segment_id')=='chp-2:02_CHP-2_sec_iv:l96-104','B578 Paris continuation pointer changed')
    for n,nums in MAPPINGS.items():
        st=at(n); q=st['qualifiers']
        avail={m['candidate_id'] for m in grouped(mentions).get(st['segment_id'],[])}
        extra=set()
        if n==2179:
            cont=q['continuation_resolved_by_segment_id']
            extra={cid(4653)}
            require(cid(4653) in {m['candidate_id'] for m in grouped(mentions).get(cont,[])},'Paris continuation mention missing')
        require(set(q['mentioned_candidate_ids'])-extra <= avail,f'Claim map points outside its source segment at {n}')

    # Repair source-claim scope and endpoint representation.
    at(2191)['object_candidate_id']=cid(12479)
    at(2191)['qualifiers'].update(see_place_candidate_id=cid(4702),qualification='“Bishop of Sinigaglia” names an ecclesiastical see, not the city itself. The see candidate is kept distinct from the place; identity alignment remains S3 undecided.')
    at(2219)['object_candidate_id']=None
    at(2219)['qualifiers'].update(historical_context='seventeenth-century papal patronage',qualification='The claim concerns novelty within papal patronage. Papal court candidate cand-4241 is not this activity/context, so no institutional object is asserted.',relation_candidate=False,relation_candidate_note='Authorial historical comparison about a theme and period; no separate institutional endpoint is asserted.')
    at(2220)['subject_candidate_id']=None
    at(2220)['object_candidate_id']=cid(4730)
    at(2220)['qualifiers'].update(claim='Haskell says the ceilings by Sacchi and Pietro da Cortona both reflect the new court’s intensely literary interests.',represented_ceiling_candidate_ids=[cid(4003),cid(4687)],qualification='The plural subject is two distinct ceiling works; the new court is the contextual object. Do not collapse the pair into Bracciolini’s programme.')
    at(2226)['qualifiers']['creator_candidate_id']=cid(2293)
    at(2235)['object_candidate_id']=None
    at(2235)['qualifiers'].update(qualification='Haskell identifies the audience only as “the Pope and his nephew”. Francesco appears in the immediate context as a papal nephew, but the text does not explicitly equate him with this unnamed admirer.',audience_candidate_ids=[cid(209),cid(12480)],open_endpoint_reason='The Pope is identified, but “his nephew” refers to one unnamed person. A source-local person candidate is recorded; his cross-chapter identity remains S3 undecided.')
    at(2259)['qualifiers'].update(qualification='Haskell calls the target a “city”, but the following succession and incorporation clauses refer to the political State. Keep the city, State of Urbino, and Papal States distinct; this reports a claim, not a completed transfer.',political_entity_candidate_id=cid(4741),city_candidate_id=cid(4648),papal_states_candidate_id=cid(1833))

    after_groups=grouped(mentions)
    # Every new/current mention span in the four source segments must still cut back to the exact source surface.
    changed_segments={sid for _,sid,_,_,_ in NEW_MENTIONS}
    source_segment_text={sid:'\n'.join(source_lines[int(sg[sid]['line_start'])-1:int(sg[sid]['line_end'])]) for sid in changed_segments}
    for sid in changed_segments:
        for m in after_groups[sid]:
            start,end=int(m['start_char']),int(m['end_char'])
            require(source_segment_text[sid][start:end]==m['surface_form'],f'Bad source span {m["mention_id"]}')
    # The previous B577 decisions in l91-94 are unaffected by the two new p.51 spans.
    cross_window=[]
    for row in roster:
        if row['segment_id']=='chp-2:02_CHP-2_sec_iv:l91-94' and int(row['current_order'])<2160:
            n=int(row['current_order'])
            require(row['current_review_status']=='reviewed_current_pass' and canonical_hash(sb[row['statement_id']])==row['current_statement_sha256'],f'Unexpected prior decision in changed segment at {n}')
            cross_window.append(n)
    require(cross_window==list(range(2146,2160)),f'Unexpected cross-window segment coverage: {cross_window}')
    # Recheck that the new spans belong to 2164 and 2171, not the already reviewed rows 2117-2159.
    for n in range(2146,2160):
        sid=next(k for k,v in rb.items() if int(v['current_order'])==n)
        q=sb[sid].get('qualifiers',{})
        require(int(q.get('source_line_start',0))<=92 or int(q.get('source_line_start',0))>=94, f'Unexpected prior claim overlap with added p.51 anchors at {n}')

    # Record decisions and refresh the current roster. The immutable history event table is never rewritten.
    before_counts=Counter(r['current_review_status'] for r in roster)
    changed={sid:s for sid,s in sb.items() if s!=old_statements[sid]}
    decision_rows=[]
    page_by_order={n:at(n)['qualifiers'].get('print_page','?') for n in MAPPINGS}
    for n,row in window.items():
        sid=row['statement_id']; old_ref=row['review_evidence_ref']; was_pass=n in EXPECTED_PRIOR_PASS
        state='pending' if n in PENDING else 'pass'
        note=PENDING[n] if state=='pending' else NOTES.get(n,f'印刷p.{page_by_order[n]}核读：claim与原句角色、时间和语气范围相符；候选仅覆盖本claim及必要指代，不扩张到同段其他提及。')
        if was_pass:
            outcome='current_semantic_pass_after_B578_segment_fingerprint_refresh'
        elif state=='pending':
            outcome='current_pending_retained_after_source_read_type_or_identity_gap'
        else:
            outcome='current_semantic_pass_after_source_read_and_claim_mapping'
        row['current_review_status']='reviewed_current_'+state
        row['review_batch_id']=BATCH;row['review_outcome']=outcome;row['review_evidence_ref']=SREF
        row['follow_up_note']=f'B578: {note} Prior current evidence: {old_ref}.\n'+row['follow_up_note']
        refs=','.join(at(n)['qualifiers'].get('mentioned_candidate_ids',[]))
        decision_rows.append(f'| {n} | `{sid}` | {state.upper()} | `{refs}` | {note} |')

    # Any row sharing a changed segment uses the current segment mention fingerprint.
    for row in roster:
        if row['segment_id'] in changed_segments:
            mm=after_groups[row['segment_id']]
            row['current_segment_mention_count']=str(len(mm));row['current_segment_mentions_sha256']=canonical_hash(mm)
        sid=row['statement_id']
        if sid in changed:
            current_hash=canonical_hash(sb[sid]);row['current_statement_sha256']=current_hash
            if int(row.get('history_9622_event_count') or 0)>0:
                row['history_9622_current_statement_match']='exact' if current_hash==row['history_9622_latest_statement_sha256'] else 'changed'
                row['prior_review_match']='exact_object_and_source_segment' if row['history_9622_current_statement_match']=='exact' and row['history_9622_source_match']=='true' else 'historical_object_or_source_differs'

    after_counts=Counter(r['current_review_status'] for r in roster)
    window_counts=Counter(r['current_review_status'] for r in window.values())
    require(window_counts==Counter({'reviewed_current_pass':98,'reviewed_current_pending':2}),f'Unexpected B578 outcome counts: {window_counts}')
    require(after_counts['reviewed_current_pass']==before_counts['reviewed_current_pass']+94,'Global PASS delta mismatch')
    require(after_counts['reviewed_current_pending']==before_counts['reviewed_current_pending']-94,'Global pending delta mismatch')
    require(len(statements)==15518 and len(mentions)==27368 and len(candidates)==12458 and len(alignment)==12806,'Unexpected post-batch table counts')
    require(sha(HISTORY.read_bytes())==EXPECTED_HISTORY,'Immutable H9622 ledger changed during plan')

    stage_record=f'''\n\n<a id="{STAGE}"></a>
### 2026-11-03 S2 当前版逐ID语义复核 B578（2160–2259）

连续100条完成本轮处置：4条既有PASS在当前statement/source及原页核平后复核；96条原pending逐条核读印刷pp.51–55及对应注释，94条转PASS、2条保留pending。窗口结果98 PASS／2 PENDING。全批新增{len(NEW_MENTIONS)}条精确mention；statement变更{len(changed)}条。B577已审的2146–2159共14条与l91–94同段；本批在段内补入两个与其claim不重叠的p.51 mention后刷新整段mention指纹，原14条statement/source哈希及decision均不变，保留既有PASS。

来源版本：CHP-2.pdf SHA-256={EXPECTED_PDF}；sec_iv Markdown SHA-256={EXPECTED_SOURCE}。原始PDF、来源Markdown与S0段落不改写。历史H9622事件账本9,622条、SHA-256={EXPECTED_HISTORY}保持不变；roster只刷新当前statement和mention版本指纹及本窗口决定。

S1/S3：补入cand-12479（Sinigaglia主教辖区／教座，区别于城市cand-4702）与cand-12480（Urban VIII未具名侄辈）；分别新增aln-12808、aln-12809，decision=undecided，等待跨章身份核对。cand-4690的教皇耶稣会顾问组与cand-4726的壁画Hercules寓意图像类型仍未决，不强行归类。

S2重点修正：Sacchi与Cortona的两幅天顶画共同反映新宫廷文学兴趣，改映cand-4003及cand-4687至cand-4730；教皇赞助语境不误映为Papal court实体；Romanelli的“Pope’s nephew”保留为单一但未具名人物；Urbino城市、政治实体和教皇国分开。Senigaglia see、Antonio侄辈及相关历史范围按来源表述保存，不用邻文猜定身份。

S6影响核查：relations.csv无改动。直接命中的既有formal裁决仍为rel-2272（太阳主题）、rel-2275/2276（蜂／月桂主题）、rel-2277（Divine Providence）、rel-2278（巨人图像）、rel-2279（Sinigaglia地点）、rel-2285（Antonio兄弟的Capuchin membership）、rel-2286（Bracciolini任秘书）；候选和来源范围一致，未新增formal关系。S3未决端点尚不生成正式边。

逐ID判读与候选去向如下；来源页与具体claim在当前statement内可追溯。待证项不计入PASS。

| 顺位 | statement ID | 当前决定 | claim-specific candidates | 判读与范围 |
|---:|---|---|---|---|
{chr(10).join(decision_rows)}

批后：statement {len(statements):,}；mention {len(mentions):,}；PASS {after_counts['reviewed_current_pass']:,}（{after_counts['reviewed_current_pass']/len(roster)*100:.2f}%）；pending {after_counts['reviewed_current_pending']:,}。下一连续窗口2260–2359。该主审批次不构成全书独立语义接收。

工具与可恢复写入：[B578裁决脚本](adjudicate_s2_current_review_b578_order_2160_2259_20261103.py)先生成含输入／输出哈希、逐ID决定和来源指纹的review-plan.json；apply仅接受计划及输入未漂移，写前保留原始字节备份。关系表、H9622历史事件账本均非写入对象。
'''
    outputs={
        TABLES/'book-statements.jsonl':jsonl_bytes(st_raw,changed),
        PROCESS/'s2-current-review-roster.csv':csv_bytes(roster,rf,reol,rbom),
        TABLES/'mentions.csv':csv_bytes(mentions,mf,meol,mbom),
        TABLES/'entity-candidates.csv':csv_bytes(candidates,cf,ceol,cbom),
        TABLES/'alignment.csv':csv_bytes(alignment,af,aeol,abom),
    }
    old_bytes={p:p.read_bytes() for p in outputs}
    for path,addition in [(PROCESS/'stages.md',stage_record),(PROCESS.parent/'results/stages.md',f'\n\n### 2026-11-03 B578当前结果\n\n连续2160–2259的100条完成本轮处置：98 PASS、2 pending；94条由pending转PASS。S2新增{len(NEW_MENTIONS)}条原文mention，修复两幅穹顶画的共同主语与宫廷端点，并区分Sinigaglia主教辖区、城市及未具名侄辈。新增2项source-derived候选及2条S3 undecided alignment；既有关系表无改动。全书{len(statements):,} statements、{len(mentions):,} mentions，PASS {after_counts["reviewed_current_pass"]:,}、pending {after_counts["reviewed_current_pending"]:,}。下一连续窗口2260–2359；本批非独立接收。详见[过程](../process/stages.md#{STAGE})与[当前交接结果](../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。\n')]:
        text,eol,bom,raw=read_text(path);old_bytes[path]=raw
        require(f'id="{STAGE}"' not in text,'B578 process record already exists')
        outputs[path]=text_bytes(text.rstrip()+addition,eol,bom)
    result_path=ROOT/'04-knowledge/results/patrons-and-painters-full-book-s2.md'
    rt,eol,bom,raw=read_text(result_path);old_bytes[result_path]=raw
    line=(f'**后续顺序（逐阶段执行）：** **S1 → S2 → S3 → S4 → S5 → S6 → S7。** S1索引、图版、书目及候选来源映射复核已完成。B578连续2160–2259完成：98 PASS、2 pending，新增{len(NEW_MENTIONS)}条精确mention；两幅穹顶画共同指向新宫廷文学兴趣，Sinigaglia教座与城市分开，未具名侄辈保留身份待S3。新增2项候选与2条undecided alignment；现有关系裁决未改。当前S2为{len(statements):,}条statement、{len(mentions):,}条mention；逐ID复核PASS {after_counts["reviewed_current_pass"]:,}（{after_counts["reviewed_current_pass"]/len(roster)*100:.2f}%）、pending {after_counts["reviewed_current_pending"]:,}，尚未全书独立语义接收。H9622历史事件账本9,622行不改写。下一连续窗口2260–2359。S3–S6逐类收口，S7待前序阶段收口后开展。详见[本批过程](../../03-processing/patrons-and-painters-full-book-s2/process/stages.md#{STAGE})。')
    rt,count=re.subn(r'(?m)^\*\*后续顺序（逐阶段执行）：\*\*[^\r\n]*',lambda _:line,rt,count=1)
    require(count==1,'Current result summary anchor missing')
    outputs[result_path]=text_bytes(rt,eol,bom)
    relation_hash=sha(rel_raw)
    summary={'batch':BATCH,'window':[2160,2259],'window_before':{'pass':4,'pending':96},'window_after':{'pass':98,'pending':2},'promoted':94,'statements_changed':len(changed),'mentions_added':len(NEW_MENTIONS),'new_candidates':['cand-12479','cand-12480'],'new_alignments':['aln-12808','aln-12809'],'global_after':dict(after_counts),'statement_count':len(statements),'mention_count':len(mentions),'candidate_count':len(candidates),'alignment_count':len(alignment),'relations_sha256':relation_hash,'cross_window_pass_fingerprint_refresh':cross_window}
    plan={'summary':summary,'source_sha256':EXPECTED_SOURCE,'pdf_sha256':EXPECTED_PDF,'history_sha256':EXPECTED_HISTORY,
          'inputs':{p.relative_to(ROOT).as_posix():sha(raw) for p,raw in old_bytes.items()},
          'outputs':{p.relative_to(ROOT).as_posix():sha(raw) for p,raw in outputs.items()},
          'statement_diffs':[{'order':rb[sid]['current_order'],'statement_id':sid,'before':old_statements[sid],'after':st} for sid,st in changed.items()],
          'retained_pending':PENDING,'mappings':{str(k):[cid(i) for i in v] for k,v in MAPPINGS.items()},'new_mentions':NEW_MENTIONS}
    RECOVERY.mkdir(parents=True,exist_ok=True)
    if not args.apply:
        PLAN.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'mode':'dry-run','plan':str(PLAN),**summary},ensure_ascii=False))
        return
    require(PLAN.exists(),'Run evidence/diff dry-run first')
    require(json.loads(PLAN.read_text(encoding='utf-8'))==json.loads(json.dumps(plan,ensure_ascii=False)),'Plan or current inputs changed; inspect before replanning')
    for p,raw in old_bytes.items(): require(p.read_bytes()==raw,'Input drift before apply: '+str(p))
    for p,raw in old_bytes.items():
        dest=RECOVERY/'before'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():
            require(dest.read_bytes()==raw,'Existing recovery copy differs from current pre-apply bytes: '+str(dest))
        else:
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
    require(sha(HISTORY.read_bytes())==EXPECTED_HISTORY,'History ledger changed during apply')
    require(sha((TABLES/'relations.csv').read_bytes())==relation_hash,'Relations table changed during apply')
    (RECOVERY/'applied.json').write_text(json.dumps({'summary':summary,'applied_outputs':plan['outputs']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'mode':'applied',**summary},ensure_ascii=False))


if __name__=='__main__':
    main()

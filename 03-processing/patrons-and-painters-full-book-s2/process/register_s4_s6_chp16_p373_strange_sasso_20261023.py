#!/usr/bin/env python3
"""Register the Chapter 16 Strange-Sasso archive endpoints and adjudicate S6.

Default mode builds a targeted preview without changing project files. Use
--apply only after reviewing the source-to-KU mappings and all 19 decisions.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_ANCHOR = "s4-s5-s6-chp16-p373-strange-sasso-endpoints-20261023"
S2_REVIEW = PROCESS / "s2-independent-review-chp13-17-20261020.md"
STAGES = PROCESS / "stages.md"
KNOWLEDGE = PROCESS / "knowledge.md"
SOURCE_16 = "02-sources/02-Markdown/16_CHP-16_intro.md"
SOURCE_17 = "02-sources/02-Markdown/17_CHP-17_sec_i.md"
SOURCE_19 = "02-sources/02-Markdown/19_CHP-19Appendix.md"
SOURCE_21 = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
NOTE_SEGMENT = "chp-16:16_CHP-16_intro:l69-89"
BODY_SEGMENT = "chp-16:16_CHP-16_intro:l3-14"


NEW_KUS = [
    {
        "candidate_id": "cand-10604",
        "group": "archive-group-d2b5daf1a095",
        "ku_id": "units/archives/strange-to-sasso-letters-epistolario-moschini",
        "type": "archive",
        "sub_type": "letter_collection",
        "canonical_name": "约翰·斯特兰奇致萨索书信群",
        "name_en": "Letters from John Strange to Sasso",
        "card_path": "04-knowledge/units/archives/strange-to-sasso-letters-epistolario-moschini.md",
        "description_zh": (
            "本卡登记哈斯克尔第16章印刷页373注2所述John Strange致G. M. Sasso的复数书信。"
            "原书将其定位于Epistolario Moschini、威尼斯Biblioteca Correr，但没有给出封数、日期或单件索书号。"
            "书信及档案目录未独立查阅；本卡不将其与已登记的1777年10月8日单封书信自动等同。"
        ),
        "description_en": (
            "This unit records the plural group of letters from John Strange to G. M. Sasso described in Haskell's "
            "Chapter 16, p. 373, note 2. The book places them in the Epistolario Moschini at Biblioteca Correr, Venice, "
            "but gives no count, dates, or item-level shelfmarks. The letters and archival catalog have not been "
            "independently consulted; this group is not automatically identified with the separately registered letter "
            "of 8 October 1777."
        ),
        "name_value": "约翰·斯特兰奇致萨索书信群；来源局部描述性名称",
        "fields": [
            ("文献类型", "书信组；原文以复数 letters 指称，未给具体封数", "S1；第16章印刷页373注2 L71"),
            ("书内所报通信方向", "John Strange → G. M. Sasso", "S1；第16章印刷页373注2 L71"),
        ],
        "sources": [
            {
                "source_file": SOURCE_16,
                "location": "第16章，印刷页373，注2，L71；PDF物理页1。",
                "sentence_summary": "哈斯克尔称John Strange致Sasso的书信位于Epistolario Moschini。",
                "source_span": "line 71; printed p. 373, note 2; PDF physical p. 1",
                "quote": "The letters from Strange to Sasso are in the Epistolario Moschini",
            }
        ],
    },
    {
        "candidate_id": "cand-10605",
        "group": "archive-group-36ae30a621a5",
        "ku_id": "units/archives/epistolario-moschini",
        "type": "archive",
        "sub_type": "manuscript collection",
        "canonical_name": "莫斯基尼书信集",
        "name_en": "Epistolario Moschini manuscript series",
        "card_path": "04-knowledge/units/archives/epistolario-moschini.md",
        "description_zh": (
            "本卡登记哈斯克尔称为Epistolario Moschini的手稿书信系列。第16章注2和第19章附录7将相关书信定位于"
            "威尼斯Biblioteca Correr；第17章注6写作Epistolario Meschini并回指附录7。保留书内拼写差异；"
            "本系列及其馆藏目录未独立查阅。"
        ),
        "description_en": (
            "This unit records the manuscript correspondence series that Haskell calls the Epistolario Moschini. "
            "Chapter 16, note 2, and Chapter 19, Appendix 7, place related letters at Biblioteca Correr, Venice; "
            "Chapter 17, note 6 spells the name Epistolario Meschini and refers to Appendix 7. The source variants "
            "are retained, and neither the series nor its catalog has been independently consulted."
        ),
        "name_value": "Epistolario Moschini；书内使用的系列名称",
        "fields": [
            ("书内所称系列名称", "Epistolario Moschini；第17章注6另作 Epistolario Meschini", "S1、S2、S3；第16章 p.373 注2 L71；第17章 p.380 注6 L31；第19章 p.395 L197"),
            ("书内所报保管机构", "Biblioteca Correr, Venice；仅为Haskell书内定位，未查馆藏目录或手稿", "S1、S3；第16章 p.373 注2 L71（印本拼作 Correr）；第19章 p.395 L197"),
        ],
        "sources": [
            {
                "source_file": SOURCE_16,
                "location": "第16章，印刷页373，注2，L71；PDF物理页1。OCR将Correr识为Cotter，按印本图像记录校正。",
                "sentence_summary": "脚注将Strange致Sasso书信定位于Epistolario Moschini和威尼斯图书馆。",
                "source_span": "line 71; printed p. 373, note 2; PDF physical p. 1; OCR Cotter corrected to printed Correr",
                "quote": "Epistolario Moschini, Biblioteca Cotter, Venice",
            },
            {
                "source_file": SOURCE_17,
                "location": "第17章，印刷页380，注6，L31。",
                "sentence_summary": "脚注以Meschini拼写系列名并回指附录7。",
                "source_span": "line 31; printed p. 380, note 6",
                "quote": "Biblioteca Correr—Epistolario Meschini—published in full in Appendix 7",
            },
            {
                "source_file": SOURCE_19,
                "location": "第19章，印刷页395，附录7标题，L197；PDF物理页10。",
                "sentence_summary": "附录7标题将Manfrin书信定位于Biblioteca Correr的Epistolario Moschini。",
                "source_span": "line 197; printed p. 395; PDF physical p. 10",
                "quote": "Biblioteca Correr, Venice—Epistolario Moschini",
            },
        ],
    },
    {
        "candidate_id": "cand-10606",
        "group": "archive-group-9c46e57b3bc4",
        "ku_id": "units/archives/mauroner-collezionisti-vedutisti-1947",
        "type": "archive",
        "sub_type": "journal_article",
        "canonical_name": "十八世纪威尼斯的收藏家与风景画家",
        "name_en": "Collezionisti e vedutisti settecenteschi a Venezia",
        "card_path": "04-knowledge/units/archives/mauroner-collezionisti-vedutisti-1947.md",
        "description_zh": (
            "本卡登记哈斯克尔书目所列F. Mauroner文章。题名保留意大利文；中文题名为项目工作译名。"
            "第16章注2称该文第48–50页引有Strange致Sasso书信。文章及所引页码未独立查阅，不补责任者全名、卷期或出版细节。"
        ),
        "description_en": (
            "This unit records the article by F. Mauroner as listed in Haskell's bibliography. The Italian title is "
            "retained; the Chinese rendering is a project working translation. Chapter 16, note 2, says that pages "
            "48–50 quote letters from Strange to Sasso. The article and cited pages have not been independently "
            "consulted; no fuller author name, volume, issue, or publication detail is inferred."
        ),
        "name_value": "十八世纪威尼斯的收藏家与风景画家；中文工作译名，非原题",
        "fields": [
            ("原文题名", "Collezionisti e vedutisti settecenteschi a Venezia", "S2；第21章书目 p.429 L782"),
            ("书目责任者形式", "F. Mauroner；不扩写名首字母", "S2；第21章书目 p.429 L782"),
            ("期刊", "Arte Veneta", "S2；第21章书目 p.429 L781–782"),
            ("书目年份", "1947", "S2；第21章书目 p.429 L782"),
            ("书目页码", "48–50", "S2；第21章书目 p.429 L782"),
        ],
        "sources": [
            {
                "source_file": SOURCE_16,
                "location": "第16章，印刷页373，注2，L71；PDF物理页1。",
                "sentence_summary": "哈斯克尔称Mauroner 1947年文章第48–50页引有相关书信。",
                "source_span": "line 71; printed p. 373, note 2; PDF physical p. 1",
                "quote": "Mauroner, 1947, pp. 48-50",
            },
            {
            "source_file": SOURCE_21,
                "location": "第21章书目，印刷页429，L781–782。",
                "sentence_summary": "书目列出作者形式F. Mauroner、期刊Arte Veneta、文章题名、1947年及页码48–50。",
                "source_span": "lines 781-782; printed p. 429",
                "quote": "Collezionisti e vedutisti settecenteschi a Venezia",
            },
        ],
    },
    {
        "candidate_id": "cand-10607",
        "group": "archive-group-4121c2b1989e",
        "ku_id": "units/archives/sasso-to-strange-four-letters-british-museum-add-ms-23730",
        "type": "archive",
        "sub_type": "letter_group",
        "canonical_name": "萨索致约翰·斯特兰奇四封书信",
        "name_en": "Four Letters from Sasso to John Strange",
        "card_path": "04-knowledge/units/archives/sasso-to-strange-four-letters-british-museum-add-ms-23730.md",
        "description_zh": (
            "本卡登记哈斯克尔第16章p.373注2报告的四封Sasso致John Strange书信，定位为British Museum所藏Add. MSS. 23,730，"
            "ff.359–363。书信未独立查阅；本卡与Epistolario Moschini中的Strange致Sasso书信群及1777年单封信分开。"
        ),
        "description_en": (
            "This unit records the four letters from Sasso to John Strange that Haskell reports in Chapter 16, p. 373, "
            "note 2, at the British Museum under Add. MSS. 23,730, folios 359–363. The manuscripts have not been "
            "independently consulted. This group remains distinct from the Strange-to-Sasso group in the Epistolario "
            "Moschini and from the separately registered 1777 letter."
        ),
        "name_value": "萨索致约翰·斯特兰奇四封书信；来源局部描述性名称",
        "fields": [
            ("文献类型", "书信组", "S1；第16章印刷页373注2 L71"),
            ("书内所报数量", "4封", "S1；第16章印刷页373注2 L71"),
            ("书内所报通信方向", "G. M. Sasso → John Strange", "S1；第16章印刷页373注2 L71"),
            ("书内所报馆藏与索书号", "British Museum, Add. MSS. 23,730, ff. 359–363；未独立查阅", "S1；第16章印刷页373注2 L71"),
        ],
        "sources": [
            {
                "source_file": SOURCE_16,
                "location": "第16章，印刷页373，注2，L71；PDF物理页1。",
                "sentence_summary": "哈斯克尔称有四封Sasso致Strange的信存于British Museum所列手稿号和叶码。",
                "source_span": "line 71; printed p. 373, note 2; PDF physical p. 1",
                "quote": "four letters from him to Strange in the British Museum, Add. MSS. 23,730",
            }
        ],
    },
]


RELATION_SPECS = [
    {
        "statement_id": "st-chp16-p373-sasso-strange-corresponded-nearly-twenty-years",
        "subject": "units/persons/g-m-sasso",
        "object": "units/persons/john-strange",
        "predicate": "corresponded_with",
        "time": "nearly twenty years (as stated by Haskell; no exact dates supplied)",
        "role": "书信往来",
        "scope": "Haskell says Sasso and Strange corresponded for nearly twenty years. The duration is approximate; neither the letters nor their dates were independently checked. The four Sasso-to-Strange letters in note 2 are additional evidence for this correspondence, not a separate relationship.",
        "note": "S2 statements: st-chp16-p373-sasso-strange-corresponded-nearly-twenty-years; st-chp16-p373-note2-sasso-wrote-four-letters-to-strange.",
        "source_span": "Chapter 16, printed p. 373 L12-13 and note 2 L71; PDF physical p. 1; both cited S2 statements",
        "source_file": SOURCE_16,
    },
    {
        "statement_id": "st-chp16-p373-strange-employed-sasso-to-buy-pictures",
        "subject": "units/persons/g-m-sasso",
        "object": "units/persons/john-strange",
        "predicate": "employed_by",
        "time": "",
        "role": "受雇代购威尼斯绘画",
        "scope": "Haskell says Strange employed Sasso to buy Venetian pictures for him. This records the stated purchasing role only; no dates, contract, or legal employment terms are supplied.",
        "note": "Direction is Sasso employed_by Strange, matching the stated employer and purchasing agent.",
        "source_span": "Chapter 16, printed p. 373 L13-14; PDF physical p. 1; statement=st-chp16-p373-strange-employed-sasso-to-buy-pictures",
        "source_file": SOURCE_16,
    },
    {
        "statement_id": "st-chp16-p373-sasso-strange-did-lucrative-business",
        "subject": "units/persons/g-m-sasso",
        "object": "units/persons/john-strange",
        "predicate": "collaborated_with",
        "time": "",
        "role": "共同从事书中所述业务",
        "scope": "Haskell says Sasso and Strange did involved, lucrative business together. The edge is limited to this reported joint business activity; it does not assert a legal partnership, equal roles, or specific transactions.",
        "note": "The controlled collaborator relation records only the source's explicit joint-business statement.",
        "source_span": "Chapter 16, printed p. 373 L13; PDF physical p. 1; statement=st-chp16-p373-sasso-strange-did-lucrative-business",
        "source_file": SOURCE_16,
    },
    {
        "statement_id": "st-chp16-p373-note2-strange-sasso-letters-in-epistolario",
        "subject": "units/archives/strange-to-sasso-letters-epistolario-moschini",
        "object": "units/archives/epistolario-moschini",
        "predicate": "part_of",
        "time": "",
        "role": "书信系列成员",
        "scope": "Haskell locates the Strange-to-Sasso letters in the Epistolario Moschini. The individual letters, series catalog, and item-level shelfmarks were not independently consulted.",
        "note": "This plural letter group is distinct from the known 1777 letter unit because no item-level identity is supplied.",
        "source_span": "Chapter 16, printed p. 373, note 2 L71; PDF physical p. 1; statement=st-chp16-p373-note2-strange-sasso-letters-in-epistolario",
        "source_file": SOURCE_16,
    },
    {
        "statement_id": "st-chp16-p373-note2-mauroner-quotes-letters",
        "subject": "units/archives/mauroner-collezionisti-vedutisti-1947",
        "object": "units/archives/strange-to-sasso-letters-epistolario-moschini",
        "predicate": "cites",
        "time": "1947 (bibliographic year as listed by Haskell)",
        "role": "刊文引述书信",
        "scope": "Haskell says pages 48-50 of Mauroner's 1947 article contain quotations from the Strange-to-Sasso letters. The article and those pages were not independently consulted.",
        "note": "The edge points from the article to the quoted letter group; no article content beyond Haskell's citation is asserted.",
        "source_span": "Chapter 16, printed p. 373, note 2 L71; Chapter 21 bibliography printed p. 429 L781-782; statement=st-chp16-p373-note2-mauroner-quotes-letters",
        "source_file": SOURCE_16,
    },
    {
        "statement_id": "st-chp16-p373-note2-epistolario-at-correr",
        "subject": "units/archives/epistolario-moschini",
        "object": "units/institutions/correr-library",
        "predicate": "located_at",
        "time": "",
        "role": "Haskell书内报告的馆藏定位",
        "scope": "Haskell's note locates the Epistolario Moschini at Biblioteca Correr, Venice. The OCR transcription says Cotter; the printed reading Correr was checked against Chapter 16 PDF physical page 1. The manuscript and current catalog were not consulted.",
        "note": "Uses the existing Correr Library KU, not the distinct Museo Correr parent institution.",
        "source_span": "Chapter 16, printed p. 373, note 2 L71; PDF physical p. 1; statement=st-chp16-p373-note2-epistolario-at-correr",
        "source_file": SOURCE_16,
    },
    {
        "statement_id": "st-chp19-p395-manfrin-edwards-letter-source",
        "subject": "units/archives/manfrin-edwards-letter-1793-12-03",
        "object": "units/archives/epistolario-moschini",
        "predicate": "part_of",
        "time": "1793-12-03 (letter date stated in Appendix 7 heading)",
        "role": "书信系列成员",
        "scope": "Appendix 7 identifies the 3 December 1793 Manfrin-to-Edwards letter and locates it in the Epistolario Moschini at Biblioteca Correr. The manuscript and catalog were not independently consulted.",
        "note": "The single letter remains distinct from the collection-level KU.",
        "source_span": "Chapter 19, printed p. 395, Appendix 7 heading L197; PDF physical p. 10; statement=st-chp19-p395-manfrin-edwards-letter-source",
        "source_file": SOURCE_19,
    },
    {
        "statement_id": "st-chp16-p373-note2-four-sasso-letters-british-museum",
        "subject": "units/archives/sasso-to-strange-four-letters-british-museum-add-ms-23730",
        "object": "units/institutions/british-museum",
        "predicate": "located_at",
        "time": "",
        "role": "书内报告的馆藏与档号定位",
        "scope": "Haskell reports four letters from Sasso to Strange at the British Museum under Add. MSS. 23,730, folios 359-363. The manuscripts and current catalog were not independently consulted.",
        "note": "The relation is limited to Haskell's reported holding and locator; it does not merge this group with the Epistolario Moschini series.",
        "source_span": "Chapter 16, printed p. 373, note 2 L71; PDF physical p. 1; statement=st-chp16-p373-note2-four-sasso-letters-british-museum",
        "source_file": SOURCE_16,
    },
    {
        "statement_id": "st-chp16-p373-note2-strange-letters-authored-by-john-strange",
        "subject": "units/archives/strange-to-sasso-letters-epistolario-moschini",
        "object": "units/persons/john-strange",
        "predicate": "authored_by",
        "time": "",
        "role": "书内所报发信人",
        "scope": "The note explicitly describes these as letters from Strange to Sasso. This records Haskell's attribution for the source-local group; the letters were not consulted.",
        "note": "No dates or item-level authorship evidence are supplied.",
        "source_span": "Chapter 16, printed p. 373, note 2 L71; PDF physical p. 1; statement=st-chp16-p373-note2-strange-letters-authored-by-john-strange",
        "source_file": SOURCE_16,
    },
    {
        "statement_id": "st-chp16-p373-note2-strange-letters-addressed-to-sasso",
        "subject": "units/archives/strange-to-sasso-letters-epistolario-moschini",
        "object": "units/persons/g-m-sasso",
        "predicate": "addressed_to",
        "time": "",
        "role": "书内所报收信人",
        "scope": "The note explicitly describes these as letters from Strange to Sasso. This records Haskell's stated addressee for the source-local group; the letters were not consulted.",
        "note": "The recipient is the existing Sasso person KU; name variation is preserved in that card.",
        "source_span": "Chapter 16, printed p. 373, note 2 L71; PDF physical p. 1; statement=st-chp16-p373-note2-strange-letters-addressed-to-sasso",
        "source_file": SOURCE_16,
    },
    {
        "statement_id": "st-chp16-p373-note2-sasso-letters-authored-by-sasso",
        "subject": "units/archives/sasso-to-strange-four-letters-british-museum-add-ms-23730",
        "object": "units/persons/g-m-sasso",
        "predicate": "authored_by",
        "time": "",
        "role": "书内所报发信人",
        "scope": "The note says there are four letters from him to Strange immediately after identifying Sasso's replies. This records Haskell's attribution of the four-letter group to Sasso; the manuscripts were not consulted.",
        "note": "The pronoun is resolved to Sasso from the immediately preceding sentence; this group remains distinct from the Strange-to-Sasso collection.",
        "source_span": "Chapter 16, printed p. 373, note 2 L71; PDF physical p. 1; statement=st-chp16-p373-note2-sasso-letters-authored-by-sasso",
        "source_file": SOURCE_16,
    },
    {
        "statement_id": "st-chp16-p373-note2-sasso-letters-addressed-to-strange",
        "subject": "units/archives/sasso-to-strange-four-letters-british-museum-add-ms-23730",
        "object": "units/persons/john-strange",
        "predicate": "addressed_to",
        "time": "",
        "role": "书内所报收信人",
        "scope": "The note explicitly says the four letters are from Sasso to Strange. This records Haskell's stated addressee for the group; the manuscripts were not consulted.",
        "note": "The addressee is the existing John Strange person KU.",
        "source_span": "Chapter 16, printed p. 373, note 2 L71; PDF physical p. 1; statement=st-chp16-p373-note2-sasso-letters-addressed-to-strange",
        "source_file": SOURCE_16,
    },
]

RELATION_ROW_ORDER = [
    "st-chp16-p373-note2-strange-sasso-letters-in-epistolario",
    "st-chp16-p373-note2-mauroner-quotes-letters",
    "st-chp16-p373-note2-epistolario-at-correr",
    "st-chp19-p395-manfrin-edwards-letter-source",
    "st-chp16-p373-note2-four-sasso-letters-british-museum",
    "st-chp16-p373-sasso-strange-corresponded-nearly-twenty-years",
    "st-chp16-p373-strange-employed-sasso-to-buy-pictures",
    "st-chp16-p373-sasso-strange-did-lucrative-business",
    "st-chp16-p373-note2-strange-letters-authored-by-john-strange",
    "st-chp16-p373-note2-strange-letters-addressed-to-sasso",
    "st-chp16-p373-note2-sasso-letters-authored-by-sasso",
    "st-chp16-p373-note2-sasso-letters-addressed-to-strange",
]


NEW_STATEMENTS = [
    {
        "statement_id": "st-chp16-p373-note2-strange-letters-authored-by-john-strange",
        "subject_candidate_id": "cand-10604",
        "object_candidate_id": "cand-2517",
        "predicate": "authored_by",
        "claim": "Haskell identifies John Strange as the sender of the letters from Strange to Sasso named in note 2.",
        "quote": "The letters from Strange to Sasso",
        "note": "Records the source-stated sender for the plural letter group; no individual letter or date is identified.",
    },
    {
        "statement_id": "st-chp16-p373-note2-strange-letters-addressed-to-sasso",
        "subject_candidate_id": "cand-10604",
        "object_candidate_id": "cand-2364",
        "predicate": "addressed_to",
        "claim": "Haskell identifies Sasso as the addressee of the letters from Strange to Sasso named in note 2.",
        "quote": "letters from Strange to Sasso",
        "note": "Records the source-stated recipient for the plural letter group; no individual letter or date is identified.",
    },
    {
        "statement_id": "st-chp16-p373-note2-sasso-letters-authored-by-sasso",
        "subject_candidate_id": "cand-10607",
        "object_candidate_id": "cand-2364",
        "predicate": "authored_by",
        "claim": "Haskell attributes the four letters from him to Strange to Sasso, the antecedent of him in the preceding clause.",
        "quote": "four letters from him to Strange",
        "note": "Resolves him to Sasso from the immediately preceding phrase Sasso's replies; the letters were not consulted.",
    },
    {
        "statement_id": "st-chp16-p373-note2-sasso-letters-addressed-to-strange",
        "subject_candidate_id": "cand-10607",
        "object_candidate_id": "cand-2517",
        "predicate": "addressed_to",
        "claim": "Haskell identifies John Strange as the addressee of four letters from Sasso.",
        "quote": "four letters from him to Strange",
        "note": "Records the source-stated recipient for the four-letter group; the manuscripts were not consulted.",
    },
]


REJECTED = {
    "st-chp16-p373-sasso-strange-shared-social-complaints": "The passage reports a shared conversational topic, not a durable relationship represented by a controlled predicate.",
    "st-chp16-p373-sasso-strange-on-excellent-terms": "Excellent terms do not by themselves establish friendship; no friend_of edge is inferred.",
    "st-chp16-p373-sasso-strange-saw-each-other": "The source reports meetings but identifies no event-level object or controlled relation that the current schema can express without invention.",
    "st-chp16-p373-sasso-strange-condoled-losses-and-illnesses": "This is episodic conduct during losses and illnesses, not a separate durable relation; no friendship or care predicate is inferred.",
    "st-chp16-p373-sasso-strange-exchanged-gossip": "This reports conversational activity without an applicable controlled relation; correspondence is separately recorded from explicit source evidence.",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bytes, str]:
    raw = path.read_bytes()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    text = raw[len(bom):].decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    with io.StringIO(text, newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader), bom, newline


def csv_bytes(fields: list[str], rows: list[dict[str, str]], bom: bytes, newline: str) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore", lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    return bom + out.getvalue().encode("utf-8")


def read_text(path: Path) -> tuple[str, bytes, str]:
    raw = path.read_bytes()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    text = raw[len(bom):].decode("utf-8")
    return text, bom, "\r\n" if "\r\n" in text else "\n"


def text_bytes(text: str, bom: bytes) -> bytes:
    return bom + text.encode("utf-8")


def read_jsonl(path: Path) -> tuple[list[dict], bytes, str]:
    raw = path.read_bytes()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    text = raw[len(bom):].decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return rows, bom, newline


def targeted_jsonl_bytes(path: Path, updates: dict[str, dict], additions: list[dict], bom: bytes, newline: str) -> bytes:
    raw = path.read_bytes()
    body = raw[len(bom):]
    lines = body.splitlines(keepends=True)
    seen: set[str] = set()
    output: list[bytes] = []
    for raw_line in lines:
        stripped = raw_line.rstrip(b"\r\n")
        if not stripped:
            output.append(raw_line)
            continue
        row = json.loads(stripped.decode("utf-8"))
        key = row.get("statement_id", "")
        if key in updates:
            row = updates[key]
            seen.add(key)
            ending = b"\r\n" if raw_line.endswith(b"\r\n") else b"\n" if raw_line.endswith(b"\n") else b""
            output.append(json.dumps(row, ensure_ascii=False).encode("utf-8") + ending)
        else:
            output.append(raw_line)
    if seen != set(updates):
        raise AssertionError(f"target statement update missing from JSONL: {sorted(set(updates) - seen)}")
    if output and not output[-1].endswith((b"\n", b"\r")):
        output.append(newline.encode("ascii"))
    output.extend(json.dumps(row, ensure_ascii=False).encode("utf-8") + newline.encode("ascii") for row in additions)
    return bom + b"".join(output)


def append_jsonl_bytes(path: Path, additions: list[dict], bom: bytes, newline: str) -> bytes:
    old = path.read_bytes()
    if old and not old.endswith((b"\n", b"\r")):
        old += newline.encode("ascii")
    return old + b"".join(json.dumps(row, ensure_ascii=False).encode("utf-8") + newline.encode("ascii") for row in additions)


def primary_alignments(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row.get("candidate_id", ""), []).append(row)
    result = {}
    for candidate_id, candidate_rows in grouped.items():
        primary = [row for row in candidate_rows if not row.get("external_source")]
        if len(primary) == 1:
            result[candidate_id] = primary[0]
    return result


def add_units_to_accepted(text: str, new_paths: list[str], newline: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.strip() == "units:"), None)
    if start is None:
        raise AssertionError("accepted.yml has no units section")
    end = start + 1
    while end < len(lines):
        stripped = lines[end].strip()
        if stripped and not lines[end].startswith((" ", "\t", "- ")):
            break
        end += 1
    existing = {line.strip()[2:] for line in lines[start + 1:end] if line.startswith("- 04-knowledge/units/")}
    if existing.intersection(new_paths):
        raise AssertionError(f"accepted.yml already contains target cards: {sorted(existing.intersection(new_paths))}")
    block = lines[start + 1:end] + [f"- {path}{newline}" for path in new_paths]
    return "".join(lines[:start + 1] + block + lines[end:])


def make_card(spec: dict) -> str:
    source_items = []
    for item in spec["sources"]:
        source_items.append(
            {
                "citation": BOOK_CITATION,
                "location": item["location"],
                "sentence_summary": item["sentence_summary"],
                "original_quotes": [{"source_span": item["source_span"], "text": item["quote"]}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": item["source_file"],
                    "source_span": item["source_span"],
                },
            }
        )
    frontmatter = {
        "title": f"{spec['canonical_name']}（{spec['name_en']}）",
        "name_en": spec["name_en"],
        "type": spec["type"],
        "sub_type": spec["sub_type"],
        "evidence_status": "source_backed",
        "sources": source_items,
        "created": "2026-10-23",
        "updated": "2026-10-23",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    rel_path = "../../../" + SOURCE_16
    body = [
        "## 内容",
        "",
        "### 描述",
        "",
        f"**中文：** {spec['description_zh']} [第16章 p.373](../../../{SOURCE_16}#L71)。",
        "",
        f"**English:** {spec['description_en']} [Chapter 16, p. 373](../../../{SOURCE_16}#L71).",
        "",
        "### 名称",
        "",
        "| 字段 | 值 | 证据 |",
        "|---|---|---|",
        f"| 描述性名称 | {spec['name_value']} | {spec['fields'][0][2].split('；', 1)[0]}；依据书内名称形成的项目描述名称 |",
        "",
        "### 文献身份与定位",
        "",
        "| 字段 | 值 | 证据 |",
        "|---|---|---|",
    ]
    body.extend(f"| {field} | {value} | {basis} |" for field, value, basis in spec["fields"])
    body.extend(
        [
            "",
            "## 关系与证据",
            "",
            "### 身份与来源边界",
            "",
            f"- **S3身份组：** `{spec['group']}`；候选 `{spec['candidate_id']}`；KU `{spec['ku_id']}`。",
            "- 所有书信馆藏定位和书目信息均为Haskell书内报告；未据此声称查阅原件或对应文献全文。",
            "",
            "### 关系记录",
            "",
            "正式关系以 `relations.csv` 为准。",
            "",
            "### 关系候选入口",
            "",
            f"[S2–S6过程记录](../../../03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR})",
            "",
        ]
    )
    return f"---\n{fm}---\n\n" + "\n".join(body)


def make_new_statements() -> list[dict]:
    rows = []
    body_link = ["st-chp16-p373-sasso-strange-corresponded-nearly-twenty-years"]
    for spec in NEW_STATEMENTS:
        candidate_ids = [spec["subject_candidate_id"], spec["object_candidate_id"]]
        row = {
            "statement_id": spec["statement_id"],
            "segment_id": NOTE_SEGMENT,
            "subject_candidate_id": spec["subject_candidate_id"],
            "object_candidate_id": spec["object_candidate_id"],
            "predicate": spec["predicate"],
            "qualifiers": {
                "source_line_start": 71,
                "source_line_end": 71,
                "printed_page": 373,
                "pdf_physical_page": 1,
                "claim": spec["claim"],
                "speaker": "Haskell, note 2",
                "text_layer": "authorial archival locator",
                "qualification": "The statements record Haskell's report only. The cited letters and manuscript records were not independently consulted.",
                "mentioned_candidate_ids": candidate_ids,
                "relation_candidate": True,
                "relation_candidate_note": spec["note"],
                "footnote_marker": "2",
                "footnote_number": 2,
                "footnote_segment": NOTE_SEGMENT,
                "footnote_refs": [{"marker": 2, "segment_id": NOTE_SEGMENT, "source_line": 71}],
                "related_segment": BODY_SEGMENT,
                "related_body_statement_ids": body_link,
                "linked_body_statement_ids": body_link,
                "footnote_link_status": "linked",
                "footnote_text_pending": False,
            },
            "original_quote": spec["quote"],
            "origin": "book",
            "source_file": SOURCE_16,
        }
        rows.append(row)
    return rows


def load_field_builder():
    root_text = str(ROOT)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    path = ROOT / "scripts" / "build_field_facts.py"
    spec = importlib.util.spec_from_file_location("build_field_facts_chp16_sasso_batch", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load field builder: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_relation_rows(next_id: int) -> list[dict[str, str]]:
    rows = []
    specs_by_id = {spec["statement_id"]: spec for spec in RELATION_SPECS}
    for offset, statement_id in enumerate(RELATION_ROW_ORDER, start=next_id):
        spec = specs_by_id[statement_id]
        rows.append(
            {
                "relation_id": f"rel-{offset:04d}",
                "subject_ku_id": spec["subject"],
                "object_ku_id": spec["object"],
                "predicate": spec["predicate"],
                "time": spec["time"],
                "role": spec["role"],
                "scope": spec["scope"],
                "origin": "book",
                "status": "formal",
                "source_id": "haskell-1980-rev-ed",
                "source_span": spec["source_span"],
                "source_file": spec["source_file"],
                "note": spec["note"] + f" Source=Haskell's book account; statement={spec['statement_id']}.",
            }
        )
    return rows


def relation_decision_rows(relation_by_statement: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    decisions = []
    for spec in RELATION_SPECS:
        row = relation_by_statement[spec["statement_id"]]
        decisions.append(
            {
                "statement_id": spec["statement_id"],
                "decision": "formal",
                "relation": f"{row['relation_id']} {spec['predicate']}",
                "reason": spec["scope"],
            }
        )
    decisions.extend(
        [
            {
                "statement_id": "st-chp16-p373-note2-correr-in-venice",
                "decision": "formal",
                "relation": "rel-0316 located_at (reused)",
                "reason": "Haskell identifies Biblioteca Correr as being in Venice; the existing formal Correr Library-to-Venice relation directly expresses this location and is reused without duplicating the edge.",
            },
            {
                "statement_id": "st-chp16-p373-note2-sasso-wrote-four-letters-to-strange",
                "decision": "formal",
                "relation": f"{relation_by_statement['st-chp16-p373-sasso-strange-corresponded-nearly-twenty-years']['relation_id']} corresponded_with (shared evidence)",
                "reason": "The note identifies four Sasso-to-Strange letters; this is additional evidence for the correspondence relation already supported by the p.373 narrative, not a second duplicate edge.",
            },
        ]
    )
    for statement_id, reason in REJECTED.items():
        decisions.append({"statement_id": statement_id, "decision": "rejected", "relation": "—", "reason": reason})
    order = [
        "st-chp16-p373-sasso-strange-corresponded-nearly-twenty-years",
        "st-chp16-p373-sasso-strange-shared-social-complaints",
        "st-chp16-p373-strange-employed-sasso-to-buy-pictures",
        "st-chp16-p373-sasso-strange-on-excellent-terms",
        "st-chp16-p373-sasso-strange-saw-each-other",
        "st-chp16-p373-sasso-strange-condoled-losses-and-illnesses",
        "st-chp16-p373-sasso-strange-exchanged-gossip",
        "st-chp16-p373-sasso-strange-did-lucrative-business",
        "st-chp16-p373-note2-strange-sasso-letters-in-epistolario",
        "st-chp16-p373-note2-mauroner-quotes-letters",
        "st-chp16-p373-note2-four-sasso-letters-british-museum",
        "st-chp16-p373-note2-epistolario-at-correr",
        "st-chp16-p373-note2-correr-in-venice",
        "st-chp16-p373-note2-sasso-wrote-four-letters-to-strange",
        "st-chp19-p395-manfrin-edwards-letter-source",
        *[row["statement_id"] for row in NEW_STATEMENTS],
    ]
    by_id = {row["statement_id"]: row for row in decisions}
    return [by_id[key] for key in order]


def update_knowledge(text: str, block: str, newline: str) -> str:
    marker = "# 全书 S3 身份对齐过程"
    if marker not in text or PROCESS_ANCHOR in text:
        raise AssertionError("knowledge.md header missing or this batch is already recorded")
    return text.replace(marker, marker + newline + newline + block.rstrip() + newline, 1)


def make_process_block(field_records: list[dict], decisions: list[dict[str, str]], relation_rows: list[dict[str, str]],
                       candidate_mappings: list[dict], newline: str) -> str:
    s4_lines = ["| 候选 | S3身份组 | S4 KU | 类型 |", "|---|---|---|---|"]
    s4_lines.extend(
        f"| `{spec['candidate_id']}` | `{spec['group']}` | `{spec['ku_id']}` | archive |" for spec in NEW_KUS
    )
    fields = ["| enrichment ID | KU | 字段 | 状态 |", "|---|---|---|---|"]
    fields.extend(
        f"| `{row['enrichment_id']}` | `{row['ku_id']}` | {row['field']} | {row['evidence_status']} |"
        for row in field_records
    )
    s6 = ["| S2关系候选 | 决定 | 正式关系 | 裁决理由与边界 |", "|---|---|---|---|"]
    s6.extend(
        f"| `{row['statement_id']}` | {row['decision']} | {row['relation']} | {row['reason']} |" for row in decisions
    )
    lines = [
        f'<a id="{PROCESS_ANCHOR}"></a>',
        "### S4/S5/S6：第16章 p.373 Strange–Sasso 跨章书信端点（2026-10-23）",
        "",
        "**S3沿用与证据范围。** 沿用四个已存在的S3 `new`身份组 `archive-group-d2b5daf1a095`、`archive-group-36ae30a621a5`、`archive-group-9c46e57b3bc4`、`archive-group-4121c2b1989e`，分别映射John Strange致Sasso书信群、Epistolario Moschini系列、F. Mauroner 1947文章、Sasso致Strange四封信；S3决定与组号均未重开。Sasso、John Strange、Correr Library、British Museum、Manfrin 1793 letter复用当前已映射KU。没有查阅原信、馆藏目录或Mauroner文章。",
        "",
        "**S4登记。**",
        "",
        *s4_lines,
        "",
        "书信群、具体信件、档案系列和书目文章分别保留，不因同一通信背景而合并。Manfrin 1793年单封信与Epistolario Moschini系列分层；Strange致Sasso群与British Museum所藏Sasso致Strange四封信亦分开。",
        "",
        "**S2定向修复。** 第16章 p.373 注2当前segment `chp-16:16_CHP-16_intro:l69-89`此前将 `cand-2517` 列入提及候选，但缺脚注局部mention。按源段字符偏移补入John Strange两处mention：`m-chp16-p373-sasso-0031`（270–277）及 `m-chp16-p373-sasso-0032`（483–490）；没有改写来源正文。既有 `st-chp16-p373-note2-epistolario-at-correr` 增加 `Cotter`→`Correr` 的印本校读记录（CHP-16.pdf physical p.1）。新增四条原子关系statement：Strange书信群的发信人与收信人、Sasso四封信的发信人与收信人；这些定向补充不计入独立S2复核分子。",
        "",
        "**S5书内支持字段。** 新卡与原文/目录条目共抽取下列字段；F. Mauroner保持原书责任者形式，文章中文名为工作译名。字段的 `source_backed` 只表示Haskell书内依据，不代表原件或文章全文已核验。",
        "",
        *fields,
        "",
        "**S6逐候选裁决。** 本批共19条：14条formal、5条rejected。两条候选复用既有或本批关系记录：`st-chp16-p373-note2-correr-in-venice`复用 `rel-0316`（Correr Library `located_at` Venice）；`st-chp16-p373-note2-sasso-wrote-four-letters-to-strange`作为本批通信关系的第二项书内证据，复用 `rel-1595`。其余12条formal边见关系表；没有pending边。",
        "",
        *s6,
        "",
        "五条rejected均保留S2原始断言：共同抱怨、关系良好、见面、互相慰问、交换闲谈分别是短暂行为或不足以推断受控关系；不从`excellent terms`推为友谊，也不把交往活动扩写成契约、正式伙伴关系或新事件。Sasso与Strange的长期通信、为购画雇佣及共同从事有利可图业务则分别依原文按 `corresponded_with`、`employed_by`、`collaborated_with` 表达，后者不表示法律合伙或角色对等。",
        "",
        "批后全书统计、审计及定向卡片写回结果见[当前结果](../../../../04-knowledge/results/patrons-and-painters-full-book-s2.md)。",
        "",
    ]
    return newline.join(lines)


def make_stage_record(new_statements: list[dict], newline: str) -> str:
    lines = [
        "",
        "### 2026-10-23：第16章 p.373 注2 S2端点定向补充",
        "",
        "对照当前 `16_CHP-16_intro.md` L71、已登记segment `chp-16:16_CHP-16_intro:l69-89` 及CHP-16.pdf physical p.1。为Strange致Sasso书信群和Sasso致Strange四封信各新增发信人与收信人原子statement；共4条，均有S2端点且标为关系候选。原书中的 `Biblioteca Cotter` 按印本图像核作Correr，原始OCR来源不改写。",
        "",
        "| 新statement | 主体候选 | 客体候选 | 谓词 |",
        "|---|---|---|---|",
    ]
    lines.extend(
        f"| `{row['statement_id']}` | `{row['subject_candidate_id']}` | `{row['object_candidate_id']}` | `{row['predicate']}` |"
        for row in new_statements
    )
    lines.extend(
        [
            "",
            "本修复回应第13–17章独立复核表指出的两个脚注局部John Strange mention缺口；不把该定向修订算作独立复核。复核原有206条分子不变，当前第16章statement分母由206增至210；新增4条未由本批自审计入独立分子。",
            "",
        ]
    )
    return newline.join(lines)


def update_review_record(text: str, newline: str) -> str:
    old = "| 第16章 `16_CHP-16_intro.md` | 206（true 129 / false 77） | 206/206；p.373–378 | 0 | 不接收；有下列未修问题 |"
    new = "| 第16章 `16_CHP-16_intro.md` | 210（true 133 / false 77） | 206/210；p.373–378；新增4条S2端点statement未计入复核分子 | 4 | 不接收；有下列未修问题 |"
    if text.count(old) != 1:
        raise AssertionError("expected one current Chapter 16 S2 review coverage row")
    text = text.replace(old, new, 1)
    insertion = (
        "### 2026-10-23：第16章 p.373 注2定向修复补记"
        + newline + newline
        + "补录John Strange在注2源段的两处局部mention（segment字符270–277、483–490），并将印本所见 `Correr` 记录为OCR `Cotter` 的校读。另新增四条书信发信人/收信人原子statement，服务于已确定S3身份组的S4登记和S6裁决；这四条是定向增补，不属于本独立复核记录的审阅分子。因此第16章记录为206/210，整章仍不接收，原有待修项继续有效。"
        + newline + newline
    )
    marker = "## 第13章待修发现"
    if marker not in text:
        raise AssertionError("could not locate S2 review findings section")
    return text.replace(marker, insertion + marker, 1)


def update_results(text: str, newline: str) -> str:
    start_marker = "### 本轮进度与后续工作（2026-10-23）"
    next_marker = "### S4/S5/S6 archive：第10章 p.302"
    start = text.find(start_marker)
    end = text.find(next_marker, start + len(start_marker))
    if start < 0 or end < 0:
        raise AssertionError("cannot isolate current result summary block")
    block = [
        start_marker,
        "",
        "本轮完成第21批S4/S5/S6跨章端点工作：沿用四个既有S3 `new`组，登记四个archive KU及四条候选映射；补入两处脚注局部mention、四条书信发信/收信原子statement，并增加17条Haskell书内支持字段。对19条直接S6候选逐项裁决：14条formal、5条rejected，新增12条formal关系记录并复用两条既有/本批关系；未重开S3。原信、馆藏目录及Mauroner文章未独立查阅。逐项依据见[本批过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-s5-s6-chp16-p373-strange-sasso-endpoints-20261023)。",
        "",
        "**当前全书状态。** S0有832个源段（678 complete、154 excluded）。S2共15,253条statement；统一独立逐条复核9,573条（62.8%，尚未接收）；第七章1,146/1,264、第八章487/1,474；第3章1,173/1,183、第10–12章1,567/1,567的独立章节记录仍分开报告，均未接收；第16章当前复核记录206/210，新增4条定向statement不计入独立复核。统一复核台账仍待按statement ID与来源版本核平。S3主决定覆盖12,390/12,410个候选，缺20项；same=2,028、new=5,032（4,801组）、conflict=9、excluded=100、undecided=5,221（含622项类型未定）；另22项跨来源决定不同。S4已登记1,548/4,801组（32.2%）、1,765/5,032条候选映射（35.1%），待登记3,253组／3,267条映射。S5共12,452条字段，1,634条 `unverified`。relation_candidate=true共10,478条；S6已裁决610/10,478条（383 formal、160 pending、67 rejected；5.8%），余9,868条；`relations.csv`共1,601条（1,592 formal、9 pending）。339条关系候选至少缺一个S2端点候选ID（subject-only 46、object-only 221、both 72）。`candidate-backlog.csv`共10条，9条完成、1条明确undecided，pending=0。",
        "",
        "本批只记录Haskell书内归属、引注、通信与馆藏定位，不声称独立查阅书信原件、馆藏目录或Mauroner文章。S3决定与身份组未改变；新增S2关系statement及mention不计入独立复核分子。关系视图仅在定向预览后更新受影响卡片。",
        "",
        "**后续工作。**",
        "",
        "1. 按关系解锁价值继续登记已有S3决定的直接端点，同批完成所有相关S6候选。",
        "2. 回源处理339条缺S2端点候选ID的关系；只补原文明确、承担正式边的对象，再依S3→S4→S6处理。",
        "3. 先核平S2复核台账的statement ID与来源版本，再接续低覆盖章节的独立逐条审读；定向修订不并入复核分子。",
        "4. S3只在当前登记或新证据触发时复核；逐类型推进既有未决队列。",
        "5. 完成S4、S5、S6收口及全库核验后准备S7；知识发现与页面仍暂不开展。",
        "",
    ]
    return text[:start] + newline.join(block) + text[end:]


def render_rejected_decision_check(statements_by_id: dict[str, dict]) -> None:
    planned_new = {row["statement_id"] for row in NEW_STATEMENTS}
    for statement_id in REJECTED:
        row = statements_by_id.get(statement_id)
        if row is None or row.get("qualifiers", {}).get("relation_candidate") is not True:
            raise AssertionError(f"rejected S6 candidate is absent or not flagged: {statement_id}")
    for spec in RELATION_SPECS:
        if spec["statement_id"] in planned_new:
            continue
        row = statements_by_id.get(spec["statement_id"])
        if row is None or row.get("qualifiers", {}).get("relation_candidate") is not True:
            raise AssertionError(f"formal S6 candidate is absent or not flagged: {spec['statement_id']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write this reviewed, targeted batch")
    args = parser.parse_args()

    source16 = (ROOT / SOURCE_16).read_text(encoding="utf-8")
    source17 = (ROOT / SOURCE_17).read_text(encoding="utf-8")
    source19 = (ROOT / SOURCE_19).read_text(encoding="utf-8")
    source21 = (ROOT / SOURCE_21).read_text(encoding="utf-8")
    if "The letters from Strange to Sasso are in the Epistolario Moschini" not in source16:
        raise AssertionError("Chapter 16 note 2 source wording changed")
    if "four letters from him to Strange in the British Museum" not in source16:
        raise AssertionError("Chapter 16 four-letter locator changed")
    if "Epistolario Moschini" not in source19 or "Epistolario Meschini" not in source17:
        raise AssertionError("cross-chapter series-name evidence changed")
    if "Collezionisti e vedutisti settecenteschi a Venezia" not in source21 or "Arte Veneta" not in source21:
        raise AssertionError("Chapter 21 bibliography evidence changed")

    candidates = {row["candidate_id"]: row for row in csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))}
    align_path = TABLES / "alignment.csv"
    align_fields, align_rows, align_bom, align_nl = read_csv(align_path)
    primaries = primary_alignments(align_rows)
    manifest_path = TABLES / "ku-manifest.csv"
    manifest_fields, manifest_rows, manifest_bom, manifest_nl = read_csv(manifest_path)
    manifest_by_id = {row["ku_id"]: row for row in manifest_rows}
    statements_path = TABLES / "book-statements.jsonl"
    statements, statements_bom, statements_nl = read_jsonl(statements_path)
    statements_by_id = {row["statement_id"]: row for row in statements}
    relation_path = TABLES / "relations.csv"
    relation_fields, relation_rows, relation_bom, relation_nl = read_csv(relation_path)
    mention_path = TABLES / "mentions.csv"
    mention_fields, mention_rows, mention_bom, mention_nl = read_csv(mention_path)
    enrichment_path = TABLES / "enrichment.jsonl"
    old_enrichment, enrichment_bom, enrichment_nl = read_jsonl(enrichment_path)
    accepted_text, accepted_bom, accepted_nl = read_text(ACCEPTED)
    knowledge_text, knowledge_bom, knowledge_nl = read_text(KNOWLEDGE)
    stages_text, stages_bom, stages_nl = read_text(STAGES)
    review_text, review_bom, review_nl = read_text(S2_REVIEW)
    result_text, result_bom, result_nl = read_text(RESULT)

    for item in NEW_KUS:
        candidate_id = item["candidate_id"]
        candidate = candidates.get(candidate_id)
        alignment = primaries.get(candidate_id)
        if candidate is None or candidate.get("suggested_type") != "archive":
            raise AssertionError(f"expected archive candidate is missing: {candidate_id}")
        if alignment is None or alignment.get("decision") != "new":
            raise AssertionError(f"expected existing S3 new decision is missing: {candidate_id}")
        if alignment.get("ku_id"):
            raise AssertionError(f"candidate already has an S4 KU mapping: {candidate_id}")
        group_match = re.search(r"(?<![A-Za-z0-9_-])group=([A-Za-z0-9_./:-]+)", alignment.get("resolution_note", ""))
        if not group_match or group_match.group(1).rstrip(".,:;") != item["group"]:
            raise AssertionError(f"S3 group changed for {candidate_id}")
        if item["ku_id"] in manifest_by_id or (ROOT / item["card_path"]).exists():
            raise AssertionError(f"target KU or card already exists: {item['ku_id']}")

    endpoint_mappings = {
        "cand-2517": "units/persons/john-strange",
        "cand-2364": "units/persons/g-m-sasso",
        "cand-8262": "units/institutions/correr-library",
        "cand-5986": "units/institutions/british-museum",
        "cand-2719": "units/places/venice",
        "cand-10849": "units/archives/manfrin-edwards-letter-1793-12-03",
    }
    for candidate_id, ku_id in endpoint_mappings.items():
        alignment = primaries.get(candidate_id)
        if alignment is None or alignment.get("ku_id") != ku_id:
            raise AssertionError(f"existing endpoint mapping changed for {candidate_id}")

    new_statement_ids = {row["statement_id"] for row in NEW_STATEMENTS}
    target_relation_ids = ({row["statement_id"] for row in RELATION_SPECS} | set(REJECTED)) - new_statement_ids
    render_rejected_decision_check(statements_by_id)
    if not target_relation_ids.issubset({row["statement_id"] for row in statements}):
        raise AssertionError("some existing S6 candidates are missing")
    if new_statement_ids.intersection(statements_by_id):
        raise AssertionError(f"new S2 statement IDs already exist: {sorted(new_statement_ids.intersection(statements_by_id))}")

    target_relations_by_statement = {}
    for row in relation_rows:
        note = row.get("note", "")
        match = re.search(r"statement=(st-[A-Za-z0-9_-]+)", note)
        if match and match.group(1) in target_relation_ids:
            raise AssertionError(f"S6 candidate already has a direct relation row: {match.group(1)}")
    existing_relation_ids = {int(m.group(1)) for row in relation_rows if (m := re.match(r"rel-(\d+)$", row.get("relation_id", "")))}
    next_relation_id = max(existing_relation_ids, default=0) + 1
    new_relations = make_relation_rows(next_relation_id)
    for row in new_relations:
        match = re.search(r"statement=(st-[A-Za-z0-9_-]+)", row["note"])
        if not match:
            raise AssertionError(f"relation row lacks statement provenance: {row['relation_id']}")
        spec = next(item for item in RELATION_SPECS if item["statement_id"] == match.group(1))
        key = (row["subject_ku_id"], row["object_ku_id"], row["predicate"], row["time"], row["role"], row["scope"])
        if any(key == (old["subject_ku_id"], old["object_ku_id"], old["predicate"], old["time"], old["role"], old["scope"]) for old in relation_rows):
            raise AssertionError(f"duplicate relation natural key for {spec['statement_id']}")

    correr_existing = next((row for row in relation_rows if row.get("relation_id") == "rel-0316"), None)
    if not correr_existing or (correr_existing.get("subject_ku_id"), correr_existing.get("object_ku_id"), correr_existing.get("predicate"), correr_existing.get("status")) != (
        "units/institutions/correr-library", "units/places/venice", "located_at", "formal"
    ):
        raise AssertionError("expected existing rel-0316 Correr-to-Venice edge is absent or changed")

    line_rows = source16.splitlines()
    note_text = "\n".join(line_rows[68:89])
    strange_positions = []
    offset = 0
    while True:
        offset = note_text.find("Strange", offset)
        if offset < 0:
            break
        strange_positions.append((offset, offset + len("Strange")))
        offset += len("Strange")
    expected_positions = [(270, 277), (483, 490)]
    if strange_positions[:2] != expected_positions:
        raise AssertionError(f"unexpected footnote mention offsets: {strange_positions[:2]}")
    new_mention_ids = ["m-chp16-p373-sasso-0031", "m-chp16-p373-sasso-0032"]
    if any(row.get("mention_id") in new_mention_ids for row in mention_rows):
        raise AssertionError("one or more planned mention IDs already exist")
    for start, end in expected_positions:
        if note_text[start:end] != "Strange":
            raise AssertionError(f"mention span does not match exact source text: {start}-{end}")

    cards = {spec["card_path"]: make_card(spec) for spec in NEW_KUS}
    new_manifest_rows = [
        {
            "ku_id": spec["ku_id"],
            "type": "archive",
            "canonical_name": spec["canonical_name"],
            "name_en": spec["name_en"],
            "source_task": TASK,
            "card_path": spec["card_path"],
        }
        for spec in NEW_KUS
    ]

    field_builder = load_field_builder()
    with tempfile.TemporaryDirectory(prefix="pnp-s4-s6-chp16-p373-") as temporary:
        temp_root = Path(temporary)
        for rel_path, body in cards.items():
            target = temp_root / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8", newline="\n")
        original_base = field_builder.BASE
        field_builder.BASE = temp_root
        try:
            field_records, source_registry, warnings, cards_with_tables = field_builder.extract_records(new_manifest_rows)
        finally:
            field_builder.BASE = original_base
    if warnings or cards_with_tables != len(NEW_KUS):
        raise AssertionError(f"target field extraction warnings={warnings}, cards_with_tables={cards_with_tables}")
    expected_field_rows = sum(1 + len(spec["fields"]) for spec in NEW_KUS)
    if len(field_records) != expected_field_rows or any(row.get("evidence_status") != "source_backed" for row in field_records):
        details = [(row.get("enrichment_id"), row.get("ku_id"), row.get("field"), row.get("evidence_status"), row.get("source_ref")) for row in field_records]
        raise AssertionError(f"expected {expected_field_rows} source-backed fields; got {len(field_records)}; rows={details}")
    if any(row.get("source_ids") != ["haskell-1980-rev-ed"] for row in field_records):
        raise AssertionError("one or more new fields did not resolve to the Haskell source")
    field_builder.assign_ids(field_records, enrichment_path)
    old_occurrences = {row.get("occurrence_id", "") for row in old_enrichment}
    if any(row.get("occurrence_id") in old_occurrences for row in field_records):
        raise AssertionError("new S5 occurrence collides with existing enrichment")

    new_statements = make_new_statements()
    if any(row.get("qualifiers", {}).get("relation_candidate") is not True for row in new_statements):
        raise AssertionError("one or more new endpoint statements are not flagged as relation candidates")
    updates: dict[str, dict] = {}
    correr_statement = statements_by_id["st-chp16-p373-note2-epistolario-at-correr"]
    updated_correr = json.loads(json.dumps(correr_statement))
    corrections = updated_correr.setdefault("qualifiers", {}).setdefault("ocr_corrections", [])
    correction = {
        "source_file": SOURCE_16,
        "source_line": 71,
        "ocr": "Cotter",
        "print": "Correr",
        "basis": "CHP-16.pdf physical page 1.",
    }
    if correction not in corrections:
        corrections.append(correction)
    updates[updated_correr["statement_id"]] = updated_correr

    updated_alignments = []
    for item in NEW_KUS:
        row = primaries[item["candidate_id"]]
        row["ku_id"] = item["ku_id"]
        row["resolution_note"] = row.get("resolution_note", "").rstrip() + (
            f" S4 registration (2026-10-23): {item['group']} maps to {item['ku_id']}; source-local archive identity only."
        )
        updated_alignments.append(row)
    strange_alignment = primaries["cand-2517"]
    for mention_id in new_mention_ids:
        if mention_id not in strange_alignment.get("resolution_note", ""):
            strange_alignment["resolution_note"] += f" Added exact Chapter 16 note 2 mention {mention_id} after S2 review repair."
    updated_alignments.append(strange_alignment)

    new_mentions = [
        {
            "mention_id": "m-chp16-p373-sasso-0031",
            "segment_id": NOTE_SEGMENT,
            "candidate_id": "cand-2517",
            "surface_form": "Strange",
            "start_char": "270",
            "end_char": "277",
            "note": "Exact local mention in 'letters from Strange to Sasso'; added after the Chapter 13-17 S2 review flagged the missing note-level anchor.",
        },
        {
            "mention_id": "m-chp16-p373-sasso-0032",
            "segment_id": NOTE_SEGMENT,
            "candidate_id": "cand-2517",
            "surface_form": "Strange",
            "start_char": "483",
            "end_char": "490",
            "note": "Exact local mention in 'four letters from him to Strange'; added after the Chapter 13-17 S2 review flagged the missing note-level anchor.",
        },
    ]

    relation_by_statement = {
        match.group(1): row
        for row in new_relations
        if (match := re.search(r"statement=(st-[A-Za-z0-9_-]+)", row["note"]))
    }
    decisions = relation_decision_rows(relation_by_statement)
    if len(decisions) != 19 or sum(row["decision"] == "formal" for row in decisions) != 14 or sum(row["decision"] == "rejected" for row in decisions) != 5:
        raise AssertionError("the targeted S6 decision set is not 14 formal plus 5 rejected")
    if relation_by_statement["st-chp16-p373-sasso-strange-corresponded-nearly-twenty-years"]["relation_id"] != f"rel-{next_relation_id + 5:04d}":
        raise AssertionError("the planned shared correspondence edge ID is unexpected")

    process_block = make_process_block(field_records, decisions, new_relations, new_manifest_rows, knowledge_nl)
    knowledge_next = update_knowledge(knowledge_text, process_block, knowledge_nl)
    stages_next = stages_text + make_stage_record(new_statements, stages_nl)
    review_next = update_review_record(review_text, review_nl)
    result_next = update_results(result_text, result_nl)
    accepted_next = add_units_to_accepted(accepted_text, [spec["card_path"] for spec in NEW_KUS], accepted_nl)

    # Keep the Chapter 16 independent-review numerator fixed; this is a targeted repair,
    # while the four new statements remain outside the independently reviewed count.
    review_rows = [line for line in review_next.splitlines() if line.startswith("| 第16章 `16_CHP-16_intro.md` |")]
    if len(review_rows) != 1 or "206/210" not in review_rows[0]:
        raise AssertionError("Chapter 16 review denominator was not updated accurately")

    # Verify all new relation rows satisfy the current domain/range matrix.
    matrix = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8"))
    candidate_type_by_id = {key: value.get("suggested_type", "") for key, value in candidates.items()}
    type_by_ku = {row["ku_id"]: row["type"] for row in manifest_rows}
    type_by_ku.update({row["ku_id"]: "archive" for row in new_manifest_rows})
    for row in new_relations:
        allowed = matrix.get("domain_range", {}).get(row["predicate"])
        if allowed and (type_by_ku.get(row["subject_ku_id"]) not in allowed.get("domain", []) or type_by_ku.get(row["object_ku_id"]) not in allowed.get("range", [])):
            raise AssertionError(f"domain/range violation: {row['relation_id']} {row['predicate']}")

    # Exact reuse edges: Correr->Venice is rel-0316; the four-letter statement
    # is recorded as evidence for the new shared correspondence relation.
    reuse_decisions = {
        "st-chp16-p373-note2-correr-in-venice": "rel-0316",
        "st-chp16-p373-note2-sasso-wrote-four-letters-to-strange": relation_by_statement[
            "st-chp16-p373-sasso-strange-corresponded-nearly-twenty-years"
        ]["relation_id"],
    }

    alignment_next = csv_bytes(align_fields, align_rows, align_bom, align_nl)
    manifest_next = csv_bytes(manifest_fields, manifest_rows + new_manifest_rows, manifest_bom, manifest_nl)
    relation_next = csv_bytes(relation_fields, relation_rows + new_relations, relation_bom, relation_nl)
    mention_next = csv_bytes(mention_fields, mention_rows + new_mentions, mention_bom, mention_nl)
    statement_updates_bytes = targeted_jsonl_bytes(
        statements_path,
        updates,
        new_statements,
        statements_bom,
        statements_nl,
    )
    enrichment_next = append_jsonl_bytes(enrichment_path, field_records, enrichment_bom, enrichment_nl)
    outputs: dict[Path, bytes] = {
        align_path: alignment_next,
        manifest_path: manifest_next,
        relation_path: relation_next,
        mention_path: mention_next,
        statements_path: statement_updates_bytes,
        enrichment_path: enrichment_next,
        ACCEPTED: text_bytes(accepted_next, accepted_bom),
        KNOWLEDGE: text_bytes(knowledge_next, knowledge_bom),
        STAGES: text_bytes(stages_next, stages_bom),
        S2_REVIEW: text_bytes(review_next, review_bom),
        RESULT: text_bytes(result_next, result_bom),
    }
    for rel_path, body in cards.items():
        outputs[ROOT / rel_path] = body.encode("utf-8")

    print("S3: 4 existing new groups reused without reopening; 4 candidate-to-KU mappings prepared")
    for item in NEW_KUS:
        print(f"  {item['candidate_id']} [{item['group']}] -> {item['ku_id']}")
    print(f"S2: +{len(new_statements)} endpoint statements; +{len(new_mentions)} exact local Strange mentions; OCR note Correr correction recorded")
    print(f"S5: {len(field_records)} extracted fields; all source_backed; IDs {field_records[0]['enrichment_id']}–{field_records[-1]['enrichment_id']}")
    print("S6: 19 candidates -> 14 formal, 5 rejected; 12 new relation rows; reuse decisions=" + json.dumps(reuse_decisions, ensure_ascii=False))
    print("Affected new cards: " + ", ".join(spec["ku_id"] for spec in NEW_KUS))
    print(f"Files prepared: {len(outputs)}; preview mode does not write")
    if not args.apply:
        print("preview only; pass --apply to write this targeted batch")
        return 0

    snapshots = {path: (path.read_bytes() if path.exists() else None) for path in outputs}
    written: list[Path] = []
    try:
        for path, data in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_name(path.name + ".batch-tmp")
            temporary.write_bytes(data)
            temporary.replace(path)
            written.append(path)
    except Exception:
        for path in reversed(written):
            previous = snapshots[path]
            if previous is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(previous)
        raise
    print("apply complete; in-process rollback snapshots were held until all targeted files were written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# 第十章候选表面提示裁决（2026-10-08）

候选表面定位器在73个reviewed/complete段中给出117条提示。定位器只覆盖当前候选名称，不代表实体召回率或语义验收。逐条回到对应来源和现有statement裁决后，60条映射、57条不写。新增1个类型待定的Crozat收藏候选、60条mentions；为既有statement补齐候选提及，并拆分Crozat的住宅、收藏内容、每周聚会、艺术家接待与收藏开放陈列等断言。补记Zuccarelli从Tuscany抵达Venice的来源断言；不新增正式S6关系。

字符跨度为拼接段文本中的零起点、右开区间；行号用于回到规范S0来源。对专名、人物、作品、地点及概念均按当前语境选择候选；重复OCR及无界泛称不另造对象。

| 序号 | 来源定位 | 字符跨度 | 提示原文 | 裁决/候选 | 判断依据 |
|---:|---|---:|---|---|---|
| 1 | 10_CHP-10_intro.md#L122 | 13:22 | Canaletto | 不写入 | This is a duplicate OCR caption already captured in the plate-list and visual-transcription records; adding a second mention would duplicate the same caption. |
| 2 | 10_CHP-10_intro.md#L128 | 872:879 | fortune | 不写入 | Fortune means the Duke of Chandos's accumulated wealth, not a named personified figure, work, or bounded financial record. |
| 3 | 10_CHP-10_intro.md#L138 | 2840:2851 | art patrons | 不写入 | Art patrons is a broad unnamed social category; no bounded group is identified in this passage. |
| 4 | 10_CHP-10_intro.md#L156 | 1295:1301 | Prince | 映射 cand-1325 (Johann Wilhelm, Elector Palatinate) | The quoted French honorific Prince magnifique refers back to Johann Wilhelm, whose death and achievements frame Pöllnitz's praise; it is not Machiavelli's book The Prince, the false index hit. |
| 5 | 10_CHP-10_intro.md#L157 | 1716:1729 | Dutch artists | 不写入 | Dutch artists is an unbounded group descriptor inside the gallery inventory; the statement already preserves the room's artists and holdings without creating an extra group entity. |
| 6 | 10_CHP-10_intro.md#L157 | 1901:1912 | old masters | 映射 cand-4288 (Old masters) | Old masters names the art-historical category contrasted with the gallery's room-by-room holdings. |
| 7 | 10_CHP-10_intro.md#L163 | 2978:2984 | Venice | 映射 cand-3401 (Venice) | Venice is the city in the Pellegrini gallery discussion; use the body-local place candidate and leave cross-source identity alignment to S3. |
| 8 | 10_CHP-10_intro.md#L171 | 1078:1088 | collection | 映射 cand-11494 (Pierre Crozat's collection of paintings and drawings (inventory and boundary unresolved)) | The paintings collection in Crozat's Rue Richelieu mansion is a source-described collection with no itemized inventory; retain its type and boundary as unresolved. |
| 9 | 10_CHP-10_intro.md#L171 | 1136:1144 | drawings | 不写入 | Drawings is one medium in Crozat's described collection; the source identifies no distinct drawing set or inventory. |
| 10 | 10_CHP-10_intro.md#L171 | 1371:1381 | collection | 映射 cand-11494 (Pierre Crozat's collection of paintings and drawings (inventory and boundary unresolved)) | His collection refers to the same Crozat collection on p.284; the statement records reported access to artists without inventing named borrowers. |
| 11 | 10_CHP-10_intro.md#L174 | 2097:2108 | Italian art | 映射 cand-4131 (Italian art) | Italian art is the broad art-historical category in Haskell's assessment of the last serious impact in France. |
| 12 | 10_CHP-10_intro.md#L185 | 1849:1858 | portraits | 映射 cand-8970 (Unidentified informal Paris portraits by Rosalba Carriera, including sitters named by Haskell) | The phrase identifies the informal Paris portrait group Haskell attributes to Carriera and names by sitter; no title, exact date, or location is inferred. |
| 13 | 10_CHP-10_intro.md#L185 | 2111:2120 | portraits | 不写入 | Their portraits describes general demand from aristocrats and ambassadors, not a bounded group of works beyond Carriera's separately identified portraits. |
| 14 | 10_CHP-10_intro.md#L202 | 2995:3002 | fortune | 不写入 | Fortune is generic wealth acquired through the South Sea Bubble, not a named or independently bounded object. |
| 15 | 10_CHP-10_intro.md#L210 | 835:844 | portraits | 不写入 | Portraits is a general category of English commissions, not an identified set of works. |
| 16 | 10_CHP-10_intro.md#L212 | 1395:1404 | portraits | 不写入 | The Van Dyck portraits are an unrealized engraving plan described generically; no completed or bounded work group is identified here. |
| 17 | 10_CHP-10_intro.md#L219 | 237:253 | Italian painting | 不写入 | Modern Italian painting is descriptive context for the project's prospects, not an independently defined term in this passage; the Ch.20 Italian-painting candidate refers to a different catalog subject. |
| 18 | 10_CHP-10_intro.md#L226 | 2569:2578 | histories | 不写入 | Histories contrasts a generic subject genre with fables; it does not identify a specific history painting or archive. |
| 19 | 10_CHP-10_intro.md#L259 | 1274:1284 | collection | 不写入 | The Duke of Richmond's collection is a generic provenance phrase for prints; the source does not define a bounded collection object here. |
| 20 | 10_CHP-10_intro.md#L269 | 221:230 | Canaletto | 映射 cand-0528 (Canaletto) | Canaletto is the painter in the p.292 account of English-client demand and the Grand Tour market; use the index candidate scoped to his English work. |
| 21 | 10_CHP-10_intro.md#L269 | 293:299 | prices | 不写入 | Prices refers to a general market response to steady demand, not a named price, transaction, or record. |
| 22 | 10_CHP-10_intro.md#L277 | 2501:2512 | Italian art | 映射 cand-4131 (Italian art) | Contemporary Italian art is the broad art-historical category in Haskell's account of French collecting. |
| 23 | 10_CHP-10_intro.md#L280 | 1282:1288 | prices | 不写入 | Prices is a generic comparative market term in the Swedish-patron discussion; no specific transaction is named. |
| 24 | 10_CHP-10_intro.md#L282 | 1615:1624 | portraits | 不写入 | Portraits is an unbounded work category among Tessin's purchases; the source does not identify a particular set. |
| 25 | 10_CHP-10_intro.md#L282 | 1666:1674 | drawings | 不写入 | Drawings is a generic medium in the Würzburg collection list; no bounded group is identified by this span. |
| 26 | 10_CHP-10_intro.md#L293 | 540:547 | theatre | 不写入 | The theatre is the general sphere of stage scenery and festivals, not a named venue or institution. |
| 27 | 10_CHP-10_intro.md#L10 | 1670:1679 | portraits | 不写入 | Pastel portraits describes Carriera's general practice; this span does not name a bounded work group. |
| 28 | 10_CHP-10_intro.md#L11 | 1827:1833 | Venice | 映射 cand-2719 (Venice) | Venice is the city in Lord Manchester's return and official-visit account. |
| 29 | 10_CHP-10_intro.md#L319 | 124:132 | churches | 不写入 | Churches is a general class of sites under Clemens August's patronage; no specific church or bounded group is named here. |
| 30 | 10_CHP-10_intro.md#L325 | 1947:1953 | Venice | 映射 cand-2719 (Venice) | Venice is the city Tiepolo names as the historical setting of the Kaisersaal scene. |
| 31 | 10_CHP-10_intro.md#L326 | 2132:2138 | palace | 映射 cand-2822 (Würzburg Residenz) | The palace is the Würzburg Residenz at which Tiepolo received the staircase-ceiling commission, not the fresco itself. |
| 32 | 10_CHP-10_intro.md#L328 | 2757:2763 | Venice | 映射 cand-2719 (Venice) | Venice is the city invoked in Haskell's description of the ancien-régime vision. |
| 33 | 10_CHP-10_intro.md#L333 | 67:75 | churches | 不写入 | Churches is a generic class in the report of Ricci's work for the royal palace and other sites; no building is identified by this word. |
| 34 | 10_CHP-10_intro.md#L340 | 2220:2239 | Venetian artists in | 不写入 | Venetian artists in the most distant outposts is a generic narrative group, not a named or bounded collective entity. |
| 35 | 10_CHP-10_intro.md#L340 | 2462:2471 | portraits | 不写入 | Portraits is one generic subject category among Rotari's hundreds of pictures; the source identifies no separate portrait group. |
| 36 | 10_CHP-10_intro.md#L370 | 667:673 | Venice | 映射 cand-3401 (Venice) | Venice is the city where Smith was known as an arts patron and was in close contact with painters. |
| 37 | 10_CHP-10_intro.md#L371 | 766:773 | theatre | 不写入 | Theatre describes Smith's general leisure activity, not a named theatre or performance institution. |
| 38 | 10_CHP-10_intro.md#L372 | 1092:1098 | Venice | 映射 cand-3401 (Venice) | Venice is the setting for Smith's palace as a meeting place and for his publishing activity. |
| 39 | 10_CHP-10_intro.md#L373 | 1363:1369 | Venice | 映射 cand-3401 (Venice) | Venice is the city whose cultural life is discussed through Lodoli, Memmo, and Smith. |
| 40 | 10_CHP-10_intro.md#L375 | 1919:1925 | Venice | 映射 cand-3401 (Venice) | Venice is the setting for the Lodoli-Memmo rivalry and its social circle. |
| 41 | 10_CHP-10_intro.md#L379 | 2633:2639 | Venice | 映射 cand-2719 (Venice) | Venice identifies the Archivio di Stato in the p.300 note citation; use the place candidate, not a topical index subentry. |
| 42 | 10_CHP-10_intro.md#L383 | 213:219 | Venice | 映射 cand-2719 (Venice) | Venice is the city context for Goldoni's dedication and Smith's will. |
| 43 | 10_CHP-10_intro.md#L389 | 2053:2059 | Venice | 映射 cand-2719 (Venice) | Venice is the city to which Smith's official visitors came. |
| 44 | 10_CHP-10_intro.md#L396 | 1636:1642 | Venice | 映射 cand-3401 (Venice) | Venice is one of the locations in the comparison of Ricci's employment, distinguished from the Turin court. |
| 45 | 10_CHP-10_intro.md#L398 | 2265:2271 | Venice | 映射 cand-3401 (Venice) | Venice is the artistic context in which Cignani was admired; retain the source's comparison and wording. |
| 46 | 10_CHP-10_intro.md#L404 | 864:872 | drawings | 映射 cand-9200 (Nearly 150 drawings by Marco Ricci in Joseph Smith’s collection) | The nearly 150 drawings are the bounded Marco Ricci group already described in Smith's collection; retain the source's approximate count. |
| 47 | 10_CHP-10_intro.md#L406 | 1634:1642 | payments | 不写入 | Payments summarizes recurring remuneration over several years; no individual payment record or bounded payment series is identified. |
| 48 | 10_CHP-10_intro.md#L413 | 238:246 | drawings | 不写入 | Drawings is a medium in the already described Smith holdings; this span does not identify a distinct drawing group. |
| 49 | 10_CHP-10_intro.md#L413 | 980:989 | portraits | 不写入 | Portraits is a general category in the contrast of Smith's collecting preferences, not a bounded work entity. |
| 50 | 10_CHP-10_intro.md#L428 | 1717:1725 | churches | 不写入 | Churches is a generic architectural category in the description of Canaletto's views, not an identified group of buildings. |
| 51 | 10_CHP-10_intro.md#L429 | 2683:2692 | Canaletto | 映射 cand-0514 (Canaletto) | Canaletto is the painter in the account of the gap in Smith commissions and subsequent English work. |
| 52 | 10_CHP-10_intro.md#L449 | 1287:1296 | Canaletto | 映射 cand-0514 (Canaletto) | Canaletto is the painter whose development was said to be influenced by Vermeer; preserve that attribution as reported, not settled. |
| 53 | 10_CHP-10_intro.md#L451 | 1606:1613 | subject | 不写入 | Subject means the generic subject matter of Canaletto's pictures, not an independently identified entity. |
| 54 | 10_CHP-10_intro.md#L452 | 2109:2119 | collection | 映射 cand-9210 (Joseph Smith’s Venetian collection of modern art and old masters (collection type unresolved)) | His collection means Smith's type-unresolved Venetian collection; Haskell's claim about the six Roman views' impact remains explicitly inferential. |
| 55 | 10_CHP-10_intro.md#L452 | 2343:2354 | Italian art | 映射 cand-4131 (Italian art) | Italian art is the broad historical field in Haskell's account of Rome and Roman values. |
| 56 | 10_CHP-10_intro.md#L453 | 2949:2958 | Canaletto | 映射 cand-0514 (Canaletto) | Canaletto is the painter of the next commissioned series; preserve Haskell's account of its architectural purpose. |
| 57 | 10_CHP-10_intro.md#L462 | 1622:1631 | Canaletto | 映射 cand-0514 (Canaletto) | Canaletto is the artist who dedicated the thirty-one-etching series to Smith. |
| 58 | 10_CHP-10_intro.md#L462 | 1738:1746 | drawings | 不写入 | Drawings is a generic medium used to compare Canaletto's etchings with his painted work; no bounded drawing set is named. |
| 59 | 10_CHP-10_intro.md#L462 | 1944:1953 | Canaletto | 映射 cand-0514 (Canaletto) | Canaletto is the artist whose etching vision Haskell characterizes; do not turn the stylistic evaluation into an independent work. |
| 60 | 10_CHP-10_intro.md#L466 | 3343:3352 | Canaletto | 映射 cand-0514 (Canaletto) | Canaletto is the artist whose departure preceded Smith's continuation of the overdoor series. |
| 61 | 10_CHP-10_intro.md#L474 | 1260:1270 | attacks on | 不写入 | Attacks on Baroque architecture describes the content of Visentini's already registered updated book; the phrase is not a separate work or named concept. |
| 62 | 10_CHP-10_intro.md#L543 | 6030:6039 | Canaletto | 不写入 | This Canaletto occurrence is part of the p.289 printed table already transcribed and represented in the dedicated visual-transcription source. |
| 63 | 10_CHP-10_intro.md#L543 | 6314:6323 | Canaletto | 不写入 | This repeated Canaletto occurrence is the same p.289 table row already represented in the dedicated visual-transcription source; do not duplicate its mentions. |
| 64 | 10_CHP-10_intro.md#L543 | 6354:6372 | private collection | 不写入 | Private collection is an anonymous parenthetical location label in the duplicated p.289 table, not an identifiable collection entity. |
| 65 | 10_CHP-10_intro.md#L543 | 6362:6372 | collection | 不写入 | Collection is a generic table-cell label in a duplicate OCR table; the curated transcription already preserves the row and its references. |
| 66 | 10_CHP-10_intro.md#L543 | 6422:6440 | private collection | 不写入 | Private collection is an anonymous parenthetical label in the duplicated p.289 table, not a separately identifiable object. |
| 67 | 10_CHP-10_intro.md#L543 | 6430:6440 | collection | 不写入 | Collection is a generic table-cell label in the duplicated p.289 table; the visual transcription already records the row. |
| 68 | 10_CHP-10_intro.md#L543 | 6522:6531 | Canaletto | 不写入 | This Canaletto occurrence is part of the p.289 printed table already represented in the dedicated visual-transcription source. |
| 69 | 10_CHP-10_intro.md#L543 | 6564:6574 | collection | 不写入 | Collection is an anonymous parenthetical table-cell label in the duplicate OCR, not a bounded collection candidate. |
| 70 | 10_CHP-10_intro.md#L566 | 9753:9782 | patronage of Venetian artists | 不写入 | The citation describes secondary literature about Clemens August's patronage; the phrase is a topical summary, not an additional named entity. |
| 71 | 10_CHP-10_intro.md#L566 | 9763:9782 | of Venetian artists | 不写入 | Of Venetian artists is a generic descriptor in the same bibliography note, not a separate group or work. |
| 72 | 10_CHP-10_intro.md#L583 | 11868:11878 | collection | 映射 cand-9497 (Unidentified collection of operatic caricatures owned by Joseph Smith, attributed to Marco Ricci, A. M. Zanetti and others) | The large collection is the identified group of operatic caricatures attributed to Marco Ricci, A. M. Zanetti, and others. |
| 73 | 10_CHP-10_intro.md#L599 | 14170:14178 | drawings | 不写入 | Drawings is a broad subject category in a secondary-literature citation about the Riccis, not a bounded set of drawings. |
| 74 | 10_CHP-10_intro.md#L613 | 16113:16121 | Florence | 映射 cand-3397 (Florence) | Florence is the location in the Biblioteca Marucelliana citation; the city's source-local place candidate is appropriate. |
| 75 | 10_CHP-10_intro.md#L615 | 16342:16350 | Florence | 映射 cand-3397 (Florence) | Florence is the location in the second Biblioteca Marucelliana letter citation. |
| 76 | 10_CHP-10_intro.md#L616 | 16671:16679 | Florence | 映射 cand-3397 (Florence) | Florence is the location of the Biblioteca Marucelliana cited for Smith's letter to Gori. |
| 77 | 10_CHP-10_intro.md#L630 | 17665:17675 | collection | 映射 cand-9210 (Joseph Smith’s Venetian collection of modern art and old masters (collection type unresolved)) | The collection of pictures refers to Smith's type-unresolved collection described at Mogliano; it is not a new set of individual works. |
| 78 | 10_CHP-10_intro.md#L60 | 1617:1623 | palace | 映射 cand-8919 (Burlington House, Lord Burlington's Piccadilly mansion (p.280)) | The palace is Burlington House, his Piccadilly mansion, as identified in the p.280 account. |
| 79 | 10_CHP-10_intro_notes_p289_visual-transcription.md#L3 | 213:220 | subject | 不写入 | Subject is a column heading in the curated p.289 table, not a subject entity. |
| 80 | 10_CHP-10_intro_plates_visual-transcription.md#L1 | 0:19 | Venetian artists in | 不写入 | Venetian artists in Germany and England is a plate-section heading, not a named group; the individual captioned works are handled separately. |
| 81 | 10_CHP-10_intro_plates_visual-transcription.md#L6 | 0:19 | Venetian artists in | 不写入 | Venetian artists in the middle of the eighteenth century is a plate-section heading, not an entity or bounded collective. |
| 82 | 10_CHP-10_sec_ii.md#L113 | 1058:1067 | Portraits | 映射 cand-9663 (Portraits of Streit’s father, mother, and sister) | The exact group is the portraits of Streit’s father, mother, and sister; no artists or dates are added. |
| 83 | 10_CHP-10_sec_ii.md#L145 | 91:98 | amateur | 映射 cand-3570 (Amateur) | Amateur is Haskell's characterization of Conti; this records the term without asserting an independently verified professional status. |
| 84 | 10_CHP-10_sec_ii.md#L159 | 2219:2226 | subject | 不写入 | Subject-matter means the generic topic of a grammatical exercise, not a separate entity. |
| 85 | 10_CHP-10_sec_ii.md#L162 | 2960:2966 | Venice | 映射 cand-2719 (Venice) | Outside Venice is a geographic reference to the city from which Haskell distinguishes Lodoli's contacts with Montesquieu and Maffei. |
| 86 | 10_CHP-10_sec_ii.md#L24 | 1461:1504 | interest in contemporary Venetian sculpture | 不写入 | The index subentry points to Schulenburg's interest, and the S2 statement already captures it; contemporary Venetian sculpture is a descriptive field here, not a distinct named concept. |
| 87 | 10_CHP-10_sec_ii.md#L27 | 2361:2371 | collection | 映射 cand-9622 (Schulenburg’s picture collection referred to as his gallery) | Schulenburg’s collection is the same type-unresolved picture collection that Haskell calls his gallery; note 2 discusses its contents and citations. |
| 88 | 10_CHP-10_sec_ii.md#L28 | 2586:2595 | Canaletto | 映射 cand-0525 (Canaletto) | Canaletto’s Corfu view is the specific work described in Schulenburg's inventory transcription; the statement preserves the source's uncertain reading. |
| 89 | 10_CHP-10_sec_ii.md#L32 | 3050:3059 | portraits | 映射 cand-2410 (Schulenburg, Marshal Johann Matthias) | Schulenburg’s portraits is the indexed portrait material to which Haskell directs readers; keep it distinct from the specific portrait works by Guardi. |
| 90 | 10_CHP-10_sec_ii.md#L179 | 213:230 | views on painting | 映射 cand-1421 (Lodoli, Padre Carlo) | Views on painting is the indexed conceptual subentry matching Haskell's statement that Lodoli's views were exceptional. |
| 91 | 10_CHP-10_sec_ii.md#L182 | 1695:1704 | portraits | 不写入 | Portraits is a generic plural already resolved into the two artist-specific portrait statements and their separate work candidates; it is not an additional group object. |
| 92 | 10_CHP-10_sec_ii.md#L188 | 354:361 | theatre | 不写入 | Theatre is the general art form being reformed by Goldoni, not a named venue, institution, or specific play. |
| 93 | 10_CHP-10_sec_ii.md#L188 | 604:611 | subject | 不写入 | Subject means the topic of Longhi's poetry and paintings, not an independent object. |
| 94 | 10_CHP-10_sec_ii.md#L188 | 672:678 | canvas | 不写入 | Canvas is a generic artistic medium in Goldoni's quotation, not a particular painting or a separately discussed support concept. |
| 95 | 10_CHP-10_sec_ii.md#L188 | 850:856 | poetry | 不写入 | Poetry is a generic literary category in the accusation against Goldoni, not an identified poem. |
| 96 | 10_CHP-10_sec_ii.md#L204 | 138:144 | Venice | 映射 cand-2719 (Venice) | Venice is the contemporary artistic context in the comparison with Millet. |
| 97 | 10_CHP-10_sec_ii.md#L206 | 981:988 | subject | 不写入 | Subject means the subject matter of Maggiotto's treatise, not a separate entity. |
| 98 | 10_CHP-10_sec_ii.md#L222 | 3340:3346 | Venice | 映射 cand-2719 (Venice) | Venice is the location of the Biblioteca Marciana holding the pamphlets. |
| 99 | 10_CHP-10_sec_ii.md#L237 | 2331:2337 | Venice | 映射 cand-2719 (Venice) | Venice is the location of the Biblioteca Correr named in the note continuation. |
| 100 | 10_CHP-10_sec_ii.md#L242 | 556:562 | Venice | 映射 cand-2719 (Venice) | Venice is the destination in the source's account of Zuccarelli's arrival from Tuscany; the source gives only an approximate date. |
| 101 | 10_CHP-10_sec_ii.md#L242 | 696:714 | landscape painting | 映射 cand-3575 (Landscape painting) | Landscape painting is the broad artistic category used to explain Zuccarelli's reception among English patrons. |
| 102 | 10_CHP-10_sec_ii.md#L243 | 934:940 | Venice | 映射 cand-2719 (Venice) | Venice is the city used metonymically for the culture Baretti criticized; it is not a claim about every resident. |
| 103 | 10_CHP-10_sec_ii.md#L243 | 1366:1372 | canvas | 不写入 | Canvas is a generic support in Baretti's description of Zuccarelli's work, not an individually identified painting. |
| 104 | 10_CHP-10_sec_ii.md#L261 | 1127:1134 | Academy | 映射 cand-0005 (Accademia di Pittura e Scultura) | The Venetian Academy is the institution Memmo asks about; the statement retains his question rather than presuming a reform. |
| 105 | 10_CHP-10_sec_ii.md#L270 | 1053:1064 | aristocracy | 不写入 | Aristocracy is a broad social class contrasted with the State; no bounded institution or source-specific group is identified. |
| 106 | 10_CHP-10_sec_ii.md#L276 | 290:296 | Venice | 映射 cand-2719 (Venice) | Venice is one of the cities in the footnote itinerary for Schulenburg. |
| 107 | 10_CHP-10_sec_ii.md#L279 | 731:737 | Venice | 映射 cand-2719 (Venice) | Venice is the location in the Biblioteca Marciana shelfmark citation. |
| 108 | 10_CHP-10_sec_ii.md#L282 | 940:950 | collection | 映射 cand-9622 (Schulenburg’s picture collection referred to as his gallery) | Schulenburg’s collection is the same picture collection whose inventories are cited for 1724–1737. |
| 109 | 10_CHP-10_sec_ii.md#L282 | 1116:1126 | collection | 不写入 | The Duke of Mantua's collection is mentioned generically as provenance for items; the passage does not identify a bounded collection object distinct from those works. |
| 110 | 10_CHP-10_sec_ii.md#L315 | 6084:6090 | Venice | 映射 cand-2719 (Venice) | Venice is the location in the Biblioteca Correr manuscript citation. |
| 111 | 10_CHP-10_sec_ii.md#L329 | 7984:7990 | Venice | 映射 cand-2719 (Venice) | Venice is the location in the Biblioteca Correr citation for Maggiotto's treatise. |
| 112 | 10_CHP-10_sec_ii.md#L336 | 8689:8695 | Venice | 映射 cand-2719 (Venice) | Venice is the location in the Biblioteca Correr citation for the Grimaldo and Balbi materials. |
| 113 | 10_CHP-10_sec_ii.md#L14 | 1632:1641 | portraits | 映射 cand-9580 (Unidentified portraits of Bourbon, Hapsburg, Farnese, and Hohenzollern dynasties at Palazzo Loredan) | The portraits form the specifically described dynastic group at Palazzo Loredan; do not infer individual makers or dates. |
| 114 | 10_CHP-10_sec_ii.md#L77 | 1947:1953 | Venice | 映射 cand-2719 (Venice) | Venice is the city context for Pittoni's reputation as one of its leading history painters. |
| 115 | 10_CHP-10_sec_ii.md#L77 | 2028:2034 | canvas | 不写入 | Canvas means an unspecified commissioned painting; no title, maker, or bounded work is identified by this singular category. |
| 116 | 10_CHP-10_sec_ii.md#L88 | 2218:2228 | collection | 映射 cand-9622 (Schulenburg’s picture collection referred to as his gallery) | The collection is Schulenburg's established type-unresolved picture collection; the claim that it was unique remains attributed to Haskell. |
| 117 | 10_CHP-10_sec_ii.md#L104 | 1663:1670 | fortune | 不写入 | Fortune is generic wealth gained through commerce, not the personified figure or the unrelated work candidate Fortune. |

## 写回与核验

- 候选数量：11472 → 11473；新候选：cand-11494，类型待定。
- mentions新增：60；statement新增：4。Crozat原有复合statement已拆为可核对的命题；收藏仍不扩写为逐件清单。
- 写后候选表面提示：57条；与裁决后的no-write残余逐跨度一致。扫描结果仍不证明候选召回完整。
- 严格S2检查：errors=[]; s2_missing=[]; candidates=11473; mentions=27319; statements=12260
- 决策计划SHA-256：dcc04acc36a61c24c05d48e515e1725c7a3cff8222ed67a9541df4819dc6c317；脚本SHA-256：a42a4fcd9a3809da6b63969db1b812558f82759b84e6b5479e4bf750d7ded00c。
- 写前表SHA-256：candidates ad016f18b25aa2e9d0ce75be7399ac5a62b3ccd51b882100c9b60bb14cad1ffd；mentions 1569933c8d788796fb56d3fbe690753dae3d9eeadbe7695fff7f96550ab728a6；statements 9a01c3ec987dd20a19773f711bfde74ed5d52d679ce83bc5d004e4124dc15280。
- 写后表SHA-256：candidates da4d8ff5b7e2ddaad15fa47fb83d48ab73071607d84b13e41885bb844e68ccda；mentions 69a9e8efad682814c6d6a18f4e4ed439cef7c9453a16875214cd2497206ee566；statements c1b5a0eea7d2d44c38c9b3965129ef9e9efd0019fe8bc3098177e18af3754445。
- 恢复副本：C:\Users\001\AppData\Local\Temp\pnp-s2-chp10-surface-prompts-20261008-114450。

候选提示裁决不取代对S2语义陈述、跨章身份、脚注、遗漏来源及关系候选的全书交接审计。

"""《审判庭》视频脚本的唯一来源：旁白切句（SCENES）+ 逐镜画面（SHOTS）。
  python3 出脚本.py     生成 配音/配音.json、分镜.json、脚本.md；不调用付费服务
画风与角色在 画风.json（平面矢量小鸟）；正文以 teshi-style/samples/12-wh40k-shenpanting.md 为准，切句后逐字校验。
"""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / '工具'))
import 脚本
C = json.load(open(HERE / '画风.json'))['cast']
CH, M, P, G, S = C['老陈'], C['小马'], C['庭长'], C['总督'], C['颅骨']
CREAM, CORAL, MUTED = [255, 243, 210, 255], [255, 125, 105, 255], [170, 178, 215, 255]
def lab(text, x, y, size=64, color=CREAM, **kw): return 脚本.lab(text, x, y, size, color, **kw)
SPACE = 'Setting: outer space, a plain deep-indigo starfield; no buildings, no desks, no candles. '
NOBIRD = ' There are NO characters, NO birds and NO creatures anywhere in this picture.'
ONLY = ' He is the only bird in the picture.'
SCRIB = 'covered with tiny illegible wavy scribble lines (no real letters)'
WINDOW = 'a small arched service-counter window with a brass grille and a wooden counter, set in a huge dark wall'
HATS = ('inquisitor birds of many DIFFERENT species and colours (a red cardinal, a green parrot, a yellow oriole, a blue jay, a brown owl, a pink galah; none of them is a white crane), '
        'each wearing a long dark coat and a wide-brimmed black hat, each with a small iron rose-shaped badge on a chain round the neck')
PURPLE = 'plump lilac-purple doves with smooth bald heads in simple green tunics'
POCKET = ' His small third wing is tucked away inside his coat pocket, so only two wings are visible and the pocket bulges a little.'
PLANET = 'a small LILAC-purple planet with pale green seas and one white polar ice cap on top'
IDOL = 'a tall dark stone statue of a hunched creature with FOUR clawed arms and a long domed head'
SISTER = 'sleek white dove-like birds with a short straight bob of white head feathers, in black iron armour with a red tabard, each with a brass flamethrower tank strapped on her back'

SCENES = [
 ('开头', ['长话短说。']),
 ('老陈', ['老陈，138岁，审判官，清教派，', '享受正处待遇，单身，痛风。']),
 ('玫瑰结', ['有玫瑰结。', '玫瑰结是个证，铁的，', '亮出来可以征用舰队，可以抓总督，', '可以把一颗星球整个炸掉，不用跟任何人商量，', '理论上只对帝皇一个人负责。', '帝皇不批文件。', '老陈实际上对窗口负责。']),
 ('三个庭', ['审判庭下面三个庭。', '异形审判庭，简称异一庭。', '恶魔审判庭，魔二庭。', '异端审判庭，端三庭。', '老陈在端三庭。', '法务部的同志一直有意见，讲审判是他们的口子。', '庭里答复，我们主要不审，也不判，名字是翻译问题。',
            '端三庭办事的都是女同志，穿铁的，背喷火器，', '中午在食堂坐一桌，吃带鱼，没人敢拼桌。']),
 ('卡隆四号', ['老陈查了十二年，认定卡隆四号整个不行了。', '上面的人拜一个四只手的像，', '总督自己也长出来第三只手，平时揣兜里。', '认定书四百页，结论两个字，炸烈。']),
 ('立案窗口', ['立案窗口在第一千二百层，原来天通苑那一片，', '早上排队的从北边排到南边。', '老陈排了三天，排到了，亮玫瑰结。', '窗口讲这个不用亮，这里人人都有，看号。', '窗口是小马，女同志，三级书记员，世袭，', '午休两小时四十分。',
              '小马翻了翻，讲材料不齐，', '缺送达地址确认书，要对方签字，盖章。', '老陈说对方是异端。', '小马说异端也要签，不签文书寄给谁。', '老陈惊了。']),
 ('皮蛋', ['去了。', '亚空间单程九年。', '总督很客气，当场签，用的是第三只手，', '签完留饭。', '桌上有一盘皮蛋，真的。', '老陈没见过，黑的，里面有花纹，', '认为是证据，拍了照，附卷。', '吃了两个。']),
 ('不收件', ['回来是十一月二十一号。', '小马讲二十号以后不收件，算明年的。', '明年表格 upgrade 了，旧版确认书作废。', '又去了一趟。']),
 ('路上', ['路上没有事情做。', '老陈这辈子认定过四十一颗星球，一颗没炸成。', '夜里从舷窗看出去，都还亮着，很远，', '上面的人在吃晚饭，', '不知道有个人为他们的事跑了半辈子。', '伙食费自理，一天十二王座币。']),
 ('转', ['材料齐了，没人收。', '端三庭讲四只手属于异形，转异一庭。', '异一庭在第三千层，电梯一趟四十分钟，四王座币。', '异一庭讲拜像属于异端，转端三庭。', '端三庭讲像有没有显过灵，显过归魔二庭。', '魔二庭在地下，电梯不到，走下去。', '魔二庭讲没显过，转异一庭。',
          '每跑一趟，材料上多一行批示，', '头一个字都是阅，', '后面一句，本庭不负责，转某庭处理。', '跑了六年，批示十四页，四百一十一个阅。', '交通费不报销。']),
 ('四百一十七号', ['第六年年底，老陈在端三庭门口坐地上哭了。', '138岁，痛风，坐下去起不来。', '正好端三庭年底对号，四百一十七号是空的，', '登记的时候跳了一个，没有这个案子。', '庭长出来打水，看见地上坐着一个，手里有材料，', '讲就他吧。']),
 ('调解', ['拉进去了，四百一十七号，先调解。', '炸之前必须调解，调解成了算成绩。', '屋子很小，老陈坐这边，总督坐那边，', '中间飘一个伺服颅骨做记录。', '总督表态，一是手以后不拿出来，', '二是像搬到地下室，', '三是税照交。',
            '庭长讲这个 case 好，可以结。', '老陈说哪能这样。', '庭长说星球炸了税谁交，对不对。', '老陈没签字。', '全庭调解率掉了零点三个点。']),
 ('执行', ['批了。', '到执行处，执行处一查，', '激进派的老吴三十年前对卡隆四号也出过文书，', '结论是留着，有用，', '两份都盖了章，都有效，', '执行处研究了八个月，意见是都执行，', '北半球炸，南半球留，', '总督住在赤道上，', '北半球没有人，全是冰，',
            '炸完冰化了，南半球涨水，', '总督家地下室淹了，像泡坏了一只手。', '结案。', '大家说老吴这个人有水平。']),
 ('看号', ['老陈超期三十九年，全庭倒数第一，', '玫瑰结年审没过，收回。', '调去窗口，坐小马旁边。', '十一月二十一号，来了个年轻人，', '很激动，亮了一下玫瑰结。', '老陈说看号。']),
]
NUMBERS = [['138岁', '一百三十八岁']]
HINTS = [
 ['炸', '(zha4)', '炸 zhà，全篇八处'],
 ['附卷', '附(juan4)', '卷 juàn'],
 ['倒数第一', '(dao4)(shu3)第一', '倒数 dào shǔ'],
 ['调去', '(diao4)去', '调 diào（调解的调不动，读 tiáo）'],
 ['伺服', '(si4)服', '伺 sì（《抄写员》首版读成了 cì）'],
]
FLAGS = ['upgrade、case 两处英文，听是不是读成了英文', '异一庭、魔二庭、端三庭 连着读清不清楚', '享受正处待遇 处 chù', '平时揣兜里 揣 chuāi', '长出来、涨水 都是 zhǎng', '四百一十七号是空的 空 kòng 或 kōng 都行',
         '炸烈 照字读 zhà liè', '调解、调解率 读 tiáo', '“讲就他吧。”要平', '最后一句之前留足停顿']

SHOTS = [
 # ---- 开头
 (0, '背影：老陈夹着一个很厚的卷宗，拄着拐，沿着一条两边全是档案架、望不到头的走廊往里走。', 'Seen from BEHIND (we see only his back, not his face): ' + CH + ', walks slowly away from the viewer down an endless vaulted corridor lined on both sides with shelves of dusty files, carrying one very thick folder tied with ribbon under his wing. Small in the frame, vast dark space.' + ONLY, {}),
 # ---- 老陈
 (1, '老陈正对镜头站着，像证件照。高，瘦，很老，白羽毛，宽檐黑帽，暗红大衣。', CH + ', stands upright facing the viewer like an identity photograph, half-length. He is in the left half of the frame; the right half is plain deep-indigo background.' + ONLY,
  dict(labels=[lab('老陈 · 138 岁', .72, .36, 84, clip=1, frac=.05), lab('审判官 · 清教派', .72, .50, 56, clip=1, frac=.5)])),
 (2, '老陈一个人坐在长椅上，缠着绷带的左脚搁在小凳子上，身边一个单人饭盒。', CH + ', sits alone at the left end of a long empty bench, his bandaged left foot propped up on a small stool, his cane leaning beside him, one small tin lunchbox for one next to him. The right half of the frame is plain dark wall.' + ONLY,
  dict(labels=[lab('正处待遇', .74, .28, 64, clip=2, frac=.0), lab('单身', .74, .42, 64, clip=2, frac=.45), lab('痛风', .74, .56, 64, CORAL, clip=2, frac=.72)])),
 # ---- 玫瑰结
 (3, '特写：暗红袖子里的白翅膀举着一枚铁做的玫瑰形徽章，带一截链子，有点锈。', 'Close view: a white wing in an oxblood-red sleeve holds up a small badge shaped like a rose, made of dull grey iron with a little rust, hanging on a short chain. No face visible. The badge is in the left half of the frame; the right half is plain deep-indigo background.',
  dict(refs=[], labels=[lab('玫瑰结', .72, .38, 110, font='song'), lab('（铁的）', .72, .54, 54, MUTED, clip=4, frac=.6)])),
 (5, '【动画】停机坪上，老陈把玫瑰结举过头顶。天上一排排黑色方块战舰的灯一艘接一艘亮起来。', 'On a wide landing platform at night, small at the bottom left: ' + CH + ', holds his iron rose badge high above his head with one wing. Filling the dark sky above him: rows of dark blocky warships with small unlit windows, all pointing towards him.' + ONLY,
  dict(setting='Setting: an enormous spaceport landing platform at night under a smoky indigo sky; no desks, no candles. ', kind='veo',
       motion='The small amber lights on the dark warships switch on one ship after another, row by row, until the whole fleet is lit. The tall white bird holds the badge up without moving.')),
 (6, '战舰舰桥上只有老陈一个人，一只翅膀搭在一根很大的黄铜拉杆上。舷窗外是一颗星球。', 'The bridge of a warship, completely empty except for one bird: ' + CH + ', stands with one wing resting on a single huge brass lever with a coral-red knob. Through the big window in front of him hangs a small blue-green planet. Empty chairs, nobody else.' + ONLY, {}),
 (7, '一座巨大的殿堂尽头，金光里一个很小的瘦鸟剪影坐在连着管线的王座上。底下很小的老陈摘了帽子鞠躬。', 'A colossal dark hall; at its far end, glowing gold, very small: the silhouette of a gaunt bird seated motionless on a huge throne with many cables running from it. At the bottom of the frame, tiny, seen from behind: ' + CH + ', hat held in his wing, bowing. Vast and distant.', {}),
 (8, '王座的台阶下面堆着小山一样没签字的文件，最上面一支鹅毛笔结满蛛网，墨水瓶干了。', 'Close view of the bottom steps of a huge golden throne (only the steps and the feet of the throne are visible): a mountain of unsigned parchment documents and files heaped up on the steps, grey with dust; on top lies one white feather quill covered in cobwebs beside a dried-up inkwell.' + NOBIRD, {}),
 (9, '一面巨大的黑墙正中，一扇很小的亮着灯的办事窗口。老陈很小，摘了帽子站在窗口前。', 'A huge dark wall fills the frame; in its exact centre, ' + WINDOW + ', glowing warm amber, the only light. In front of it, very small, seen from behind: ' + CH + ', hat held in his wing.' + ONLY, {}),
 # ---- 三个庭
 (10, '并排三扇一模一样的拱门，门上各一块黄铜牌：一条卷着的触手、一团长角的火、一支火把。', 'Three identical tall gothic arched doors side by side in a dark stone wall, evenly spaced across the frame, all closed. Above each door one round brass plaque with a simple emblem and no writing: on the left a coiled tentacle, in the middle a small flame with two horns, on the right a burning torch. The bottom third of the frame is plain dark floor.' + NOBIRD,
  dict(labels=[lab('异形审判庭', .18, .70, 44, MUTED, clip=11, frac=.0), lab('异一庭', .18, .82, 92, clip=11, frac=.55),
               lab('恶魔审判庭', .5, .70, 44, MUTED, clip=12, frac=.0), lab('魔二庭', .5, .82, 92, clip=12, frac=.55),
               lab('异端审判庭', .82, .70, 44, MUTED, clip=13, frac=.0), lab('端三庭', .82, .82, 92, CORAL, clip=13, frac=.55)])),
 (14, '老陈站在最右边那扇火把牌子的门下面，门比他高三倍。', 'One tall gothic arched door in a dark stone wall with a round brass plaque above it showing a burning torch (no writing). In front of the door, small: ' + CH + ', standing and waiting. The door is three times his height. The left half of the frame is plain dark wall.' + ONLY, {}),
 (15, '一只穿深蓝盔甲、夹着一本厚法典的鲸头鹳（法务部），板着脸站在一扇关着的门前。门上的投信口里递出来一张小纸条。', 'In front of a closed heavy gothic door with a narrow letter slot stands one big stern grey SHOEBILL stork with a massive beak, in dark navy armour and a round helmet, a huge thick law book under one wing and a wooden gavel in the other. A thin slip of paper is poking out of the letter slot towards him and he frowns down at it. Only this one bird. The right third of the frame is plain dark wall.',
  dict(labels=[lab('法务部', .80, .26, 84, clip=15, frac=.0), lab('答复：', .80, .46, 50, MUTED, clip=16, frac=.0), lab('名字是翻译问题', .80, .58, 58, CORAL, clip=16, frac=.62)])),
 (17, '【动画】食堂。四只穿黑铁甲、背着喷火器的白鸟坐一桌，面前是带鱼形状的灰色淀粉。别的桌都挤满了，旁边空着的座位没人去坐。', 'A dim canteen with long metal tables. At the table in the middle sit exactly four ' + SISTER + ', eating in silence; on each metal tray lies a grey paste moulded in the shape of a long flat fish. The other seats at their table are empty. The tables in the background are jammed with small round birds of many colours in teal robes, and a few stand holding trays rather than sit down at the empty seats.',
  dict(kind='veo', refs=[], motion='The four armoured white birds raise their spoons and eat at exactly the same moment, in unison. In the background one small bird with a tray walks towards the empty seats, looks at the four, turns around and walks away.')),
 # ---- 卡隆四号
 (19, '老陈举着放大镜站在一面墙前，墙上钉满小画片，用红线连着，正中是一颗淡紫色的星球。', CH + ', stands in the left third of the frame holding a magnifying glass up to a big wall covered with small pinned sketches and notes connected by coral-red strings; in the centre of the wall is pinned a picture of ' + PLANET + '. One candle. The top right of the frame is plain dark wall.' + ONLY,
  dict(labels=[lab('查了 12 年', .78, .14, 64, clip=19, frac=.1, box=True), lab('卡隆四号', .78, .27, 84, CORAL, clip=19, frac=.5, box=True)])),
 (20, '【动画】那颗星球上的大殿：一群光头的淡紫色胖鸽子，朝一尊四只手的石像一起弯腰。', 'A great temple hall lit by braziers: at the far end stands ' + IDOL + '. In front of it a crowd of ' + PURPLE + ', seen from behind in neat rows, all bowing towards the statue.',
  dict(setting='Setting: the inside of a gloomy temple on a distant planet, flat style, lit by braziers; no desks, no service windows. ', kind='veo', refs=[],
       motion='All the purple birds bow down low together, straighten up together, and bow again, slowly, in unison. The brazier flames flicker. The statue does not move.')),
 (21, '总督的半身像：淡紫色胖鸽子，光头，绿底金线的大衣，笑眯眯。胸口多出来的第三只小翅膀从衣兜里露出三个小爪尖。', 'Half-length portrait: ' + G + ', smiling politely at the viewer, his two normal wings folded over his belly. His small third wing is tucked inside his coat pocket, and just three tiny claws peek out over the edge of the pocket. He is in the left half of the frame; the right half is plain deep-indigo background. Only this one bird.',
  dict(labels=[lab('总督', .74, .34, 100, clip=21, frac=.0), lab('第三只：平时揣兜里', .74, .50, 52, CORAL, clip=21, frac=.6)])),
 (22, '桌上一本比砖头还厚的认定书，老陈的翅膀把一枚大印按在封面上。', 'Close view of a desk: one enormous bound report as thick as three bricks, with a plain cream cover. A white wing in an oxblood-red sleeve presses a big brass stamp down on the cover, leaving a round coral-red seal mark with no writing. The report is in the left half of the frame; the right half is plain dark desk and background. No face visible.',
  dict(refs=[], labels=[lab('认定书 · 400 页', .74, .30, 60, clip=22, frac=.0), lab('结论：', .68, .50, 54, MUTED, clip=22, frac=.4), lab('炸烈', .80, .50, 130, CORAL, font='song', clip=22, frac=.72)])),
 # ---- 立案窗口
 (23, '【动画】从高处看一个大得没边的办事大厅：一条队在围栏里来回折了十几道，排队的每只鸟都戴宽檐黑帽、挂着玫瑰结。尽头只有一扇窗口亮着。', 'High wide view of a vast windowless vaulted concourse: one single enormous queue winds back and forth a dozen times between rope barriers across the whole floor. The queue is made of ' + HATS + '. At the far end a long wall of small arched service-counter windows, all dark except ONE that glows amber. Tiny figures, vast space. The top fifth of the frame is plain dark vault.',
  dict(kind='veo', refs=[], motion='The whole queue shuffles forward one small step, stops, waits, then shuffles forward one more small step. Nobody leaves the line.',
       labels=[lab('第 1,200 层 · 立案窗口', .5, .10, 64, clip=23, frac=.05, box=True), lab('原天通苑一带', .5, .21, 50, MUTED, clip=23, frac=.6, box=True)])),
 (25, '老陈终于站到窗口前，肩上披着毯子，把玫瑰结举到窗口的铜栅栏前。', 'At ' + WINDOW + ': ' + CH + ', a crumpled blanket over his shoulders and three burnt-out candle stubs at his feet, stands at the counter and proudly holds his iron rose badge up to the brass grille. He is seen from the side, in the left half of the frame. Behind the grille only a dim amber glow, no clerk visible.' + ONLY,
  dict(labels=[lab('排了 3 天', .78, .16, 72, clip=25, frac=.1, box=True)])),
 (26, '从窗口里往外看：老陈身后长长的队，每只鸟都举着一枚一模一样的玫瑰结。窗台上一台黄铜取号机，吐出一张小票。', 'Seen from inside the counter window looking out through the brass grille: in front stands ' + CH + ', badge still raised, looking puzzled. Behind him, the long queue of ' + HATS + ', and every one of them is holding up an identical iron rose badge. On the counter in the foreground at the right stands a small brass ticket machine with one blank paper ticket sticking out of its slot.',
  dict(labels=[lab('看号', .80, .16, 120, CORAL, font='song', clip=26, frac=.8, box=True)])),
 (27, '窗口里的小马，像证件照：天蓝色小圆鸟，头顶一个小髻，半月形眼镜，青绿袍子戴黑袖套，面无表情。', 'Seen through the arch of the counter window, half-length, like an identity photograph: ' + M + ', sitting behind the counter with a stack of forms and a brass stamp. She is in the left half of the frame; the right half is plain dark wall. Only this one bird.',
  dict(labels=[lab('小马', .74, .32, 100, clip=27, frac=.0), lab('三级书记员 · 世袭', .74, .48, 54, clip=27, frac=.5)])),
 (28, '窗口的铜卷帘拉下来一半。小马戴着眼罩趴在桌上睡，台面上一个大沙漏。外面的队一动不动。', 'The brass shutter of the counter window is pulled half-way down. Under it we see ' + M + ', asleep with her head on the desk, a sleep mask over her eyes. On the counter stands one big brass hourglass, its sand barely started. In front of the window the first few waiting birds in wide-brimmed black hats (a red cardinal, a green parrot, a brown owl) stand perfectly still. The top fifth of the frame is plain dark wall.',
  dict(labels=[lab('午休：2 小时 40 分', .5, .10, 68, box=True)])),
 (29, '小马一只翅膀尖压着那本厚厚的认定书，另一只举起一张空白表格，上面两个空框。', 'Behind the counter, in the left half of the frame: ' + M + ', rests one wingtip on an enormous thick bound report and with the other wing holds up one single blank form with two empty boxes at the bottom (one for a signature, one for a seal; nothing written in them). The right half of the frame is plain dark wall. Only this one bird.',
  dict(labels=[lab('材料不齐', .74, .22, 84, CORAL, clip=29, frac=.55), lab('缺：送达地址确认书', .74, .42, 52, clip=30, frac=.0), lab('对方签字 · 盖章', .74, .55, 52, clip=30, frac=.55)])),
 (31, '窗口两边：老陈把四只手石像的画片拍在栅栏上，翅膀尖戳着它。小马眼皮都没抬，举着一个空信封。', 'Side view of the counter window with its brass grille in the middle of the frame. On the left: ' + CH + ', presses a small sketch of a four-armed idol against the grille and jabs at it with a wingtip, beak open. On the right, behind the grille: ' + M + ', not looking up, holds up one empty envelope. Only these two birds.', {}),
 (33, '老陈的大头近景：半闭的眼睛瞪圆了，宽檐帽歪到一边。', 'Extreme close-up of the face of ' + CH + ', his usually half-closed eyes now very wide, beak slightly open, his wide-brimmed black hat slipping to one side. Plain dark background.' + ONLY, {}),
 # ---- 皮蛋
 (34, '【动画】一艘黑色的小船驶进紫、红、青绿搅在一起的大旋涡。', 'One small dark blocky ship with a single row of amber lights sails into a huge swirling whirlpool of violet, coral and teal light. The ship is small, in the left third of the frame; the whirlpool fills the right.' + NOBIRD,
  dict(setting=SPACE, kind='veo', motion='The whirlpool of coloured light turns slowly. The small dark ship drifts steadily towards its centre and grows smaller.',
       labels=[lab('亚空间', .2, .16, 84, clip=35, frac=.0, box=True), lab('单程 9 年', .2, .30, 64, CORAL, clip=35, frac=.4, box=True)])),
 (36, '总督的书房。总督两只翅膀客气地扶着表格，胸口那只小翅膀握着笔签字。老陈僵直地站在旁边看着。', 'A rich study with green drapes and gold lamps. At a desk in the middle: ' + G + ', smiling, holds a form flat on the desk with his two normal wings and signs it with a quill held in his small third wing. At the left stands ' + CH + ', stiff and upright, staring at the third wing. Only these two birds.',
  dict(setting='Setting: a rich governor\'s palace on a distant planet, flat style: green drapes, gold lamps, polished wood; no service windows, no pipes. ')),
 (38, '俯视一只白瓷盘：切成两半的皮蛋摆成一圈，蛋白是透亮的黑褐色，上面有雪花一样的白花纹，蛋黄灰绿。', 'Seen from directly above on a dark wooden table: one white porcelain plate with Chinese century eggs (preserved eggs) cut in halves and arranged in a ring: each half is an egg shape whose "white" is a glossy, translucent dark amber-black jelly with pale snowflake-like pine-branch patterns on it, and whose yolk in the centre is soft grey-green. A pair of chopsticks beside the plate. Nothing else.' + NOBIRD,
  dict(setting='Setting: a table top in a rich dining room, warm lamp light; no pipes, no desks. ', labels=[lab('皮蛋', .16, .20, 100, font='song', box=True), lab('（真的）', .16, .36, 54, CORAL, clip=38, frac=.7, box=True)])),
 (39, '老陈弯着长脖子，拿放大镜凑到半个皮蛋跟前，眯着眼。', 'At a dining table: ' + CH + ', bends his long neck down and examines through a magnifying glass one half of a dark century egg held up on a chopstick, eyes narrowed with suspicion. On the table a white plate with more dark egg halves. The right third of the frame is plain dark background.' + ONLY,
  dict(setting='Setting: a table in a rich dining room, warm lamp light; no pipes, no desks. ')),
 (40, '老陈端着一台老式木箱照相机对着盘子拍，闪光粉冒出一团白烟。旁边摊开的卷宗里已经夹着一张照片。', CH + ', aims an old wooden box camera on a tripod at the plate of dark egg halves on the table; a puff of white smoke rises from the flash tray. Beside the plate lies his open folder with one small photograph already clipped inside. The top right of the frame is plain dark background.' + ONLY,
  dict(setting='Setting: a table in a rich dining room, warm lamp light; no pipes, no desks. ', labels=[lab('证据', .80, .16, 100, CORAL, font='song', clip=40, frac=.0, box=True), lab('附卷', .80, .33, 60, clip=40, frac=.7, box=True)])),
 (41, '老陈鼓着腮帮子嚼，面无表情。盘子里那一圈皮蛋缺了两个位置。', 'Half-length: ' + CH + ', chews with bulging cheeks and a completely blank expression, chopsticks in one wing. On the white plate in front of him the ring of dark egg halves has two clear gaps. He is in the left half of the frame; the right half is plain dark background.' + ONLY,
  dict(setting='Setting: a table in a rich dining room, warm lamp light; no pipes, no desks. ')),
 # ---- 不收件
 (42, '老陈一身灰，帽子上挂着蛛网，把签好字、盖了章的表格举到窗口前。', 'At ' + WINDOW + ': ' + CH + ', covered in grey dust with a cobweb on his hat, holds up to the grille one form with a scribbled signature, a three-clawed print and a round coral-red seal on it. He is in the left half of the frame, seen from the side.' + ONLY,
  dict(labels=[lab('十一月二十一号', .76, .16, 68, box=True)])),
 (43, '窗口里的小马把铜卷帘拉到只剩一条缝，从缝里伸出一只翅膀摆了摆。', 'The brass shutter of the counter window is pulled almost all the way down; through the narrow gap at the bottom one small sky-blue wing in a black sleeve cover waves "no". In front stands ' + CH + ', holding his form, seen from behind. Only the tall white bird and the small blue wing are visible.',
  dict(refs=['老陈'], labels=[lab('20 号以后不收件', .5, .10, 68, box=True), lab('算明年的', .5, .22, 56, CORAL, clip=43, frac=.68, box=True)])),
 (44, '小马一只翅膀举着一张浅蓝色的新表格，另一只翅膀拿大印往米黄色的旧表格上盖了一个大叉。', 'Behind the counter: ' + M + ', holds up in one wing a new pale-BLUE form with three empty boxes, and with the other wing stamps a big coral-red X onto an old CREAM-coloured form lying on the counter. She is in the left half of the frame; the right half is plain dark wall. Only this one bird.',
  dict(labels=[lab('upgrade', .76, .26, 100, CORAL, clip=44, frac=.2), lab('旧版确认书：作废', .76, .44, 54, clip=44, frac=.6)])),
 (45, '背影：老陈夹着卷宗，拄着拐，又走上那艘小黑船的舷梯。', 'Seen from BEHIND: ' + CH + ', folder under his wing, limps up the boarding ramp of the same small dark blocky ship with one row of amber lights. Night, empty landing platform.' + ONLY,
  dict(setting='Setting: an empty spaceport landing platform at night under a smoky indigo sky; no desks, no candles. ')),
 # ---- 路上
 (46, '很小的舱室。老陈坐在窄床上，帽子挂在钩子上。墙上一张星图，钉着几十枚小图钉。', 'A tiny bare ship cabin: ' + CH + ', sits on the edge of a narrow bunk at the left, his hat hanging on a hook (his head bare, a few thin white feathers), staring at the opposite wall. On that wall hangs a big dark star chart with dozens of small brass pins stuck in it, each pin on a small glowing dot. The top right corner of the frame is plain dark wall.' + ONLY,
  dict(setting='Setting: a tiny bare metal cabin inside a spaceship, one small lamp; no service windows. ', labels=[lab('认定过 41 颗', .76, .13, 64, clip=47, frac=.1, box=True), lab('炸成：0 颗', .76, .26, 64, CORAL, clip=47, frac=.72, box=True)])),
 (48, '【动画】背影：老陈站在一扇圆舷窗前。窗外很黑，远处散着几十颗小小的、亮着暖色灯火的星球。', 'Seen from BEHIND, in the left third of the frame: ' + CH + ', without his hat, stands at a big round porthole. Outside, deep dark space, and scattered far away dozens of very small planets, each with tiny warm amber lights on its night side. Quiet, still.' + ONLY,
  dict(setting='Setting: inside a dark spaceship cabin looking out of a round porthole at deep space; no desks, no candles, no service windows. ', kind='veo',
       motion='The tiny warm lights on the distant planets twinkle softly and the planets drift very slowly across the porthole. The tall white bird stands completely still.')),
 (49, '一户人家的窗户里：一家四只小圆鸟围着桌子吃晚饭，灯是暖的。窗外的夜空里，很高很远的地方有一个小光点在走。', 'A warm lit room seen from inside: a family of exactly four small round birds of different colours (one yellow, one green, one orange, one small pink chick) sit round a table eating supper under a lamp, chatting, none of them looking at the window. Through the window behind them, a dark night sky in which, very high and far away, one tiny dot of light is passing.',
  dict(setting='Setting: an ordinary small home on a distant planet at night, warm lamp light; no pipes, no desks, no service windows. ', refs=[])),
 (51, '铁盘里一块灰色的方块。旁边老陈的翅膀把一枚一枚小铜币数进墙上的投币口。', 'Close view: a metal tray with one plain grey cube of paste and a spoon on a small fold-down table. Beside it a white wing in an oxblood-red sleeve drops small brass coins one by one into a coin slot in the metal wall. No face visible. The right half of the frame is plain dark metal wall.',
  dict(setting='Setting: a tiny bare metal cabin inside a spaceship, one small lamp; no service windows. ', refs=[], labels=[lab('伙食费自理', .74, .30, 64, clip=51, frac=.0), lab('12 王座币 / 天', .74, .44, 72, CORAL, clip=51, frac=.45)])),
 # ---- 转
 (52, '老陈抱着一摞捆得整整齐齐的材料，站在三扇关着的拱门前。', 'The three identical tall gothic arched doors side by side in a dark stone wall, all closed, each with a round brass plaque above it (a coiled tentacle, a horned flame, a burning torch; no writing). In front of them, small in the middle: ' + CH + ', hugging a neat tall bundle of documents tied with ribbon, looking from one door to the next.' + ONLY, {}),
 (53, '端三庭的柜台。一只穿黑铁甲的白鸟办事员一只翅膀把材料推回来，另一只往左边指。', 'A dark office counter with a torch emblem on the wall behind it. Behind the counter ONE sleek white dove-like bird clerk with a short straight bob of white head feathers, in black iron armour with a red tabard, pushes a bundle of documents back across the counter with one wing and points off to the LEFT with the other. In front of the counter, seen from behind: ' + CH + '. Only these two birds. The top fifth of the frame is plain dark wall.',
  dict(labels=[lab('四只手 = 异形', .5, .09, 56, clip=53, frac=.1, box=True), lab('转 → 异一庭', .5, .20, 68, CORAL, clip=53, frac=.62, box=True)])),
 (54, '【动画】一口望不到顶的电梯井。一只铁笼电梯里挤满了鸟，慢慢往上升。门边一个投币箱。', 'A bottomless, topless square lift shaft seen from the side: one iron cage lift packed tight with birds of many colours; among them, pressed against the bars, ' + CH + ', hugging his bundle of documents. A brass coin box hangs by the cage door. Chains and counterweights. The cage is in the lower middle of the frame; the shaft rises far above it into darkness.',
  dict(kind='veo', motion='The crowded iron cage lift creeps slowly upwards, swaying a little; the chains move; floor after floor slides down past it. The birds inside stand squashed and motionless.',
       labels=[lab('异一庭：第 3,000 层', .22, .14, 58, clip=54, frac=.0, box=True), lab('40 分钟 · 4 王座币', .22, .26, 58, CORAL, clip=54, frac=.5, box=True)])),
 (55, '异一庭的办公室，架子上全是泡着触手的玻璃罐。一只戴护目镜的绿鹦鹉把材料推回来，往右边指。', 'An office whose shelves are crammed with glass specimen jars holding pale tentacles, claws and eyeballs in green liquid. Behind the desk one green PARROT in a white lab coat and brass goggles pushes a bundle of documents back across the desk with one wing and points off to the RIGHT with the other. In front of the desk, seen from behind: ' + CH + '. Only these two birds. The top fifth of the frame is plain dark wall.',
  dict(labels=[lab('拜像 = 异端', .5, .09, 56, clip=55, frac=.1, box=True), lab('转 → 端三庭', .5, .20, 68, CORAL, clip=55, frac=.62, box=True)])),
 (56, '又是端三庭的柜台。同一只白鸟办事员把石像的画片举到耳朵边上听了听，另一只翅膀往下指。', 'The same dark office counter with a torch emblem on the wall. Behind the counter ONE sleek white dove-like bird clerk with a short straight bob of white head feathers, in black iron armour with a red tabard, holds a small sketch of a four-armed idol up to the side of her head as if listening to it, and points straight DOWN at the floor with her other wing. In front of the counter, seen from behind: ' + CH + ', shoulders drooping. Only these two birds. The top fifth of the frame is plain dark wall.',
  dict(labels=[lab('显过灵 → 归魔二庭', .5, .10, 64, CORAL, clip=56, frac=.5, box=True)])),
 (57, '一道往下转的石头楼梯，看不见底。电梯门上钉着木板。老陈拄着拐，一级一级往下挪。', 'An endless stone spiral staircase winding DOWN into darkness, lit by a few candle stubs in wall niches. At the top left, a lift door boarded up with two crossed planks. On the stairs, small: ' + CH + ', limps down one step at a time on his bandaged foot, leaning on his cane, his bundle of documents under his wing.' + ONLY,
  dict(labels=[lab('魔二庭：地下', .76, .14, 64, box=True)])),
 (58, '地下室里烛光昏暗。一只穿银灰色全身甲、个头顶到天花板的大鸟坐在一张很小的桌子后面，把材料推回来，翅膀往上指。', 'A low candle-lit cellar with chalk circles on the floor. Behind a very small desk sits one gigantic bird in full silver-grey plate armour and a closed helmet with a short beak-shaped visor, so tall that its head touches the ceiling; it pushes a bundle of documents back across the tiny desk with one armoured wing and points UP with the other. In front of the desk, small, seen from behind: ' + CH + '. Only these two birds. The top right of the frame is plain dark wall.',
  dict(labels=[lab('没显过', .78, .12, 56, clip=58, frac=.1, box=True), lab('转 → 异一庭', .78, .23, 68, CORAL, clip=58, frac=.55, box=True)])),
 (59, '一张批示单的特写：一行一行小波浪线，每一行最左边都空着一小格。', 'An extreme close-up, so tight that one sheet of pale cream parchment covers the ENTIRE frame from edge to edge like a background: no desk, no room and no dark areas are visible. The sheet has eight evenly spaced horizontal rows; in each row the left fifth is an empty blank space and the rest of the row is tiny illegible wavy scribble lines (no real letters). Nothing else.' + NOBIRD,
  dict(labels=[lab('阅', .11, .11 + .105 * i, 62, [150, 40, 30, 255], font='song', clip=60, frac=round(.12 * i, 2)) for i in range(8)])),
 (61, '示意图：三扇小门摆成三角形，箭头从一扇指向下一扇，转成一个圈。老陈很小，站在圈中间。', 'A simple diagram on a plain deep-indigo background: three small identical arched doors placed at the three corners of a big triangle, joined by three thick curved coral-red arrows that go from each door to the next, forming a closed loop. In the exact middle of the loop, tiny: ' + CH + ', holding a bundle of documents. The bottom fifth of the frame is plain background.' + ONLY,
  dict(setting='Setting: a simple diagram on a plain deep-indigo background; no room, no furniture. ', labels=[lab('本庭不负责，转某庭处理', .5, .90, 60, box=True)])),
 (62, '老陈怀里的材料已经摞到比他的帽子还高，最上面厚厚一沓全是批示单。他从材料后面探出半张脸。', CH + ', stands in the left half of the frame hugging a tower of documents that now rises higher than his hat, the top part of it a thick wad of thin slips; he peers round the side of the tower with one tired eye. The right half of the frame is plain deep-indigo background.' + ONLY,
  dict(labels=[lab('跑了 6 年', .74, .26, 68, clip=62, frac=.0), lab('批示 14 页', .74, .40, 68, clip=62, frac=.3), lab('411 个“阅”', .74, .55, 84, CORAL, clip=62, frac=.6)])),
 (63, '另一扇小窗口。老陈把一把电梯票递进去，里面一只翅膀把票原样推了出来。', 'At another small arched counter window with a brass grille: ' + CH + ', seen from the side at the left, pushes a fat handful of small blank lift tickets across the counter; from behind the grille a single brown wing in a black sleeve pushes them straight back out. Only the tall white bird and the brown wing are visible. The top right of the frame is plain dark wall.',
  dict(labels=[lab('交通费：不报销', .74, .16, 68, CORAL, box=True)])),
 # ---- 四百一十七号
 (64, '【动画】火把牌子的大门边上，老陈坐在地上哭，帽子掉在一边，材料抱在怀里。', 'Beside a tall closed gothic door with a brass torch plaque above it: ' + CH + ', sits slumped on the stone floor against the wall, his wide-brimmed hat lying on the floor beside him, his tall bundle of documents hugged in his lap, beak open, crying, big tears on his face. He is small, in the lower left; the long empty corridor stretches away to the right.' + ONLY,
  dict(kind='veo', motion='The old white bird sobs: his shoulders shake, his head bows over the bundle of documents, and big tears roll down and drip onto the papers. Nothing else moves.')),
 (65, '特写：缠着绷带的肿脚伸在地上，拐杖倒在够不着的地方。老陈撑着墙想站起来，没站起来。', 'Low close view along the stone floor: in the foreground a swollen foot wrapped in a thick white bandage sticks out; a thin wooden cane lies on the floor just out of reach. Behind, slightly blurred, ' + CH + ', pushes against the wall with one wing trying to stand up and failing. The top right of the frame is plain dark wall.' + ONLY,
  dict(labels=[lab('138 岁', .78, .14, 72, clip=65, frac=.0, box=True), lab('痛风', .78, .28, 72, CORAL, clip=65, frac=.35, box=True)])),
 (66, '端三庭里一面墙的小格子，每格插着一卷卷宗。办事员拿着登记簿对号，正中一格是空的，结着蛛网。', 'A whole wall of small square pigeonholes, each holding one rolled file with a small blank tag, row after row. Exactly ONE pigeonhole in the middle is EMPTY, with a little cobweb in it. In front, at the lower left, one sleek white dove-like bird clerk with a short straight bob of white head feathers, in black iron armour with a red tabard, holds an open ledger and points her quill at the empty pigeonhole, puzzled. Only this one bird. The top fifth of the frame is plain dark wall.',
  dict(labels=[lab('№ 417：空的', .5, .10, 72, CORAL, clip=66, frac=.5, box=True), lab('（登记的时候跳了一个）', .5, .22, 50, MUTED, clip=67, frac=.1, box=True)])),
 (68, '门开了，庭长（一只大白鹈鹕，黑袍金领）夹着暖壶走出来，低头看见门边地上坐着的老陈。', 'The tall gothic door with the torch plaque now stands open. In the doorway: ' + P + ', has stopped and looks down. On the floor beside the door, small: ' + CH + ', sitting slumped with his bundle of documents in his lap, hat on the floor. Only these two birds.', {}),
 (69, '老陈仰着满是眼泪的脸。画面上方伸下来一只巨大的白翅膀尖，指着他。', 'Close-up from above: ' + CH + ', sitting on the floor, looks up at the viewer with a tear-streaked face, hugging his documents. From the top edge of the frame one big white wingtip in a black sleeve with a gold cuff points straight down at him. The right third of the frame is plain dark floor.' + ONLY,
  dict(refs=['老陈'], labels=[lab('就他吧', .80, .46, 96, CORAL, font='song', box=True)])),
 # ---- 调解
 (70, '两只翅膀一边一个架着老陈往门里拖，他的帽子上给贴了一张小纸签。', 'In the open doorway with the torch plaque: two sleek white dove-like bird clerks in black iron armour with red tabards drag ' + CH + ' backwards through the door, one holding each of his wings; his bandaged foot trails along the floor; a small blank paper tag has been stuck on the front of his hat. The top fifth of the frame is plain dark wall.',
  dict(labels=[lab('№ 417', .5, .09, 84, CORAL, clip=70, frac=.25, box=True), lab('先调解', .5, .22, 60, clip=70, frac=.7, box=True)])),
 (71, '一面墙上挂满了小红花和没有字的小锦旗，庭长正拿袖子擦其中一面。', 'A wall hung with rows of small coral-red rosettes and little cream-and-gold pennant banners (all completely blank, no writing). In the left half of the frame ' + P + ', lovingly polishes one of the pennants with his sleeve. The right half of the frame shows only the wall of pennants. Only this one bird.',
  dict(labels=[lab('调解成了算成绩', .70, .86, 64, box=True)])),
 (72, '【动画】很小的屋子，一张小方桌。老陈坐左边，总督坐右边，中间飘着一个鸟头骨，吊着的小爪子拿笔在小本子上记。', 'A very small bare room with one small square table under a hanging lamp. On the left side of the table sits ' + CH + ', stiff, wings folded. On the right side sits ' + G + ', smiling.' + POCKET + ' Between them, floating above the middle of the table: ' + S + '; here its dangling claw holds a white feather quill instead of the ink bottle, writing on a small notepad lying on the table.',
  dict(kind='veo', motion='The floating bird skull bobs gently and its little claw scribbles on the notepad. The purple bird nods and smiles politely. The tall white bird sits completely still and stares at him.')),
 (74, '总督笑眯眯地竖起一只翅膀尖。衣兜鼓鼓的，他另一只翅膀按着兜口。', 'Half-length, in the left half of the frame: ' + G + ', smiling, raises one wingtip as he counts off his first point, and presses his other normal wing firmly over his bulging coat pocket.' + POCKET + ' The right half of the frame is plain dark wall. Only this one bird.',
  dict(labels=[lab('一、手以后不拿出来', .74, .40, 58, clip=74, frac=.35)])),
 (75, '地下室。那尊四只手的石像挤在咸菜坛子和旧箱子中间，头上盖着一块布。', 'A low cellar with a small candle: ' + IDOL + ', now stands squeezed in a corner between big earthenware pickle jars and old crates, with a dust sheet draped over its head and two of its four clawed arms sticking out from under the sheet. The right third of the frame is plain dark wall.' + NOBIRD,
  dict(setting='Setting: a cluttered household cellar on a distant planet, one candle; no service windows, no pipes. ', labels=[lab('二、像搬到地下室', .76, .30, 56)])),
 (76, '总督把一只装满铜币的小箱子从桌面上推过来。', 'Close view of the small square table: two lilac-purple wings in dark-green sleeves with gold embroidery push a small open chest heaped with brass coins across the table towards the viewer. No face visible. The top third of the frame is plain dark background.',
  dict(refs=[], labels=[lab('三、税照交', .5, .14, 68, CORAL)])),
 (77, '庭长眉开眼笑，一只翅膀举着大印，另一只按着一张纸。', 'Half-length, in the left half of the frame: ' + P + ', beaming with delight, holds a big brass stamp raised in one wing over a sheet of paper on the table, about to bring it down; the thermos stands on the table. The right half of the frame is plain dark wall. Only this one bird.',
  dict(labels=[lab('case', .74, .34, 120, CORAL, clip=77, frac=.3), lab('可以结', .74, .52, 60, clip=77, frac=.7)])),
 (78, '老陈站起来，两只翅膀摊开，张着嘴。对面的庭长一只翅膀慢慢拍着那箱铜币，眉毛抬着。', 'At the small square table: on the left ' + CH + ', has stood up, both wings spread wide, beak open, protesting. On the right ' + P + ', sits calmly and pats the small open chest of brass coins on the table with one wing, eyebrows raised as if explaining something obvious. Only these two birds.', {}),
 (80, '桌上的调解书特写：两个签名框，右边一个画了波浪线、按了一个三个爪尖的印，左边一个空着。旁边一支没动过的笔。', 'Close view from above of one sheet of parchment on the table, ' + SCRIB + ', with two boxes at the bottom: the right-hand box contains a scribbled signature and a small print of three claws; the left-hand box is completely EMPTY. Beside the sheet lies an untouched white feather quill. The top third of the frame is plain dark table.' + NOBIRD,
  dict(labels=[lab('老陈：没签字', .5, .14, 68, box=True)])),
 (81, '墙上一张大图表，一条线一直平着走，到最后往下掉了一小截。庭长仰头看着，嘴角往下。角落里很小的老陈。', 'A big wall chart drawn on parchment with no numbers and no writing: a single line that runs flat and level all the way from the left and dips down a little just at the right-hand end. In front of it, at the right, ' + P + ', looks up at the dip sourly. In the bottom left corner, very small: ' + CH + ', standing with his documents. Only these two birds. The top fifth of the frame is plain dark wall.',
  dict(labels=[lab('全庭调解率', .34, .10, 58, clip=81, frac=.0, box=True), lab('− 0.3', .62, .10, 84, CORAL, clip=81, frac=.55, box=True)])),
 # ---- 执行
 (82, '俯视：一只大翅膀握着大印，刚按在那本厚厚的认定书上，留下一个圆圆的红印。', 'Close view from above: a big white wing in a black sleeve with a gold cuff holds a large brass-and-wood stamp that has just been pressed down on the cream cover of an enormous thick bound report in the left half of the frame, leaving a big round coral-red seal mark with no writing in it; a small puff of dust. The right half is plain dark desk.' + NOBIRD.replace('NO characters, NO birds and NO creatures', 'NO faces and NO whole birds'),
  dict(refs=[], labels=[lab('批准', .78, .50, 150, CORAL, font='song', box=True)])),
 (83, '执行处：一面墙全是抽屉。一只戴绿眼罩的老苍鹭办事员踩着梯子，拉出一个很长的抽屉。', 'An office whose back wall is entirely made of hundreds of small filing drawers with brass handles. On a tall ladder at the right, one old stooped grey HERON clerk with a green eyeshade and black sleeve covers pulls one very long drawer far out of the wall and peers into it. At the bottom left, small, seen from behind: ' + CH + ', waiting with his report. Only these two birds. The top left of the frame is plain dark wall.',
  dict(labels=[lab('执行处', .20, .12, 84, box=True)])),
 (84, '三十年前（淡色）：一只胖喜鹊（老吴）戴着同样的宽檐帽，脖子上挂满奇怪的小零碎，跟年轻一点的总督握着翅膀，笑。', 'A memory, drawn in pale, faded, washed-out tones, filling the whole frame (no inset panel): a plump, sly black-and-white MAGPIE in a long dark coat and a wide-brimmed black hat, with strings of odd little alien trinkets, teeth and crystals hanging round his neck, shakes wings warmly with a plump smiling lilac-purple bald dove in a dark-green coat with gold embroidery. Both grin. Only these two birds; the tall white crane is NOT in this picture. The top fifth of the frame is plain background.',
  dict(refs=[], setting='Setting: a rich governor\'s palace on a distant planet, flat style, pale and faded like an old memory; no service windows, no pipes. ',
       labels=[lab('激进派 · 老吴 · 30 年前', .5, .09, 58, clip=84, frac=.1, box=True), lab('结论：留着，有用', .5, .21, 64, CORAL, clip=85, frac=.1, box=True)])),
 (86, '桌上并排两份文书，一份黑边，一份金边，各盖着一个一样大的红印。', 'Seen from above on a dark desk: two documents lying side by side, the same size. The LEFT one has a thick BLACK border; the RIGHT one has a GOLD border. Each is ' + SCRIB + ' and each carries one identical big round coral-red wax seal at the bottom. The top quarter of the frame is plain dark desk.' + NOBIRD,
  dict(labels=[lab('炸', .30, .13, 110, CORAL, font='song', box=True), lab('留', .70, .13, 110, font='song', box=True), lab('都有效', .5, .90, 64, clip=86, frac=.6, box=True)])),
 (87, '一张长会议桌，一圈办事员有的托腮有的睡着了，桌上堆满茶缸，一个大沙漏漏完了又被翻过来。两份文书摆在正中。', 'A long meeting table seen from above at an angle: round it sit six old heron and stork clerks in green eyeshades and black sleeve covers, some propping their heads on a wing, two asleep; the table is crowded with tin tea mugs and a big brass hourglass; in the middle of the table lie the two documents, one black-bordered and one gold-bordered. The top fifth of the frame is plain dark wall.',
  dict(refs=[], labels=[lab('研究了 8 个月', .5, .09, 64, clip=87, frac=.2, box=True), lab('意见：都执行', .5, .21, 72, CORAL, clip=87, frac=.65, box=True)])),
 (88, '示意图：那颗淡紫色的星球，中间一道虚线。上半个涂了红，下半个原样。', 'A simple diagram: ' + PLANET + ', in the middle of the frame, cut exactly in half by one horizontal dashed cream line across its equator. The whole upper half is tinted coral-red; the lower half keeps its normal colours. The left and right thirds of the frame are empty space.' + NOBIRD,
  dict(setting=SPACE, labels=[lab('北半球：炸', .17, .34, 72, CORAL, clip=88, frac=.0), lab('南半球：留', .83, .66, 72, clip=88, frac=.5)])),
 (89, '地面上一道画出来的虚线一直伸到天边，总督的宅子正好骑在线上。总督站在阳台上往天上看，一只脚在线这边，一只脚在线那边。', 'A wide landscape on the lilac planet: one dashed cream line is painted along the ground from the foreground to the horizon, and a rich little palace with green roofs and gold lamps stands exactly astride the line. On its balcony, small: ' + G + ', looking up at the sky, standing with one foot on each side of the line.' + POCKET + ' Only this one bird. The top fifth of the frame is plain night sky.',
  dict(setting='Setting: open country on a distant lilac-coloured planet at dusk; no desks, no pipes, no service windows. ', labels=[lab('赤道', .16, .86, 64, MUTED, box=True)])),
 (90, '一望无际的冰原，什么也没有，只有一根歪着的小旗杆。', 'An endless flat white ice field under a dark indigo sky, completely empty: no buildings, no tracks; just one small crooked flagpole with a tattered plain flag in the middle distance. The top third of the frame is plain night sky.' + NOBIRD,
  dict(setting='Setting: the frozen polar ice cap of a distant planet at night; no buildings, no desks, no pipes. ', labels=[lab('北半球：没有人', .5, .14, 68)])),
 (91, '【动画】从太空看：三艘黑色方块战舰往星球顶上的白色冰盖打下三道光。冰盖发亮、冒白汽，下面的海往上涨。', 'Seen from space: ' + PLANET + ', in the lower middle of the frame; three dark blocky warships hang above its top, and three thin beams of light go down from them onto the white polar ice cap, which glows where they hit and gives off white steam. The top fifth of the frame is empty space.' + NOBIRD,
  dict(setting=SPACE, kind='veo', fit=True, motion='The three beams burn into the white ice cap; the ice cap glows, shrinks and melts away in clouds of white steam, and the pale green seas spread wider over the lower half of the planet. The three dark ships do not move.')),
 (92, '淹了水的地下室。石像泡在齐腰的水里，四只手断了一只，漂在水面上。总督卷着裤腿举着蜡烛站在楼梯上看。', 'A flooded cellar, water up to the middle of the wall: ' + IDOL + ', stands half under water; one of its four clawed arms has broken off and floats on the surface among bobbing pickle jars. On the cellar stairs at the right, holding a candle: ' + G + ', robe hitched up, looking at it sadly.' + POCKET + ' Only this one bird.',
  dict(setting='Setting: a flooded household cellar on a distant planet, one candle; no service windows, no pipes. ')),
 (93, '一只翅膀把那本厚厚的卷宗合上，系上带子，按进一个抽屉。', 'Close view: a grey wing in a black sleeve cover pushes an enormous thick file, closed and tied with ribbon, down into a long open filing drawer full of other tied files. No face visible. The top third of the frame is plain dark wall of drawers.',
  dict(refs=[], labels=[lab('结案', .5, .15, 130, CORAL, font='song', box=True)])),
 (94, '大厅里，胖喜鹊老吴胸口别着大红花，一圈戴宽檐帽的鸟围着他鼓掌。老陈站在最边上，没鼓。', 'In a vaulted hall: in the middle a plump, sly black-and-white MAGPIE in a long dark coat and a wide-brimmed black hat, one big coral-red rosette pinned on his chest, bows modestly. Around him a ring of five ' + HATS.replace('inquisitor birds', 'applauding inquisitor birds') + ', clapping their wings. At the far left edge, apart from the others: ' + CH + ', wings hanging at his sides, not clapping.', {}),
 # ---- 看号
 (95, '墙上一块排名板：一竖列小圆相框，最底下那一个是老陈。', 'A tall wooden ranking board on a wall: a single vertical column of nine small round portrait frames, each with a different bird in a wide-brimmed black hat (a red cardinal, a green parrot, a magpie, a yellow oriole, a blue jay, a brown owl, a pink galah, a grey heron), and in the lowest frame at the very bottom the portrait of ' + CH + '. The board is in the left third of the frame; the right two thirds are plain dark wall. No whole birds, only portraits.',
  dict(labels=[lab('超期 39 年', .70, .34, 72, clip=95, frac=.0), lab('全庭倒数第一', .70, .50, 72, CORAL, clip=95, frac=.55)])),
 (96, '一只翅膀把铁玫瑰从老陈脖子上摘下来，丢进一个抽屉，抽屉里已经有一堆一样的。', 'Close view: a wing in a black sleeve cover drops a small iron rose-shaped badge on a chain into an open drawer that already holds a heap of identical iron rose badges. At the left edge, the long white neck and oxblood-red collar of a tall bird, now without the badge. No faces visible. The top right of the frame is plain dark wall.',
  dict(refs=[], labels=[lab('年审：没过', .74, .16, 68, CORAL, clip=96, frac=.3, box=True), lab('收回', .74, .29, 60, clip=96, frac=.75, box=True)])),
 (97, '并排两扇办事窗口。左边坐着小马，右边坐着没戴帽子、套着黑袖套的老陈。', 'Two identical small arched service-counter windows with brass grilles side by side in a dark wall. In the LEFT window sits ' + M + '. In the RIGHT window sits ' + CH.replace('a wide-brimmed black hat, a small iron rose-shaped badge on a chain round his neck, ', 'NO hat (his head bare, a few thin white feathers) and NO badge, with black sleeve covers on his wings, ') + ' Both stare straight ahead. Only these two birds.', {}),
 (98, '【动画】窗口外面，一只帽子大了两号的小黄鸟气喘吁吁地跑到跟前，踮着脚把一枚玫瑰结高高举起来。窗口里的老陈没有抬头。', 'Side view of one small arched service-counter window with its brass grille. Outside it, on the left, one small round bright-YELLOW young bird in a long dark coat and a wide-brimmed black hat two sizes too big for him stands on tiptoe, panting, and proudly holds an iron rose badge up to the grille. Behind the grille on the right sits ' + CH.replace('a wide-brimmed black hat, a small iron rose-shaped badge on a chain round his neck, ', 'NO hat (his head bare, a few thin white feathers) and NO badge, with black sleeve covers on his wings, ') + ' He is looking down at the papers on his desk, not at the young bird. Only these two birds.',
  dict(kind='veo', motion='The small yellow bird bounces on tiptoe, panting, waving the badge eagerly at the grille. The tall white bird behind the counter keeps looking down at his papers and does not raise his head.',
       labels=[lab('十一月二十一号', .5, .10, 64, clip=98, frac=.0, box=True)])),
 (100, '老陈低着头，一只翅膀伸出去，指着窗台上的黄铜取号机。小黄鸟举着玫瑰结的翅膀停在半空。', 'Seen from inside the counter window: in the foreground at the right, from behind, the bare white head and shoulder of a tall white crane-like bird in an oxblood-red coat with black sleeve covers, looking down; one of his wings stretches out and points at a small brass ticket machine on the counter with one blank paper ticket sticking out of its slot. Beyond the brass grille, the small round bright-YELLOW young bird in an oversized wide-brimmed black hat stares at the machine, his raised wing with the iron rose badge frozen half-way down.',
  dict(refs=['老陈'])),
]

# ---- 首轮审图后的返工：按镜头首句序号换提示词（原提示词留在上面的 SHOTS 里备查）
PLAIN = 'Setting: a plain flat deep-indigo background with a soft glow; no room, no furniture. '
NOFACE = ' Only the wingtip(s) and sleeve(s) are visible: NO head, NO face, NO eyes, NO body anywhere in the picture.'
CH_CLERK = CH.replace('a wide-brimmed black hat, a small iron rose-shaped badge on a chain round his neck, ', 'NO hat (his head is bare, with a few thin white feathers) and NO badge and NO chain, with black sleeve covers on his wings, ')
assert CH_CLERK != CH
FIX = {
 3: ('Extreme close-up: one small badge shaped like a rose, made of dull grey iron with a little rust, hangs on a short iron chain from the tip of a single white wing that enters from the bottom edge of the frame in an oxblood-red sleeve.' + NOFACE + ' The badge is in the left half of the frame; the right half is plain deep-indigo background.', dict(setting=PLAIN, refs=[])),
 21: ('Half-length portrait: ' + G + ', smiling politely at the viewer, his two normal wings folded over his belly. In this picture his small third wing is hidden inside the big side pocket of his coat: the pocket bulges, and just three tiny claws peek out over its edge; there is NO wing on his chest. He is in the left half of the frame; the right half is plain deep-indigo background. Only this one bird.', dict(setting=PLAIN)),
 22: ('Close view from above of a dark desk: one enormous bound report as thick as three bricks, with a plain cream cover, lies in the left half of the frame. A big brass-and-wood stamp stands upright on the cover beside a fresh round coral-red seal mark with no writing that it has just made. Nothing else on the desk except one candle at the far edge. The right half of the frame is plain dark desk.' + NOBIRD, dict(setting=PLAIN, refs=[])),
 41: ('Half-length: ' + CH + ', chews with bulging cheeks and a completely blank expression, holding a pair of chopsticks in one wing. On the wooden table in front of him STANDS a white plate (the plate is on the table, nobody holds it) on which dark egg halves are arranged in a ring with two clear gaps. He is in the left half of the frame; the right half is plain dark background.' + ONLY, {}),
 43: ('One small arched service-counter window in a dark wall. Its brass roller SHUTTER is pulled DOWN and closed almost completely, leaving only a narrow strip of amber light at the bottom just above the wooden counter; out of that narrow gap pokes one small sky-blue wingtip in a black sleeve cover, waving "no". No clerk is visible; the window is shut. In front of the window, seen from behind: ' + CH + ', holding a form.' + ONLY, dict(refs=['老陈'])),
 65: (CH + ', sits on the stone floor against a wall and tries to push himself up with both wings, and cannot. His bandaged left foot, still attached to his leg, is stretched out in front of him; his thin wooden cane lies on the floor out of reach at the right; his hat lies beside him. He is in the left half of the frame; the top right of the frame is plain dark wall. Nothing else lies on the floor.' + ONLY, {}),
 72: ('A very small bare room with one small square table under a hanging lamp. On the LEFT side of the table sits ' + CH + ', stiff, wings folded, looking across the table. On the RIGHT side of the table, on a chair, sits ' + G + ', smiling, his two normal wings resting on the table, holding nothing.' + POCKET + ' Exactly between them, floating in the air above the middle of the table: ' + S + '; here its dangling claw holds a white feather QUILL (not a bottle) whose tip touches a small notepad lying on the table. Only the skull writes.', {}),
 76: ('Close view from above of a small square wooden table: one small open wooden chest heaped with brass coins is being pushed across the table by two lilac-purple wingtips in dark-green sleeves with gold embroidery that enter from the top edge of the frame.' + NOFACE + ' The bottom third of the frame is plain table.', dict(setting='Setting: a wooden table top under a lamp, seen from above; no room visible. ', refs=[], labels=[lab('三、税照交', .5, .86, 68, CORAL, box=True)])),
 78: ('At the small square table: on the left ' + CH + ', has stood up from his chair and leans forward over the table, beak wide open, shaking his cane in the air with one wing (his wings are small and ordinary; they are NOT spread out). On the right ' + P + ', sits calmly and pats a small open chest of brass coins on the table with one wing, eyebrows raised as if explaining something obvious. Only these two birds.', {}),
 83: ('An office whose back wall is entirely made of hundreds of small filing drawers with brass handles. On a tall ladder in the middle of the frame, ONE old stooped GREY heron clerk (grey feathers, bare head, no hat, no coat) with a green eyeshade and black sleeve covers, in a plain teal robe, pulls one very long drawer far out of the wall and peers into it. Only this one bird; no other characters. The top left of the frame is plain dark wall.', dict(refs=[])),
 89: ('A wide landscape on a lilac-coloured planet at dusk: one dashed cream line is painted along the ground, running straight from the bottom centre of the frame to the horizon. In the middle distance a LARGE rich palace with green roofs and gold lamps stands exactly astride the line, half of it on each side. On the small central balcony of the palace stands a TINY figure, far smaller than the palace: ' + G + ', looking up at the sky. Only this one bird. The top fifth of the frame is plain night sky.', {}),
 96: (CH_CLERK + ' He stands at the left of the frame, looking down sadly. At the right, a single grey wing in a black sleeve cover, entering from the right edge, drops his small iron rose-shaped badge into an open drawer that is already full of a heap of identical iron rose badges. His is the only face in the picture. The top right of the frame is plain dark wall.', {}),
 97: ('Two identical small arched service-counter windows with brass grilles side by side in a dark wall, each with a wooden counter. Behind the counter of the LEFT window, half-length, sits ' + M + '. Behind the counter of the RIGHT window, half-length, sits ' + CH_CLERK + ' Both sit BEHIND their counters so that only their upper bodies show, and both stare straight ahead. Only these two birds.', {}),
 98: ('Side view of a service counter with a brass grille running down the middle of the frame. On the LEFT, outside the grille: one small round bright-YELLOW young bird in a long dark coat and a wide-brimmed black hat two sizes too big for him stands on tiptoe, panting, and holds up to the grille a small dull-GREY IRON badge on a chain (a grey metal badge shaped like a rose: it is metal, NOT a flower and NOT red). On the RIGHT, behind the grille, seated at the counter: ' + CH_CLERK + ' He is looking down at the papers on his desk, not at the young bird. Only these two birds.', {}),
 100: ('Close side view at a service counter with a brass grille. Behind the grille, in the right half of the frame, sits ' + CH_CLERK + ' He keeps his eyes down on the papers on his desk and does not look up, while one of his wings stretches out and points at a small brass ticket machine standing on the counter with one blank paper ticket sticking out of its slot. Beyond the grille, in the left half of the frame, stands one small round bright-YELLOW young bird in a long dark coat and an oversized wide-brimmed black hat, staring at the machine, his raised wing holding a small grey iron badge frozen half-way down. Only these two birds.', {}),
}
SHOTS = [(c, cn, FIX[c][0], dict(ex, **FIX[c][1])) if c in FIX else (c, cn, en, ex) for c, cn, en, ex in SHOTS]

# ---- 出图后逐镜对过的叠字位置（按镜头首句序号整组替换）
DKRED = [150, 40, 30, 255]
LABELS = {
 10: [lab('异形审判庭', .30, .58, 40, MUTED, clip=11, frac=.0, box=True), lab('异一庭', .30, .70, 84, clip=11, frac=.55, box=True),
      lab('恶魔审判庭', .50, .58, 40, MUTED, clip=12, frac=.0, box=True), lab('魔二庭', .50, .70, 84, clip=12, frac=.55, box=True),
      lab('异端审判庭', .70, .58, 40, MUTED, clip=13, frac=.0, box=True), lab('端三庭', .70, .70, 84, CORAL, clip=13, frac=.55, box=True)],
 15: [lab('法务部', .86, .12, 76, clip=15, frac=.0, box=True), lab('答复：', .30, .14, 50, MUTED, clip=16, frac=.0, box=True), lab('名字是翻译问题', .30, .26, 58, CORAL, clip=16, frac=.62, box=True)],
 27: [lab('小马', .66, .32, 96, clip=27, frac=.0, box=True), lab('三级书记员 · 世袭', .66, .48, 50, clip=27, frac=.5, box=True)],
 46: [lab('认定过 41 颗', .74, .69, 60, clip=47, frac=.1, box=True), lab('炸成：0 颗', .74, .80, 60, CORAL, clip=47, frac=.72, box=True)],
 51: [lab('伙食费自理', .72, .66, 64, clip=51, frac=.0), lab('12 王座币 / 天', .72, .79, 72, CORAL, clip=51, frac=.45)],
 53: [lab('四只手 = 异形', .80, .09, 56, clip=53, frac=.1, box=True), lab('转 → 异一庭', .80, .20, 68, CORAL, clip=53, frac=.62, box=True)],
 58: [lab('没显过', .85, .12, 56, clip=58, frac=.1, box=True), lab('转 → 异一庭', .85, .23, 64, CORAL, clip=58, frac=.55, box=True)],
 59: [lab('阅', .165, round(.203 + .0755 * i, 4), 56, DKRED, font='song', clip=60, frac=round(.1 * i, 2)) for i in range(9)],
 61: [lab('本庭不负责，', .20, .44, 56, clip=61, frac=.25), lab('转某庭处理', .20, .56, 56, CORAL, clip=61, frac=.6)],
 63: [lab('交通费：不报销', .15, .30, 54, CORAL)],
 66: [lab('№ 417：空的', .34, .058, 60, CORAL, clip=66, frac=.5, box=True), lab('（登记的时候跳了一个）', .68, .058, 42, clip=67, frac=.1, box=True)],
 71: [lab('调解成了算成绩', .42, .10, 60, clip=71, frac=.5, box=True)],
 74: [lab('一、手以后不拿出来', .76, .14, 56, clip=74, frac=.35, box=True)],
 76: [lab('三、税照交', .84, .46, 64, CORAL)],
 77: [lab('case', .76, .30, 120, CORAL, clip=77, frac=.3, box=True), lab('可以结', .76, .49, 60, clip=77, frac=.7, box=True)],
 81: [lab('全庭调解率', .34, .10, 58, clip=81, frac=.0, box=True), lab('↓ 0.3 个点', .64, .10, 72, CORAL, clip=81, frac=.55, box=True)],
 84: [lab('激进派 · 老吴 · 30 年前', .74, .08, 54, clip=84, frac=.1, box=True), lab('结论：留着，有用', .74, .19, 60, CORAL, clip=85, frac=.1, box=True)],
 86: [lab('炸', .33, .13, 110, CORAL, font='song', box=True), lab('留', .675, .13, 110, font='song', box=True), lab('都有效', .12, .62, 64, clip=86, frac=.6, box=True)],
 89: [lab('赤道', .36, .74, 60, MUTED, box=True)],
 95: [lab('超期 39 年', .70, .34, 72, clip=95, frac=.0, box=True), lab('全庭倒数第一', .70, .50, 72, CORAL, clip=95, frac=.55, box=True)],
}
SHOTS = [(c, cn, en, dict(ex, labels=LABELS[c])) if c in LABELS else (c, cn, en, ex) for c, cn, en, ex in SHOTS]

# 叠字要和画面对齐的镜头：不推拉（按镜头首句序号）
STATIC = {10, 59, 66, 86, 88}
SHOTS = [(c, cn, en, dict(ex, static=True)) if c in STATIC else (c, cn, en, ex) for c, cn, en, ex in SHOTS]

REFKEYS = [('LAO CHEN', '老陈'), ('XIAO MA', '小马'), ('PRESIDING CHIEF', '庭长'), ('GOVERNOR', '总督'), ('SERVO SKULL', '颅骨')]
META = dict(title='材料交了四十年', tag='（励志向上）', source='战锤 40K 同人戏说', credit_src='teshi-style / samples / 12-wh40k-shenpanting',
            credit_note='战锤 40K（Warhammer 40,000）的世界观属于 Games Workshop；本片为同人戏说，人物、情节虚构',
            output='审判庭-小鸟短剧.mp4', card_background='09', title_size=120, dark=True, numbers=NUMBERS,
            card=dict(subtitle='异端审判庭的老陈想炸一颗星球，', subtitle_size=60, subtitle_y=0.29, subtitle_color=[255, 243, 210, 235], title_y=0.43, tag_y=0.58),
            vstyle=' Static camera. 2D flat vector animation, limited smooth motion, keep the exact flat art style and colours of the input image, nothing new appears, no text.',
            style_note='平面矢量小鸟（与《抄写员》同一套画法）：深靛蓝底、无描边、圆胖小鸟。老陈是又高又瘦的老白鹤，宽檐黑帽、暗红大衣、左脚缠着绷带；小马是天蓝色的虎皮鹦鹉；庭长是大白鹈鹕；总督是淡紫色的光头胖鸽子，胸口多长一只小翅膀；伺服颅骨沿用《抄写员》的鸟头骨。画面里不出字，数字、庭名和批示用后期叠字。')
TODO = ['读音：5 处加了拼音提示，两处英文单词（upgrade、case）要听。', '音乐：出两个候选，等旁白出来再定。', '叠字位置是按构图预估的，出图后逐镜对。',
        '“第三只手”在画面里是第三只小翅膀，“四只手的像”保留成四只手的石像（不是鸟）。', '颅骨的参照图是《抄写员》里拎墨水瓶的那张，这里要它拿笔，可能要多出一两次。']

if __name__ == '__main__':
    脚本.build(HERE, HERE.parent.parent / 'teshi-style' / 'samples' / '12-wh40k-shenpanting.md', META, SCENES, SHOTS, HINTS, FLAGS, REFKEYS, TODO)

"""《抄写员》视频脚本的唯一来源：旁白切句（SCENES）+ 逐镜画面（SHOTS）。
  python3 出脚本.py     生成 配音/配音.json、分镜.json、脚本.md；不调用付费服务
画风与角色在 画风.json（平面矢量小鸟）；正文以 teshi-style/samples/09-wh40k-chaoxieyuan.md 为准，切句后逐字校验。
"""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / '工具'))
import 脚本
C = json.load(open(HERE / '画风.json'))['cast']
L, K, S, T = C['老刘'], C['科长'], C['颅骨'], C['机械教']
CREAM, CORAL, MUTED = [255, 243, 210, 255], [255, 125, 105, 255], [170, 178, 215, 255]
def lab(text, x, y, size=64, color=CREAM, **kw): return 脚本.lab(text, x, y, size, color, **kw)
SPACE = 'Setting: outer space, a plain deep-indigo starfield; no buildings, no desks, no candles. '
HALL = "the scribes' hall (a windowless vaulted hall with rows of small wooden writing desks, one candle per desk)"
OTHERS = 'of OTHER species (sparrows, finches, robins and tits with fully feathered heads; none of them is a pigeon, none is grey and none is bald)'
TEAL = 'small round scribe birds ' + OTHERS + ' in plain TEAL robes'
FOUR = 'exactly four other scribes, each a different small round bird in a teal robe: one YELLOW canary, one RED-breasted robin, one BLUE tit and one BROWN sparrow (none of them grey, none bald)'
NOBIRD = ' There are NO characters, NO birds and NO creatures anywhere in this picture.'
INKC, DKRED = [44, 38, 32, 255], [196, 52, 36, 255]
MAROON = 'small round scribe birds ' + OTHERS + ' in MAROON robes'
SCRIB = 'covered with tiny illegible wavy scribble lines (no real letters)'

SCENES = [
 ('开头', ['是这样的。']),
 ('老刘', ['老刘，45岁，帝国内务部三级抄写员，', '世袭，第十一代，秃。', '月入2300王座币。', '单位在泰拉，北半球，原来保定那一片，', '上面盖了四千层，老刘在第2311层，没见过天。']),
 ('一份文件', ['全科一百六十人，抄一份文件。', '文件是塔兰七号递上来的增援申请。', '上面写，绿皮来了，很多，请派人。', '递上来三千年了，前面两千七百年在收发室排队。', '一共九页，一式四十份，手抄。',
              '机器是有的，机械教的同志讲机器有魂，', '魂不高兴，要烧香，烧香排队九十年。', '科长说手抄好，有仪式感，鹅毛笔，德味。']),
 ('十一代', ['老刘他太爷爷抄到第四页。', '他爸抄到第五页。', '老刘第六页，第三行。', '今年是哪年，科里有两种说法，中间差八百年。', '不影响抄。']),
 ('老王', ['老王上个月死了。', '科里肥肠重视，把头留下，做成伺服颅骨，', '现在在屋里飘着，负责添墨水。', '编制保留，工龄连续计算。', '大家都惊了！', '惊的是颅骨不吃饭，食堂多出半份淀粉，归了科长。']),
 ('保定', ['保定以前出驴肉火烧。', '这个事档案里有，在地下第九百层，没人下去过。']),
 ('隔壁', ['礼拜二，老刘去隔壁科借墨水，', '看了一眼人家抄的东西，是塔兰七号的灭绝令，', '已经执行，两百年前，自己人炸的，', '手续齐全，一式四十份，隔壁也抄了六代，', '两个科隔一堵墙，', '食堂是同一个食堂，打饭排同一个队，', '从来没人提过。', '老刘惊了。']),
 ('科长', ['去找科长。', '科长讲，一是申请归我们科，灭绝归隔壁科，两个口子，不要串。', '二是星球没了文件还在，文件在科就在，科在你才有编制，对不对。', '三是你这个 situation 以后不要再讲。', '老刘说哪能这样。', '科长说回去抄。', '老刘回去了。']),
 ('远方', ['帝皇在喜马拉雅那边坐着，坐了一万年，没下来过，', '每天要用掉一千个人。', '银河里有一百万个世界，老刘一个没去过。', '所有的远方到他手上，就是第六页第三行一个编号。', '夜里梦见过一次，是条河，很宽，没有编号。']),
 ('两个零', ['醒了。', '早饭是尸体淀粉，灰的，科里都说有肘子味。', '心里有事，手抖。', '申请上要八千人，老刘多抄了两个零。']),
 ('批了', ['偏偏这一份批了。', '上面讲这个科效率高，十一代就见到成果。', 'ridiculous。', '八十万人上了船，去一个没有了的地方。', '亚空间这个东西不好讲，有时候走四十年，有时候出发前一天就到。']),
 ('表彰', ['老刘受了表彰。', '奖励是调去抄阵亡通知，八十万份，一式四十份，', '提前抄，等人到了正好用上。', '完了。', '老王从头顶飘过去，撞了一下门框。']),
]
NUMBERS = [['45岁', '四十五岁'], ['2300', '两千三百'], ['2311', '两千三百一十一']]
HINTS = [
 ['第三行', '第三(hang2)', '行 háng，两处'],
 ['中间差', '中间(cha4)', '差 chà'],
 ['炸的', '(zha4)的', '炸 zhà'],
 ['调去', '(diao4)去', '调 diào'],
 ['伺服', '(si4)服', '伺 sì（首版读成了 cì）'],
 ['借墨水', '(jie4)墨水', '借 jiè（首版听着像“见”）'],
]
FLAGS = ['situation、ridiculous 两处英文，听是不是读成了英文', '肥肠重视 照字读 féi cháng', '德味 dé wèi', '哪能 nǎ néng', '尸体淀粉、肘子味 照字读', '一式四十份 三处',
         '“完了。”要平', '最后一句之前留足停顿']

SHOTS = [
 # ---- 开头
 (0, '一眼望不到头的大厅，一排排小书桌，每桌一支蜡烛、一只埋头抄写的小鸟。', 'Very wide high view of an enormous windowless vaulted hall receding into darkness: hundreds of identical small wooden writing desks in perfectly straight rows, each with one candle and one tiny round scribe bird in a teal robe bent over a sheet of parchment. Brass pipes and cables hang from the vault. Tiny figures, vast dark space.', {}),
 # ---- 老刘
 (1, '老刘坐在小书桌后面，正对镜头，握着鹅毛笔，像证件照。', L + ', sits upright at a small wooden writing desk facing the viewer, holding a white goose-feather quill, one candle on the desk, like an identity photograph. He is in the left half of the frame; the right half is plain deep-indigo background.',
  dict(labels=[lab('老刘 · 45 岁', .72, .36, 84, clip=1, frac=.05), lab('帝国内务部 三级抄写员', .72, .50, 54, clip=1, frac=.4)])),
 (2, '墙上一排十一个椭圆相框，里面是几乎一样的秃头灰鸽子。老刘站在最后一个下面。', 'A long dark wall with a single row of eleven small oval portrait frames; every portrait shows almost the same plump grey bald pigeon in a teal robe, the ones on the left faded and dusty. The portraits hang high on the wall. Below them, standing on the floor a little right of the centre and completely inside the frame, small: ' + L + ', looking exactly like the portraits. The top fifth of the frame is plain dark wall.',
  dict(labels=[lab('世袭 · 第 11 代', .5, .13, 72)])),
 (3, '老刘低头看着桌上三枚小铜币，另一只翅膀捏着一张薄薄的工资条。', L + ', sits at his desk looking down at three small brass coins lying on the desk in front of him; in his other wing a thin narrow slip of paper. Close view. He is in the right half of the frame; the left half is plain deep-indigo background.',
  dict(labels=[lab('月入 2,300 王座币', .27, .40, 72)])),
 (4, '从太空看：整颗星球盖满了城市和金属，上半球有一个很小的亮点。', 'Seen from space: a whole planet whose entire surface is covered by one continuous city of metal plates, spires and tiny amber lights, no oceans, no green, wrapped in thin bands of smog; one single tiny brighter amber dot glows in its upper half. The planet fills the right two thirds of the frame; the left third is empty starry space.' + NOBIRD,
  dict(setting=SPACE, labels=[lab('泰拉', .17, .36, 110), lab('北半球 · 原保定一带', .17, .50, 50, clip=4, frac=.45)])),
 (5, '一栋望不到顶也望不到底的楼的剖面，几千层薄薄地叠着，中间只有一扇窗亮着，里面坐着一只小灰鸟。', 'A simple architectural cross-section of one single, very tall, narrow tower block that rises out of the top of the frame and sinks below the bottom: it is made of a great many very thin horizontal floor slabs stacked like the pages of a closed book, every floor a thin dark navy stripe with a row of tiny dark windows, all identical, no coloured blocks. Exactly ONE small window near the middle is lit warm amber, and in it a tiny grey bird sits at a desk. The tower stands in the left half of the frame; the right half is plain deep-indigo background.',
  dict(setting='Setting: a simple diagram on a plain deep-indigo background; no sky. ', labels=[lab('地上 4,000 层', .72, .30, 64), lab('老刘：第 2,311 层', .72, .45, 76, CORAL, clip=5, frac=.38), lab('没见过天', .72, .59, 54, MUTED, clip=5, frac=.78)])),
 # ---- 一份文件
 (6, '【动画】俯视大厅：一排排书桌，所有小鸟同一个姿势，同时蘸墨、同时写。', 'High wide view of ' + HALL + ': many identical desks in straight rows filling the frame, at each desk one of the ' + TEAL + ' holding a white feather quill over a sheet of parchment, all in exactly the same pose. The birds are of many different colours.',
  dict(kind='veo', refs=[], motion='All the small scribe birds dip their quills into their inkwells at the same moment and then write in perfect unison, heads moving from left to right together. Candle flames flicker.', labels=[lab('全科 160 人', .5, .12, 72, box=True)])),
 (7, '一张盖着火漆印的旧羊皮纸飘在画面右边，左上角远处是一颗土黄色的小星球。', 'A single old sheet of parchment with a round coral-red wax seal and a ribbon, ' + SCRIB + ', floats large in the right half of the frame, slightly tilted. Far behind it, small in the upper left, a little ochre-yellow desert planet. The lower left of the frame is empty space.' + NOBIRD,
  dict(setting=SPACE, labels=[lab('塔兰七号', .25, .58, 64), lab('增援申请', .25, .72, 100, font='song')])),
 (8, '小星球的沙丘上，一只戴破头盔的小兵鸟举着小旗。对面地平线上挤满了龇着下牙的绿胖鸟。', 'On a low dune at the left stands one tiny frightened soldier bird in a dented round helmet holding a small plain flag. The whole horizon on the right is crowded with a huge horde of fat, grinning GREEN birds with jutting lower tusks, carrying clubs and plain scrap-metal banners, raising dust.',
  dict(setting='Setting: the surface of a small ochre desert planet under a dark indigo sky; no buildings, no desks. ')),
 (9, '收发室的小窗口，值班的小鸟在打瞌睡。窗口前排队的不是鸟，是一卷一卷落满灰和蛛网的文件，排到看不见的地方。', 'A mail room: a small counter window with a sleepy clerk bird in a teal robe dozing behind it. In front of the window stands a queue made not of birds but of rolled parchment scrolls and tied paper bundles, lined up one behind another across the floor and winding far away into the dark; the nearest ones are covered in dust and cobwebs. The top quarter of the frame is plain dark wall.',
  dict(labels=[lab('递上来 3,000 年', .5, .12, 72), lab('其中 2,700 年在收发室排队', .5, .24, 54, CORAL, clip=9, frac=.42)])),
 (10, '俯视桌面：九张羊皮纸摆成扇形，后面是一摞一摞同样的纸。一支鹅毛笔，一个墨水瓶。', 'Seen from above on a dark wooden desk: exactly nine sheets of parchment fanned out in an arc, ' + SCRIB + '; behind them rows of identical tall stacks of the same sheets. One white feather quill and one inkwell. The picture shows only the desk top.' + NOBIRD,
  dict(labels=[lab('9 页 × 40 份 · 手抄', .5, .13, 76, box=True)])),
 (11, '【动画】角落里一台盖着防尘布、结了蛛网的黄铜复印机。红袍的机械教小鸟对着它摇香炉。', 'In a dusty corner of the hall stands a big, old brass copying machine with rollers, a crank, a funnel and one small dark lamp on top, half covered by a dust sheet and cobwebs. In front of it ' + T + ', swings the incense burner; pale smoke curls up. A few small candles on the floor as an offering.',
  dict(kind='veo', motion='The red-robed bird slowly swings the incense burner back and forth; pale smoke curls up around the machine. The small lamp on top of the machine flickers on for a moment, then goes dark again. The machine itself does not move.',
       labels=[lab('烧香排队：90 年', .5, .075, 68, CORAL, clip=12, frac=.55, box=True)])),
 (13, '科长（猫头鹰）举着一根白鹅毛笔，眯着眼端详，像在品鉴。', 'One continuous picture filling the whole frame edge to edge (no inset panel, no rounded vignette): in his dim office, in the left third of the frame, half-length, ' + K + ', holds up one long white goose-feather quill in front of his face and admires it with half-closed eyes like a connoisseur, the other wing on his chest. The right two thirds of the frame are just a plain dark wall with the soft glow of one lamp.',
  dict(labels=[lab('德味', .76, .38, 130, CORAL, font='song', clip=13, frac=.82)])),
 # ---- 十一代
 (14, '回忆（淡色半透明）：一只很老的秃头鸽子在同一张小桌上抄写，下巴上一撮长羽毛。', 'A memory, drawn in pale, faded, washed-out tones, filling the whole frame (no inset panel, no arch): the great-grandfather of LAO LIU, who looks just like the reference bird (the same plump grey bald pigeon in the same teal robe) but is very old, with a long thin white wispy beard of feathers and a stoop, sits at a small desk in the left half of the frame, writing with a quill by candlelight. The right half is plain deep-indigo background. Only this one bird.',
  dict(labels=[lab('太爷爷：第 4 页', .72, .42, 72)])),
 (15, '回忆（淡色半透明）：一只戴小圆眼镜的中年秃头鸽子在同一张小桌上抄写。', 'A memory, drawn in pale, faded, washed-out tones, filling the whole frame (no inset panel, no arch): the father of LAO LIU, who looks just like the reference bird (the same plump grey bald pigeon in the same teal robe) but wears small round spectacles and a small moustache of feathers, sits at a small desk in the left half of the frame, writing with a quill by candlelight. The right half is plain deep-indigo background. Only this one bird.',
  dict(labels=[lab('他爸：第 5 页', .72, .42, 72)])),
 (16, '越过老刘的肩膀看：鹅毛笔尖停在纸上第三行，下面还是空的。', 'Close view over the shoulder of ' + L + ', seen from behind at the left edge: the tip of his white quill rests on the third line of a sheet of parchment whose first lines are tiny illegible wavy scribble; the rest of the sheet below is still empty. Candlelight. He is the only bird in the picture; the background is a dark empty wall.',
  dict(labels=[lab('老刘：第 6 页 · 第 3 行', .5, .13, 72, CORAL, box=True)])),
 (17, '后景两只小鸟各指着一个沙漏，嘴对嘴地争。两个沙漏里的沙明显不一样多。前景老刘头也不抬地抄。', 'In ' + HALL + ': in the background stand exactly two ' + TEAL + ', arguing beak to beak, each pointing a wing at a different large brass hourglass standing on a shelf between them; the two hourglasses hold clearly different amounts of sand. In the foreground ' + L + ', keeps writing at his desk without looking up. Only these three birds.',
  dict(labels=[lab('± 800 年', .30, .12, 84, box=True)])),
 # ---- 老王
 (19, '一排书桌中间空着一张：蜡烛灭了，冒一缕烟，笔搁在没抄完的纸上，椅背上系着一条黑布。两边的鸟照常抄。', 'In a row of occupied desks, one small wooden writing desk in the middle is empty: its candle has gone out with a thin wisp of smoke, a white quill lies on an unfinished sheet, and a small black ribbon is tied to the empty chair. The small scribe birds in teal robes on both sides keep writing without looking.', {}),
 (20, '科长一只翅膀指向一个红绒垫子，垫子上方飘着一个鸟头骨，一只眼窝里亮着红色镜片。三只小鸟礼貌地鼓掌。', K + ', stands proudly, presenting with one outstretched wing a small red velvet cushion on a pedestal. Just above the cushion hovers ' + S + '. At the side three small scribe birds in teal robes clap politely.', {}),
 (21, '【动画】鸟头骨飘在老刘的桌子上方，用下面吊着的小爪子往墨水瓶里添墨水。老刘面无表情地看着。', 'In ' + HALL + ', in the left and middle of the frame: ' + S + ', hovers above the small desk of ' + L + ', tilting the small ink bottle held in its claw over the inkwell on the desk. He looks up at it blankly, quill in his wing. The upper right of the frame is plain dark background.',
  dict(kind='veo', motion='The floating bird skull bobs gently in the air and pours a thin stream of ink from the small bottle into the inkwell on the desk, then straightens up. The grey bird at the desk watches it without expression and blinks once.',
       labels=[lab('编制：保留', .78, .20, 64, clip=22, frac=.0, box=True), lab('工龄：连续计算', .78, .33, 64, clip=22, frac=.42, box=True)])),
 (23, '正面一排五只小鸟，全都瞪圆了眼、张着嘴，笔停在半空。', 'Seen from the front: a row of five small round scribe birds in teal robes at their desks, all with eyes wide open and beaks hanging open in shock, white quills frozen in mid-air. Plain dark background behind them.', {}),
 (24, '食堂。科长面前的铁盘里一块半灰色的方块，他正往领口掖餐巾。鸟头骨从后面空着手飘过。', 'A dim canteen with long metal tables. ' + K + ', sits contentedly at a table with a metal tray holding one whole grey cube of paste and one half cube, tucking a napkin under his chin. Behind him ' + S + ', hovers past carrying no tray.',
  dict(labels=[lab('+ 半份淀粉', .76, .22, 72, CORAL, clip=24, frac=.5)])),
 # ---- 保定
 (25, '一张暖色的旧档案图：盘子里一个驴肉火烧，冒着热气。后面一头驴看着它。', 'A warm, glowing, faded archive picture: on a small plate in the middle, one Chinese donkey-meat flatbread sandwich (NOT a hamburger: no bun, no sesame seeds, no lettuce): a thin, round, flat, crisp, flaky layered pastry, golden brown, slit open along one side like a pocket and stuffed with chopped dark stewed meat and a little green pepper, steam rising. Behind it, small and soft, one ordinary grey DONKEY standing on four legs with hooves, long ears and a soft muzzle (a real mammal donkey: no beak, no wings, no feathers) looks at it. No birds in this picture. Warm amber and cream light in the centre, fading into deep indigo at the edges.',
  dict(setting='Setting: an old sunlit street-food stall, long ago, shown as a faded warm memory; no desks, no pipes, no candles. ', labels=[lab('驴肉火烧', .5, .062, 66, font='song', box=True)])),
 (26, '往下看一口没有底的档案井：四壁全是落灰的卷宗，一层一层缩进黑暗里，一条铁楼梯结满蛛网。没有人。', 'Looking straight down a bottomless square archive shaft: shelves crammed with dusty files and scrolls line all four walls, level below level, shrinking into total darkness; a narrow iron staircase spirals down, covered in cobwebs; one loose sheet of paper drifts in the air. No characters at all.',
  dict(labels=[lab('地下第 900 层', .5, .5, 76, box=True)])),
 # ---- 隔壁
 (27, '一堵墙上一扇半开的小门。老刘拿着空墨水瓶探进半个身子，里面是一屋子穿绛红袍子的小鸟在抄写。', 'A plain dark wall with one small wooden door standing half open. ' + L + ', holding an empty ink bottle, leans through the doorway and peeks into the next room, where ' + MAROON + ' sit at identical small desks writing by candlelight.',
  dict(labels=[lab('礼拜二', .14, .13, 60, MUTED)])),
 (28, '越过老刘的肩膀：隔壁桌上的羊皮纸有黑边和一个很大的红火漆印。穿绛红袍子的小鸟头也不抬地抄。', 'Over-the-shoulder view: ' + L + ', seen from behind at the left edge, looks over at the next desk in the middle of the frame, where one small brown sparrow in a MAROON robe sits writing, not looking up. On that desk lies a sheet of parchment with a thick black border and one round coral-red wax seal, ' + SCRIB + '. Only these two birds. The upper right of the frame is plain dark wall with nothing on it.',
  dict(labels=[lab('塔兰七号', .74, .16, 64, clip=28, frac=.5), lab('灭绝令', .74, .31, 120, CORAL, font='song', clip=28, frac=.72)])),
 (29, '【动画】太空里那颗土黄色的小星球裂开一道发光的缝。上方悬着三艘黑色方块战舰。', 'Seen from space: the same small ochre-yellow desert planet in the middle of the frame, with one bright glowing crack running across it and a few chunks starting to drift away; three dark blocky warships hang above it, thin beams of light going down from them to the planet. Silent and distant. The top fifth of the frame is empty space.',
  dict(setting=SPACE, kind='veo', fit=True, motion='The glowing cracks spread slowly across the small planet and it silently breaks apart into drifting glowing chunks. The three dark ships do not move.',
       labels=[lab('已执行 · 200 年前', .22, .42, 64), lab('（自己人炸的）', .22, .54, 50, MUTED, clip=29, frac=.62)])),
 (30, '隔壁的墙上六个相框，下面长桌上四十摞一模一样、盖了红印的纸。一只绛红袍子的小鸟往上再放一张。', 'A wall in the neighbouring office: a single row of six small oval portrait frames, each showing a similar round scribe bird in a MAROON robe; below, a long table with many identical neat stacks of parchment in a row, each stack sealed with a coral-red wax seal. One small scribe bird in a MAROON robe adds one more sheet to a stack. The top fifth of the frame is plain dark wall.',
  dict(labels=[lab('手续齐全 · 一式 40 份', .34, .42, 60, box=True), lab('隔壁：第 6 代', .34, .55, 60, CORAL, clip=30, frac=.62, box=True)])),
 (31, '剖面：正中一堵厚墙。左边一屋青绿袍子的小鸟在抄，右边一屋绛红袍子的小鸟在抄，两边像照镜子。', 'One continuous picture like a doll\'s house cut open: two identical rectangular offices side by side, separated by ONE thick dark brick wall running from top to bottom in the exact centre of the frame. LEFT room: four small round birds at small desks writing by candlelight, and every one of them wears a TEAL robe (no maroon in the left room). RIGHT room: four small round birds at identical desks writing by candlelight, and every one of them wears a MAROON robe (no teal in the right room). The two rooms are mirror images. Nobody looks at the wall.', {}),
 (32, '食堂打饭的队：青绿、绛红、青绿、绛红，一只挨一只，都端着空盘子直直看着前面，没有谁说话。', 'A dim canteen: one single long queue of small round scribe birds holding empty metal trays in front of a serving hatch, their robes alternating teal, maroon, teal, maroon. All of them stare straight ahead in silence with closed beaks; nobody looks at anybody. At the hatch a ladle drops a grey cube onto the first tray.', {}),
 (34, '老刘的大头近景，眼睛瞪圆，空墨水瓶从翅膀里滑下去。', 'Extreme close-up of the face of ' + L + ', his usually heavy eyes now very wide, beak slightly open; an empty ink bottle is slipping from his wing at the bottom of the frame. Plain dark background.', {}),
 # ---- 科长
 (35, '一张巨大的办公桌，一盏吊灯。科长坐在后面，竖起一只翅膀尖。桌前很小的老刘抱着墨水瓶站着。', 'A huge dark desk seen from the side under one hanging lamp, with towers of parchment on it; behind it, large, sits ' + K + ', raising one wingtip as he counts off his first point. In front of the desk, very small, stands ' + L + ', holding an ink bottle. The top fifth of the frame is plain dark background.',
  dict(labels=[lab('一、两个口子，不要串', .5, .11, 60, clip=36, frac=.55)])),
 (37, '科长一只翅膀慈爱地拍着身边一摞歪歪的、比他还高的文件。', 'Half-length: ' + K + ', lovingly pats a leaning tower of parchment taller than himself with one wing, looking at the viewer with raised eyebrows as if explaining something obvious. The top fifth of the frame is plain dark background.',
  dict(labels=[lab('二、文件在 → 科在 → 编制在', .5, .11, 60, clip=37, frac=.3)])),
 (38, '科长的近景：身子探过桌面，眼睛在镜片后面眯着，一只翅膀尖竖在嘴前。', 'Close-up: ' + K + ', leans forward over his desk towards the viewer, eyes narrowed behind his spectacles, one wingtip held upright in front of his beak in a hushing gesture. Dark background, lamp light from above. The right third of the frame is plain dark background.',
  dict(labels=[lab('三、', .74, .28, 64, clip=38, frac=.0), lab('situation', .80, .42, 84, CORAL, clip=38, frac=.3)])),
 (39, '很小的老刘站在大桌子前，两只翅膀摊开，张着嘴。', 'In front of the edge of the huge dark desk, small in the middle of the frame: ' + L + ', stands with both wings spread wide and his beak open, protesting. Only the dark edge of the desk and the lamp glow are visible besides him.', {}),
 (40, '科长已经低头在写别的东西，一只翅膀横着指向门，眼皮都没抬。', K + ', already looking down at the papers on his desk and writing with a quill, points one wing sideways towards the door without raising his eyes.', {}),
 (41, '背影：老刘沿着两排书桌中间长长的过道往回走，肩膀塌着。别的鸟照常抄。', 'In ' + HALL + ', seen from BEHIND (we see only his back and the back of his bald head, not his face): ' + L + ', walks slowly away from the viewer down the long central aisle, shoulders drooping, small in the frame. At the desks beside the aisle sit ' + FOUR + ', writing without looking up.', {}),
 # ---- 远方
 (42, '【动画】夜里的雪山。最高的峰上一座巨大的黑色宫殿，一扇拱门里透出金光，光里一个很小的坐着的瘦鸟剪影。一条很细的小鸟队伍沿山路往门里走。', 'On the highest peak stands a colossal dark palace with many buttresses and one tall arched doorway glowing gold from inside; deep inside the glow, very small, the silhouette of a gaunt bird seated on a huge throne with cables running from it. A long thin queue of tiny birds winds up a mountain path from the bottom right of the frame into the glowing doorway. Vast and distant. The upper left of the frame is plain night sky.',
  dict(setting='Setting: a snow-covered mountain range at night under a dark indigo sky with a few stars; no desks, no candles. ', kind='veo',
       motion='The queue of tiny birds shuffles slowly up the path and one by one disappears into the glowing doorway. The golden glow pulses faintly. A little snow drifts across.',
       labels=[lab('坐了一万年', .2, .16, 76, clip=42, frac=.45), lab('1,000 人 / 天', .2, .30, 76, CORAL, clip=43, frac=.3)])),
 (44, '一个由无数小光点组成的旋涡星系。右下角很小的老刘坐在小桌前，背对镜头，仰头看着。', 'A great spiral galaxy made of countless tiny dots of light fills the frame. In the bottom right corner, tiny, seen from behind: ' + L + ', sitting at his small desk with one candle, looking up at it.',
  dict(setting=SPACE.replace('no desks, no candles', 'no buildings'), labels=[lab('1,000,000 个世界', .28, .15, 72)])),
 (45, '羊皮纸的特写：一行行小波浪线，第三行中间空着一截，烛光正照在那里。笔尖停在旁边。', 'Extreme close view of a sheet of parchment: rows of tiny illegible wavy scribble lines; the third row is interrupted in the middle by a short empty gap of bare parchment (just blank, nothing drawn in the gap, no circle, no spot). The tip of a white feather quill rests beside the gap. The parchment fills most of the frame.' + NOBIRD,
  dict(labels=[lab('№ 0007-0611-0003', .5, .13, 76, font='song', clip=45, frac=.5, box=True)])),
 (46, '【动画】梦：一条很宽很宽的河，头顶是敞开的天和一轮满月。近岸很小的老刘背对镜头站着。', 'A dream: a very wide, calm river stretches across the whole frame under an enormous open sky with a full cream moon; moonlight on the water, a few reeds. On the near bank, small, seen from behind: ' + L + ', standing still, looking at the water. Lighter and more luminous than usual, soft teal and cream.',
  dict(setting='Setting: a dream of open country at night: a wide river, an open sky, a full moon. No buildings, no pipes, no desks, no candles. ', kind='veo',
       motion='The wide river flows slowly from left to right, moonlight ripples on the water, the reeds sway gently. The small grey bird stands completely still.')),
 # ---- 两个零
 (47, '食堂的长桌。老刘握着勺子，垂着眼皮看铁盘里一块灰色的方块。', 'A dim canteen table. ' + L + ', sits in the left half of the frame staring down at a metal tray holding one plain grey cube of paste, a spoon in his wing. Further along the table sit exactly two other birds in teal robes eating the same grey cubes: one YELLOW canary and one BLUE tit (neither grey, neither bald). The upper right of the frame is plain dark background.',
  dict(labels=[lab('灰的', .84, .11, 60, MUTED, clip=48, frac=.38, box=True), lab('有肘子味', .84, .23, 60, clip=48, frac=.62, box=True)])),
 (49, '特写：握着鹅毛笔的灰翅膀在抖，纸上滴了两滴墨。', 'Close view: the wing of a grey bird in a teal sleeve holds a white feather quill above a sheet of parchment; small shake lines around the trembling quill tip, and two small ink drops have fallen on the sheet. Candlelight. No face visible.', {}),
 (50, '羊皮纸特写：中间横着一道空白，笔尖悬在空白的右端，下面一滴新墨。', 'An extreme close-up, so tight that flat pale cream parchment covers the ENTIRE frame from edge to edge like a background: no desk, no room, no scroll ends and no dark areas are visible at all. The top two thirds of the frame are completely blank bare parchment with a faint paper grain; only the bottom quarter is ' + SCRIB + '. From the right edge the tip of a white feather quill pokes in at mid height, with one fresh dark ink drop under it.' + NOBIRD,
  dict(labels=[lab('8,000', 0.415, .34, 120, INKC), lab('00', 0.559, .34, 120, DKRED, clip=50, frac=.72)])),
 # ---- 批了
 (51, '俯视：一只镶金边袖子里的大翅膀握着一枚大印章，刚按在纸上，留下一个圆圆的红印，扬起一点灰。', 'Close view from above: a big wing in a gold-trimmed sleeve holds a large brass-and-wood stamp that has just been pressed down on a sheet of parchment in the left half of the frame, leaving a big round coral-red seal mark with no writing in it; a small puff of dust. The right half is plain dark desk.',
  dict(labels=[lab('批准', .78, .56, 150, CORAL, font='song', clip=51, frac=.55, box=True)])),
 (52, '大厅里，一面没有字的锦旗用两根绳子从天花板的黑洞里放下来。科长挺着胸举起两只翅膀去接。前景左边，老刘转过来面无表情地看着镜头。', 'In ' + HALL + ': a long cream-and-gold pennant banner (completely blank, with a gold fringe and one coral-red rosette, no writing) is being lowered on two ropes from a dark hole in the vaulted ceiling. Below it ' + K + ', stands with his chest puffed out and both wings raised to receive it. In the foreground at the left, turned to face the viewer with a flat, expressionless stare: ' + L + '.', {}),
 (54, '【动画】从很高很远的地方看：一列一列戴头盔的小兵鸟沿着宽坡道走进三艘巨大的黑色方块运输船，队伍排到地平线。', 'Seen from high up and far away: endless straight columns of tiny soldier birds in round helmets with packs march up wide ramps into three enormous dark blocky transport ships with rows of small amber lights. The columns stretch back to the horizon. The top fifth of the frame is smoky sky.',
  dict(setting='Setting: a vast spaceport landing field at night under a smoky indigo sky; no desks, no candles. ', kind='veo',
       motion='The columns of tiny soldier birds march steadily up the ramps into the ships. Small lights on the ships blink. Smoke drifts slowly.', labels=[lab('800,000 人', .5, .11, 84, CORAL)])),
 (55, '一艘黑色方块运输船驶进一个紫、红、青绿搅在一起的大旋涡。旋涡周围飘着几个没有数字的钟面，指针各指各的，有一根往回弯。', 'A dark blocky transport ship with rows of small amber lights sails into a huge swirling whirlpool of violet, coral and teal light. Around the whirlpool float several brass clock faces without any numerals, their hands pointing in different directions, one hand bent backwards.',
  dict(setting=SPACE, labels=[lab('走 40 年', .18, .16, 76, clip=55, frac=.42, box=True), lab('或者：出发前一天到', .76, .16, 60, CORAL, clip=55, frac=.68, box=True)])),
 # ---- 表彰
 (56, '大厅里一个矮矮的小台子。老刘僵直地站在上面，胸口别着一朵大红花，两眼发直。科长在旁边拍翅膀。后面的鸟没抬头。', 'A small low podium in ' + HALL + ': ' + L + ', stands on it stiffly with one big coral-red rosette ribbon pinned to his robe, staring blankly ahead. Beside the podium ' + K + ', claps his wings. A few small scribe birds at their desks behind do not look up.', {}),
 (57, '画面底部正中，很小的老刘坐在小桌前握着笔。左右和身后是一摞摞黑边空白表格，高得顶出画面。', L + ', sits very small at a small desk at the bottom centre of the frame, quill in his wing, one candle, walled in on both sides and behind by enormously tall towers of blank black-bordered forms that rise out of the top of the frame. The middle of the upper half of the frame, between the towers, is plain dark background.',
  dict(labels=[lab('阵亡通知', .5, .14, 96, font='song', box=True), lab('800,000 份 × 40', .5, .29, 64, CORAL, clip=57, frac=.5, box=True)])),
 (59, '从桌面的高度横着看大厅：一排排书桌和蜡烛退进黑暗里，每只鸟都在抄。远处尽头一扇黑黑的门。', 'Wide view of ' + HALL + ' from the side at desk level: endless rows of desks with candles receding into darkness, every small scribe bird in a teal robe writing. Far away at the end of the hall, one dark doorway.', {}),
 (60, '【动画】大厅右边一扇又高又窄的门。鸟头骨从书桌上方飘向门口，飘得偏高，撞了一下门框上沿，晃一晃，矮下去一点飘出去。老刘在下面抄，没抬头。', 'In ' + HALL + ': a tall narrow OPEN doorway (an empty opening with a wooden frame and no door leaf, darkness beyond it) in the wall at the right side of the frame. In the middle of the frame, in the air above the rows of desks, ' + S + ', floats towards the doorway, slightly too high: the top of the skull is level with the top beam of the door frame. Below, at the left, ' + L + ', sits at his desk writing, not looking up. At other desks sit ' + FOUR + ', also writing.',
  dict(kind='veo', fit=True, motion='The floating bird skull drifts slowly to the right towards the open doorway, bumps its head against the wooden door frame with a small jolt, wobbles back a little, then steers around the frame and floats out through the dark opening. The birds at the desks keep writing and do not look up.')),
]

REFKEYS = [('LAO LIU', '老刘'), ('SECTION CHIEF', '科长'), ('SERVO SKULL', '颅骨'), ('TECH-PRIEST', '机械教')]
META = dict(title='他们家一份文件抄了十一代', tag='（温馨感人）', source='战锤 40K 同人戏说', credit_src='teshi-style / samples / 09-wh40k-chaoxieyuan',
            credit_note='战锤 40K（Warhammer 40,000）的世界观属于 Games Workshop；本片为同人戏说，人物、情节虚构',
            output='抄写员-小鸟短剧.mp4', card_background='01', title_size=110, dark=True, numbers=NUMBERS,
            card=dict(subtitle='泰拉内务部一个三级抄写员老刘，', subtitle_size=60, subtitle_y=0.29, subtitle_color=[255, 243, 210, 235], title_y=0.43, tag_y=0.58),
            vstyle=' Static camera. 2D flat vector animation, limited smooth motion, keep the exact flat art style and colours of the input image, nothing new appears, no text.',
            style_note='平面矢量小鸟（与《金句》小鸟版同一套画法）：深靛蓝底、无描边、圆胖小鸟。老刘是秃顶灰鸽子，科长是猫头鹰，老王的伺服颅骨是一个飘着的鸟头骨，机械教同志是红袍小鸟。画面里不出字，数字和文件名用后期叠字。')
TODO = ['读音：4 处加了拼音提示，两处英文单词（situation、ridiculous）要听。', '音乐：出两个候选，见 音乐.json。', '叠字位置是按构图预估的，出图后逐镜对。']

if __name__ == '__main__':
    脚本.build(HERE, HERE.parent.parent / 'teshi-style' / 'samples' / '09-wh40k-chaoxieyuan.md', META, SCENES, SHOTS, HINTS, FLAGS, REFKEYS, TODO)

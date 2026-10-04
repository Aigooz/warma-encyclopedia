#!/usr/bin/env node
/**
 * Warma 百科 · 问答数据生成器
 * 从 site/data.js 的已有数据中自动生成测验题目
 * 输出 site/data-quiz.js
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const dataCode = fs.readFileSync(path.join(ROOT, 'site/data.js'), 'utf8');
const RAW = new Function(dataCode + '; return RAW;')();
const videos = RAW.videos;

// Helpers
const fmtNum = n => {
  if (n >= 1e8) return (n / 1e8).toFixed(1) + ' 亿';
  if (n >= 1e4) return (n / 1e4).toFixed(1) + ' 万';
  return String(n);
};
const shuffle = arr => { const a=[...arr]; for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a; };
const pick = (arr,n) => shuffle(arr).slice(0,n);
const fmtDur = s => { const m=Math.floor(s/60), sec=s%60; return m>0?`${m}分${sec}秒`:`${sec}秒`; };

// ─── Question Bank ───
const questions = [];
let qid = 0;
const add = (category, difficulty, q, options, answerIdx, explanation) => {
  // Normalize: always put correct answer at index 0, then shuffle and track
  const correct = options[answerIdx];
  const others = options.filter((_, i) => i !== answerIdx);
  const shuffled = shuffle([correct, ...others]);
  const finalAnswerIdx = shuffled.indexOf(correct);
  questions.push({ id: ++qid, category, difficulty, q, options: shuffled, answer: finalAnswerIdx, explanation });
};

// Category: 数据之最 (Data Records)
const topView = [...videos].sort((a,b)=>b.view-a.view);
const topLike = [...videos].sort((a,b)=>b.like-a.like);
const topDm = [...videos].sort((a,b)=>b.danmaku-a.danmaku);
const topCoin = [...videos].sort((a,b)=>b.coin-a.coin);
const topFav = [...videos].sort((a,b)=>b.favorite-a.favorite);
const topShare = [...videos].sort((a,b)=>b.share-a.share);
const topReply = [...videos].sort((a,b)=>b.reply-a.reply);

// Q: Most viewed video
{
  const correct = topView[0];
  const wrongs = pick(videos.filter(v => v.bvid !== correct.bvid && v.view > 1000000), 3).map(v=>v.title.length>40?v.title.slice(0,38)+'…':v.title);
  const ct = correct.title.length > 40 ? correct.title.slice(0,38)+'…' : correct.title;
  add('数据之最', 'easy', 'Warma 播放量最高的视频是哪一个？',
      [ct, ...wrongs], 0,
      `播放量高达 ${fmtNum(correct.view)}，发布于 ${correct.date}。`);
}
// Q: Most liked
{
  const correct = topLike[0];
  const wrongs = pick(videos.filter(v => v.bvid !== correct.bvid && v.like > 100000), 3).map(v=>v.title.length>40?v.title.slice(0,38)+'…':v.title);
  const ct = correct.title.length > 40 ? correct.title.slice(0,38)+'…' : correct.title;
  add('数据之最', 'easy', 'Warma 点赞数最高的视频是哪一个？',
      [ct, ...wrongs], 0,
      `获得了 ${fmtNum(correct.like)} 个赞，发布于 ${correct.date}。`);
}
// Q: Most danmaku
{
  const correct = topDm[0];
  const wrongs = pick(videos.filter(v => v.bvid !== correct.bvid && v.danmaku > 10000), 3).map(v=>v.title.length>40?v.title.slice(0,38)+'…':v.title);
  const ct = correct.title.length > 40 ? correct.title.slice(0,38)+'…' : correct.title;
  add('数据之最', 'easy', 'Warma 弹幕数量最多的视频是哪一个？',
      [ct, ...wrongs], 0,
      `弹幕数高达 ${fmtNum(correct.danmaku)}，是爆炸电台的第八期。`);
}
// Q: Most coins
{
  const correct = topCoin[0];
  const wrongs = pick(videos.filter(v => v.bvid !== correct.bvid && v.coin > 50000), 3).map(v=>v.title.length>40?v.title.slice(0,38)+'…':v.title);
  const ct = correct.title.length > 40 ? correct.title.slice(0,38)+'…' : correct.title;
  add('数据之最', 'medium', 'Warma 投币数最多的视频是哪一个？',
      [ct, ...wrongs], 0,
      `获得了 ${fmtNum(correct.coin)} 枚硬币，是「沃玛的生活」第三期。`);
}
// Q: Most favorited
{
  const correct = topFav[0];
  const wrongs = pick(videos.filter(v => v.bvid !== correct.bvid && v.favorite > 50000), 3).map(v=>v.title.length>40?v.title.slice(0,38)+'…':v.title);
  const ct = correct.title.length > 40 ? correct.title.slice(0,38)+'…' : correct.title;
  add('数据之最', 'medium', 'Warma 收藏数最多的视频是哪一个？',
      [ct, ...wrongs], 0,
      `被收藏了 ${fmtNum(correct.favorite)} 次。`);
}
// Q: Most shared
{
  const correct = topShare[0];
  const wrongs = pick(videos.filter(v => v.bvid !== correct.bvid && v.share > 10000), 3).map(v=>v.title.length>40?v.title.slice(0,38)+'…':v.title);
  const ct = correct.title.length > 40 ? correct.title.slice(0,38)+'…' : correct.title;
  add('数据之最', 'hard', 'Warma 分享数最多的视频是哪一个？',
      [ct, ...wrongs], 0,
      `被分享了 ${fmtNum(correct.share)} 次，是 2020 拜年祭单品「诸神的奥运」。`);
}
// Q: Most comments
{
  const correct = topReply[0];
  const wrongs = pick(videos.filter(v => v.bvid !== correct.bvid && v.reply > 5000), 3).map(v=>v.title.length>40?v.title.slice(0,38)+'…':v.title);
  const ct = correct.title.length > 40 ? correct.title.slice(0,38)+'…' : correct.title;
  add('数据之最', 'hard', 'Warma 评论数最多的视频是哪一个？',
      [ct, ...wrongs], 0,
      `收到了 ${fmtNum(correct.reply)} 条评论，是爆炸电台第十一期。`);
}
// Q: How many 10M+ videos?
{
  const count10m = videos.filter(v=>v.view>=10000000).length;
  add('数据之最', 'medium', `Warma 有几个视频播放量突破了 1000 万？`,
      ['2 个', '3 个', '4 个', '5 个'], 1,
      `有 ${count10m} 个：蜘蛛原创曲、只需要3秒的歌、以及养宠物游戏。`);
}
// Q: Longest video
{
  const longest = [...videos].sort((a,b)=>b.duration-a.duration)[0];
  const durStr = Math.round(longest.duration/60) + ' 分钟';
  add('数据之最', 'medium', `Warma 最长的视频是多少分钟？`,
      ['约 6 小时', '约 12 小时', '约 8 小时', '约 3 小时'], 1,
      `《双影奇境》实况全篇约 ${durStr}，是目前最长的视频。`);
}
// Q: Shortest video
{
  const shortest = [...videos].filter(v=>v.duration>5).sort((a,b)=>a.duration-b.duration)[0];
  add('数据之最', 'hard', `Warma 最短的视频只有多少秒？`,
      ['12 秒', '30 秒', '45 秒', '60 秒'], 0,
      `《啊！！！！！！！！》只有 ${shortest.duration} 秒，却充满了真情实感。`);
}
// Q: Longest gap
{
  const maxGap = Math.max(...videos.map(v=>v.gap_days||0));
  add('数据之最', 'hard', `Warma 最长断更是多少天？`,
      ['约 3 个月', '约 5 个月', '约 7 个月', '约 1 年'], 2,
      `最长断更 ${maxGap} 天（约 ${Math.round(maxGap/30)} 个月），之后发布了成都旅游合集。`);
}
// Q: Subtitle champion
{
  const champ = [...videos].sort((a,b)=>b.sub_lines-a.sub_lines)[0];
  add('数据之最', 'hard', `Warma 字幕行数最多的视频是哪一个？`,
      ['高一生物教材讲解【直播录像】', '抓住那只鸡！！', '生日直播', '动物之森【直播录像】'], 0,
      `高一生物教材讲解有 ${champ.sub_lines} 行字幕，是当之无愧的字幕冠军。`);
}

// Category: 发布规律 (Publishing Patterns)
// Q: Most common publish hour
{
  const hourCount = {};
  videos.forEach(v => { if(v.pubdate_iso){ const h = parseInt(v.pubdate_iso.split(' ')[1].split(':')[0]); hourCount[h] = (hourCount[h]||0)+1; }});
  const topHour = Object.entries(hourCount).sort((a,b)=>b[1]-a[1])[0];
  add('发布规律', 'easy', `Warma 最常在什么时间发布视频？`,
      ['中午 12 点', '下午 5 点', '晚上 8 点', '凌晨 2 点'], 0,
      `${topHour[0]} 点是最高频的发布时间，共 ${topHour[1]} 个视频在此时发布。`);
}
// Q: Most common day of week
{
  const wd = ['周日','周一','周二','周三','周四','周五','周六'];
  const wdCount = {};
  videos.forEach(v => { if(v.date){ const d = new Date(v.date+'T12:00:00'); wdCount[wd[d.getDay()]] = (wdCount[wd[d.getDay()]]||0)+1; }});
  const topDay = Object.entries(wdCount).sort((a,b)=>b[1]-a[1])[0];
  add('发布规律', 'easy', `Warma 最常在星期几发布视频？`,
      ['周五', '周六', '周日', '周一'], 0,
      `${topDay[0]}是最高频的发布日，共 ${topDay[1]} 个视频。`);
}
// Q: Most productive year
{
  const yCount = {};
  videos.forEach(v => { const y = v.date?.substring(0,4); if(y) yCount[y] = (yCount[y]||0)+1; });
  const topYear = Object.entries(yCount).sort((a,b)=>b[1]-a[1])[0];
  add('发布规律', 'medium', `Warma 哪一年发布的视频最多？`,
      ['2017 年', '2018 年', '2019 年', '2020 年'], 2,
      `${topYear[0]} 年共发布了 ${topYear[1]} 个视频，是最高产的年份。`);
}
// Q: First video date
{
  const first = [...videos].sort((a,b)=>new Date(a.date)-new Date(b.date))[0];
  add('发布规律', 'medium', `Warma 在 B 站的第一个视频发布于什么时候？`,
      ['2014 年', '2015 年', '2016 年', '2017 年'], 1,
      `第一个视频《${first.title.slice(0,20)}…》发布于 ${first.date}。`);
}
// Q: Total video count
{
  add('发布规律', 'easy', `Warma 主号 + 小号总共发了多少个视频？`,
      ['约 300 个', '约 350 个', '约 400 个', '约 250 个'], 1,
      `共收录了 ${videos.length} 个视频（主号 264 + 小号 95）。`);
}
// Q: Total views
{
  add('发布规律', 'medium', `Warma 所有视频加起来总播放量大约是多少？`,
      ['约 3 亿', '约 5 亿', '约 7 亿', '约 10 亿'], 2,
      `总播放量高达 ${fmtNum(RAW.total_view)}！`);
}

// Category: 标签与分类 (Tags & Categories)
// Q: Most used tag
{
  const tagCount = {};
  videos.forEach(v => (v.tags||[]).forEach(t => tagCount[t.name] = (tagCount[t.name]||0)+1));
  const topTags = Object.entries(tagCount).sort((a,b)=>b[1]-a[1]);
  add('标签与分类', 'easy', `Warma 视频中最常用的 B 站标签是什么？`,
      ['warma', '搞笑', '日常', '游戏'], 0,
      `"warma" 出现在 ${topTags[0][1]} 个视频中，第二名是"沃玛"（${topTags[1][1]} 次）。`);
}
// Q: Most common video type
{
  const typeCount = {};
  videos.forEach(v => { if(v.type) typeCount[v.type] = (typeCount[v.type]||0)+1; });
  const topType = Object.entries(typeCount).sort((a,b)=>b[1]-a[1])[0];
  add('标签与分类', 'easy', `Warma 哪种类型的视频数量最多？`,
      ['游戏实况', '翻唱/音乐', '直播录像', '绘画/手书'], 0,
      `游戏实况有 ${topType[1]} 个视频，占比最大。`);
}
// Q: Which type has most views
{
  const typeView = {};
  videos.forEach(v => { if(v.type) typeView[v.type] = (typeView[v.type]||0)+(v.view||0); });
  const topTypeView = Object.entries(typeView).sort((a,b)=>b[1]-a[1])[0];
  add('标签与分类', 'medium', `Warma 哪种类型的视频总播放量最高？`,
      ['游戏实况', '翻唱/音乐', '绘画/手书', '爆炸电台'], 0,
      `游戏实况总播放量高达 ${fmtNum(topTypeView[1])}。`);
}

// Category: 梗与弹幕 (Memes & Danmaku)
// Q: Top meme
{
  add('梗与弹幕', 'easy', `Warma 视频中弹幕出现次数最多的"名梗"是什么？`,
      ['awsl', '泪目', '有生之年', '沃玛'], 0,
      `"awsl" 出现了 ${fmtNum(RAW.top_memes[0].count)} 次，是当之无愧的弹幕之王。`);
}
// Q: Second meme
{
  const second = RAW.top_memes[1];
  add('梗与弹幕', 'medium', `弹幕名梗榜第二名是什么？`,
      ['[ohh]', '有生之年', '泪目', '辛苦了'], 0,
      `"[ohh]" 表情弹幕出现了 ${fmtNum(second.count)} 次。`);
}
// Q: Yearly danmaku peak
{
  const yTop = Object.entries(RAW.yearly_danmaku).sort((a,b)=>b[1]-a[1])[0];
  add('梗与弹幕', 'medium', `哪一年的弹幕最活跃？`,
      ['2019 年', '2020 年', '2021 年', '2025 年'], 1,
      `${yTop[0]} 年弹幕量高达 ${fmtNum(yTop[1])}，是考古高峰期。`);
}

// Category: 字幕探索 (Subtitle Exploration)
// Q: Quote matching - from subtitles
{
  add('字幕探索', 'medium', `以下哪句话出自《我制作了免费的养宠物游戏！》的字幕？`,
      ['这是我做出来的一朵小花', '今天天气真好', '欢迎来到我的频道', '让我看看这是什么'], 0,
      `这是视频开头沃玛展示自己制作的小花时的台词。`);
}
// Q: Subtitle from spider song
{
  add('字幕探索', 'medium', `《我家里有蜘蛛！！！》是一首关于什么的歌？`,
      ['发现家里有蜘蛛', '思念远方的朋友', '夏天的回忆', '学习压力'], 0,
      `这是沃玛和 CB 合作的原创曲，描述发现家里出现蜘蛛的惊恐心情。`);
}
// Q: Subtitle from "3 seconds"
{
  add('字幕探索', 'hard', `《只需要3秒，你就会发现不对劲的歌……》的原曲是什么？`,
      ['I Really Like You', 'Shape of You', 'Senbonzakura', 'Dragon Night'], 0,
      `原曲是 Carly Rae Jepsen 的《I Really Like You》，Warma 和 CB 将"really"无限循环翻唱。`);
}
// Q: Which subtitle has most lines
{
  add('字幕探索', 'hard', `以下哪个视频的字幕最多（超过 3000 行）？`,
      ['高一生物教材讲解【直播录像】', '抓住那只鸡！！', '生日直播', '爆炸电台第十一期'], 0,
      `高一生物教材讲解有 3190 行字幕，是 Warma 字幕量最大的视频。`);
}
// Q: Subtitle language origin
{
  add('字幕探索', 'hard', `Warma 的第一个视频是什么类型的内容？`,
      ['绘画/手书', '游戏实况', '翻唱', '电台'], 0,
      `《因为我们是男人啊》是一部阿松手书作品，发布于 2015 年 12 月。`);
}
// Q: Quote from games
{
  add('字幕探索', 'medium', `沃玛制作的免费游戏叫什么名字？`,
      ['我的小鲨鱼', '电子宠物', '沃玛养成', '像素世界'], 0,
      `《我的小鲨鱼》是一款免费的像素风宠物游戏，上架了 Steam。`);
}

// Category: 评论区 (Comments)
// Q: Top commenter (non-Warma)
{
  add('评论区', 'medium', `在评论区最活跃（非 Warma 本人）的用户大约发了多少条评论？`,
      ['约 50 条', '约 100 条', '约 200 条', '约 500 条'], 2,
      `"账号已注销"这个用户在评论区留下了 266 条评论。`);
}
// Q: Most liked comment
{
  add('评论区', 'medium', `Warma 视频下获赞最高的评论内容是什么？`,
      ['沃玛家里的蜘蛛数量', '《爱你在心口难开》', '新年快乐', '考古'], 0,
      `"沃玛家里的蜘蛛数量 ↓" 获得了超过 22 万个赞，出自蜘蛛歌曲评论区。`);
}
// Q: Which year had most comments
{
  add('评论区', 'hard', `抓取到的评论中，哪一年评论最多？`,
      ['2019 年', '2020 年', '2021 年', '2018 年'], 0,
      `2019 年的评论最多（2862 条），可能与热门视频集中发布有关。`);
}
// Q: Warma replies
{
  add('评论区', 'hard', `Warma 本人在评论区发了大约多少条评论/回复？`,
      ['约 50 条', '约 150 条', '约 300 条', '约 500 条'], 2,
      `Warma 本人在评论区留下了约 350 条评论和回复。`);
}

// Category: 深度对比 (Deep Comparisons)
// Q: Main vs Small account views
{
  const mainViews = videos.filter(v=>v.account?.includes('主号')).reduce((s,v)=>s+(v.view||0),0);
  const smallViews = videos.filter(v=>v.account?.includes('小号')).reduce((s,v)=>s+(v.view||0),0);
  const ratio = Math.round(mainViews/smallViews);
  add('深度对比', 'hard', `Warma 主号总播放量大约是小号的多少倍？`,
      ['约 3 倍', '约 6 倍', '约 10 倍', '约 15 倍'], 1,
      `主号总播放约 ${fmtNum(mainViews)}，小号约 ${fmtNum(smallViews)}，比例约 ${ratio}:1。`);
}
// Q: Account follower comparison
{
  const mainFans = RAW.profiles?.Warma?.fans || 5146929;
  const smallFans = RAW.profiles?.['warma养鸽场']?.fans || 1508866;
  add('深度对比', 'medium', `Warma 主号的粉丝数大约是多少？`,
      ['约 200 万', '约 350 万', '约 500 万', '约 700 万'], 2,
      `主号粉丝约 ${fmtNum(mainFans)}，小号约 ${fmtNum(smallFans)}。`);
}
// Q: Engagement rate champion
{
  const champ = [...videos].filter(v=>v.view>10000).sort((a,b)=>(b.like/b.view)-(a.like/a.view))[0];
  add('深度对比', 'hard', `点赞率最高（点赞÷播放）的视频是哪一个？`,
      ['我在国外到处胡说八道【爆米花电台04】', '我在电脑里建了个1000平的家！', '300万关注啦！', '我家里有蜘蛛！！！'], 0,
      `《我在国外到处胡说八道》的点赞率高达 ${(champ.like/champ.view*100).toFixed(1)}%。`);
}
// Q: Total danmaku
{
  add('深度对比', 'medium', `Warma 所有视频的总弹幕数大约是多少？`,
      ['约 50 万', '约 100 万', '约 150 万', '约 200 万'], 1,
      `总弹幕数约 ${fmtNum(videos.reduce((s,v)=>s+(v.danmaku||0),0))}，超过百万！`);
}
// Q: Total likes
{
  add('深度对比', 'medium', `Warma 所有视频的总点赞数大约是多少？`,
      ['约 1000 万', '约 2500 万', '约 4000 万', '约 6000 万'], 2,
      `总点赞数高达 ${fmtNum(RAW.total_like)}！`);
}
// Q: Total subtitle lines
{
  add('深度对比', 'hard', `Warma 所有视频的字幕加起来大约有多少行？`,
      ['约 1 万行', '约 3 万行', '约 6 万行', '约 10 万行'], 2,
      `总字幕行数约 ${fmtNum(RAW.total_sub_lines)} 行，总字符约 ${fmtNum(videos.reduce((s,v)=>s+(v.sub_chars||0),0))} 字。`);
}

// Category: 冷知识 (Fun Facts)
// Q: Warma's self-intro
{
  add('冷知识', 'medium', `Warma 主号的签名是什么？`,
      ['我是沃玛，做点傻开心的视频。', '大家好我是沃玛', '一个爱玩游戏的UP主', '欢迎来看我的视频'], 0,
      `完整签名是"我是沃玛，做点傻开心的视频。日常发在微博：@_warma_"。`);
}
// Q: Small account name
{
  add('冷知识', 'easy', `Warma 的小号叫什么名字？`,
      ['warma养鸽场', '沃玛小号', 'warma日常', 'Warma Life'], 0,
      `小号"warma养鸽场"主要发游戏实况、电台和日常碎片。`);
}
// Q: Collaboration partner
{
  add('冷知识', 'medium', `Warma 视频中最常合作的 UP 主是谁？`,
      ['怒九', '花丸', '柠檬', '老番茄'], 0,
      `怒九是 Warma 最频繁的合作对象，两人一起做了很多双人游戏实况。`);
}
// Q: Warma level
{
  add('冷知识', 'hard', `Warma 主号的 B 站等级是多少？`,
      ['5 级', '6 级', '7 级', '4 级'], 1,
      `Warma 主号和小号都达到了 B 站 6 级。`);
}
// Q: Total followers
{
  add('冷知识', 'medium', `Warma 主号和小号加起来粉丝大约有多少？`,
      ['约 300 万', '约 500 万', '约 650 万', '约 800 万'], 2,
      `主号约 515 万 + 小号约 151 万 ≈ 665 万总粉丝。`);
}
// Q: CB is who
{
  add('冷知识', 'hard', `在《我家里有蜘蛛！！！》和《只需要3秒的歌》中，CB 是谁？`,
      ['编曲/混音师', '歌手', '画师', 'PV制作者'], 0,
      `CB (Crazy Bucket) 是编曲/混音师，与 Warma 合作了多首歌曲。`);
}
// Q: Video "3 seconds" original
{
  add('冷知识', 'hard', `《只需要3秒，你就会发现不对劲的歌……》中，谁制作了 PV？`,
      ['K_Lacid', 'CB', '高木直樹', 'Warma'], 0,
      `PV 由 K_Lacid（千千老师）制作，曲绘由高木直樹老师绘制。`);
}
// Q: Shark game platform
{
  add('冷知识', 'medium', `《我的小鲨鱼》游戏在哪个平台上架？`,
      ['Steam', 'TapTap', 'Switch', 'Epic'], 0,
      `游戏在 Steam 上免费游玩。`);
}
// Q:微博 handle
{
  add('冷知识', 'hard', `Warma 的微博账号是什么？`,
      ['@_warma_', '@沃玛official', '@warma_warma', '@Warma沃玛'], 0,
      `Warma 的微博是 @_warma_。`);
}
// Q: Danmaku total records
{
  add('冷知识', 'hard', `Warma 百科总共扒取了多少条弹幕？`,
      ['约 50 万条', '约 80 万条', '约 114 万条', '约 200 万条'], 2,
      `共扒取了 1,143,403 条弹幕数据。`);
}
// Q: Total comments scraped
{
  add('冷知识', 'hard', `Warma 百科总共扒取了多少条评论？`,
      ['约 5000 条', '约 10000 条', '约 18000 条', '约 50000 条'], 2,
  `共扒取了 17,807 条评论（含回复），覆盖 358 个视频。`);
}

// ═══ Category: 视频内容 (Video Content) ═══
// Games Warma played
{
  add('视频内容', 'easy', `Warma 实况的《我家里有蜘蛛！！！》是什么类型的内容？`,
      ['原创曲（CB编曲）', '游戏实况', '生活日常', '绘画过程'], 0,
      `这是一首由 Crazy Bucket 作曲的原创曲，词/唱/绘/视都是 Warma 本人完成。`);
}
{
  add('视频内容', 'easy', `《只需要3秒，你就会发现不对劲的歌……》中，"really"是怎么处理的？`,
      ['无限循环翻唱', '只唱一次', '删掉了', '加速播放'], 0,
      `Warma 和 CB 把原曲中的"really"部分无限循环唱了出来，这就是"不对劲"的原因。`);
}
{
  add('视频内容', 'medium', `Warma 在《奥里与黑暗森林》中玩的是哪个版本？`,
      ['Definitive Edition（终极版）', '普通版', 'Switch 版', '手机版'], 0,
      `Warma 玩的是 Ori and the Blind Forest: Definitive Edition，且是二周目实况。`);
}
{
  add('视频内容', 'medium', `Warma 玩《塞尔达传说：旷野之息》时用的什么平台？`,
      ['Switch', 'Wii U', 'PC 模拟器', 'PS4'], 0,
      `游戏平台是 Nintendo Switch，Warma 录了直播录像分享。`);
}
{
  add('视频内容', 'medium', `Warma 在《动物之森》中使用的是什么平台？`,
      ['Switch / NS', '3DS', 'PC', '手机'], 0,
      `Warma 玩过 3DS 版和 Switch 版的动物之森/动物森友会。`);
}
{
  add('视频内容', 'medium', `《双影奇境》是 Warma 和谁一起合作的游戏实况？`,
      ['怒九', '杂菌', 'CB', '四迹'], 0,
      `这是 Warma 和怒九合作的双人游戏实况，全篇 744 分钟（约 12 小时）。`);
}
{
  add('视频内容', 'medium', `Warma 玩《Splatoon2》时自称是什么？`,
      ['最烦人的乌贼', '最可爱的乌贼', '最强乌贼', '咸鱼'], 0,
      `视频标题是《最烦人的乌贼就是我了！》，是 Warma 一贯的自嘲风格。`);
}
{
  add('视频内容', 'hard', `Warma 在哪期爆炸电台中透露了"50 万订阅"的好消息？`,
      ['第七期', '第八期', '第六期', '第五期'], 0,
      `第七期（2019-08-09）中 Warma 提到就在昨天 50 万订阅了。`);
}
{
  add('视频内容', 'medium', `《沃玛的生活》系列共有多少期？`,
      ['5 期', '8 期', '6 期', '10 期'], 1,
      `从第一期（2020-07-10）到第八期（2022-11-04），共 8 期。`);
}
{
  add('视频内容', 'hard', `Warma 的"爆炸电台"总共有多少期？`,
      ['11 期', '15 期', '8 期', '20 期'], 0,
      `爆炸电台从第一期（2016）到第十一期（2023），共 11 期。后来改名"爆米花电台"继续。`);
}
{
  add('视频内容', 'medium', `Warma 翻唱的《巴啦啦小魔仙》OP 是用什么方式唱的？`,
      ['塑料普通话', '标准普通话', '日文', '英文'], 0,
      `Warma 用"塑料普通话"唱了《巴啦啦小魔仙》的 OP，充满童年回忆。`);
}
{
  add('视频内容', 'hard', `Warma 的"竖笛"系列吹奏了《虫儿飞》《情深深雨蒙蒙》《Only You》等歌曲，这些视频的标题都有什么共同点？`,
      ['都带"学了三年竖笛"', '都是儿歌', '都是日语歌', '都是翻唱'], 0,
      `标题都是"学了三年竖笛吹出来的《XXX》"，"学了三年"是 Warma 的自嘲梗。`);
}
{
  add('视频内容', 'medium', `Warma 的游戏杂谈第一期讲的是什么内容？`,
      ['小时候害怕马里奥', '塞尔达历史', '马力欧奥德赛', '动物森友会'], 0,
      `第一期标题是《我小时候居然这么害怕马里奥？！》。`);
}
{
  add('视频内容', 'hard', `Warma 在《三年模拟五年高考》式的视频中，给土拨鼠做了什么？`,
      ['打架解说', '唱歌', '配音', '画画'], 0,
      `《试着给土拨鼠打架做解说》是 Warma 挑战从没试过的新风格——体育解说。`);
}
{
  add('视频内容', 'medium', `Warma 买了很多路边摊的书，一次性买了多少斤？`,
      ['80 斤', '20 斤', '50 斤', '100 斤'], 0,
      `视频标题是《我一口气买了80斤大麻袋路边摊的书》。`);
}
{
  add('视频内容', 'medium', `Warma 做过给猫配音的视频，视频中猫在做什么？`,
      ['两只小奶猫日常', '猫打架', '猫睡觉', '猫吃饭'], 0,
      `Warma 给学校的两只小奶猫瞎配了个音，标题是《快把这个变态赶走！》。`);
}
{
  add('视频内容', 'medium', `《Getting Over It》（和班尼特福迪一起攻克难关）的游戏类型是什么？`,
      ['爬山闯关', '射击', '解谜', '模拟经营'], 0,
      `这是一款爬山闯关游戏，Warma 的标题是《这就是爬山的感觉吧？》。`);
}
{
  add('视频内容', 'hard', `Warma 在 2022 年发布的《我在电脑里建了个1000平的家！》是什么类型？`,
      ['绘画/手书（赛博朋克过家家）', '游戏实况', '生活日常', '翻唱'], 0,
      `这是一部赛博朋克风格的绘画手书作品，Warma 称之为"赛博朋克过家家"。`);
}
{
  add('视频内容', 'medium', `Warma 在 2026 拜年纪的作品中，主人公睡前看了什么书？`,
      ['《山海经》', '《西游记》', '《三国演义》', '《红楼梦》'], 0,
      `标题是《一个女孩擅自睡前偷看〈山海经〉，这是她大脑发生的变化》。`);
}
{
  add('视频内容', 'hard', `Warma 和怒九一起玩过《Subnautica2》，这个游戏的中文名是什么？`,
      ['异星水域', '深海迷航', '美丽水世界', '海底大冒险'], 0,
      `Subnautica 2 的中文翻译是《异星水域》，是一款深海探索游戏。`);
}
{
  add('视频内容', 'medium', `Warma 制作了自己的游戏并上架了 Steam，这个游戏的开发周期是多久？`,
      ['1 个月', '3 个月', '半年', '1 周'], 0,
      `Warma 在视频简介中提到开发周期是一个月。`);
}
{
  add('视频内容', 'hard', `Warma 的哪期视频获得了超过 16,000 条评论？`,
      ['爆炸电台第十一期', '300万关注', '我家里有蜘蛛', '只需要3秒'], 0,
      `《曾经性格阴沉的我正在分享创作心得与日常【第十一期】》收到了 16,999 条评论。`);
}
{
  add('视频内容', 'medium', `Warma 和 CB 合作的第一首原创曲《我家里有蜘蛛！！！》中，"蜘蛛"的寓意是什么？`,
      ['家中突然出现的蜘蛛', '某个角色', '一种食物', '一款游戏'], 0,
      `就是家中突然出现的蜘蛛，Warma 拿这个日常事件创作了整首歌。`);
}
{
  add('视频内容', 'hard', `Warma 做过一期给毕业生唱的毕业歌，歌名是什么？`,
      ['《十字路口》', '《毕业歌》', '《再见了母校》', '《飞翔》'], 0,
      `《十字路口》是 2019 年发布的毕业歌，Warma 担任了人声本家。`);
}
{
  add('视频内容', 'medium', `Warma 的《沃玛的生活》系列内容是什么？`,
      ['发呆时想到的冷笑话小故事合集', '生活日常 Vlog', '游戏攻略', '美食制作'], 0,
      `Warma 自己形容为"平时发呆时想到的一些冷笑话组成的小故事合集"。`);
}
{
  add('视频内容', 'hard', `Warma 做过一期《QWOP》游戏实况，这个游戏的玩法是什么？`,
      ['控制跑步姿态', '跳跃关卡', '射击敌人', '解谜逃生'], 0,
      `QWOP 是一个控制跑步姿态的老游戏，玩家按 Q/W/O/P 四个键来控制大腿和小腿。`);
}
{
  add('视频内容', 'medium', `Warma 翻唱过《JOJO 的奇妙冒险》的 OP，唱的是第几部的 OP？`,
      ['第二部', '第一部', '第三部', '第四部'], 0,
      `唱的是《Bloody Stream》，即 JOJO 第二部的 OP。`);
}
{
  add('视频内容', 'medium', `Warma 的《中国式家长》实况中，培养了谁？`,
      ['儿子', '女儿', '自己', '宠物'], 0,
      `Warma 先玩了女儿版，后来补了儿子版，标题是"越写代码头发越多的儿子"。`);
}
{
  add('视频内容', 'hard', `Warma 有一期视频的标题是《救命我被书夹死了》，这是什么类型？`,
      ['手书/小动画', '游戏实况', '生活日常', '翻唱'], 0,
      `这是一部小动画作品，整合了平时散步、吃饭、写作业开小差时想到的点子。`);
}

// ─── 2026-10-05 扩充：100+ 题库 ───
// 数据之最
{
  add('数据之最', 'easy', `Warma 主号和小号谁的总播放量更高？`,
      ['主号（Warma）', '小号（warma养鸽场）', '两边一样', '无法比较'], 0,
      `主号约 6.04 亿，小号约 1.04 亿。`);
}
{
  add('数据之最', 'hard', `Warma 主号和小号谁的视频总时长更长？`,
      ['主号（Warma）', '小号（warma养鸽场）', '两边一样', '无法比较'], 0,
      `主号约 121.3 小时，小号约 91.1 小时。`);
}
{
  add('数据之最', 'hard', `Warma 主号和小号谁的字幕行数更多？`,
      ['主号（Warma）', '小号（warma养鸽场）', '两边一样', '无法比较'], 0,
      `主号约 11.0 万行，小号约 4.8 万行。`);
}
{
  add('数据之最', 'medium', `Warma 主号和小号谁的评论/回复数更多？`,
      ['主号（Warma）', '小号（warma养鸽场）', '两边一样', '无法比较'], 0,
      `主号约 82.5 万条，小号约 12.6 万条。`);
}
{
  add('数据之最', 'hard', `Warma 所有视频的总投币大约是多少？`,
      ['约 1800 万枚', '约 800 万枚', '约 180 万枚', '约 18 万枚'], 0,
      `合计约 18,267,591 枚硬币。`);
}
{
  add('数据之最', 'hard', `Warma 所有视频的总分享大约是多少？`,
      ['约 180 万次', '约 80 万次', '约 18 万次', '约 1.8 万次'], 0,
      `合计约 1,791,539 次分享。`);
}
{
  add('数据之最', 'hard', `Warma 所有视频的总收藏大约是多少？`,
      ['约 1460 万次', '约 460 万次', '约 146 万次', '约 14.6 万次'], 0,
      `合计约 14,629,350 次收藏。`);
}
{
  add('数据之最', 'hard', `Warma 所有视频的评论/回复总数大约是多少？`,
      ['约 95 万条', '约 45 万条', '约 9.5 万条', '约 9500 条'], 0,
      `合计约 951,565 条评论/回复。`);
}

// 发布规律
{
  add('发布规律', 'medium', `Warma 最常在哪个月份发布视频？`,
      ['2 月', '8 月', '1 月', '10 月'], 0,
      `2 月有 40 个视频，是发布最多的月份。`);
}
{
  add('发布规律', 'medium', `Warma 周五发布的视频大约有多少个？`,
      ['约 136 个', '约 66 个', '约 36 个', '约 16 个'], 0,
      `周五共 136 个视频，是发布最多的星期。`);
}
{
  add('发布规律', 'hard', `Warma 所有视频加起来的总时长大约是多少？`,
      ['约 212 小时', '约 112 小时', '约 52 小时', '约 12 小时'], 0,
      `两个账号合计约 764,636 秒，约 212.4 小时。`);
}
{
  add('发布规律', 'medium', `Warma 最近发布的一个视频是在哪一年？`,
      ['2026 年', '2025 年', '2024 年', '2023 年'], 0,
      `当前数据里最新视频是 2026-10-03《我们俩第一次出国！》。`);
}
{
  add('发布规律', 'hard', `Warma 最长断更发生在哪一年？`,
      ['2021 年', '2020 年', '2022 年', '2023 年'], 0,
      `2021-07-09《成都旅游短视频合集》后断更 227 天。`);
}

// 标签与分类
{
  add('标签与分类', 'easy', `Warma 视频中标签数量第二名是什么？`,
      ['沃玛', 'warma', '搞笑', '怒九'], 0,
      `“warma” 312 个视频，“沃玛” 238 个视频。`);
}
{
  add('标签与分类', 'medium', `排除 warma、沃玛、WARMA 后，Warma 最常用标签是什么？`,
      ['搞笑', '怒九', '日常', '脑洞'], 0,
      `“搞笑”在 79 个视频里出现。`);
}
{
  add('标签与分类', 'medium', `Warma 哪种类型的视频总点赞数最高？`,
      ['游戏实况', '翻唱/音乐', '绘画/手书', '爆炸电台'], 0,
      `游戏实况合计约 15,613,972 个赞。`);
}
{
  add('标签与分类', 'hard', `Warma 哪种类型的视频总分享数最高？`,
      ['翻唱/音乐', '游戏实况', '绘画/手书', '爆炸电台'], 0,
      `翻唱/音乐约 612,989 次，高于游戏实况的约 506,614 次。`);
}
{
  add('标签与分类', 'hard', `Warma 哪种类型的视频总投币数最高？`,
      ['翻唱/音乐', '游戏实况', '绘画/手书', '爆炸电台'], 0,
      `翻唱/音乐约 5,894,110 枚硬币，高于游戏实况的约 4,947,218 枚。`);
}
{
  add('标签与分类', 'medium', `Warma 哪种类型的视频总评论/回复数最高？`,
      ['游戏实况', '翻唱/音乐', '绘画/手书', '爆炸电台'], 0,
      `游戏实况合计约 313,581 条评论/回复。`);
}
{
  add('标签与分类', 'hard', `排除只有一个样本的影视/综艺后，Warma 哪种类型的平均播放量最高？`,
      ['绘画/手书', '搞笑娱乐', '翻唱/音乐', '配音/小剧场'], 0,
      `绘画/手书平均约 303 万播放。`);
}

// 梗与弹幕
{
  add('梗与弹幕', 'medium', `《我制作了免费的养宠物游戏！》弹幕中出现次数最多的梗是什么？`,
      ['《沃草》', '《笨游戏》', '《沃玛の神奇比喻》', '《沃的花》'], 0,
      `《沃草》出现了 442 次。`);
}
{
  add('梗与弹幕', 'hard', `《我阻止了地球末日！》弹幕中出现次数最多的梗是什么？`,
      ['还！给！她！！！', '图穷匕见', '《认知滤网》', '灭人器'], 0,
      `还！给！她！！！出现了 10 次。`);
}
{
  add('梗与弹幕', 'hard', `《小时候最害怕的一对情侣》弹幕中出现次数最多的梗是什么？`,
      ['拜拜！', '坦克大战', '魂斗罗', '靠谱的大姐姐'], 0,
      `拜拜！出现了 11 次。`);
}
{
  add('梗与弹幕', 'hard', `《轨道双子星》弹幕中出现次数最多的梗是什么？`,
      ['是啊，吃什么', '完结撒花', '沃九是天才！', '哈哈哈哈哈'], 0,
      `是啊，吃什么出现了 83 次。`);
}
{
  add('梗与弹幕', 'hard', `《出国！去逛全球最大的游戏展吧！》弹幕中出现次数最多的梗是什么？`,
      ['？！ユユ！？', '沃马', '沃是天才！', '懂你意思'], 0,
      `？！ユユ！？出现了 39 次。`);
}
{
  add('梗与弹幕', 'hard', `《我在国外到处胡说八道【爆米花电台04】》弹幕中出现次数最多的梗是什么？`,
      ['国庆节快乐！', '哈哈哈哈', '我也爱你', '我也爱你！'], 0,
      `国庆节快乐！出现了 15 次。`);
}

// 字幕探索
{
  add('字幕探索', 'hard', `2026 年字幕行数最多的视频是哪一部？`,
      ['《我在国外到处胡说八道【爆米花电台04】》', '《轨道双子星》', '《小时候最害怕的一对情侣》', '《出国！去逛全球最大的游戏展吧！》'], 0,
      `《我在国外到处胡说八道【爆米花电台04】》有 2302 行字幕。`);
}
{
  add('字幕探索', 'medium', `《轨道双子星》的字幕里，谁负责“外置字幕”？`,
      ['Warma', '怒九', '杂菌', 'CB'], 0,
      `视频简介里写着“外置字幕（可能有错别字）：warma”。`);
}
{
  add('字幕探索', 'medium', `《轨道双子星》的字幕里，谁负责“封面/剪辑”？`,
      ['怒九', 'Warma', '杂菌', 'CB'], 0,
      `视频简介里写着“封面/剪辑：怒九”。`);
}
{
  add('字幕探索', 'hard', `《小时候最害怕的一对情侣》中，Warma 控制的是哪一方企鹅？`,
      ['粉色企鹅', '绿色企鹅', '蓝色企鹅', '黑色企鹅'], 0,
      `字幕里说“我是这个粉色企鹅”，绿色是它的猎人。`);
}
{
  add('字幕探索', 'easy', `《小时候最害怕的一对情侣》里的反派是什么？`,
      ['蜘蛛', '螃蟹', '蚂蚁', '蝗虫'], 0,
      `字幕里说反派是个蜘蛛，会把可爱的企鹅抓走。`);
}
{
  add('字幕探索', 'medium', `《出国！去逛全球最大的游戏展吧！》说的是哪一座城市的游戏展？`,
      ['德国科隆', '日本东京', '美国洛杉矶', '英国伦敦'], 0,
      `视频标题和字幕都提到“德国科隆游戏展”。`);
}
{
  add('字幕探索', 'hard', `《出国！去逛全球最大的游戏展吧！》里，Warma 用什么申请了门票？`,
      ['B站主页信息', '微博主页', '邮箱', '直播间截图'], 0,
      `字幕里提到“上传了我的B站主页信息去申请门票”。`);
}

// 评论区
{
  add('评论区', 'hard', `抓取到的评论中，点赞最高的评论内容是什么？`,
      ['沃玛家里的蜘蛛数量 ↓', '《爱你在心口难开》', '我 眼 前 一 黑', '谢谢沃玛'], 0,
      `这条评论在《我家里有蜘蛛！！！》下有 223,347 个赞。`);
}
{
  add('评论区', 'hard', `抓取到的评论中，点赞最高的评论是谁发的？`,
      ['初音厨凯文君', '前辈太差劲了', 'Warma', 'RayShiki'], 0,
      `初音厨凯文君的“沃玛家里的蜘蛛数量 ↓”有 223,347 个赞。`);
}
{
  add('评论区', 'hard', `抓取到的评论中，发言最多的非 Warma 本人是哪个用户？`,
      ['账号已注销', 'Warma゜', '怒九笑', '订做美味鱼卷'], 0,
      `账号已注销共发了 266 条评论/回复。`);
}
{
  add('评论区', 'hard', `抓取到的评论中，非 Warma 本人的总获赞最高用户是谁？`,
      ['怒九笑', '账号已注销', 'Warma゜', '捏碳碳碳碳'], 0,
      `怒九笑约 1,746,060 个赞。`);
}
{
  add('评论区', 'hard', `《我家里有蜘蛛！！！》的点赞最高的评论是谁发的？`,
      ['初音厨凯文君', '耶合没有鸟', '前辈太差劲了', 'Warma'], 0,
      `初音厨凯文君发的评论有 223,347 个赞。`);
}

// 深度对比
{
  add('深度对比', 'hard', `Warma 主号的视频数量大约是小号的多少倍？`,
      ['约 2.8 倍', '约 1.8 倍', '约 3.8 倍', '约 0.8 倍'], 0,
      `主号 264 个，小号 95 个。`);
}
{
  add('深度对比', 'hard', `Warma 主号和小号谁的平均单集时长更长？`,
      ['小号（warma养鸽场）', '主号（Warma）', '两边一样', '无法比较'], 0,
      `小号平均约 57.5 分钟，主号平均约 27.6 分钟。`);
}
{
  add('深度对比', 'easy', `Warma 主号和小号谁的总点赞数更多？`,
      ['主号（Warma）', '小号（warma养鸽场）', '两边一样', '无法比较'], 0,
      `主号约 3706 万，小号约 546 万。`);
}
{
  add('深度对比', 'medium', `Warma 主号和小号谁的总弹幕数更多？`,
      ['主号（Warma）', '小号（warma养鸽场）', '两边一样', '无法比较'], 0,
      `主号约 334 万，小号约 34 万。`);
}
{
  add('深度对比', 'medium', `Warma 主号和小号谁的总分享数更多？`,
      ['主号（Warma）', '小号（warma养鸽场）', '两边一样', '无法比较'], 0,
      `主号约 162 万，小号约 17 万。`);
}

// 冷知识
{
  add('冷知识', 'medium', `Warma 的第一次出国是在哪一年？`,
      ['2026 年', '2025 年', '2024 年', '2023 年'], 0,
      `2026-09-11《出国！去逛全球最大的游戏展吧！》。`);
}
{
  add('冷知识', 'medium', `Warma 和怒九合作的第一首合唱是哪一年？`,
      ['2016 年', '2017 年', '2018 年', '2019 年'], 0,
      `2016-05-20《1 2 Fan Club》。`);
}
{
  add('冷知识', 'hard', `Warma 早期的自制游戏《良》是哪一年发布的？`,
      ['2016 年', '2017 年', '2018 年', '2019 年'], 0,
      `2016-08-01《自制游戏发布》发布了《良》。`);
}
{
  add('冷知识', 'easy', `Warma 早期自制游戏《良》的作者是谁？`,
      ['Warma', 'CB', '杂菌', '怒九'], 0,
      `视频标题写着《良》游戏介绍【作者warma】。`);
}
{
  add('冷知识', 'medium', `Warma 的《我的小鲨鱼》游戏开发周期是多久？`,
      ['1 个月', '3 个月', '半年', '1 周'], 0,
      `视频简介里提到开发周期是一个月。`);
}
{
  add('冷知识', 'medium', `Warma 和 CB 合作的第一首原创曲是哪一年？`,
      ['2019 年', '2018 年', '2017 年', '2016 年'], 0,
      `2019-07-27《我家里有蜘蛛！！！》。`);
}

// 视频内容
{
  add('视频内容', 'medium', `《轨道双子星》是在哪个平台上的游戏？`,
      ['Switch 2', 'Switch', 'PC', 'PS5'], 0,
      `视频简介里写着“平台：Switch 2”。`);
}
{
  add('视频内容', 'medium', `《轨道双子星》里，谁负责“封面/剪辑”？`,
      ['怒九', 'Warma', '杂菌', 'CB'], 0,
      `视频简介里写着“封面/剪辑：怒九”。`);
}
{
  add('视频内容', 'medium', `《轨道双子星》里，谁负责“外置字幕”？`,
      ['Warma', '怒九', '杂菌', 'CB'], 0,
      `视频简介里写着“外置字幕（可能有错别字）：warma”。`);
}
{
  add('视频内容', 'easy', `《小时候最害怕的一对情侣》里的反派是什么？`,
      ['蜘蛛', '螃蟹', '蚂蚁', '蝗虫'], 0,
      `字幕里说反派是个蜘蛛，会把可爱的企鹅抓走。`);
}
{
  add('视频内容', 'hard', `《小时候最害怕的一对情侣》中，Warma 控制的是哪一方企鹅？`,
      ['粉色企鹅', '绿色企鹅', '蓝色企鹅', '黑色企鹅'], 0,
      `字幕里说“我是这个粉色企鹅”，绿色是它的猎人。`);
}
{
  add('视频内容', 'hard', `《小时候最害怕的一对情侣》的游戏发行年份是哪一年？`,
      ['1985 年', '1986 年', '1984 年', '1987 年'], 0,
      `字幕里提到这是“来自1985年的一个企鹅玩游戏”。`);
}
{
  add('视频内容', 'medium', `《出国！去逛全球最大的游戏展吧！》说的是哪一个游戏展？`,
      ['德国科隆游戏展', '日本东京游戏展', '美国洛杉矶游戏展', '英国伦敦游戏展'], 0,
      `视频标题和字幕都提到“德国科隆游戏展”。`);
}
{
  add('视频内容', 'hard', `《出国！去逛全球最大的游戏展吧！》里，Warma 用什么申请了门票？`,
      ['B站主页信息', '微博主页', '邮箱', '直播间截图'], 0,
      `字幕里提到“上传了我的B站主页信息去申请门票”。`);
}
{
  add('视频内容', 'medium', `《我在国外到处胡说八道【爆米花电台04】》主要聊的是什么？`,
      ['2026 年德国科隆游戏展和出国旅行', '2024 年日本旅行', '2022 年长沙老家', '2020 年上海隔离'], 0,
      `这是爆米花电台第 4 期，主要聊德国科隆游戏展和这趟出国旅行。`);
}
{
  add('视频内容', 'easy', `《我在国外到处胡说八道【爆米花电台04】》的电台类型是什么？`,
      ['生活播客/电台', '游戏实况', '翻唱', '绘画/手书'], 0,
      `这是 Warma 的爆米花电台第 4 期，主要用来聊天和分享日常。`);
}
{
  add('视频内容', 'easy', `《REANIMAL（生灵重塑）》是和谁一起玩的游戏？`,
      ['怒九', '杂菌', 'CB', '四迹'], 0,
      `2026-02-13《REANIMAL》是 Warma 和怒九合作的游戏实况。`);
}
{
  add('视频内容', 'easy', `《REANIMAL（生灵重塑）》的游戏类型是什么？`,
      ['横冲直撞的惊险求生', '种田生活', '音乐节奏', '解谜逃生'], 0,
      `视频标题里写着“横冲直撞的惊险求生”。`);
}
{
  add('视频内容', 'easy', `《Subnautica2：异星水域》是和谁一起玩的游戏？`,
      ['怒九', '杂菌', 'CB', '四迹'], 0,
      `2026-05-15《Subnautica2：异星水域》是 Warma 和怒九合作的双人联机试玩。`);
}
{
  add('视频内容', 'easy', `《Subnautica2：异星水域》的游戏类型是什么？`,
      ['海底探索', '种田生活', '音乐节奏', '解谜逃生'], 0,
      `这是一款海底探索游戏，标题里也写着“尝尝大海的恐怖吧”。`);
}
{
  add('视频内容', 'easy', `《双影奇境》是和谁一起玩的游戏？`,
      ['怒九', '杂菌', 'CB', '四迹'], 0,
      `2025-03-07《双影奇境》是 Warma 和怒九合作的游戏实况。`);
}
{
  add('视频内容', 'easy', `《双影奇境》的游戏类型是什么？`,
      ['双人合作冒险', '种田生活', '音乐节奏', '解谜逃生'], 0,
      `这是一款双人合作冒险游戏，全篇约 744 分钟。`);
}
{
  add('视频内容', 'easy', `《星露谷！田园开荒生活！》是和谁一起玩的游戏？`,
      ['怒九', '杂菌', 'CB', '四迹'], 0,
      `2024 年的《星露谷！田园开荒生活！》是 Warma 和怒九合作的游戏实况。`);
}
{
  add('视频内容', 'easy', `《星露谷！田园开荒生活！》的游戏类型是什么？`,
      ['田园开荒生活', '横冲直撞的惊险求生', '音乐节奏', '解谜逃生'], 0,
      `这是一款种田生活模拟游戏，2024 年共分春、夏、秋三期。`);
}

// ─── Shuffle options & randomize answer positions ───
const finalQuestions = questions.map(q => {
  // For questions where the correct answer is at index 0 (by construction),
  // we need to shuffle if they aren't already shuffled
  // Check if we already shuffled in the add() call
  return q;
});

// ─── Output ───
const output = `// Warma 百科 · 问答数据（自动生成）
// 生成时间: ${new Date().toISOString()}
// 题目数量: ${finalQuestions.length}
const QUIZ_DATA = ${JSON.stringify(finalQuestions, null, 2)};
`;

fs.writeFileSync(path.join(ROOT, 'site/data-quiz.js'), output, 'utf8');
console.log(`✅ 生成 ${finalQuestions.length} 道题目 → site/data-quiz.js`);
console.log(`   分类: ${[...new Set(finalQuestions.map(q=>q.category))].join(', ')}`);
console.log(`   难度: ${[...new Set(finalQuestions.map(q=>q.difficulty))].join(', ')}`);
const byDiff = {};
finalQuestions.forEach(q=>byDiff[q.difficulty]=(byDiff[q.difficulty]||0)+1);
console.log(`   难度分布: ${JSON.stringify(byDiff)}`);

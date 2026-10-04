import fs from "node:fs/promises";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const dataPath = "F:\\warma百科\\warma-encyclopedia\\tools\\artifact_tmp\\reconciled_videos.json";
const data = JSON.parse(await fs.readFile(dataPath, "utf8"));
const siteText = await fs.readFile("F:\\warma百科\\warma-encyclopedia\\site\\data.js", "utf8");
const siteData = JSON.parse(siteText.slice(siteText.indexOf("=") + 1).trim().replace(/;$/, ""));
const commentsData = JSON.parse(await fs.readFile("F:\\warma百科\\warma-encyclopedia\\tools\\bili_comments_cache.json", "utf8"));
const siteByBvid = new Map(siteData.videos.map(row => [row.bvid, row]));
const targets = [
  { key: "main_wbi", path: "F:\\warma百科\\@Warma 相关.xlsx" },
  { key: "small_wbi", path: "F:\\warma百科\\@warma养鸽场 相关.xlsx" },
];
const stamp = new Date().toISOString().slice(0, 10).replace(/-/g, "");
const backupDir = "F:\\warma百科\\backup_xlsx";

const parseDate = (s) => new Date(`${s}T00:00:00`);
const rangeOf = (dq, col, last) => `${dq}!$${col}$2:$${col}$${last}`;

function uniqueRows(rows) {
  const seen = new Set();
  const result = [];
  for (const r of rows) {
    if (!r.bvid || seen.has(r.bvid)) continue;
    seen.add(r.bvid);
    if (!r.aid || !r.date || !r.duration) throw new Error(`Missing required fields for ${r.bvid}`);
    result.push({
      ...r,
      type: r.type || "其他",
      source: r.source || "B站用户视频列表",
    });
  }
  result.sort((a, b) => a.date.localeCompare(b.date) || String(a.title).localeCompare(String(b.title)));
  return result;
}

function styleHeader(sheet, lastCol, lastRow = 1) {
  const rng = sheet.getRange(`A1:${lastCol}${lastRow}`);
  rng.format.fill = "#4F46E5";
  rng.format.font = { bold: true, color: "#FFFFFF" };
  rng.format.horizontalAlignment = "center";
  rng.format.verticalAlignment = "center";
}

function clipText(value, max = 160) {
  const text = String(value ?? "").replace(/\s+/g, " ").trim();
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

function timeLabel(sec) {
  const total = Math.max(0, Math.round(Number(sec) || 0));
  const m = Math.floor(total / 60);
  const s = total % 60;
  const h = Math.floor(m / 60);
  return h > 0 ? `${h}:${String(m % 60).padStart(2, "0")}:${String(s).padStart(2, "0")}` : `${m}:${String(s).padStart(2, "0")}`;
}

async function buildAndSave(rows, targetPath, accountKey) {
  const rowsClean = uniqueRows(rows);
  const last = rowsClean.length + 1;
  const dq = "'数据总表'";
  const R = (col) => rangeOf(dq, col, last);

  const workbook = Workbook.create();
  const guide = workbook.worksheets.add("使用说明");
  const dataSheet = workbook.worksheets.add("数据总表");
  const yearSheet = workbook.worksheets.add("年度分析");
  const typeSheet = workbook.worksheets.add("类型分析");
  const durationSheet = workbook.worksheets.add("时长分段");
  const dashboard = workbook.worksheets.add("仪表盘");
  const unmatched = workbook.worksheets.add("未匹配记录");
  const quality = workbook.worksheets.add("数据质量");
  const updateLog = workbook.worksheets.add("更新日志");
  const siteSheet = workbook.worksheets.add("网站联动");

  // Data sheet
  const headers = ["序号", "标题", "BV号", "AV号", "投稿日期", "内容类型", "时长(秒)", "时长", "距上次投稿(天)", "间隔等级", "视频链接", "数据来源", "备注"];
  dataSheet.getRange("A1:M1").values = [headers];
  dataSheet.getRange(`A2:G${last}`).values = rowsClean.map((r, i) => [
    i + 1,
    r.title,
    r.bvid,
    String(r.aid),
    parseDate(r.date),
    r.type,
    r.duration,
  ]);
  dataSheet.getRange(`H2:H${last}`).formulas = rowsClean.map((_, i) => [
    `=IF($G${i + 2}="","",TEXT($G${i + 2}/86400,"[h]:mm:ss"))`,
  ]);
  if (rowsClean.length > 1) {
    dataSheet.getRange(`I3:I${last}`).formulas = rowsClean.slice(1).map((_, i) => [
      `=IF(OR($E${i + 3}="",$E${i + 2}=""),"",$E${i + 3}-$E${i + 2})`,
    ]);
    dataSheet.getRange(`J3:J${last}`).formulas = rowsClean.slice(1).map((_, i) => [
      `=IF($I${i + 3}="","",IF($I${i + 3}<=7,"≤7天",IF($I${i + 3}<=30,"≤30天",IF($I${i + 3}<=90,"≤90天",">90天"))))`,
    ]);
  }
  dataSheet.getRange(`K2:K${last}`).formulas = rowsClean.map((_, i) => [
    `=IF($C${i + 2}="","","https://www.bilibili.com/video/"&$C${i + 2})`,
  ]);
  dataSheet.getRange(`L2:L${last}`).values = rowsClean.map((r) => [r.source]);
  dataSheet.getRange(`M2:M${last}`).values = rowsClean.map(() => [""]);

  dataSheet.getRange(`A2:M${last}`).format.font = { name: "Arial", size: 10 };
  dataSheet.getRange(`A2:M${last}`).format.verticalAlignment = "center";
  dataSheet.getRange(`A2:M${last}`).format.borders = { preset: "all", style: "thin", color: "#E5E7EB" };
  dataSheet.getRange("A1:M1").format.rowHeight = 24;
  styleHeader(dataSheet, "M");
  dataSheet.getRange(`A2:A${last}`).setNumberFormat("0");
  dataSheet.getRange(`C2:D${last}`).setNumberFormat("@");
  dataSheet.getRange(`E2:E${last}`).setNumberFormat("yyyy-mm-dd");
  dataSheet.getRange(`G2:G${last}`).setNumberFormat("#,##0");
  dataSheet.getRange(`I2:I${last}`).setNumberFormat("#,##0");
  dataSheet.getRange(`K2:K${last}`).setNumberFormat("@");
  const widths = { A: 8, B: 44, C: 20, D: 14, E: 12, F: 18, G: 12, H: 12, I: 16, J: 14, K: 44, L: 22, M: 18 };
  for (const [col, width] of Object.entries(widths)) {
    dataSheet.getRange(`${col}1:${col}${last}`).format.columnWidth = width;
  }
  dataSheet.freezePanes.freezeRows(1);
  dataSheet.showGridLines = false;

  // Website-linked enrichment sheet. Keep the requested 13-column data sheet untouched.
  const siteHeaders = [
    "序号", "标题", "BV号", "AV号", "投稿日期", "播放量", "点赞", "点赞率",
    "弹幕", "评论数", "收藏", "投币", "分享", "互动率", "B站标签",
    "最高赞评论", "评论用户", "评论点赞", "弹幕峰值时间", "峰值弹幕",
    "峰值弹幕样例", "主要梗/热词", "荣誉记录"
  ];
  siteSheet.getRange("A1:W1").values = [siteHeaders];
  rowsClean.forEach((tableRow, index) => {
    const rowNo = index + 2;
    const siteRow = siteByBvid.get(tableRow.bvid) || {};
    const topComment = ((commentsData[tableRow.bvid] || {}).comments || [])
      .slice()
      .sort((a, b) => (b.like || 0) - (a.like || 0))[0] || {};
    const peak = (siteRow.peaks || [])[0] || {};
    siteSheet.getRange(`A${rowNo}:A${rowNo}`).values = [[index + 1]];
    siteSheet.getRange(`B${rowNo}:E${rowNo}`).formulas = [[
      `='数据总表'!B${rowNo}`,
      `='数据总表'!C${rowNo}`,
      `='数据总表'!D${rowNo}`,
      `='数据总表'!E${rowNo}`,
    ]];
    siteSheet.getRange(`F${rowNo}:G${rowNo}`).values = [[
      siteRow.view ?? "",
      siteRow.like ?? "",
    ]];
    siteSheet.getRange(`H${rowNo}:H${rowNo}`).formulas = [[
      `=IF(OR($F${rowNo}="",$F${rowNo}=0,$G${rowNo}=""),"",$G${rowNo}/$F${rowNo})`,
    ]];
    siteSheet.getRange(`I${rowNo}:M${rowNo}`).values = [[
      siteRow.danmaku ?? "",
      siteRow.reply ?? "",
      siteRow.favorite ?? "",
      siteRow.coin ?? "",
      siteRow.share ?? "",
    ]];
    siteSheet.getRange(`N${rowNo}:N${rowNo}`).formulas = [[
      `=IF(OR($F${rowNo}="",$F${rowNo}=0),"",SUM($G${rowNo},$I${rowNo},$J${rowNo},$K${rowNo},$L${rowNo},$M${rowNo})/$F${rowNo})`,
    ]];
    siteSheet.getRange(`O${rowNo}:W${rowNo}`).values = [[
      (siteRow.tags || []).slice(0, 8).map(tag => tag.name).join("、"),
      clipText(topComment.message, 160),
      topComment.name || "",
      topComment.like ?? "",
      peak.t == null ? "" : timeLabel(peak.t),
      peak.count ?? "",
      clipText((peak.samples || [])[0], 80),
      (siteRow.memes || []).slice(0, 5).map(meme => `${meme.content}×${meme.count}`).join("、"),
      (siteRow.honors || []).map(honor => honor.desc || honor.type).join("；"),
    ]];
  });
  const siteLast = rowsClean.length + 1;
  siteSheet.getRange(`A2:W${siteLast}`).format.font = { name: "Arial", size: 10 };
  siteSheet.getRange(`A2:W${siteLast}`).format.verticalAlignment = "center";
  siteSheet.getRange(`A2:W${siteLast}`).format.borders = { preset: "all", style: "thin", color: "#E5E7EB" };
  siteSheet.getRange("A1:W1").format.rowHeight = 24;
  styleHeader(siteSheet, "W");
  siteSheet.getRange(`A2:A${siteLast}`).setNumberFormat("0");
  siteSheet.getRange(`C2:D${siteLast}`).setNumberFormat("@");
  siteSheet.getRange(`E2:E${siteLast}`).setNumberFormat("yyyy-mm-dd");
  siteSheet.getRange(`F2:G${siteLast}`).setNumberFormat("#,##0");
  siteSheet.getRange(`H2:H${siteLast}`).setNumberFormat("0.0%");
  siteSheet.getRange(`I2:M${siteLast}`).setNumberFormat("#,##0");
  siteSheet.getRange(`N2:N${siteLast}`).setNumberFormat("0.0%");
  siteSheet.getRange(`R2:R${siteLast}`).setNumberFormat("#,##0");
  siteSheet.getRange(`T2:T${siteLast}`).setNumberFormat("#,##0");
  const siteWidths = { A: 7, B: 42, C: 19, D: 13, E: 11, F: 12, G: 11, H: 10, I: 11, J: 10, K: 10, L: 10, M: 10, N: 10, O: 35, P: 46, Q: 15, R: 10, S: 12, T: 10, U: 34, V: 34, W: 24 };
  for (const [col, width] of Object.entries(siteWidths)) {
    siteSheet.getRange(`${col}1:${col}${siteLast}`).format.columnWidth = width;
  }
  siteSheet.freezePanes.freezeRows(1);
  siteSheet.showGridLines = false;

  // Year analysis
  const years = [];
  const yearVals = rowsClean.map((r) => new Date(r.date).getFullYear());
  const minYear = Math.min(...yearVals);
  const maxYear = Math.max(...yearVals);
  for (let y = minYear; y <= maxYear; y++) years.push(y);
  const yearLast = years.length + 1;
  yearSheet.getRange("A1:E1").values = [["年份", "视频数", "总时长(小时)", "平均时长(分钟)", "平均间隔(天)"]];
  yearSheet.getRange(`A2:A${yearLast}`).values = years.map((y) => [y]);
  yearSheet.getRange(`B2:E${yearLast}`).formulas = years.map((_, idx) => {
    const r = idx + 2;
    return [
      `=COUNTIFS(${R("E")},">="&DATE($A${r},1,1),${R("E")},"<"&DATE($A${r}+1,1,1))`,
      `=ROUND(SUMIFS(${R("G")},${R("E")},">="&DATE($A${r},1,1),${R("E")},"<"&DATE($A${r}+1,1,1))/3600,1)`,
      `=IFERROR(ROUND(AVERAGEIFS(${R("G")},${R("E")},">="&DATE($A${r},1,1),${R("E")},"<"&DATE($A${r}+1,1,1))/60,1),"")`,
      `=IFERROR(ROUND(AVERAGEIFS(${R("I")},${R("E")},">="&DATE($A${r},1,1),${R("E")},"<"&DATE($A${r}+1,1,1)),1),"")`,
    ];
  });
  yearSheet.getRange(`A2:E${yearLast}`).format.font = { name: "Arial", size: 10 };
  yearSheet.getRange(`A2:E${yearLast}`).format.verticalAlignment = "center";
  yearSheet.getRange(`A2:E${yearLast}`).format.borders = { preset: "all", style: "thin", color: "#E5E7EB" };
  styleHeader(yearSheet, "E");
  yearSheet.getRange(`A2:A${yearLast}`).setNumberFormat("0");
  yearSheet.getRange(`B2:B${yearLast}`).setNumberFormat("#,##0");
  yearSheet.getRange(`C2:E${yearLast}`).setNumberFormat("#,##0.0");
  yearSheet.freezePanes.freezeRows(1);
  yearSheet.showGridLines = false;

  // Type analysis
  const typeCounts = new Map();
  for (const r of rowsClean) typeCounts.set(r.type, (typeCounts.get(r.type) || 0) + 1);
  const typeNames = [...typeCounts.entries()].sort((a, b) => b[1] - a[1]).map(([t]) => t);
  const typeLast = typeNames.length + 1;
  typeSheet.getRange("A1:D1").values = [["内容类型", "视频数", "总时长(小时)", "平均时长(分钟)"]];
  typeSheet.getRange(`A2:A${typeLast}`).values = typeNames.map((t) => [t]);
  typeSheet.getRange(`B2:D${typeLast}`).formulas = typeNames.map((_, idx) => {
    const r = idx + 2;
    return [
      `=COUNTIF(${R("F")},$A${r})`,
      `=ROUND(SUMIF(${R("F")},$A${r},${R("G")})/3600,1)`,
      `=IFERROR(ROUND(AVERAGEIF(${R("F")},$A${r},${R("G")})/60,1),"")`,
    ];
  });
  typeSheet.getRange(`A2:D${typeLast}`).format.font = { name: "Arial", size: 10 };
  typeSheet.getRange(`A2:D${typeLast}`).format.verticalAlignment = "center";
  typeSheet.getRange(`A2:D${typeLast}`).format.borders = { preset: "all", style: "thin", color: "#E5E7EB" };
  styleHeader(typeSheet, "D");
  typeSheet.getRange(`B2:B${typeLast}`).setNumberFormat("#,##0");
  typeSheet.getRange(`C2:D${typeLast}`).setNumberFormat("#,##0.0");
  typeSheet.freezePanes.freezeRows(1);
  typeSheet.showGridLines = false;

  // Duration segments
  const segments = [
    { label: "0-59秒", low: 0, high: 59 },
    { label: "1-2分钟", low: 60, high: 119 },
    { label: "2-5分钟", low: 120, high: 299 },
    { label: "5-10分钟", low: 300, high: 599 },
    { label: "10-30分钟", low: 600, high: 1799 },
    { label: "30-60分钟", low: 1800, high: 3599 },
    { label: "1-2小时", low: 3600, high: 7199 },
    { label: ">2小时", low: 7200, high: 1000000000 },
  ];
  const durationLast = segments.length + 1;
  durationSheet.getRange("A1:B1").values = [["时长段", "视频数"]];
  durationSheet.getRange(`A2:A${durationLast}`).values = segments.map((s) => [s.label]);
  durationSheet.getRange(`B2:B${durationLast}`).formulas = segments.map((s) => [
    `=COUNTIFS(${R("G")},">=${s.low}",${R("G")},"<=${s.high}")`,
  ]);
  durationSheet.getRange(`A2:B${durationLast}`).format.font = { name: "Arial", size: 10 };
  durationSheet.getRange(`A2:B${durationLast}`).format.verticalAlignment = "center";
  durationSheet.getRange(`A2:B${durationLast}`).format.borders = { preset: "all", style: "thin", color: "#E5E7EB" };
  styleHeader(durationSheet, "B");
  durationSheet.getRange(`B2:B${durationLast}`).setNumberFormat("#,##0");
  durationSheet.freezePanes.freezeRows(1);
  durationSheet.showGridLines = false;

  // Dashboard
  dashboard.getRange("A1").values = [["Warma 数据仪表盘"]];
  dashboard.getRange("A2").values = [["以下数据会随“数据总表”自动刷新。"]];
  dashboard.getRange("A3:B3").values = [["指标", "数值"]];
  const kpiLabels = ["视频总数", "总时长(小时)", "平均时长(分钟)", "最新投稿日期", "平均间隔(天)", "内容类型数", "最早投稿日期"];
  const kpiFormulas = [
    `=COUNTA(${R("B")})`,
    `=ROUND(SUM(${R("G")})/3600,1)`,
    `=IFERROR(ROUND(AVERAGE(${R("G")})/60,1),"")`,
    `=IFERROR(TEXT(MAX(${R("E")}),"yyyy-mm-dd"),"-")`,
    `=IFERROR(ROUND(AVERAGE(${R("I")}),1),"")`,
    `=COUNTA('类型分析'!$A$2:$A$${typeLast})`,
    `=IFERROR(TEXT(MIN(${R("E")}),"yyyy-mm-dd"),"-")`,
  ];
  dashboard.getRange(`A4:A${3 + kpiLabels.length}`).values = kpiLabels.map((x) => [x]);
  dashboard.getRange(`B4:B${3 + kpiFormulas.length}`).formulas = kpiFormulas.map((x) => [x]);
  dashboard.getRange(`A4:B${3 + kpiLabels.length}`).format.font = { name: "Arial", size: 10 };
  dashboard.getRange(`A4:B${3 + kpiLabels.length}`).format.verticalAlignment = "center";
  dashboard.getRange(`A4:B${3 + kpiLabels.length}`).format.borders = { preset: "all", style: "thin", color: "#E5E7EB" };
  dashboard.getRange(`B4:B${3 + kpiLabels.length}`).format.font = { bold: true };
  dashboard.getRange("A3:B3").format.fill = "#4F46E5";
  dashboard.getRange("A3:B3").format.font = { bold: true, color: "#FFFFFF" };
  dashboard.getRange("A3:B3").format.horizontalAlignment = "center";
  dashboard.getRange("A3:B3").format.verticalAlignment = "center";
  dashboard.getRange("A1").format.font = { size: 16, bold: true, color: "#111827" };
  dashboard.getRange("A2").format.font = { size: 10, color: "#6B7280" };
  dashboard.getRange("A1:A11").format.columnWidth = 22;
  dashboard.getRange("B1:B11").format.columnWidth = 18;
  dashboard.getRange("A1:B1").format.rowHeight = 28;
  dashboard.getRange("A2:B2").format.rowHeight = 18;
  dashboard.showGridLines = false;

  // Stable chart helper sources (values mirror the formula-backed analysis tables).
  const yearCounts = years.map((year) => rowsClean.filter((r) => new Date(r.date).getFullYear() === year).length);
  const yearHours = years.map((year) => Math.round(rowsClean
    .filter((r) => new Date(r.date).getFullYear() === year)
    .reduce((sum, r) => sum + Number(r.duration), 0) / 3600 * 10) / 10);
  const dashboardChart1 = [["年份", "视频数"], ...years.map((y, i) => [y, yearCounts[i]])];
  const dashboardChart2 = [["年份", "总时长(小时)"], ...years.map((y, i) => [y, yearHours[i]])];
  const dashboardChart3 = [["内容类型", "视频数"], ...typeNames.map((t, i) => [t, typeCounts.get(t) || 0])];
  const dashboardChart4 = [["时长段", "视频数"], ...segments.map((s) => [s.label, rowsClean.filter((r) => r.duration >= s.low && r.duration <= s.high).length])];
  dashboard.getRange(`U1:V${yearLast}`).values = dashboardChart1;
  dashboard.getRange(`X1:Y${yearLast}`).values = dashboardChart2;
  dashboard.getRange(`AA1:AB${typeLast}`).values = dashboardChart3;
  dashboard.getRange(`AD1:AE${durationLast}`).values = dashboardChart4;
  for (const range of ["U1:V1", "X1:Y1", "AA1:AB1", "AD1:AE1"]) {
    dashboard.getRange(range).format.fill = "#4F46E5";
    dashboard.getRange(range).format.font = { bold: true, color: "#FFFFFF" };
  }

  await workbook.recalculate();

  const chart1 = dashboard.charts.add("bar", dashboard.getRange(`U1:V${yearLast}`));
  chart1.title = "年度视频数";
  chart1.legend = { position: "top" };
  chart1.setPosition("D4", "J18");
  const chart2 = dashboard.charts.add("bar", dashboard.getRange(`X1:Y${yearLast}`));
  chart2.title = "年度总时长";
  chart2.legend = { position: "top" };
  chart2.setPosition("L4", "R18");
  const chart3 = dashboard.charts.add("pie", dashboard.getRange(`AA1:AB${typeLast}`));
  chart3.title = "内容类型分布";
  chart3.legend = { position: "top" };
  chart3.setPosition("D20", "J34");
  const chart4 = dashboard.charts.add("bar", dashboard.getRange(`AD1:AE${durationLast}`));
  chart4.title = "时长分段分布";
  chart4.legend = { position: "top" };
  chart4.setPosition("L20", "R34");
  for (const chart of [chart1, chart2, chart4]) {
    chart.xAxis = { axisType: "textAxis", textStyle: { typeface: "Arial", fontSize: 10 } };
    chart.yAxis = { textStyle: { typeface: "Arial", fontSize: 10 } };
    chart.titleTextStyle.typeface = "Arial";
    chart.titleTextStyle.fontSize = 12;
  }
  chart3.titleTextStyle.typeface = "Arial";
  chart3.titleTextStyle.fontSize = 12;

  // Unmatched
  unmatched.getRange("A1").values = [["未匹配记录"]];
  unmatched.getRange("A3:B3").values = [["项目", "结果"]];
  unmatched.getRange("A4:B4").values = [["当前未匹配记录", "无"]];
  unmatched.getRange("A4:B4").format.font = { name: "Arial", size: 10 };
  unmatched.getRange("A4:B4").format.verticalAlignment = "center";
  unmatched.getRange("A4:B4").format.borders = { preset: "all", style: "thin", color: "#E5E7EB" };
  styleHeader(unmatched, "B", 3);
  unmatched.getRange("A1").format.font = { size: 16, bold: true };
  unmatched.showGridLines = false;

  // Quality
  quality.getRange("A1").values = [["数据质量检查"]];
  quality.getRange("A3:B3").values = [["检查项", "数量"]];
  const qualityLabels = ["数据行数", "缺失 BV 号", "缺失 AV 号", "缺失投稿日期", "缺失内容类型", "缺失时长", "缺失视频链接", "重复 BV 号", "重复 AV 号", "最早投稿日期", "最新投稿日期"];
  const qualityFormulas = [
    `=COUNTA(${R("B")})`,
    `=COUNTBLANK(${R("C")})`,
    `=COUNTBLANK(${R("D")})`,
    `=COUNTBLANK(${R("E")})`,
    `=COUNTBLANK(${R("F")})`,
    `=COUNTBLANK(${R("G")})`,
    `=COUNTBLANK(${R("K")})`,
    `=SUMPRODUCT((COUNTIF(${R("C")},${R("C")})>1)*1)`,
    `=SUMPRODUCT((COUNTIF(${R("D")},${R("D")})>1)*1)`,
    `=IFERROR(TEXT(MIN(${R("E")}),"yyyy-mm-dd"),"-")`,
    `=IFERROR(TEXT(MAX(${R("E")}),"yyyy-mm-dd"),"-")`,
  ];
  quality.getRange(`A4:A${3 + qualityLabels.length}`).values = qualityLabels.map((x) => [x]);
  quality.getRange(`B4:B${3 + qualityFormulas.length}`).formulas = qualityFormulas.map((x) => [x]);
  quality.getRange(`A4:B${3 + qualityLabels.length}`).format.font = { name: "Arial", size: 10 };
  quality.getRange(`A4:B${3 + qualityLabels.length}`).format.verticalAlignment = "center";
  quality.getRange(`A4:B${3 + qualityLabels.length}`).format.borders = { preset: "all", style: "thin", color: "#E5E7EB" };
  quality.getRange(`B4:B${3 + qualityLabels.length}`).format.font = { bold: true };
  styleHeader(quality, "B", 3);
  quality.getRange("A1").format.font = { size: 16, bold: true };
  quality.getRange(`A4:B${3 + qualityLabels.length}`).format.autofitColumns();
  quality.showGridLines = false;

  // Update log
  updateLog.getRange("A1").values = [["更新日志"]];
  updateLog.getRange("A3:C3").values = [["时间", "操作", "说明"]];
  updateLog.getRange("A4:C5").values = [
    [
      new Date().toISOString().slice(0, 10),
      "清理冗余列并更新链接",
      "移除字幕/播放等冗余列；按最新用户视频列表刷新 BV、AV 和视频链接，并重建分析表和图表。",
    ],
    [
      new Date().toISOString().slice(0, 10),
      "新增网站联动页",
      "按 BV 号回填网站数据：播放、点赞、弹幕、评论、标签、峰值弹幕、热词与荣誉。",
    ],
  ];
  updateLog.getRange("A4:C5").format.font = { name: "Arial", size: 10 };
  updateLog.getRange("A4:C5").format.verticalAlignment = "center";
  updateLog.getRange("A4:C5").format.borders = { preset: "all", style: "thin", color: "#E5E7EB" };
  styleHeader(updateLog, "C", 3);
  updateLog.getRange("A1").format.font = { size: 16, bold: true };
  updateLog.getRange("A4:C4").format.autofitColumns();
  updateLog.showGridLines = false;

  // Guide
  guide.getRange("A1").values = [["使用说明"]];
  guide.getRange("A3:B3").values = [["项目", "说明"]];
  const guideRows = [
    ["数据范围", "以B站用户视频列表为准，覆盖两个账号的全部公开视频。"],
    ["主要字段", "序号、标题、BV号、AV号、投稿日期、内容类型、时长、间隔、视频链接、数据来源、备注。"],
    ["已移除字段", "字幕行数、字幕字符数、播放量、弹幕、评论、收藏、投币、分享、点赞、点赞率、互动率、年、月、星期、账号。"],
    ["自动更新字段", "时长、距上次投稿(天)、间隔等级、视频链接由公式自动生成。"],
    ["分析表", "年度分析、类型分析、时长分段均由数据总表公式驱动。"],
    ["网站联动", "“网站联动”页按 BV 号回填网站播放、点赞、评论、标签、高能弹幕和热词；不改动主表 13 栏。"],
    ["仪表盘", "包含核心指标和 4 张图表。"],
    ["数据来源", "B站用户视频列表与B站元数据。"],
    ["维护方式", "如需刷新，可重新拉取用户视频列表后重建数据总表。"],
  ];
  guide.getRange(`A4:B${3 + guideRows.length}`).values = guideRows;
  guide.getRange(`A4:B${3 + guideRows.length}`).format.font = { name: "Arial", size: 10 };
  guide.getRange(`A4:B${3 + guideRows.length}`).format.verticalAlignment = "top";
  guide.getRange(`A4:B${3 + guideRows.length}`).format.borders = { preset: "all", style: "thin", color: "#E5E7EB" };
  guide.getRange(`B4:B${3 + guideRows.length}`).format.wrapText = true;
  styleHeader(guide, "B", 3);
  guide.getRange("A1").format.font = { size: 16, bold: true };
  guide.getRange(`A4:B${3 + guideRows.length}`).format.autofitColumns();
  guide.showGridLines = false;

  await workbook.recalculate();
  const errScan = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
    options: { useRegex: true, maxResults: 300 },
    summary: "final formula error scan",
  });
  if (errScan.ndjson && /#[A-Z]+!|#N\/A|#NULL!|#SPILL!|#CALC!/.test(errScan.ndjson)) {
    console.log("FORMULA_SCAN", errScan.ndjson.slice(0, 3000));
    throw new Error("Formula errors detected");
  }

  await fs.mkdir(backupDir, { recursive: true });
  const base = targetPath.split(/[\\/]/).pop();
  const backupPath = `${backupDir}\\${stamp}_${base}`;
  await fs.copyFile(targetPath, backupPath);
  const tempPath = `${targetPath}.tmp.xlsx`;
  await fs.rm(tempPath, { force: true });
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(tempPath);
  await fs.rename(tempPath, targetPath);
  console.log("Saved", targetPath, "rows", rowsClean.length, "siteRows", rowsClean.length, "years", years.length, "types", typeNames.length, "siteVersion", siteData.docx_version);
}

for (const target of targets) {
  await buildAndSave(data[target.key], target.path, target.key);
}

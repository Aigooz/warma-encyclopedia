import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile } from "@oai/artifact-tool";

const outputDir = "F:\\warma百科\\warma-encyclopedia\\tools\\artifact_tmp\\previews";
await fs.rm(outputDir, { recursive: true, force: true });
await fs.mkdir(outputDir, { recursive: true });

const jobs = [
  { file: "F:\\warma百科\\@Warma 相关.xlsx", label: "main" },
  { file: "F:\\warma百科\\@warma养鸽场 相关.xlsx", label: "small" },
];
const views = [
  { sheet: "数据总表", range: "A1:N20" },
  { sheet: "年度分析", range: "A1:E20" },
  { sheet: "类型分析", range: "A1:D20" },
  { sheet: "时长分段", range: "A1:B20" },
  { sheet: "仪表盘", range: "A1:S36" },
  { sheet: "未匹配记录", range: "A1:C16" },
  { sheet: "数据质量", range: "A1:C20" },
  { sheet: "更新日志", range: "A1:C16" },
  { sheet: "使用说明", range: "A1:B16" },
];

for (const job of jobs) {
  const buffer = await fs.readFile(job.file);
  const workbook = await SpreadsheetFile.importXlsx(buffer);
  for (const view of views) {
    const png = await workbook.render({
      sheetName: view.sheet,
      range: view.range,
      scale: 1,
      format: "png",
    });
    const out = path.join(outputDir, `${job.label}_${view.sheet}.png`);
    await fs.writeFile(out, new Uint8Array(await png.arrayBuffer()));
  }
  console.log("Rendered", job.label);
}

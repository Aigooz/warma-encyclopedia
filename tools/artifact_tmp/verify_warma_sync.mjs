import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile } from "@oai/artifact-tool";

const outputDir = "F:\\warma百科\\warma-encyclopedia\\tools\\artifact_tmp\\previews_sync";
await fs.rm(outputDir, { recursive: true, force: true });
await fs.mkdir(outputDir, { recursive: true });

const jobs = [
  { file: "F:\\warma百科\\@Warma 相关.xlsx", label: "main" },
  { file: "F:\\warma百科\\@warma养鸽场 相关.xlsx", label: "small" },
];

for (const job of jobs) {
  const workbook = await SpreadsheetFile.importXlsx(await fs.readFile(job.file));
  const overview = await workbook.inspect({ kind: "workbook,sheet,table", maxChars: 4000, tableMaxRows: 3, tableMaxCols: 8 });
  const link = await workbook.inspect({ kind: "table", sheetId: "网站联动", range: "A1:W8", include: "values,formulas", tableMaxRows: 8, tableMaxCols: 23, maxChars: 5000 });
  const errors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
    options: { useRegex: true, maxResults: 100 },
    summary: `${job.label} formula error scan`,
  });
  const png = await workbook.render({ sheetName: "网站联动", range: "A1:N20", scale: 1, format: "png" });
  await fs.writeFile(path.join(outputDir, `${job.label}_site_link.png`), new Uint8Array(await png.arrayBuffer()));
  console.log(`==== ${job.label} ====`);
  console.log(overview.ndjson.slice(0, 2000));
  console.log("LINK\n" + link.ndjson.slice(0, 3500));
  console.log("ERRORS\n" + errors.ndjson.slice(0, 1000));
}

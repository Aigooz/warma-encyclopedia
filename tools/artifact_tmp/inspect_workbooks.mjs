import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const files = [
  "F:/warma百科/@Warma 相关.xlsx",
  "F:/warma百科/@warma养鸽场 相关.xlsx",
];

for (const file of files) {
  console.log(`\n=== ${file} ===`);
  const input = await FileBlob.load(file);
  const wb = await SpreadsheetFile.importXlsx(input);
  const summary = await wb.inspect({
    kind: "workbook,sheet,table,drawing,definedName",
    maxChars: 12000,
    tableMaxRows: 4,
    tableMaxCols: 30,
    tableMaxCellChars: 80,
  });
  console.log(summary.ndjson);
}

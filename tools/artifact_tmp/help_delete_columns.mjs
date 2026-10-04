import { Workbook } from "@oai/artifact-tool";

const workbook = Workbook.create();
const help = workbook.help("delete columns", { include: "index,examples,notes", maxChars: 6000 });
console.log(help.ndjson);

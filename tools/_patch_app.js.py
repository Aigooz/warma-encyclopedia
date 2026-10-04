from pathlib import Path
p=Path('site/app.js')
s=p.read_text(encoding='utf-8')
s=s.replace("    if (q && !`${row.title} ${row.type} ${row.account} ${row.bvid}`.toLowerCase().includes(q)) return false;", "    const tagText = (row.tags || []).map(t => t.name).join(' ');\n    if (q && !`${row.title} ${row.type} ${row.account} ${row.bvid} ${tagText}`.toLowerCase().includes(q)) return false;")
s=s.replace("function renderTagCloud(rows) {\n  const counts = new Map();\n  rows.forEach(row => row.keywords.forEach(keyword => counts.set(keyword, (counts.get(keyword) || 0) + 1)));\n  const list = [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 36);", "function renderTagCloud(rows) {\n  const counts = new Map();\n  rows.forEach(row => {\n    (row.tags || []).forEach(tag => {\n      const name = tag.name;\n      if (!name || /^(warma|沃玛|箱眠)$/i.test(name)) return;\n      counts.set(name, (counts.get(name) || 0) + 1);\n    });\n  });\n  const list = [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 36);")
p.write_text(s,encoding='utf-8')
print('patched app.js')

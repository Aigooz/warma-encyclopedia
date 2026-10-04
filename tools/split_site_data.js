const fs = require('fs');
const path = require('path');

const siteDir = path.join(__dirname, '..', 'site');
const raw = fs.readFileSync(path.join(siteDir, 'data.js'), 'utf-8');
const fn = new Function(raw + '; return RAW;');
const data = fn();

// Split comments out of videos
const commentsMap = {};
const coreVideos = data.videos.map(v => {
  const { comments, ...rest } = v;
  if (comments && comments.length > 0) {
    commentsMap[v.bvid] = comments;
  }
  return rest;
});

// Write core data.js
const coreData = { ...data, videos: coreVideos };
const coreJs = 'const RAW = ' + JSON.stringify(coreData) + ';\n';
fs.writeFileSync(path.join(siteDir, 'data.js'), coreJs);

// Write comments file
const commentsJs = 'const RAW_COMMENTS = ' + JSON.stringify(commentsMap) + ';\n';
fs.writeFileSync(path.join(siteDir, 'data-comments.js'), commentsJs);

const coreSize = (coreJs.length / 1024).toFixed(0);
const commentsSize = (commentsJs.length / 1024).toFixed(0);
console.log(`data.js (core): ${coreSize} KB`);
console.log(`data-comments.js: ${commentsSize} KB`);
console.log(`Videos with comments: ${Object.keys(commentsMap).length}`);
console.log(`Total comments: ${Object.values(commentsMap).reduce((a,c)=>a+c.length,0)}`);

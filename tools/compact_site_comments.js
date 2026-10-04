const fs = require('fs');
const path = require('path');

const siteDir = path.join(__dirname, '..', 'site');
const sourcePath = path.join(siteDir, 'data-comments.js');
const source = fs.readFileSync(sourcePath, 'utf8');
const parsed = JSON.parse(source.slice(source.indexOf('=') + 1, source.lastIndexOf(';')));

const packed = {};
for (const [bvid, comments] of Object.entries(parsed)) {
  packed[bvid] = comments.map(comment => [
    comment.name ?? '',
    comment.like ?? 0,
    comment.ctime ?? 0,
    comment.message ?? '',
    (comment.replies || []).map(reply => [
      reply.name ?? '',
      reply.like ?? 0,
      reply.message ?? ''
    ])
  ]);
}

const output = `const RAW_PACKED_COMMENTS = ${JSON.stringify(packed)};
const RAW_COMMENTS = (() => {
  const unpacked = {};
  for (const [bvid, comments] of Object.entries(RAW_PACKED_COMMENTS)) {
    unpacked[bvid] = comments.map(([name, like, ctime, message, replies]) => ({
      name,
      like,
      ctime,
      message,
      replies: replies.map(([name, like, message]) => ({ name, like, message }))
    }));
  }
  return unpacked;
})();
`;

fs.writeFileSync(path.join(siteDir, 'data-comments.js'), output);
console.log(`Packed comment videos: ${Object.keys(packed).length}`);
console.log(`Packed comments: ${Object.values(packed).reduce((sum, list) => sum + list.length, 0)}`);

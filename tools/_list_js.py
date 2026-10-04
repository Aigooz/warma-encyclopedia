import re
html=open('tools/_bili_page.html',encoding='utf-8').read()
for m in re.finditer(r'<script[^>]+src="([^"]+)"',html): print(m.group(1))
print('dm substr', [html[max(0,i-50):i+100] for i in [m.start() for m in re.finditer('dm',html)][:10]])

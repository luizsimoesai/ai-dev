# The html2text module is used to convert HTML into plain text,
# preserving basic formatting like links and lists.

import html2text

html_content = """
<h1>Title</h1>
<p>This is a <b>paragraph</b> with <a href="https://example.com">a link</a>.</p>
"""

text = html2text.html2text(html_content)
print(text)

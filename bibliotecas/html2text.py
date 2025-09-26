# O módulo html2text é usado para transformar HTML em texto simples, 
# preservando formatação básica como links e listas.

import html2text

html_content = """
<h1>Título</h1>
<p>Este é um <b>parágrafo</b> com <a href="https://exemplo.com">um link</a>.</p>
"""

text = html2text.html2text(html_content)
print(text)

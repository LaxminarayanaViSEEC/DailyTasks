import fitz

pdf_path = 'D:\\iDX\\dataset\\hindi.pdf'

doc = fitz.open(pdf_path)

x = doc.loadPage(0).getText('blocks')[20]

print(x[4])
import fitz


file_path = 'D:\\gitworkflow\\DT#19062020\\334782083.pdf'
pdf = '2083'

doc=fitz.Document(file_path,filetype='pdf')
for page in range(doc.pageCount):
    words = doc.loadPage(page).getText('words')
    for i in range(len(words)):
        doc.loadPage(page).drawRect(rect=(words[i][0],words[i][1],words[i][2],words[i][3]),width=0.2,color=fitz.utils.getColor('green'))
    blocks = doc.loadPage(page).getText('dict')['blocks']
    for block in blocks:
        if block['type'] == 1:
            rectang = block['bbox']
            doc.loadPage(page).drawRect(rect=rectang,width=2.5,color=fitz.utils.getColor('red'))
        elif block['type'] == 0:
            rectang = block['bbox']
            doc.loadPage(page).drawRect(rect=rectang,width=2,color=fitz.utils.getColor('black'))
            for line in block['lines']:
                bbox_line = line['bbox']
                doc.loadPage(page).drawRect(rect=bbox_line,width=1.5,color=fitz.utils.getColor('yellow'))
                for span in line['spans']:
                    bbox_=span['bbox']
                    doc.loadPage(page).drawRect(rect=bbox_,width=0.2,color=fitz.utils.getColor('blue'))
doc.save(f'All_Highligths_{pdf}.pdf')
doc=fitz.Document(file_path,filetype='pdf')
for page in range(doc.pageCount):
    words = doc.loadPage(page).getText('words')
    for i in range(len(words)):
        doc.loadPage(page).drawRect(rect=(words[i][0],words[i][1],words[i][2],words[i][3]),
                                    width=1,
                                    color=fitz.utils.getColor('green'))
doc.save(f'words_{pdf}.pdf')
doc=fitz.Document(file_path,filetype='pdf')
for page in range(doc.pageCount):
    blocks = doc.loadPage(page).getText('dict')['blocks']
    for block in blocks:
        if block['type'] == 1:
            rectang = block['bbox']
            doc.loadPage(page).drawRect(rect=rectang,width=2.5,color=fitz.utils.getColor('red')) 
doc.save(f'images_{pdf}.pdf')
doc=fitz.Document(file_path,filetype='pdf')
for page in range(doc.pageCount):
    blocks = doc.loadPage(page).getText('dict')['blocks']
    for block in blocks:
        if block['type'] == 0:
            rectang = block['bbox']
            doc.loadPage(page).drawRect(rect=rectang,width=2,color=fitz.utils.getColor('black'))
doc.save(f'blocks_{pdf}.pdf')
doc=fitz.Document(file_path,filetype='pdf')
for page in range(doc.pageCount):
    blocks = doc.loadPage(page).getText('dict')['blocks']
    for block in blocks:
        if block['type'] == 0:
            for line in block['lines']:
                bbox_line = line['bbox']
                doc.loadPage(page).drawRect(rect=bbox_line,width=1.5,color=fitz.utils.getColor('yellow'))
doc.save(f'lines_{pdf}.pdf')
doc=fitz.Document(file_path,filetype='pdf')
for page in range(doc.pageCount):
    blocks = doc.loadPage(page).getText('dict')['blocks']
    for block in blocks:
        if block['type'] == 0:
            for line in block['lines']:
                for span in line['spans']:
                    bbox=span['bbox']
                    doc.loadPage(page).drawRect(rect=bbox,width=1,color=fitz.utils.getColor('blue'))
doc.save(f'spans_{pdf}.pdf')
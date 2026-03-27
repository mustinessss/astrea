from docx import Document

doc = Document('Описание функционала Астреи .docx')
for para in doc.paragraphs:
    if para.text.strip():
        print(para.text)

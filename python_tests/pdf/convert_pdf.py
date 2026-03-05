import fitz  # PyMuPDF

in_pdf = "Agentic-Workflows-Guide.pdf"
out_pdf = "Agentic-Workflows-Guide_invertito.pdf"
dpi = 300

doc = fitz.open(in_pdf)
out = fitz.open()

zoom = dpi / 72
mat = fitz.Matrix(zoom, zoom)

for page in doc:
    pix = page.get_pixmap(matrix=mat, alpha=False)
    pix.invert_irect(pix.irect)  # inverte i colori dell'intera pagina

    rect = fitz.Rect(0, 0, pix.width, pix.height)
    newp = out.new_page(width=rect.width, height=rect.height)
    newp.insert_image(rect, pixmap=pix)

out.save(out_pdf, deflate=True)
out.close()
doc.close()
print("Creato:", out_pdf)
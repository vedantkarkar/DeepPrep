import docx
import pypdf
from pypdf import PdfWriter
from reportlab.pdfgen import canvas
import io

def make_test_pdf(filename: str, text: str):
    import reportlab.lib.pagesizes as pagesizes
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=pagesizes.letter)
    y = 750
    for line in text.splitlines():
        can.drawString(50, y, line[:80])
        y -= 15
        if y < 50:
            can.showPage()
            y = 750
    can.save()
    packet.seek(0)
    with open(filename, "wb") as f:
        f.write(packet.read())

def make_test_docx(filename: str, text: str):
    doc = docx.Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    doc.save(filename)

if __name__ == "__main__":
    with open("data/resumes/demo_resume.txt", "r") as f:
        resume_text = f.read()

    try:
        make_test_pdf("data/resumes/demo_resume.pdf", resume_text)
        print("Generated data/resumes/demo_resume.pdf")
    except ImportError:
        print("reportlab not installed, generating minimal PDF")
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with open("data/resumes/demo_resume.pdf", "wb") as f:
            writer.write(f)

    make_test_docx("data/resumes/demo_resume.docx", resume_text)
    print("Generated data/resumes/demo_resume.docx")

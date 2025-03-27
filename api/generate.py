from flask import Flask, request, send_file
from bs4 import BeautifulSoup as bs
from PyPDF2 import PdfReader, PdfWriter
import io

app = Flask(__name__)

@app.route("/api/generate", methods=["POST"])
def generate_pdf():
    xml_file = request.files["xml"]
    soup = bs(xml_file.read(), features="xml")

    def find(tag): return soup.find(tag).text if soup.find(tag) else ""

    full_name = find("xml001_B00160")
    furigana = find("xml001_B00150")
    zip_code = find("xml001_B00180")
    zip_3_digit, zip_4_digit = zip_code[:3], zip_code[3:]
    address_parts = [
        find("xml001_B00200"),
        find("xml001_B00210"),
        find("xml001_B00220")
    ]
    address = " ".join(address_parts).replace("－", "-")

    era_dict = {'1': '明', '2': '大', '3': '昭', '4': '平', '5': '令'}
    birth_era = era_dict.get(find("xml001_B00250"), "")
    birth_era_numeral = find("xml001_B00260")
    birth_month = find("xml001_B00270")
    birth_date = find("xml001_B00280")
    house_holder_name = find("xml001_B00300")
    house_holder = {'0': '初期値', '1': '本人', '2': '配偶者', '3': '子', '4': '親', '5': '孫', '6': '祖父母', '99': 'その他'}.get(find("xml001_B00320"), "")
    spouse = {'0':' 無', '1':' 有', '2':' 無'}.get(find("xml001_C00001"), "")
    tax_office = find("xml001_B00050")
    regarding_office = find("xml001_B00060")
    payers_name = find("xml001_B00080")
    payers_address = find("xml001_B00110")
    payers_official_number = find("xml001_B00090")
    spouse_dependent_furigana = find("xml001_C00030")
    spouse_dependent_name = find("xml001_C00040")
    spouse_dependent_number = find("xml001_C00050")
    spouse_birth_era = era_dict.get(find("xml001_C00080"), "")

    reader = PdfReader("extractable.pdf")
    existing_page = reader.pages[0]
    fields = reader.get_fields()
    new_fields = {k: " " for k in fields}

    new_fields.update({
        "Text7": full_name,
        "Text6": furigana,
        "Text9-1": zip_3_digit,
        "Text9-2": zip_4_digit,
        "Text10": address,
        "Dropdown2":  birth_era,
        "Text11": birth_era_numeral,
        "Text12": birth_month,
        "Text13": birth_date,
        "Text14": house_holder_name,
        "Text15": house_holder,
        "Dropdown16": spouse,
        "Text1": tax_office,
        "Text2": regarding_office,
        "Text3": payers_name,
        "Text5": payers_address,
        "Text4": payers_official_number,
        "Text18": spouse_dependent_furigana,
        "Text19": spouse_dependent_name,
        "Text20": spouse_dependent_number,
        "Dropdown21": spouse_birth_era
    })

    writer = PdfWriter()
    writer.update_page_form_field_values(existing_page, new_fields)
    writer.add_page(existing_page)
    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="output.pdf", mimetype="application/pdf")

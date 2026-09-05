import docx
import re
import io

def cyrillic_to_latin(text):
    mapping = {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo', 'Ж': 'J', 'З': 'Z',
        'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
        'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'X', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sh',
        'Ъ': "'", 'Ы': 'I', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya', 'Ў': "O'", 'Қ': 'Q', 'Ғ': "G'", 'Ҳ': 'H',
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'j', 'з': 'z',
        'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'x', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sh',
        'ъ': "'", 'ы': 'i', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya', 'ў': "o'", 'қ': 'q', 'ғ': "g'", 'ҳ': 'h'
    }
    
    import re
    text = re.sub(r"(^|\s|[АЕЁИОУЫЭЮЯЎҚҒҲаеёиоуыэюяўқғҳ])Е", r"\1Ye", text)
    text = re.sub(r"(^|\s|[АЕЁИОУЫЭЮЯЎҚҒҲаеёиоуыэюяўқғҳ])е", r"\1ye", text)
    
    for cyr, lat in mapping.items():
        text = text.replace(cyr, lat)
    return text

def parse_person_document(filepath):
    try:
        import docx
        import re
        doc = docx.Document(filepath)
    except Exception as e:
        print(f"Error reading docx: {e}")
        return {}
        
    data = {
        'first_name': '', 'last_name': '', 'patronymic': '',
        'birth_date': '', 'position': '', 'languages': '',
        'passport': '', 'pinfl': '', 'birth_place': '', 'nationality': '',
        'party_membership': '', 'education': '', 'graduated_from': '', 'education_specialty': '',
        'academic_degree': '', 'academic_title': '', 'state_awards': '', 'deputy_status': '',
        'employment': '', 'relatives': []
    }
    
    key_mapping = {
        "Tug'ilgan yili": 'birth_date',
        "Tug'ilgan joyi": 'birth_place',
        "Millati": 'nationality',
        "Partiyaviyligi": 'party_membership',
        "Ma'lumoti": 'education', 
        "Tamomlagan": 'graduated_from',
        "mutaxassisligi": 'education_specialty',
        "Ilmiy darajasi": 'academic_degree',
        "Ilmiy unvoni": 'academic_title',
        "tillari": 'languages',
        "mukofotlari": 'state_awards',
        "deputatlari": 'deputy_status'
    }

    # 1. Extract relatives (Table with 5 cols)
    for table in doc.tables:
        is_relatives_table = False
        if len(table.rows) > 0 and len(table.rows[0].cells) >= 5:
            header_cell = cyrillic_to_latin(table.rows[0].cells[0].text.strip()).lower()
            if 'qarindosh' in header_cell:
                is_relatives_table = True
                
        if is_relatives_table:
            for i in range(1, len(table.rows)):
                row = table.rows[i]
                if len(row.cells) >= 5:
                    rel = {
                        'relationship': cyrillic_to_latin(row.cells[0].text.strip()),
                        'full_name': cyrillic_to_latin(row.cells[1].text.strip()),
                        'birth_info': cyrillic_to_latin(row.cells[2].text.strip()),
                        'work_info': cyrillic_to_latin(row.cells[3].text.strip()),
                        'residence': cyrillic_to_latin(row.cells[4].text.strip())
                    }
                    if rel['full_name'] or rel['relationship']:
                        data['relatives'].append(rel)

    # 2. Extract visual lines
    text_blocks = []
    for element in doc.element.body:
        if element.tag.endswith('p'):
            p = docx.text.paragraph.Paragraph(element, doc)
            if p.text.strip(): text_blocks.append(cyrillic_to_latin(p.text.strip()))
        elif element.tag.endswith('tbl'):
            t = docx.table.Table(element, doc)
            # Skip relatives table
            if len(t.rows) > 0 and len(t.rows[0].cells) >= 5:
                header_cell = cyrillic_to_latin(t.rows[0].cells[0].text.strip()).lower()
                if 'qarindosh' in header_cell:
                    continue
            for row in t.rows:
                cells_text = [cyrillic_to_latin(c.text.strip()) for c in row.cells]
                # Join with tab to act like a visual line
                text_blocks.append('	'.join(cells_text))

    # Convert text_blocks into 2D tokens grid
    lines = []
    for block in text_blocks:
        tokens = [t.strip() for t in re.split(r'\t|\s{2,}', block) if t.strip()]
        if tokens: lines.append(tokens)

    # Search for keys
    for k_str, k_key in key_mapping.items():
        found = False
        k_clean = k_str.lower().replace(':', '')
        
        for r, row in enumerate(lines):
            if found: break
            for c, token in enumerate(row):
                if k_clean in token.lower():
                    # Case 1: The value is in the same token (separated by single space or just colon)
                    parts = token.split(':')
                    val = ""
                    if len(parts) > 1:
                        for j, p in enumerate(parts):
                            if k_clean in p.lower() and j + 1 < len(parts):
                                val = parts[j+1].strip()
                                break
                        if val:
                            # Clean trailing keys
                            for other_k in key_mapping.keys():
                                if other_k != k_str:
                                    other_clean = other_k.lower().replace(':', '')
                                    idx = val.lower().find(other_clean)
                                    if idx != -1:
                                        val = val[:idx].strip()
                            if val:
                                data[k_key] = val
                                found = True
                                break
                                
                    if found: break
                    
                    # Case 2: Check next token on same line
                    if c + 1 < len(row):
                        next_tok = row[c+1]
                        if not any(k.lower().replace(':', '') in next_tok.lower() for k in key_mapping.keys() if k != k_str):
                            data[k_key] = next_tok
                            found = True
                            break
                            
                    # Case 3: Check next line, same or closest column
                    if r + 1 < len(lines):
                        next_row = lines[r+1]
                        if c < len(next_row):
                            next_tok = next_row[c]
                            if not any(k.lower().replace(':', '') in next_tok.lower() for k in key_mapping.keys() if k != k_str):
                                if "MEHNAT" not in next_tok.upper() and "FAOLIYATI" not in next_tok.upper():
                                    data[k_key] = next_tok
                                    found = True
                                    break
                                    
    # Name and Position
    for i, row in enumerate(lines):
        full_line = " ".join(row).upper()
        if "MA'LUMOTNOMA" in full_line or "МАЪЛУМОТНОМА" in full_line:
            if i + 1 < len(lines):
                name_line = " ".join(lines[i+1])
                parts = name_line.split()
                if len(parts) >= 2:
                    data['last_name'] = parts[0]
                    data['first_name'] = parts[1]
                    if len(parts) >= 3:
                        data['patronymic'] = " ".join(parts[2:])
        
        # Position (looks for "dan:" or date format)
        if "dan:" in full_line.lower() or re.search(r'\d{4}\s*yil.*dan:', full_line.lower()):
            if i + 1 < len(lines):
                pos_line = " ".join(lines[i+1])
                if i + 2 < len(lines):
                    next_line_str = " ".join(lines[i+2])
                    if "Tug'ilgan" not in next_line_str:
                        pos_line += " " + next_line_str
                data['position'] = pos_line

    # Employment history
    in_employment = False
    emp_lines = []
    for row in lines:
        full_line = " ".join(row)
        if "MEHNAT FAOLIYATI" in full_line.upper():
            in_employment = True
            continue
        if in_employment:
            if "QARINDOSHLARI" in full_line.upper() or "MA'LUMOT" in full_line.upper() and len(row) > 1:
                # the relatives header might contain MA'LUMOT
                if "QARINDOSHLAR" in full_line.upper():
                    in_employment = False
                    break
            if full_line.strip() and "QARINDOSHLAR" not in full_line.upper():
                emp_lines.append(full_line)
                
    if emp_lines:
        data['employment'] = '\n'.join(emp_lines)

    # Date cleanup for birth_date
    if data['birth_date']:
        bmatch = re.search(r'(\d{2}\.\d{2}\.\d{4}|\d{4})', data['birth_date'])
        if bmatch:
            val = bmatch.group(1)
            if '.' in val:
                parts = val.split('.')
                data['birth_date'] = f"{parts[2]}-{parts[1]}-{parts[0]}"
            else:
                data['birth_date'] = f"{val}-01-01"

    # PINFL and Passport fallback
    combined_all = '\n'.join([" ".join(l) for l in lines])
    pinfl_match = re.search(r'\b[3-6]\d{13}\b', combined_all)
    if pinfl_match: data['pinfl'] = pinfl_match.group(0)
    
    passport_match = re.search(r'\b[A-Za-z]{2}\s*\d{7}\b', combined_all)
    if passport_match: data['passport'] = passport_match.group(0).replace(" ", "").upper()

    # Extract profile image
    try:
        import zipfile
        with zipfile.ZipFile(filepath, 'r') as docx_zip:
            image_files = [f for f in docx_zip.namelist() if f.startswith('word/media/')]
            if image_files:
                image_files.sort()
                data['photo_person'] = docx_zip.read(image_files[0])
    except Exception as e:
        print(f"Error extracting image: {e}")

    return data

import re
import csv
import os
import argparse

def parse_nested_braces(text, start_index):
    """
    Parses a balanced brace structure starting at start_index.
    Returns the content inside the braces and the index after the closing brace.
    """
    if start_index >= len(text) or text[start_index] != '{':
        return None, start_index

    balance = 1
    i = start_index + 1
    content_start = i

    while i < len(text) and balance > 0:
        if text[i] == '{':
            balance += 1
        elif text[i] == '}':
            balance -= 1
        i += 1

    if balance == 0:
        return text[content_start:i-1], i
    else:
        return None, start_index

def extract_presentations(tex_file, output_csv):
    if not os.path.exists(tex_file):
        print(f"Error: File {tex_file} not found.")
        return

    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()

    presentations = []
    # Search for \Pres
    # The format is \Pres{Location}{Date}{Description}{Title}{Type}

    current_idx = 0
    while True:
        pres_idx = content.find(r'\Pres', current_idx)
        if pres_idx == -1:
            break

        # Check if it's really \Pres and not \PresentationSomething
        next_char_idx = pres_idx + 5
        # Skip whitespace
        while next_char_idx < len(content) and content[next_char_idx].isspace():
            next_char_idx += 1

        if next_char_idx < len(content) and content[next_char_idx] == '{':
            args = []
            curr_arg_idx = next_char_idx
            for _ in range(5):
                # Skip whitespace between arguments
                while curr_arg_idx < len(content) and content[curr_arg_idx].isspace():
                    curr_arg_idx += 1

                arg_content, next_idx = parse_nested_braces(content, curr_arg_idx)
                if arg_content is not None:
                    # Clean up the content
                    clean_content = ' '.join(arg_content.split())
                    args.append(clean_content)
                    curr_arg_idx = next_idx
                else:
                    break

            if len(args) == 5:
                presentations.append(args)
                current_idx = curr_arg_idx
            else:
                current_idx = pres_idx + 1
        else:
             current_idx = pres_idx + 1

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Location', 'Date', 'Description', 'Title', 'Type'])
        writer.writerows(presentations)

    print(f"Extracted {len(presentations)} presentations to {output_csv}")

def parse_bib_strings(strings_file):
    strings = {}
    if not os.path.exists(strings_file):
        return strings

    with open(strings_file, 'r', encoding='utf-8') as f:
        content = f.read()

    idx = 0
    content_lower = content.lower()
    while True:
        start = content_lower.find('@string', idx)
        if start == -1:
            break

        # Find start of entry
        brace_start = content.find('{', start)
        if brace_start == -1:
            idx = start + 7
            continue

        entry_content, end_idx = parse_nested_braces(content, brace_start)
        if entry_content:
            # entry_content is like: key = "value"
            parts = entry_content.split('=', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip()
                # Remove quotes or braces around value
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                elif val.startswith('{') and val.endswith('}'):
                    val = val[1:-1]
                strings[key] = val
            idx = end_idx
        else:
            idx = start + 7

    return strings

def parse_bib_entries(bib_file, strings_map, output_csv):
    if not os.path.exists(bib_file):
        print(f"Error: File {bib_file} not found.")
        return

    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()

    entries = []

    idx = 0
    while True:
        # Find next @
        start = content.find('@', idx)
        if start == -1:
            break

        # Determine type
        type_end = content.find('{', start)
        if type_end == -1:
            idx = start + 1
            continue

        entry_type = content[start+1:type_end].strip().lower()
        if entry_type in ['comment', 'string', 'preamble']:
            _, end_idx = parse_nested_braces(content, type_end)
            idx = end_idx
            continue

        body, end_idx = parse_nested_braces(content, type_end)
        idx = end_idx

        if body:
            # Parse body: KEY, field=value, field=value
            first_comma = body.find(',')
            if first_comma == -1:
                continue

            key = body[:first_comma].strip()
            fields_str = body[first_comma+1:]

            fields = {}
            field_idx = 0
            while field_idx < len(fields_str):
                eq_idx = fields_str.find('=', field_idx)
                if eq_idx == -1:
                    break

                field_name = fields_str[field_idx:eq_idx].strip()
                val_start = eq_idx + 1
                while val_start < len(fields_str) and fields_str[val_start].isspace():
                    val_start += 1

                if val_start >= len(fields_str):
                    break

                val_char = fields_str[val_start]
                field_val = ""
                next_field_idx = -1

                if val_char == '{':
                    val_content, val_end = parse_nested_braces(fields_str, val_start)
                    field_val = val_content
                    comma_pos = fields_str.find(',', val_end)
                    next_field_idx = len(fields_str) if comma_pos == -1 else comma_pos + 1
                elif val_char == '"':
                    quote_end = fields_str.find('"', val_start + 1)
                    while quote_end != -1 and fields_str[quote_end-1] == '\\':
                         quote_end = fields_str.find('"', quote_end + 1)

                    if quote_end != -1:
                        field_val = fields_str[val_start+1:quote_end]
                        comma_pos = fields_str.find(',', quote_end)
                        next_field_idx = len(fields_str) if comma_pos == -1 else comma_pos + 1
                    else:
                        break
                else:
                    comma_pos = fields_str.find(',', val_start)
                    raw_val = fields_str[val_start:].strip() if comma_pos == -1 else fields_str[val_start:comma_pos].strip()
                    next_field_idx = len(fields_str) if comma_pos == -1 else comma_pos + 1

                    parts = [p.strip() for p in raw_val.split('#')]
                    resolved_parts = []
                    for p in parts:
                        if p in strings_map:
                            resolved_parts.append(strings_map[p])
                        elif (p.startswith('"') and p.endswith('"')) or (p.startswith('{') and p.endswith('}')):
                             resolved_parts.append(p[1:-1])
                        else:
                             resolved_parts.append(p)
                    field_val = "".join(resolved_parts)

                fields[field_name.lower()] = field_val
                field_idx = next_field_idx

            title = ' '.join(fields.get('title', '').split())
            author = ' '.join(fields.get('author', '').split())
            year = fields.get('year', '')
            journal = fields.get('journal', '') or fields.get('booktitle', '')
            note = fields.get('note', '')

            submission = (entry_type == 'unpublished') or ("submitted" in note.lower() or "under review" in note.lower())

            entries.append({
                'Key': key,
                'Type': entry_type,
                'Author': author,
                'Title': title,
                'Journal': journal,
                'Year': year,
                'Note': note,
                'Submission': submission
            })

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Key', 'Type', 'Author', 'Title', 'Journal', 'Year', 'Note', 'Submission']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)

    print(f"Extracted {len(entries)} publications to {output_csv}")

def main():
    parser = argparse.ArgumentParser(description='Extract presentations and publications from CV LaTeX files.')
    parser.add_argument('--tex', default='cv/cv_enrico_facca.tex', help='Path to the main LaTeX CV file')
    parser.add_argument('--bib', default='cv/pubblication_ef.bib', help='Path to the BibTeX file')
    parser.add_argument('--strings', default='cv/strings.bib', help='Path to the BibTeX strings file')
    parser.add_argument('--out-pres', default='presentations.csv', help='Output CSV for presentations')
    parser.add_argument('--out-pubs', default='publications.csv', help='Output CSV for publications')

    args = parser.parse_args()

    extract_presentations(args.tex, args.out_pres)
    strings_map = parse_bib_strings(args.strings)
    parse_bib_entries(args.bib, strings_map, args.out_pubs)

if __name__ == "__main__":
    main()

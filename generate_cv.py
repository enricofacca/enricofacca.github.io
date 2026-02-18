import csv
import argparse

def load_csv(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def generate_publications_latex(publications):
    misc = [p for p in publications if p['Type'] == 'misc']
    articles = [p for p in publications if p['Type'] == 'article']
    unpublished = [p for p in publications if p['Type'] == 'unpublished']

    latex_lines = []

    def format_entry(p):
        title = p['Title']
        if p['Submission'] == 'True':
            title = f"\\textbf{{{title}}}"

        author = p['Author']
        journal = p['Journal Full']
        year = p['Year']
        note = p['Note']

        authors = author.replace(' and ', ', ')

        entry_text = f"{authors}, {title}"
        if journal:
            entry_text += f", \\emph{{{journal}}}"
        if note:
            entry_text += f", {note}"
        entry_text += "."

        return f"\\cvitem{{{year}}}{{{entry_text}}}"

    if misc:
        latex_lines.append("\\subsection{PhD Thesis}")
        for p in misc:
            latex_lines.append(format_entry(p))

    if articles:
        latex_lines.append("\\subsection{Peer-Reviewed Journal Articles}")
        for p in articles:
            latex_lines.append(format_entry(p))

    if unpublished:
        latex_lines.append("\\subsection{Preprints}")
        for p in unpublished:
            latex_lines.append(format_entry(p))

    return "\n".join(latex_lines)

def generate_presentations_latex(presentations):
    latex_lines = []
    for p in presentations:
        loc = p['Location']
        date = p['Date']
        desc = p['Description']
        title = p['Title']
        ptype = p['Type']

        if 'Invited' in ptype:
            title = f"\\textbf{{{title}}}"

        line = f"\\Pres{{{loc}}}{{{date}}}\n  {{{desc}}}\n  {{{title}}}\n  {{{ptype}}}"
        latex_lines.append(line)
        latex_lines.append("")

    return "\n".join(latex_lines)

def generate_cv(template_file, presentations_csv, publications_csv, output_file):
    presentations = load_csv(presentations_csv)
    publications = load_csv(publications_csv)

    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()

    pub_start_marker = r'\section{List of Publications}'
    pub_start = content.find(pub_start_marker)
    pres_start_marker = r'\section{List of Scientific Presentations}'
    pres_start = content.find(pres_start_marker)

    if pub_start != -1 and pres_start != -1:
        new_pubs = generate_publications_latex(publications)
        pub_header_end = content.find('\n', pub_start) + 1
        pre_pub = content[:pub_header_end]
        post_pub = content[pres_start:]
        content = pre_pub + new_pubs + "\n\n" + post_pub
    else:
        print("Could not find List of Publications section boundaries.")
        return

    pres_start = content.find(pres_start_marker)
    if pres_start == -1:
         print("Could not find List of Scientific Presentations section.")
         return

    first_pres = content.find(r'\Pres', pres_start)
    if first_pres != -1:
        lines = content.splitlines(keepends=True)
        pres_section_idx = -1
        for i, line in enumerate(lines):
            if r'\section{List of Scientific Presentations}' in line:
                pres_section_idx = i
                break

        if pres_section_idx != -1:
            end_of_block_idx = len(lines)
            for i in range(pres_section_idx + 1, len(lines)):
                sline = lines[i].strip()
                if sline.startswith(r'\section') or sline.startswith(r'%\section') or sline.startswith(r'\end{document}'):
                    end_of_block_idx = i
                    break

            new_pres = generate_presentations_latex(presentations)
            new_lines = lines[:pres_section_idx+1] + [new_pres + "\n\n"] + lines[end_of_block_idx:]
            content = "".join(new_lines)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Generated {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate a new CV LaTeX file from CSV data.')
    parser.add_argument('--template', default='cv/cv_enrico_facca.tex', help='Path to the template LaTeX file')
    parser.add_argument('--pres-csv', default='presentations.csv', help='Path to the presentations CSV file')
    parser.add_argument('--pubs-csv', default='publications.csv', help='Path to the publications CSV file')
    parser.add_argument('--out', default='cv/new_cv.tex', help='Path to the output LaTeX file')

    args = parser.parse_args()

    generate_cv(args.template, args.pres_csv, args.pubs_csv, args.out)

if __name__ == "__main__":
    main()

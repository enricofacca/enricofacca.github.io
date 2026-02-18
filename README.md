# CV Automation Tools

This directory contains Python scripts to automate the extraction of information from LaTeX CV files and regenerate them with custom styling.

## Scripts

### `extract_info.py`

Extracts presentation and publication information from existing LaTeX and BibTeX files into CSV format.

**Usage:**

```bash
python3 extract_info.py [--tex TEX_FILE] [--bib BIB_FILE] [--strings STRINGS_FILE] [--out-pres PRES_CSV] [--out-pubs PUBS_CSV]
```

**Defaults:**
- `--tex`: `cv/cv_enrico_facca.tex`
- `--bib`: `cv/pubblication_ef.bib`
- `--strings`: `cv/strings.bib`
- `--out-pres`: `presentations.csv`
- `--out-pubs`: `publications.csv`

### `generate_cv.py`

Generates a new LaTeX CV file from the extracted CSV data, applying custom styles (e.g., bolding invited presentations and submitted articles).

**Usage:**

```bash
python3 generate_cv.py [--template TEMPLATE_FILE] [--pres-csv PRES_CSV] [--pubs-csv PUBS_CSV] [--out OUT_FILE]
```

**Defaults:**
- `--template`: `cv/cv_enrico_facca.tex`
- `--pres-csv`: `presentations.csv`
- `--pubs-csv`: `publications.csv`
- `--out`: `cv/new_cv.tex`

## Workflow

1.  Run `python3 extract_info.py` to generate the CSV files from your current CV.
2.  Modify the CSV files if needed.
3.  Run `python3 generate_cv.py` to generate the new CV LaTeX file (`cv/new_cv.tex`).
4.  Compile the new LaTeX file using `pdflatex` or similar tools.

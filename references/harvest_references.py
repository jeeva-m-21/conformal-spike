#!/usr/bin/env python3
"""
Systematic literature harvest for IoV, CAN bus, and neuromorphic / spiking intrusion detection.
Retrieves ~30 high-impact papers (2024-2026), prioritizing journals and top conferences.
Extracts abstracts, BibTeX, and downloads open-access PDFs into references/.
"""

import os
import sys
import json
import time
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

REF_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(REF_DIR, "pdfs")
META_DIR = os.path.join(REF_DIR, "metadata")
BIB_FILE = os.path.join(REF_DIR, "references.bib")
SURVEY_MD = os.path.join(REF_DIR, "PAPERS_SURVEY_30.md")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(META_DIR, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (mailto:research@vitstudent.ac.in)"

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def download_file(url, target_path, timeout=30):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read()
            if len(content) > 1000 and (content.startswith(b'%PDF') or b'PDF' in content[:100]):
                with open(target_path, 'wb') as f:
                    f.write(content)
                return True
            elif len(content) > 5000:
                with open(target_path, 'wb') as f:
                    f.write(content)
                return True
    except Exception as e:
        # print(f"    Failed download {url}: {e}")
        pass
    return False

def harvest_openalex():
    queries = [
        "spiking neural network CAN bus intrusion detection",
        "neuromorphic intrusion detection Internet of Vehicles",
        "CAN bus intrusion detection deep learning 2024 2025 2026",
        "spiking neural network network intrusion detection",
        "lightweight CAN bus intrusion detection FPGA RISC-V",
        "automotive CAN intrusion detection real-time edge"
    ]
    collected = []
    seen_titles = set()

    for q in queries:
        print(f"[*] Querying OpenAlex: {q}")
        url = f"https://api.openalex.org/works?search={urllib.parse.quote(q)}&filter=publication_year:2024-2026&per_page=15&mailto=research@vitstudent.ac.in"
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                for item in data.get('results', []):
                    title = clean_text(item.get('title', ''))
                    if not title or title.lower() in seen_titles:
                        continue
                    seen_titles.add(title.lower())
                    
                    year = item.get('publication_year')
                    venue_info = item.get('primary_location', {}).get('source') if item.get('primary_location') else None
                    venue = venue_info.get('display_name', 'Unknown Venue') if venue_info else 'Unknown Venue'
                    venue_type = venue_info.get('type', '') if venue_info else ''
                    
                    # Authors
                    authors_list = []
                    for auth in item.get('authorships', []):
                        raw_name = auth.get('author', {}).get('display_name')
                        if raw_name:
                            authors_list.append(raw_name)
                    
                    # Abstract
                    abstract = ""
                    abstract_inverted = item.get('abstract_inverted_index')
                    if abstract_inverted:
                        word_positions = []
                        for word, positions in abstract_inverted.items():
                            for pos in positions:
                                word_positions.append((pos, word))
                        word_positions.sort()
                        abstract = " ".join([w for _, w in word_positions])
                    abstract = clean_text(abstract)

                    doi = item.get('doi')
                    if doi and doi.startswith("https://doi.org/"):
                        doi = doi.replace("https://doi.org/", "")

                    pdf_url = item.get('open_access', {}).get('oa_url')
                    
                    collected.append({
                        'title': title,
                        'authors': authors_list,
                        'year': year,
                        'venue': venue,
                        'venue_type': venue_type,
                        'abstract': abstract,
                        'doi': doi,
                        'pdf_url': pdf_url,
                        'source': 'openalex'
                    })
        except Exception as e:
            print(f"Error querying OpenAlex for {q}: {e}")
        time.sleep(0.5)
    return collected

def harvest_arxiv():
    queries = [
        'all:"spiking neural network" AND all:"intrusion detection"',
        'all:"CAN bus" AND all:"intrusion detection"',
        'all:"in-vehicle" AND all:"intrusion detection"',
        'all:"neuromorphic" AND all:"intrusion detection"'
    ]
    collected = []
    seen_titles = set()

    for q in queries:
        print(f"[*] Querying arXiv: {q}")
        url = f"http://export.arxiv.org/api/query?search_query={urllib.parse.quote(q)}&start=0&max_results=12&sortBy=submittedDate&sortOrder=descending"
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                root = ET.fromstring(resp.read())
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                for entry in root.findall('atom:entry', ns):
                    title = clean_text(entry.find('atom:title', ns).text)
                    if not title or title.lower() in seen_titles:
                        continue
                    seen_titles.add(title.lower())
                    
                    pub_str = entry.find('atom:published', ns).text[:10]
                    year = int(pub_str[:4])
                    if year < 2024:
                        continue
                        
                    authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
                    abstract = clean_text(entry.find('atom:summary', ns).text)
                    arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                    
                    collected.append({
                        'title': title,
                        'authors': authors,
                        'year': year,
                        'venue': f"arXiv preprint arXiv:{arxiv_id}",
                        'venue_type': 'repository',
                        'abstract': abstract,
                        'doi': f"10.48550/arXiv.{arxiv_id}",
                        'pdf_url': pdf_url,
                        'source': 'arxiv'
                    })
        except Exception as e:
            print(f"Error querying arXiv for {q}: {e}")
        time.sleep(0.5)
    return collected

def harvest_crossref():
    queries = [
        "CAN bus intrusion detection spiking neural network",
        "CAN bus intrusion detection deep learning",
        "Internet of Vehicles spiking neural network IDS",
        "automotive in-vehicle network security intrusion detection"
    ]
    collected = []
    seen_titles = set()

    for q in queries:
        print(f"[*] Querying Crossref: {q}")
        url = f"https://api.crossref.org/works?query={urllib.parse.quote(q)}&rows=15&filter=from-pub-date:2024-01-01&select=DOI,title,author,published,container-title,abstract,type"
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                for item in data.get('message', {}).get('items', []):
                    title_list = item.get('title', [])
                    if not title_list:
                        continue
                    title = clean_text(title_list[0])
                    if not title or title.lower() in seen_titles:
                        continue
                    seen_titles.add(title.lower())

                    venue_list = item.get('container-title', [])
                    venue = venue_list[0] if venue_list else 'Unknown'

                    pub_parts = item.get('published', {}).get('date-parts', [[2024]])[0]
                    year = pub_parts[0] if pub_parts else 2024

                    authors = []
                    for a in item.get('author', []):
                        fn = a.get('given', '')
                        ln = a.get('family', '')
                        if ln:
                            authors.append(f"{fn} {ln}".strip())

                    abstract = clean_text(item.get('abstract', ''))
                    doi = item.get('DOI', '')

                    collected.append({
                        'title': title,
                        'authors': authors,
                        'year': year,
                        'venue': venue,
                        'venue_type': item.get('type', ''),
                        'abstract': abstract,
                        'doi': doi,
                        'pdf_url': None,
                        'source': 'crossref'
                    })
        except Exception as e:
            print(f"Error querying Crossref: {e}")
        time.sleep(0.5)
    return collected

def calculate_relevance(paper):
    title = paper['title'].lower()
    abstract = paper['abstract'].lower()
    venue = paper['venue'].lower()
    text = f"{title} {abstract} {venue}"

    score = 0
    # Core domains
    if "can bus" in text or "controller area network" in text or "in-vehicle" in text:
        score += 35
    if "intrusion detection" in text or "ids" in text or "anomaly detection" in text or "cyber" in text or "attack" in text:
        score += 30
    if "spiking" in text or "snn" in text or "neuromorphic" in text:
        score += 35
    elif "lightweight" in text or "fpga" in text or "edge" in text or "real-time" in text or "energy" in text:
        score += 15
    if "vehicle" in text or "automotive" in text or "iov" in text or "cav" in text:
        score += 15

    # Prioritize 2026 and 2025
    if paper['year'] == 2026:
        score += 20
    elif paper['year'] == 2025:
        score += 15
    elif paper['year'] == 2024:
        score += 10

    # Prioritize journal venues
    if any(j in venue for j in ["ieee", "transactions", "access", "nature", "scientific reports", "springer", "elsevier", "mdpi", "journal"]):
        score += 15

    # Having abstract is a plus
    if len(abstract) > 100:
        score += 10
    
    return score

def make_bib_key(authors, year, title):
    first_author = "Unknown"
    if authors:
        parts = authors[0].split()
        first_author = parts[-1] if parts else "Unknown"
    first_author = re.sub(r'[^a-zA-Z]', '', first_author)
    first_word = "paper"
    words = [w for w in re.sub(r'[^a-zA-Z\s]', '', title).split() if len(w) > 3]
    if words:
        first_word = words[0].lower()
    return f"{first_author.lower()}{year}{first_word}"

def format_bibtex(key, paper):
    entry_type = "article"
    authors_str = " and ".join(paper['authors']) if paper['authors'] else "Unknown"
    title_str = paper['title']
    year_str = str(paper['year'])
    venue_str = paper['venue']
    doi_str = paper['doi'] or ""
    
    bib = [
        f"@{entry_type}{{{key},",
        f"  author = {{{authors_str}}},",
        f"  title = {{{title_str}}},",
        f"  journal = {{{venue_str}}},",
        f"  year = {{{year_str}}},"
    ]
    if doi_str:
        bib.append(f"  doi = {{{doi_str}}},")
    if paper.get('pdf_url'):
        bib.append(f"  url = {{{paper['pdf_url']}}},")
    bib.append("}\n")
    return "\n".join(bib)

def main():
    print("[+] Starting comprehensive paper harvest...")
    pool = []
    pool.extend(harvest_openalex())
    pool.extend(harvest_arxiv())
    pool.extend(harvest_crossref())

    # Deduplicate by normalized title
    dedup = {}
    for p in pool:
        norm_title = re.sub(r'[^a-z0-9]', '', p['title'].lower())
        if norm_title not in dedup:
            dedup[norm_title] = p
        else:
            # Merge fields if missing
            existing = dedup[norm_title]
            if not existing['abstract'] and p['abstract']:
                existing['abstract'] = p['abstract']
            if not existing['pdf_url'] and p['pdf_url']:
                existing['pdf_url'] = p['pdf_url']
            if not existing['doi'] and p['doi']:
                existing['doi'] = p['doi']

    all_papers = list(dedup.values())
    print(f"[+] Total unique candidates gathered: {len(all_papers)}")

    # Score and rank
    for p in all_papers:
        p['relevance_score'] = calculate_relevance(p)

    all_papers.sort(key=lambda x: x['relevance_score'], reverse=True)

    # Select top ~30
    top_papers = all_papers[:32]

    # Assign keys, save metadata, download PDFs
    bib_entries = []
    survey_rows = []

    print(f"[+] Processing top {len(top_papers)} papers...")
    used_keys = set()
    for idx, p in enumerate(top_papers, 1):
        key = make_bib_key(p['authors'], p['year'], p['title'])
        orig_key = key
        counter = 1
        while key in used_keys:
            key = f"{orig_key}_{counter}"
            counter += 1
        used_keys.add(key)
        p['bib_key'] = key
        p['index'] = idx

        # Download PDF if URL available
        pdf_filename = f"{idx:02d}_{key}.pdf"
        pdf_path = os.path.join(PDF_DIR, pdf_filename)
        p['local_pdf'] = None

        if p['pdf_url']:
            print(f"[{idx}/{len(top_papers)}] Downloading PDF: {p['title'][:50]}...")
            if download_file(p['pdf_url'], pdf_path):
                p['local_pdf'] = os.path.relpath(pdf_path, REF_DIR)
                print(f"    Saved to {pdf_filename}")
            else:
                print(f"    Direct download failed for {p['pdf_url']}")
        else:
            print(f"[{idx}/{len(top_papers)}] No direct OA PDF URL for {p['title'][:50]}")

        # Save single paper metadata JSON
        meta_path = os.path.join(META_DIR, f"{idx:02d}_{key}.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(p, f, indent=2, ensure_ascii=False)

        bib_text = format_bibtex(key, p)
        bib_entries.append(bib_text)

        survey_rows.append({
            'index': idx,
            'key': key,
            'year': p['year'],
            'title': p['title'],
            'authors': ", ".join(p['authors'][:3]) + (" et al." if len(p['authors']) > 3 else ""),
            'venue': p['venue'],
            'doi': p['doi'] or "N/A",
            'pdf': p['local_pdf'] or "Pending OA",
            'score': p['relevance_score'],
            'abstract': p['abstract']
        })

    # Write combined references.bib
    with open(BIB_FILE, 'w', encoding='utf-8') as f:
        f.write("% ================================================================\n")
        f.write("% Curated 30+ Research Literature Database: CAN Bus & Neuromorphic IDS\n")
        f.write("% Generated for IEEE Conference Research Paper in research-can\n")
        f.write("% ================================================================\n\n")
        f.write("\n\n".join(bib_entries))
    print(f"[+] Saved {len(bib_entries)} BibTeX entries to {BIB_FILE}")

    # Write comprehensive survey markdown
    with open(SURVEY_MD, 'w', encoding='utf-8') as f:
        f.write("# Systematic Survey: Neuromorphic Computing & Intrusion Detection in IoV and CAN Bus Networks\n\n")
        f.write(f"**Curated Corpus:** {len(top_papers)} Papers | **Publication Years:** 2024–2026 | **Target Venue:** IEEE Conference\n\n")
        f.write("## 1. Summary Matrix\n\n")
        f.write("| # | Year | Key | Title | Venue | Score | PDF Status |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for row in survey_rows:
            f.write(f"| {row['index']} | {row['year']} | `{row['key']}` | {row['title']} | {row['venue'][:40]} | {row['score']} | {row['pdf']} |\n")
        
        f.write("\n\n## 2. Detailed Annotated Abstracts & Analysis\n\n")
        for row in survey_rows:
            f.write(f"### [{row['index']}] {row['title']}\n")
            f.write(f"- **BibTeX Key:** `{row['key']}`\n")
            f.write(f"- **Authors:** {row['authors']}\n")
            f.write(f"- **Venue & Year:** {row['venue']} ({row['year']})\n")
            f.write(f"- **DOI:** `{row['doi']}`\n")
            f.write(f"- **PDF Artifact:** `{row['pdf']}`\n")
            f.write(f"- **Relevance Score:** {row['score']}\n\n")
            f.write("**Abstract:**\n")
            if row['abstract']:
                f.write(f"> {row['abstract']}\n\n")
            else:
                f.write("> *(Abstract pending retrieval from publisher DOI index)*\n\n")
            f.write("---\n\n")

    print(f"[+] Written detailed survey synthesis to {SURVEY_MD}")

if __name__ == '__main__':
    main()

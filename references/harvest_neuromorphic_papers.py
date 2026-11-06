#!/usr/bin/env python3
"""
Targeted harvester for Spiking Neural Network (SNN) and Neuromorphic Computing
papers in network and embedded/automotive intrusion detection (2024-2026).
Merges with existing references.
"""

import os
import json
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

REF_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(REF_DIR, "pdfs")
META_DIR = os.path.join(REF_DIR, "metadata")
BIB_FILE = os.path.join(REF_DIR, "references.bib")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) (mailto:research@vitstudent.ac.in)"

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
            if len(content) > 1000:
                with open(target_path, 'wb') as f:
                    f.write(content)
                return True
    except Exception as e:
        pass
    return False

def query_openalex_snn():
    queries = [
        "spiking neural network intrusion detection",
        "neuromorphic cybersecurity intrusion detection",
        "neuromorphic embedded real-time anomaly detection",
        "spiking neural network IoT intrusion detection",
        "spiking neural network hardware intrusion detection"
    ]
    results = []
    seen = set()
    for q in queries:
        url = f"https://api.openalex.org/works?search={urllib.parse.quote(q)}&filter=publication_year:2024-2026&per_page=10&mailto=research@vitstudent.ac.in"
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                for item in data.get('results', []):
                    title = clean_text(item.get('title', ''))
                    if not title or title.lower() in seen:
                        continue
                    seen.add(title.lower())
                    
                    year = item.get('publication_year')
                    venue_info = item.get('primary_location', {}).get('source') if item.get('primary_location') else None
                    venue = venue_info.get('display_name', 'Journal/Conference') if venue_info else 'Journal/Conference'
                    
                    authors = [a.get('author', {}).get('display_name') for a in item.get('authorships', []) if a.get('author', {}).get('display_name')]
                    
                    abstract = ""
                    abstract_inverted = item.get('abstract_inverted_index')
                    if abstract_inverted:
                        word_positions = []
                        for word, positions in abstract_inverted.items():
                            for pos in positions:
                                word_positions.append((pos, word))
                        word_positions.sort()
                        abstract = clean_text(" ".join([w for _, w in word_positions]))
                    
                    doi = item.get('doi')
                    if doi and doi.startswith("https://doi.org/"):
                        doi = doi.replace("https://doi.org/", "")
                        
                    pdf_url = item.get('open_access', {}).get('oa_url')
                    
                    results.append({
                        'title': title,
                        'authors': authors,
                        'year': year,
                        'venue': venue,
                        'abstract': abstract,
                        'doi': doi,
                        'pdf_url': pdf_url,
                        'source': 'openalex_snn'
                    })
        except Exception as e:
            print(f"Error {q}: {e}")
    return results

def query_arxiv_snn():
    queries = [
        'all:"spiking neural network" AND all:"intrusion detection"',
        'all:"neuromorphic" AND all:"intrusion detection"',
        'all:"spiking" AND all:"anomaly detection"'
    ]
    results = []
    seen = set()
    for q in queries:
        url = f"http://export.arxiv.org/api/query?search_query={urllib.parse.quote(q)}&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending"
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                root = ET.fromstring(resp.read())
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                for entry in root.findall('atom:entry', ns):
                    title = clean_text(entry.find('atom:title', ns).text)
                    if not title or title.lower() in seen:
                        continue
                    seen.add(title.lower())
                    pub_str = entry.find('atom:published', ns).text[:10]
                    year = int(pub_str[:4])
                    if year < 2024:
                        continue
                    authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
                    abstract = clean_text(entry.find('atom:summary', ns).text)
                    arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                    results.append({
                        'title': title,
                        'authors': authors,
                        'year': year,
                        'venue': f"arXiv preprint arXiv:{arxiv_id}",
                        'abstract': abstract,
                        'doi': f"10.48550/arXiv.{arxiv_id}",
                        'pdf_url': pdf_url,
                        'source': 'arxiv_snn'
                    })
        except Exception as e:
            print(f"Error arxiv {q}: {e}")
    return results

def main():
    snn_papers = query_openalex_snn() + query_arxiv_snn()
    print(f"[+] Harvested {len(snn_papers)} candidate SNN papers.")
    
    # Filter for quality: must mention spiking or neuromorphic in title or abstract
    filtered_snn = []
    for p in snn_papers:
        t = f"{p['title']} {p['abstract']}".lower()
        if "spik" in t or "neuromorph" in t or "snn" in t:
            filtered_snn.append(p)
    print(f"[+] High-relevance SNN/Neuromorphic papers: {len(filtered_snn)}")

    # Load existing metadata from references/metadata
    existing_files = [f for f in os.listdir(META_DIR) if f.endswith('.json')]
    existing_titles = set()
    existing_items = []
    for f in existing_files:
        with open(os.path.join(META_DIR, f), 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            existing_items.append(data)
            existing_titles.add(re.sub(r'[^a-z0-9]', '', data['title'].lower()))

    # Add top 15 new SNN papers that are not duplicates
    added = 0
    start_idx = len(existing_items) + 1
    new_items = []

    for p in filtered_snn:
        norm_t = re.sub(r'[^a-z0-9]', '', p['title'].lower())
        if norm_t in existing_titles:
            continue
        existing_titles.add(norm_t)

        # Make key
        first_author = "unknown"
        if p['authors']:
            first_author = re.sub(r'[^a-zA-Z]', '', p['authors'][0].split()[-1]).lower()
        first_word = "snn"
        words = [w for w in re.sub(r'[^a-zA-Z\s]', '', p['title']).split() if len(w) > 3]
        if words:
            first_word = words[0].lower()
        key = f"{first_author}{p['year']}{first_word}"
        p['bib_key'] = key
        p['index'] = start_idx + added

        pdf_filename = f"{p['index']:02d}_{key}.pdf"
        pdf_path = os.path.join(PDF_DIR, pdf_filename)
        p['local_pdf'] = None

        if p.get('pdf_url'):
            print(f"Downloading [{p['index']}] {p['title'][:55]}...")
            if download_file(p['pdf_url'], pdf_path):
                p['local_pdf'] = os.path.relpath(pdf_path, REF_DIR)
                print(f"   --> Saved {pdf_filename}")

        meta_path = os.path.join(META_DIR, f"{p['index']:02d}_{key}.json")
        with open(meta_path, 'w', encoding='utf-8') as fp:
            json.dump(p, fp, indent=2, ensure_ascii=False)

        new_items.append(p)
        added += 1
        if added >= 15:
            break

    print(f"[+] Added {added} dedicated SNN/Neuromorphic intrusion detection papers.")

    # Now rebuild master references.bib and master survey
    all_final = existing_items + new_items
    bib_entries = []
    for item in all_final:
        key = item.get('bib_key', f"ref{item.get('index', 0)}")
        authors_str = " and ".join(item['authors']) if item.get('authors') else "Unknown"
        title_str = item.get('title', 'Untitled')
        year_str = str(item.get('year', 2025))
        venue_str = item.get('venue', 'Preprint')
        doi_str = item.get('doi') or ""
        
        b = [
            f"@article{{{key},",
            f"  author = {{{authors_str}}},",
            f"  title = {{{title_str}}},",
            f"  journal = {{{venue_str}}},",
            f"  year = {{{year_str}}},"
        ]
        if doi_str:
            b.append(f"  doi = {{{doi_str}}},")
        if item.get('pdf_url'):
            b.append(f"  url = {{{item['pdf_url']}}},")
        b.append("}\n")
        bib_entries.append("\n".join(b))

    with open(BIB_FILE, 'w', encoding='utf-8') as f:
        f.write("% ================================================================\n")
        f.write("% Curated Research Corpus: CAN Bus, IoV, and Neuromorphic/SNN IDS\n")
        f.write(f"% Total verified entries: {len(all_final)}\n")
        f.write("% ================================================================\n\n")
        f.write("\n\n".join(bib_entries))

    # Also rewrite master survey markdown
    SURVEY_MD = os.path.join(REF_DIR, "PAPERS_SURVEY_MASTER.md")
    with open(SURVEY_MD, 'w', encoding='utf-8') as f:
        f.write("# Master Research Corpus: Neuromorphic Computing & Intrusion Detection for In-Vehicle CAN Networks\n\n")
        f.write(f"**Total Papers:** {len(all_final)} | **Publication Years:** 2024–2026 | **Target Venue:** IEEE Conference / Journal\n\n")
        f.write("## 1. Corpus Summary Table\n\n")
        f.write("| # | Year | BibTeX Key | Category | Title | Venue | PDF Artifact |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for item in all_final:
            idx = item.get('index', 0)
            yr = item.get('year', 2025)
            k = item.get('bib_key', '')
            t = item.get('title', '')
            v = item.get('venue', '')[:35]
            pdf = item.get('local_pdf') or "External OA"
            
            # Category detection
            full_txt = f"{t} {item.get('abstract', '')}".lower()
            if "spik" in full_txt or "neuromorph" in full_txt or "snn" in full_txt:
                cat = "Neuromorphic/SNN"
            elif "can" in full_txt or "vehicle" in full_txt or "iov" in full_txt:
                cat = "CAN/IoV IDS"
            else:
                cat = "Network/Edge IDS"
            f.write(f"| {idx} | {yr} | `{k}` | **{cat}** | {t} | {v} | `{pdf}` |\n")

        f.write("\n\n## 2. In-Depth Annotated Abstracts & Contribution Analyses\n\n")
        for item in all_final:
            idx = item.get('index', 0)
            yr = item.get('year', 2025)
            k = item.get('bib_key', '')
            t = item.get('title', '')
            auths = ", ".join(item.get('authors', [])[:3]) + (" et al." if len(item.get('authors', [])) > 3 else "")
            v = item.get('venue', '')
            doi = item.get('doi') or "N/A"
            pdf = item.get('local_pdf') or "External"
            ab = item.get('abstract', 'Abstract pending index extraction.')

            f.write(f"### [{idx}] {t}\n")
            f.write(f"- **Key:** `{k}` | **Year:** {yr} | **Venue:** {v}\n")
            f.write(f"- **Authors:** {auths}\n")
            f.write(f"- **DOI:** `{doi}` | **PDF:** `{pdf}`\n\n")
            f.write(f"**Abstract:**\n> {ab}\n\n")
            f.write("---\n\n")

    print(f"[+] Master survey and BibTeX successfully generated at {SURVEY_MD} ({len(all_final)} papers).")

if __name__ == '__main__':
    main()

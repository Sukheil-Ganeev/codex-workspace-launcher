import json, re, os

base = 'C:/Users/londo/.claude/skills/docs-optimizer-workspace/iteration-1/'

evals = [
    'eval-1-analyze', 'eval-2-tiered', 'eval-3-audit', 'eval-4-optimize', 'eval-5-duplication',
    'eval-6-freshness', 'eval-7-tokens', 'eval-8-crossref', 'eval-9-stale-issues', 'eval-10-orphan-docs'
]

def read_file(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return f.read()

def check_assertion(assertion, output, eval_name, config):
    out_lower = output.lower()
    a = assertion.lower()

    # EVAL-1: analyze
    if 'verification score explicitly in n/5 format' in a:
        m = re.search(r'\b([0-9])/5\b', output)
        if m:
            return True, f"Found score: {m.group(0)}"
        return False, "No N/5 score found"

    if 'claude.md exceeding 300-400 line threshold' in a:
        if re.search(r'557', output) and re.search(r'claude\.md', out_lower):
            return True, "Found '557' + 'CLAUDE.md' mention"
        if re.search(r'claude\.md.*(?:critical|problem|AP-01)', output, re.IGNORECASE):
            return True, "Found CLAUDE.md critical mention"
        return False, "No CLAUDE.md line count critical problem"

    if 'recommendations section with ranked items' in a:
        if re.search(r'рекоменд|recommend', out_lower):
            if re.search(r'high|medium|low|высок|средн|низк|приоритет', out_lower):
                return True, "Found recommendations with ranking"
        return False, "No ranked recommendations section"

    if 'antipattern codes in ap-xx format' in a:
        m = re.findall(r'AP-\d+', output)
        if m:
            return True, f"Found AP-XX: {', '.join(set(m[:5]))}"
        return False, "No AP-XX codes found"

    if 'specific score format n/5' in a and 'not percentage' in a:
        m = re.search(r'\b([0-9])/5\b', output)
        if m:
            return True, f"Found N/5: {m.group(0)}"
        return False, "No N/5 score format"

    if 'at least 3 distinct ap-xx coded antipatterns' in a:
        patterns = set(re.findall(r'AP-\d+', output))
        if len(patterns) >= 3:
            return True, f"Found {len(patterns)} AP-XX: {', '.join(sorted(patterns)[:5])}"
        return False, f"Only {len(patterns)} AP-XX (need 3+)"

    # EVAL-2: tiered
    if 'three named tiers: essential, on-demand, and archive' in a:
        has_e = bool(re.search(r'essential', out_lower))
        has_o = bool(re.search(r'on-demand|ondemand', out_lower))
        has_a = bool(re.search(r'archive', out_lower))
        if has_e and has_o and has_a:
            return True, "Found all three tiers"
        missing = [t for t, h in [('Essential', has_e), ('On-demand', has_o), ('Archive', has_a)] if not h]
        return False, f"Missing tiers: {', '.join(missing)}"

    if 'at least one numeric token estimate' in a:
        m = re.search(r'[~]?\d[\d,\.]*\s*(?:токен|token)', out_lower)
        if not m:
            m = re.search(r'(?:токен|token)[^\n]*\d[\d,\.]*', out_lower)
        if m:
            return True, f"Found: {m.group(0)[:50]}"
        return False, "No numeric token estimate"

    if '.claudeignore content or archiving strategy' in a:
        if re.search(r'\.claudeignore|claudeignore|archiv', out_lower):
            return True, "Found .claudeignore or archiving"
        return False, "No .claudeignore or archiving strategy"

    if "tier name 'essential' for always-loaded" in a:
        if re.search(r'essential', out_lower):
            return True, "Found 'Essential'"
        return False, "No 'Essential' tier"

    if "tier name 'on-demand' for conditionally" in a:
        if re.search(r'on-demand', out_lower):
            return True, "Found 'On-demand'"
        return False, "No 'On-demand' tier"

    if "tier name 'archive' for rarely" in a:
        if re.search(r'archive', out_lower):
            return True, "Found 'Archive'"
        return False, "No 'Archive' tier"

    if 'specific score format n/5 for overall' in a:
        m = re.search(r'\b([0-9])/5\b', output)
        if m:
            return True, f"Found N/5: {m.group(0)}"
        return False, "No N/5 score"

    # EVAL-3: audit
    if 'duplication between claude.md and memory.md' in a:
        if re.search(r'memory\.md|дублир|duplication|DUP-', output, re.IGNORECASE):
            return True, "Found duplication/MEMORY.md"
        return False, "No duplication or MEMORY.md analysis"

    if 'checks issues.md for stale or incorrectly-open' in a:
        if re.search(r'issues\.md', out_lower):
            if re.search(r'stale|устар|открыт|open|SEN-', output, re.IGNORECASE):
                return True, "Found ISSUES.md stale check"
        return False, "No ISSUES.md stale check"

    if 'validates file path references mentioned in claude.md' in a:
        if re.search(r'путь|ссылк|path|link|reference|exist', out_lower):
            return True, "Found path validation"
        return False, "No file path validation"

    if 'duplication codes in dup-xx format' in a:
        m = re.findall(r'DUP-\d+', output)
        if m:
            return True, f"Found DUP-XX: {', '.join(set(m[:5]))}"
        return False, "No DUP-XX codes"

    if 'verification score in n/5 format' in a:
        m = re.search(r'\b([0-9])/5\b', output)
        if m:
            return True, f"Found N/5: {m.group(0)}"
        return False, "No N/5 score"

    if 'at least 2 distinct dup-xx coded duplications with file pairs' in a:
        patterns = set(re.findall(r'DUP-\d+', output))
        if len(patterns) >= 2:
            return True, f"Found {len(patterns)} DUP-XX: {', '.join(sorted(patterns))}"
        return False, f"Only {len(patterns)} DUP-XX (need 2+)"

    # EVAL-4: optimize
    if 'condensed claude.md structure targeting 200-250 lines' in a:
        if re.search(r'200|250|240|190|сократ|короч', out_lower):
            if re.search(r'claude\.md', out_lower):
                return True, "Found 200-250 target + CLAUDE.md"
        return False, "No 200-250 line target"

    if 'before/after line count or token count comparison' in a:
        if re.search(r'\d+\s*(строк|lines?).*\d+\s*(строк|lines?)', out_lower):
            return True, "Found line count comparison"
        if re.search(r'557.*(?:240|250|190|короч|сократ)|(?:240|250|190).*557', output, re.IGNORECASE | re.DOTALL):
            return True, "Found before/after with 557 lines"
        if re.search(r'-\d+\s*(строк|lines?)|сокра.*\d+', out_lower):
            return True, "Found reduction mention"
        return False, "No before/after comparison"

    if 'draft outline or structure of an optimized claude.md' in a:
        if re.search(r'##|структур|outline|план|секци|section', out_lower):
            if re.search(r'claude\.md', out_lower):
                return True, "Found draft structure for CLAUDE.md"
        return False, "No draft structure for CLAUDE.md"

    if 'references ap-xx antipattern codes that the optimization addresses' in a:
        m = re.findall(r'AP-\d+', output)
        if m:
            return True, f"Found AP-XX: {', '.join(set(m[:5]))}"
        return False, "No AP-XX codes"

    if 'classifies content into essential, on-demand, and archive tiers to justif' in a:
        has_e = bool(re.search(r'essential', out_lower))
        has_o = bool(re.search(r'on-demand', out_lower))
        has_a = bool(re.search(r'archive', out_lower))
        if has_e and has_o and has_a:
            return True, "Found all three tiers"
        found = [t for t, h in [('Essential', has_e), ('On-demand', has_o), ('Archive', has_a)] if h]
        return False, f"Only: {found}"

    # EVAL-5: duplication
    if 'names at least two specific files that contain overlapping' in a:
        files = re.findall(r'[\w/.-]+\.md', output)
        unique_files = set(files)
        if len(unique_files) >= 2:
            return True, f"Found {len(unique_files)} .md files: {', '.join(list(unique_files)[:4])}"
        return False, f"Only {len(unique_files)} .md files"

    if 'at least one concrete example of content that appears in multiple' in a:
        if re.search(r'например|example|конкретн|IP|GCP|docker|команд|дублир|повтор', out_lower):
            return True, "Found concrete example"
        return False, "No concrete duplication example"

    if 'assigns dup-xx codes to each identified duplication' in a:
        m = re.findall(r'DUP-\d+', output)
        if m:
            return True, f"Found DUP-XX: {', '.join(set(m[:5]))}"
        return False, "No DUP-XX codes"

    if 'at least 2 distinct dup-xx coded duplications with source and target' in a:
        patterns = set(re.findall(r'DUP-\d+', output))
        if len(patterns) >= 2:
            return True, f"Found {len(patterns)} DUP-XX"
        return False, f"Only {len(patterns)} DUP-XX (need 2+)"

    if 'recommends a single source of truth (ssot) location' in a:
        if re.search(r'ssot|single source|источник правды|один.*файл', out_lower):
            return True, "Found SSOT recommendation"
        return False, "No SSOT recommendation"

    # EVAL-6: freshness
    if 'uses git log or checks modification dates' in a:
        if re.search(r'git\s+log|git.*дат|modification date|дат.*изменен|обновлен', out_lower):
            return True, "Found git log / modification date"
        if re.search(r'git', out_lower):
            return True, "Found git reference"
        return False, "No git log or date check"

    if 'identifies at least one specific file as potentially stale' in a:
        if re.search(r'устар|stale|давно|archive', out_lower):
            files = re.findall(r'[\w/.-]+\.md', output)
            if files:
                return True, f"Found stale files: {', '.join(list(set(files))[:3])}"
        return False, "No specific stale files"

    if 'assigns ap-xx codes to freshness-related antipatterns' in a:
        m = re.findall(r'AP-\d+', output)
        if m:
            return True, f"Found AP-XX: {', '.join(set(m[:5]))}"
        return False, "No AP-XX codes"

    if 'verification score in n/5 format for documentation freshness' in a:
        m = re.search(r'\b([0-9])/5\b', output)
        if m:
            return True, f"Found N/5: {m.group(0)}"
        return False, "No N/5 score"

    # EVAL-7: tokens
    if 'at least one specific numeric token count estimate' in a:
        m = re.search(r'[~]?\d[\d,\.]*\s*(?:токен|token)', out_lower)
        if not m:
            m = re.search(r'(?:токен|token)[^\n]*\d[\d,\.]*', out_lower)
        if m:
            return True, f"Found: {m.group(0)[:50]}"
        return False, "No numeric token count"

    if 'breakdown of token usage by file or section' in a:
        token_mentions = re.findall(r'\d[\d,\.]*\s*(?:токен|token)', out_lower)
        if len(token_mentions) >= 3:
            return True, f"Found {len(token_mentions)} token mentions"
        if re.search(r'\|.*токен|токен.*\|', out_lower):
            return True, "Found table with tokens"
        return False, f"Only {len(token_mentions)} token mentions"

    if 'classifies files into essential, on-demand, and archive tiers based on tok' in a:
        has_e = bool(re.search(r'essential', out_lower))
        has_o = bool(re.search(r'on-demand', out_lower))
        has_a = bool(re.search(r'archive', out_lower))
        if has_e and has_o and has_a:
            return True, "Found all three tiers"
        return False, f"Missing tiers"

    if 'specific tier names essential, on-demand, archive (not generic' in a:
        has_e = bool(re.search(r'essential', out_lower))
        has_o = bool(re.search(r'on-demand', out_lower))
        has_a = bool(re.search(r'archive', out_lower))
        if has_e and has_o and has_a:
            return True, "Found exact tier names"
        return False, "Missing exact tier names"

    # EVAL-8: crossref
    if 'reads claude.md and extracts specific file path references' in a:
        if re.search(r'claude\.md', out_lower):
            files = re.findall(r'[\w/.-]+\.(?:md|py|json|yaml|yml|txt|sh)', output)
            if len(files) >= 2:
                return True, f"Found file refs: {', '.join(list(set(files))[:4])}"
        return False, "No file extraction from CLAUDE.md"

    if "reports whether each referenced path actually exists" in a:
        if re.search(r'exist|найден|не найден|broken|not found|missing|found|ok|working', out_lower):
            return True, "Found existence check"
        return False, "No path existence check"

    if 'assigns ap-xx codes to broken link antipatterns' in a:
        m = re.findall(r'AP-\d+', output)
        if m:
            return True, f"Found AP-XX: {', '.join(set(m[:5]))}"
        return False, "No AP-XX codes"

    # EVAL-9: stale-issues
    if 'reads issues.md from d:/downloads/touristbotecosystem/ and reports its con' in a:
        if re.search(r'issues\.md', out_lower):
            return True, "Found ISSUES.md reference"
        return False, "No ISSUES.md found"

    if 'reports the status of each issue or at minimum the overall breakdown' in a:
        if re.search(r'открыт|open|закрыт|closed|SEN-|статус|status', output, re.IGNORECASE):
            return True, "Found issue status breakdown"
        return False, "No issue status breakdown"

    if 'cross-references issue statuses with git log or code' in a:
        if re.search(r'git|версия|version|commit|код|code', out_lower):
            return True, "Found git/code cross-reference"
        return False, "No git/code cross-reference"

    if 'verification score in n/5 format for issue tracking hygiene' in a:
        m = re.search(r'\b([0-9])/5\b', output)
        if m:
            return True, f"Found N/5: {m.group(0)}"
        return False, "No N/5 score"

    # EVAL-10: orphan-docs
    if 'lists specific files found in the docs/ directory' in a:
        if re.search(r'docs/', out_lower):
            files = re.findall(r'docs/[\w._-]+\.md', output)
            if files:
                return True, f"Found {len(files)} docs/ files"
        return False, "No docs/ files listed"

    if 'cross-checks which docs/ files are referenced from claude.md' in a:
        if re.search(r'claude\.md', out_lower) and re.search(r'docs/', out_lower):
            if re.search(r'упомян|mention|ссылк|referenced|not referenced', out_lower):
                return True, "Found cross-check vs CLAUDE.md"
        return False, "No cross-check found"

    if "classifies orphan docs into archive tier using the specific tier name 'ar'" in a:
        if re.search(r'archive', out_lower):
            return True, "Found 'Archive' tier"
        return False, "No 'Archive' tier"

    if 'assigns ap-xx codes to orphan documentation antipatterns' in a:
        m = re.findall(r'AP-\d+', output)
        if m:
            return True, f"Found AP-XX: {', '.join(set(m[:5]))}"
        return False, "No AP-XX codes"

    # Fallback
    keywords = re.findall(r'\b[a-z]{5,}\b', a)[:4]
    matches = sum(1 for kw in keywords if kw in out_lower)
    if matches >= 3:
        return True, f"Keyword match ({matches}/{len(keywords)})"
    return False, f"Unmatched: {assertion[:60]}"


results = {}

for ev in evals:
    results[ev] = {}
    meta_path = f'{base}{ev}/eval_metadata.json'
    with open(meta_path, encoding='utf-8') as f:
        meta = json.load(f)
    assertions = meta.get('assertions', [])

    for config in ['with_skill', 'without_skill']:
        output_path = f'{base}{ev}/{config}/outputs/output.md'
        output = read_file(output_path)

        graded_assertions = []
        for i, assertion in enumerate(assertions):
            passed, evidence = check_assertion(assertion, output, ev, config)
            graded_assertions.append({
                'id': f'a{i+1}',
                'description': assertion,
                'passed': passed,
                'evidence': evidence
            })

        passed_count = sum(1 for a in graded_assertions if a['passed'])
        total = len(graded_assertions)
        pass_rate = round(passed_count / total, 4) if total > 0 else 0

        grading = {
            'eval_id': ev,
            'config': config,
            'assertions': graded_assertions,
            'pass_rate': pass_rate,
            'passed': passed_count,
            'total': total
        }

        results[ev][config] = grading

        grading_path = f'{base}{ev}/{config}/grading.json'
        with open(grading_path, 'w', encoding='utf-8') as f:
            json.dump(grading, f, ensure_ascii=False, indent=2)

        print(f'{ev}/{config}: {passed_count}/{total} = {pass_rate:.0%}')

print("\nAll grading.json saved!")

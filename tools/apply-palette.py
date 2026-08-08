"""Single source of truth for the diagrams' dark palette.

Rewrites every `classDef <name> ...;` line across the site so all 8 diagrams stay
consistent. Dark canvas, muted fills, luminous borders, light text.

Run from the repository root:  python3 tools/apply-palette.py
"""
import glob, re, sys

# name: (fill, stroke, text, extra)
P = {
    # actors / clients
    'user':    ('#241f4d', '#a78bfa', '#ede9fe', 'stroke-width:2.5px'),
    'client':  ('#241f4d', '#a78bfa', '#ede9fe', 'stroke-width:2.5px'),
    # the hinge — brightest thing on the canvas
    'gate':    ('#40280c', '#fbbf24', '#fde68a', 'stroke-width:3px'),
    'pool':    ('#0b3444', '#22d3ee', '#a5f3fc', 'stroke-width:3px'),
    # app surfaces
    'ui':      ('#12294d', '#60a5fa', '#dbeafe', 'stroke-width:2.5px'),
    'auto':    ('#451331', '#f472b6', '#fbcfe8', 'stroke-width:2.5px'),
    'mcp':     ('#0a3b36', '#2dd4bf', '#ccfbf1', 'stroke-width:2.5px'),
    # models
    'model':   ('#0c3327', '#34d399', '#d1fae5', 'stroke-width:2.5px'),
    'qwen':    ('#0c3327', '#34d399', '#d1fae5', 'stroke-width:2.5px'),
    'gemma':   ('#3a250e', '#fb923c', '#fed7aa', 'stroke-width:2.5px'),
    'emb':     ('#2c1147', '#c084fc', '#f3e8ff', 'stroke-width:2.5px'),
    # per-family VM leaves — deliberately dim so the family nodes lead
    'vmq':     ('#12241d', '#2f855a', '#a7f3d0', 'stroke-width:1.5px'),
    'vmg':     ('#26190c', '#9a5b25', '#fed7aa', 'stroke-width:1.5px'),
    'vme':     ('#1e1230', '#7e4bab', '#e9d5ff', 'stroke-width:1.5px'),
    'vm':      ('#1a2234', '#64748b', '#cbd5e1', 'stroke-width:1.5px'),
    # data stores
    'pg':      ('#0b3444', '#22d3ee', '#a5f3fc', 'stroke-width:2.5px'),
    'vec':     ('#2c1147', '#c084fc', '#f3e8ff', 'stroke-width:2.5px'),
    'cache':   ('#3d240c', '#fdba74', '#ffedd5', 'stroke-width:2.5px'),
    'obj':     ('#45101f', '#fb7185', '#ffe4e6', 'stroke-width:2.5px'),
    # observability
    'obs':     ('#26330d', '#a3e635', '#ecfccb', 'stroke-width:2.5px'),
    'otel':    ('#26330d', '#a3e635', '#ecfccb', 'stroke-width:2.5px'),
    'prom':    ('#43220a', '#fb923c', '#fed7aa', 'stroke-width:3px'),
    'alert':   ('#450f1c', '#fb7185', '#fecdd3', 'stroke-width:2.5px'),
    # things this platform does NOT deploy -> dashed border, neutral fill
    'external':('#1b2333', '#94a3b8', '#e2e8f0', 'stroke-width:2px,stroke-dasharray:6 4'),
    'backend': ('#1b2333', '#94a3b8', '#cbd5e1', 'stroke-width:2px,stroke-dasharray:6 4'),
    # misc
    'root':    ('#312e81', '#818cf8', '#e0e7ff', 'stroke-width:3px'),
    'docs':    ('#1a2234', '#64748b', '#cbd5e1', 'stroke-width:1.5px'),
    'plain':   ('#1a2234', '#64748b', '#cbd5e1', 'stroke-width:2px'),
}

# subgraph tier bands: name-fragment -> (fill, stroke)
BANDS = {
    'T1': ('#1b1830', '#6d5ba8'), 'T2': ('#13203a', '#3b6ea8'),
    'T3': ('#0f2b2a', '#2f7f6f'), 'T4': ('#1e2a12', '#5f7a2a'),
    'T5': ('#1b2333', '#64748b'),
    'VA': ('#13203a', '#3b6ea8'), 'VB': ('#0f2b2a', '#2f7f6f'),
    'CA': ('#0d2b38', '#2b7f96'), 'CB': ('#341128', '#9d4a77'),
    'CLIENTS': ('#1b1830', '#6d5ba8'), 'FLEET': ('#0f2b2a', '#2f7f6f'),
    'NS': ('#0c2f2c', '#2f7f74'), 'BACK': ('#1b2333', '#64748b'),
    'SRC': ('#1a2234', '#4b5a72'), 'EXT': ('#1b2333', '#64748b'),
}

def classdef(name):
    fill, stroke, color, extra = P[name]
    return f'classDef {name} fill:{fill},stroke:{stroke},{extra},color:{color};'

changed = 0
unknown = set()
for f in sorted(glob.glob('*.html')):
    s = open(f).read()
    orig = s

    def repl(m):
        global unknown
        name = m.group(1)
        indent = m.group(0)[:len(m.group(0)) - len(m.group(0).lstrip())]
        if name not in P:
            unknown.add(name)
            return m.group(0)
        return indent + classdef(name)

    s = re.sub(r'[ \t]*classDef (\w+) [^\n]*;', repl, s)

    def band(m):
        indent, sid, rest = m.group(1), m.group(2), m.group(3)
        if sid not in BANDS:
            return m.group(0)
        fill, stroke = BANDS[sid]
        dash = ',stroke-dasharray:6 4' if sid in ('T5', 'EXT', 'BACK') else ''
        return f'{indent}style {sid} fill:{fill},stroke:{stroke},stroke-width:2px{dash}'

    s = re.sub(r'([ \t]*)style (\w+) (fill:[^\n]*)', band, s)

    if s != orig:
        open(f, 'w').write(s)
        changed += 1
        print(f'  {f}: palette applied')

print(f'\n{changed} file(s) updated')
if unknown:
    print(f'UNKNOWN classDef names (left untouched): {sorted(unknown)}')
    sys.exit(1)

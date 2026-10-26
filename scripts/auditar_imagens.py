#!/usr/bin/env python3
"""Auditoria editorial: nunca confundir URL candidata com imagem validada."""
import json, pathlib, sys, urllib.request, urllib.parse
root=pathlib.Path(__file__).resolve().parents[1]
issues=[]
for file in sorted((root/"data").glob("*.json")):
    d=json.loads(file.read_text(encoding="utf-8"))
    santos=d.get("santos",[])
    for s in santos:
        name=s.get("nome","(sem nome)")
        im=s.get("imagem") or {}
        prefix=f"{file.name} | {name}"
        if not im.get("url"):
            issues.append((prefix,"SEM_IMAGEM"))
            continue
        if not im.get("verificada"):
            issues.append((prefix,"IMAGEM_NAO_VERIFICADA"))
            continue
        if not all(im.get(k) for k in ("fonte","licenca","descricao")):
            issues.append((prefix,"METADADOS_INCOMPLETOS"))
            continue
        try:
            req=urllib.request.Request(im["url"],headers={"User-Agent":"SantosDoDiaImageAudit/1.0 (GitHub Actions)"},method="GET")
            with urllib.request.urlopen(req,timeout=18) as resp:
                typ=resp.headers.get("Content-Type","")
                if not typ.startswith("image/"): issues.append((prefix,f"URL_NAO_E_IMAGEM:{typ}"))
                resp.read(64)
        except Exception as e:
            issues.append((prefix,f"IMAGEM_INACESSIVEL:{type(e).__name__}"))
    if not santos: issues.append((file.name,"SEM_SANTOS"))
print(f"Auditadas {len(list((root/'data').glob('*.json')))} datas; {len(issues)} pendências")
for who,issue in issues: print(f"::warning::{who} | {issue}")
sys.exit(1 if issues else 0)

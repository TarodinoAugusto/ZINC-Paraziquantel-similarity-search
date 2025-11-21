#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extrai moléculas similares ao praziquantel do ZINC20 via API oficial.
Saída: CSV com ZINC ID + SMILES.
"""

import requests
import csv
import time
import os

SMILES_PRAZI = "CCOC(=O)N1CCC[C@H]1C2=NC3=CC=CC=C3C(=O)O2"
THRESHOLD = 0.65          # similaridade Tanimoto (ajusta entre 0.6–0.75)
MAX_HITS = 1200           # quantos resultados deseja (>500 garantido)
PAGE_SIZE = 200
BASE = "https://zinc20.docking.org/api/substances/"

OUT_DIR = "zinc_prazi_output"
os.makedirs(OUT_DIR, exist_ok=True)


def fetch_page(smiles, page, threshold=0.65):
    params = {
        "similarity": smiles,
        "threshold": threshold,
        "page": page,
        "count": PAGE_SIZE,
        "format": "json"
    }
    r = requests.get(BASE, params=params, timeout=30)
    if r.status_code != 200:
        print("Erro:", r.status_code, r.text[:200])
        return None
    return r.json()


def main():
    collected = []
    page = 1

    print("\nBuscando compostos similares ao praziquantel no ZINC20...\n")

    while len(collected) < MAX_HITS:
        print(f"Página {page}...")
        data = fetch_page(SMILES_PRAZI, page)

        if not data or "substances" not in data:
            print("Fim dos resultados ou erro.")
            break

        substances = data["substances"]
        if not substances:
            print("Sem mais substâncias.")
            break

        for s in substances:
            zinc_id = s.get("zinc_id")
            smiles = s.get("smiles")
            if zinc_id and smiles:
                collected.append((zinc_id, smiles))

        print(f"Coletados: {len(collected)}")
        page += 1
        time.sleep(0.5)  # cortesia à API

    # Guardar resultados
    final = collected[:MAX_HITS]

    csv_path = os.path.join(OUT_DIR, "zinc_prazi_smiles.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["zinc_id", "smiles"])
        writer.writerows(final)

    print(f"\nTotal extraído: {len(final)} moléculas.")
    print("Arquivo salvo em:", csv_path)
    print("Concluído.\n")


if __name__ == "__main__":
    main()

Adiciona script de extração ZINC20

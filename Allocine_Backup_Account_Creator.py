# -*- coding: utf-8 -*-
"""
AlloCine Backup Account Creator
Sauvegarde les notes de films et séries d'un profil AlloCiné public.

Fork de https://github.com/CLeBeRFR/AlloCine-Backup-Account-Creator
"""
import sys
import re
import argparse

from bs4 import BeautifulSoup
import requests

ALLOCINE_BASE = "https://www.allocine.fr"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def recuperer_notes(identifiant_utilisateur, type_media, output_format="standard"):
    """Scrape les notes d'un profil AlloCiné pour un type de média donné."""
    print(f"Récupération des notes : {type_media}")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    # Déterminer le nombre de pages
    nombre_de_pages = 1
    url_test = f"{ALLOCINE_BASE}/{identifiant_utilisateur}/{type_media}/?page=999"
    response = session.get(url_test)
    if "page" in response.url:
        nombre_de_pages = int(response.url.rsplit("=", 1)[1])

    print(f"  Pages à parcourir : {nombre_de_pages}")

    # Récupérer toutes les pages
    code_html = ""
    for i in range(1, nombre_de_pages + 1):
        url = f"{ALLOCINE_BASE}/{identifiant_utilisateur}/{type_media}/?page={i}"
        code_html += session.get(url).text
        # Progression
        if nombre_de_pages > 5 and i % 5 == 0:
            print(f"  Page {i}/{nombre_de_pages}...")

    # Parser le HTML
    soup = BeautifulSoup(code_html, "html.parser")
    resultats = []

    for card in soup.find_all(
        "div", class_="card entity-card-simple userprofile-entity-card-simple"
    ):
        # Récupérer le titre (nettoyer le préfixe "poster de/du" de l'attribut alt)
        img = card.find("img")
        if not img or not img.get("alt"):
            continue
        titre = img["alt"]
        for prefix in ("poster de ", "poster du ", "poster d'"):
            if titre.lower().startswith(prefix):
                titre = titre[len(prefix):]
                break

        # Extraire la note depuis la classe CSS (ex: "n35" → 3.5)
        regex_class = re.compile(r"rating-mdl n[0-5][0-9] stareval-stars")
        note_div = card.find("div", {"class": regex_class})
        if not note_div:
            continue
        note_code = note_div["class"][1][1:]  # ex: "n35" → "35"
        note = float(note_code[0] + "." + note_code[1])

        resultats.append((titre, note))

    # Écriture du fichier CSV
    if output_format == "standard":
        filename = f"liste_notes_{type_media}.csv"
        sep = ";"
        header = "Nom;Note"
        fmt_note = lambda n: str(n).replace(".", ",")
    else:
        filename = f"notes_{type_media}.csv"
        sep = ","
        header = "title,rating"
        fmt_note = lambda n: str(n)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        for titre, note in resultats:
            if sep == ",":
                # Échapper les virgules dans le titre
                titre = f'"{titre}"'
            f.write(f"{titre}{sep}{fmt_note(note)}\n")

    print(f"  {len(resultats)} {type_media} sauvegardés → {filename}")
    return resultats


def main():
    parser = argparse.ArgumentParser(
        description="Sauvegarde les notes AlloCiné d'un profil public.",
        epilog="Exemple : python Allocine_Backup_Account_Creator.py https://www.allocine.fr/membre-Z20100120021920830649555/",
    )
    parser.add_argument(
        "url",
        help="URL du profil AlloCiné public",
    )
    parser.add_argument(
        "--format",
        choices=["standard", "clean"],
        default="standard",
        help="Format CSV : 'standard' (Nom;Note avec virgule décimale) ou 'clean' (title,rating avec point décimal, compatible mesfilms)",
    )
    parser.add_argument(
        "--films-only",
        action="store_true",
        help="Ne récupérer que les films (pas les séries)",
    )
    parser.add_argument(
        "--series-only",
        action="store_true",
        help="Ne récupérer que les séries (pas les films)",
    )
    args = parser.parse_args()

    # Extraire l'identifiant membre de l'URL
    match = re.search(r"membre-([A-Z0-9]+)", args.url)
    if not match:
        print("Erreur : impossible d'extraire l'identifiant membre de l'URL.")
        print("L'URL doit contenir 'membre-...' (ex: https://www.allocine.fr/membre-Z20100120021920830649555/)")
        sys.exit(1)

    identifiant = match.group(0)

    if not args.series_only:
        recuperer_notes(identifiant, "films", args.format)
    if not args.films_only:
        recuperer_notes(identifiant, "series", args.format)

    print("Fichiers sauvegardés dans le répertoire courant.")


if __name__ == "__main__":
    main()

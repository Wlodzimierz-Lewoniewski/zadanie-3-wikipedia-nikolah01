import re
import requests
import itertools

def pobierz_html(adres_url):
    odpowiedz = requests.get(adres_url)
    return odpowiedz.text if odpowiedz.status_code == 200 else None

def utworz_url_kategorii(nazwa_kategorii):
    sformatowana_nazwa = nazwa_kategorii.replace(' ', '_')
    return f'https://pl.wikipedia.org/wiki/Kategoria:{sformatowana_nazwa}'

def znajdz_artykuly_kategorii(nazwa_kategorii, maks_artykulow=2):
    url = utworz_url_kategorii(nazwa_kategorii)
    zawartosc_html = pobierz_html(url)
    if not zawartosc_html:
        return []

    wzorzec = r'<li[^>]*>.*<a[^>]*href=\"(/wiki/(?![^"]*:)[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>.*</li>'
    dopasowania = re.finditer(wzorzec, zawartosc_html)
    return [(dopasowanie.group(1), dopasowanie.group(2)) for dopasowanie in
            itertools.islice(dopasowania, maks_artykulow)]

def wyciagnij_linki_wewnetrzne(html_artykulu, maks_linkow=5):
    sekcja_tresci = html_artykulu[
                    html_artykulu.find('<div id="mw-content-text"'):html_artykulu.find('<div id="catlinks"')]

    wzorzec = r'<a[^>]*href=\"(/wiki/(?![^"]*:)[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'
    dopasowania = re.finditer(wzorzec, sekcja_tresci)
    return [dopasowanie.group(2) for dopasowanie in itertools.islice(dopasowania, maks_linkow)]

def wyciagnij_obrazki(html_artykulu, maks_obrazkow=3):
    sekcja_tresci = html_artykulu[
                    html_artykulu.find('<div id="mw-content-text"'):html_artykulu.find('<div id="catlinks"')]

    wzorzec = r'<img[^>]*src=\"(//upload\.wikimedia\.org/[^"]+)\"[^>]*/>'
    dopasowania = re.finditer(wzorzec, sekcja_tresci)
    return [dopasowanie.group(1) for dopasowanie in itertools.islice(dopasowania, maks_obrazkow)]

def wyciagnij_linki_zewnetrzne(html_artykulu, maks_linkow=3):
    sekcja_przypisy = html_artykulu[html_artykulu.find('id="Przypisy"'):]
    sekcja_przypisy = sekcja_przypisy[:sekcja_przypisy.find('<div class="mw-heading')]

    wzorzec = r'<a[^>]*class=\"external[^"]*\"[^>]*href=\"([^"]+)\"[^>]*>'
    dopasowania = re.finditer(wzorzec, sekcja_przypisy)
    return [dopasowanie.group(1) for dopasowanie in itertools.islice(dopasowania, maks_linkow)]

def wyciagnij_kategorie(html_artykulu, maks_kategorii=3):
    sekcja_kategorii = html_artykulu[html_artykulu.find('<div id="catlinks"'):]

    wzorzec = r'<a[^>]*href=\"(/wiki/Kategoria:[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'
    dopasowania = re.finditer(wzorzec, sekcja_kategorii)
    return [dopasowanie.group(2).replace('Kategoria:', '') for dopasowanie in
            itertools.islice(dopasowania, maks_kategorii)]

def wyswietl_wyniki(nazwa_kategorii):
    artykuly = znajdz_artykuly_kategorii(nazwa_kategorii)
    if not artykuly:
        print("Nie udało się znaleźć artykułów w tej kategorii.")
        return

    for link_artykulu, tytul_artykulu in artykuly:
        html_artykulu = pobierz_html("https://pl.wikipedia.org" + link_artykulu)
        if not html_artykulu:
            continue

        linki_wewnetrzne = wyciagnij_linki_wewnetrzne(html_artykulu)
        print(" | ".join(linki_wewnetrzne))

        obrazki = wyciagnij_obrazki(html_artykulu)
        print(" | ".join(obrazki))

        linki_zewnetrzne = wyciagnij_linki_zewnetrzne(html_artykulu)
        print(" | ".join(linki_zewnetrzne))

        kategorie = wyciagnij_kategorie(html_artykulu)
        print(" | ".join(kategorie))

def glowna():
    nazwa_kategorii = input().strip()
    wyswietl_wyniki(nazwa_kategorii)


if __name__ == '__main__':
    glowna()

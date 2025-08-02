import os
import hashlib
import base64
from cryptography.fernet import Fernet
import webbrowser
import shutil

BAZA = "baza.txt"

def generuj_klucz(haslo_glowne):
    klucz = hashlib.sha256(haslo_glowne.encode()).digest()
    return base64.urlsafe_b64encode(klucz)

def zaszyfruj(tekst, klucz):
    f = Fernet(klucz)
    return f.encrypt(tekst.encode()).decode()

def odszyfruj(tekst_zaszyfrowany, klucz):
    f = Fernet(klucz)
    return f.decrypt(tekst_zaszyfrowany.encode()).decode()

def wczytaj_wpisy(klucz):
    wpisy = []
    if not os.path.exists(BAZA):
        return wpisy
    with open(BAZA, "r") as f:
        for i, linia in enumerate(f, 1):
            try:
                s, l, h, link = linia.strip().split(":")
                serwis = odszyfruj(s, klucz)
                login = odszyfruj(l, klucz)
                haslo = odszyfruj(h, klucz)
                link = odszyfruj(link, klucz)
                wpisy.append((serwis, login, haslo, link))
            except Exception:
                print(f"⚠️ Błąd odczytu linii {i}")
    return wpisy

def zapisz_wpisy(wpisy, klucz):
    with open(BAZA, "w") as f:
        for serwis, login, haslo, link in wpisy:
            linia = f"{zaszyfruj(serwis, klucz)}:{zaszyfruj(login, klucz)}:{zaszyfruj(haslo, klucz)}:{zaszyfruj(link, klucz)}\n"
            f.write(linia)

def dodaj_haslo(klucz):
    serwis = input("Serwis: ")
    login = input("Login: ")
    haslo = input("Hasło: ")
    link = input("Link (opcjonalnie): ")
    wpisy = wczytaj_wpisy(klucz)
    wpisy.append((serwis, login, haslo, link))
    zapisz_wpisy(wpisy, klucz)
    print("✅ Hasło dodane.")

def pokaz_hasla(klucz):
    wpisy = wczytaj_wpisy(klucz)
    if not wpisy:
        print("Brak zapisanych haseł.")
        return

    for idx, (serwis, login, haslo, link) in enumerate(wpisy, 1):
        print(f"{idx}. Serwis: {serwis} | Login: {login} | Hasło: {haslo} | Link: {link if link else '(brak)'}")

    # Otwieranie linków
    while True:
        odp = input("\nWpisz numer wpisu, aby otworzyć link, lub Enter aby wyjść: ").strip()
        if odp == "":
            break
        if odp.isdigit():
            num = int(odp)
            if 1 <= num <= len(wpisy):
                link = wpisy[num - 1][3]
                if link:
                    print(f"Otwarcie linku: {link}")
                    webbrowser.open(link)
                else:
                    print("Brak linku w tym wpisie.")
            else:
                print("Niepoprawny numer.")
        else:
            print("Wpisz numer lub Enter.")

def edytuj_haslo(klucz):
    wpisy = wczytaj_wpisy(klucz)
    if not wpisy:
        print("Brak wpisów do edycji.")
        return

    for idx, (serwis, login, haslo, link) in enumerate(wpisy, 1):
        print(f"{idx}. Serwis: {serwis} | Login: {login} | Hasło: {haslo} | Link: {link if link else '(brak)'}")

    num = input("Podaj numer wpisu do edycji: ").strip()
    if not num.isdigit() or not (1 <= int(num) <= len(wpisy)):
        print("Niepoprawny numer.")
        return
    idx = int(num) - 1

    serwis, login, haslo, link = wpisy[idx]
    print("Zostaw puste, aby nie zmieniać wartości.")

    nowy_serwis = input(f"Serwis [{serwis}]: ").strip()
    nowy_login = input(f"Login [{login}]: ").strip()
    nowe_haslo = input(f"Hasło [{haslo}]: ").strip()
    nowy_link = input(f"Link [{link}]: ").strip()

    wpisy[idx] = (
        nowy_serwis if nowy_serwis else serwis,
        nowy_login if nowy_login else login,
        nowe_haslo if nowe_haslo else haslo,
        nowy_link if nowy_link else link,
    )
    zapisz_wpisy(wpisy, klucz)
    print("✅ Wpis zaktualizowany.")

def eksportuj():
    if not os.path.exists(BAZA):
        print("Brak bazy do eksportu.")
        return
    dest = input("Podaj nazwę pliku eksportu (np. baza_backup.txt): ").strip()
    if not dest:
        print("Niepoprawna nazwa pliku.")
        return
    shutil.copy(BAZA, dest)
    print(f"✅ Eksport zapisany do {dest}")

def importuj():
    src = input("Podaj nazwę pliku do importu: ").strip()
    if not os.path.exists(src):
        print("Plik nie istnieje.")
        return
    with open(src, "r") as f_src, open(BAZA, "a") as f_dest:
        for linia in f_src:
            f_dest.write(linia)
    print(f"✅ Import z {src} zakończony.")

def main():
    haslo_glowne = input("Podaj hasło główne: ")
    klucz = generuj_klucz(haslo_glowne)

    while True:
        print("\nCo chcesz zrobić?")
        print("1 - Dodaj hasło")
        print("2 - Pokaż hasła")
        print("3 - Edytuj hasło")
        print("4 - Eksportuj bazę")
        print("5 - Importuj bazę")
        print("6 - Wyjdź")

        wybor = input("Wybierz opcję (1-6): ").strip()

        if wybor == "1":
            dodaj_haslo(klucz)
        elif wybor == "2":
            pokaz_hasla(klucz)
        elif wybor == "3":
            edytuj_haslo(klucz)
        elif wybor == "4":
            eksportuj()
        elif wybor == "5":
            importuj()
        elif wybor == "6":
            print("Do zobaczenia!")
            break
        else:
            print("Nieznana opcja.")

if __name__ == "__main__":
    main()

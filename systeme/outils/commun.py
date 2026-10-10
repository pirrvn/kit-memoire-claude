"""Fonctions communes aux outils du kit (bibliothèque standard de Python 3.9 uniquement)."""
import json
import os
import urllib.parse

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CONFIG = os.path.join(RACINE, "systeme", "config.json")
_config = None


def config():
    """Réglages de systeme/config.json (dictionnaire vide si le fichier manque ou est mal formé)."""
    global _config
    if _config is None:
        try:
            with open(CONFIG, encoding="utf-8") as f:
                _config = json.load(f)
        except (OSError, ValueError) as e:
            print("Attention : systeme/config.json illisible ({}) ; réglages par défaut.".format(e))
            _config = {}
    return _config


def rempli(valeur):
    """Vrai si un réglage a été rempli (ni vide, ni « À REMPLIR »)."""
    return bool(valeur) and "À REMPLIR" not in str(valeur)


def avec_contact(url):
    """Ajoute l'e-mail de contact aux requêtes OpenAlex et Crossref s'il est réglé (accès plus rapide et plus fiable)."""
    email = config().get("email_contact", "")
    if rempli(email) and ("api.openalex.org" in url or "api.crossref.org" in url) and "mailto=" not in url:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode({"mailto": email})
    return url

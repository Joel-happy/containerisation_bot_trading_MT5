# Gère la connexion à MT5

import MetaTrader5 as mt5
from config import ACCOUNTS

def connect_to_mt5(account_id):
    """Connecte à MetaTrader 5 en utilisant les identifiants du compte."""
    account_info = ACCOUNTS.get(account_id)
    if not account_info:
        raise KeyError(f"⚠️ Compte {account_id} introuvable dans la configuration.")

    if not mt5.initialize(login=account_id, password=account_info["password"], server=account_info["server"]):
        raise ConnectionError(f"Erreur de connexion à MT5 : {mt5.last_error()}")
    
    print(f"Connexion réussie au compte {account_id} sur le serveur {account_info['server']}.")

def disconnect_from_mt5():
    """Déconnecte de MetaTrader 5."""
    mt5.shutdown()
    print("Déconnexion de MT5.")



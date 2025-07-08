import MetaTrader5 as mt5
from mt5_connection import connect_to_mt5, disconnect_from_mt5
from mt5_trading import (
    place_buy_order, place_sell_order, 
    close_buy_order, close_sell_order, close_all_orders,
    get_price, get_balance, has_open_position,
    place_buy_limit, place_sell_limit
)
from mt5_data import get_candles
from config import ACCOUNT_ID, SYMBOL, VOLUME
import time

def display_menu():
    """Affiche le menu des options de trading."""
    print("\n" + "="*50)
    print("🚀 TRADING BOT - Menu Principal")
    print("="*50)
    print("1. 📊 Afficher le prix actuel")
    print("2. 💰 Afficher le solde")
    print("3. 🟢 Placer un ordre d'achat (BUY)")
    print("4. 🔴 Placer un ordre de vente (SELL)")
    print("5. 📈 Placer un ordre BUY LIMIT")
    print("6. 📉 Placer un ordre SELL LIMIT")
    print("7. ❌ Clôturer toutes les positions")
    print("8. 📋 Voir les positions ouvertes")
    print("9. 📜 Voir l'historique des bougies")
    print("0. 🚪 Quitter")
    print("="*50)

def show_positions():
    """Affiche les positions ouvertes."""
    positions = mt5.positions_get(symbol=SYMBOL)
    if not positions:
        print(f"🔍 Aucune position ouverte pour {SYMBOL}")
        return
    
    print(f"\n📋 Positions ouvertes pour {SYMBOL}:")
    print("-" * 60)
    for pos in positions:
        pos_type = "ACHAT" if pos.type == mt5.ORDER_TYPE_BUY else "VENTE"
        profit_color = "🟢" if pos.profit >= 0 else "🔴"
        print(f"Ticket: {pos.ticket} | Type: {pos_type} | Volume: {pos.volume}")
        print(f"Prix: {pos.price_open} | Profit: {profit_color} {pos.profit:.2f}")
        print(f"Commentaire: {pos.comment}")
        print("-" * 60)

def show_candles():
    """Affiche les dernières bougies."""
    print(f"\n📜 Dernières 10 bougies pour {SYMBOL}:")
    df = get_candles(SYMBOL, mt5.TIMEFRAME_M1, 10)
    if df is not None:
        print(df[['time', 'open', 'high', 'low', 'close']].to_string(index=False))
    else:
        print("❌ Impossible de récupérer les données")

def main():
    """Fonction principale du bot de trading."""
    try:
        # Connexion à MT5
        print("🔌 Connexion à MetaTrader 5...")
        connect_to_mt5(ACCOUNT_ID)
        
        # Vérification de la connexion
        if not mt5.terminal_info():
            print("❌ Échec de la connexion à MT5")
            return
        
        print("✅ Connexion réussie !")
        print(f"📊 Symbole configuré: {SYMBOL}")
        print(f"📦 Volume par ordre: {VOLUME}")
        
        # Boucle principale
        while True:
            try:
                display_menu()
                choice = input("Choisissez une option: ").strip()
                
                if choice == "0":
                    print("👋 Au revoir !")
                    break
                
                elif choice == "1":
                    bid, ask = get_price(SYMBOL)
                    if bid and ask:
                        print(f"💹 Prix actuel de {SYMBOL}:")
                        print(f"   BID: {bid}")
                        print(f"   ASK: {ask}")
                        print(f"   Spread: {ask - bid:.5f}")
                
                elif choice == "2":
                    balance = get_balance()
                    print(f"💰 Solde du compte: {balance:.2f}")
                
                elif choice == "3":
                    if has_open_position(SYMBOL, 'buy'):
                        print("⚠️ Position d'achat déjà ouverte")
                    else:
                        sl = input("Stop Loss (optionnel, Entrée pour ignorer): ").strip()
                        tp = input("Take Profit (optionnel, Entrée pour ignorer): ").strip()
                        
                        sl_value = float(sl) if sl else None
                        tp_value = float(tp) if tp else None
                        
                        result = place_buy_order(SYMBOL, sl_value, tp_value)
                        if result:
                            print("✅ Ordre d'achat traité")
                
                elif choice == "4":
                    if has_open_position(SYMBOL, 'sell'):
                        print("⚠️ Position de vente déjà ouverte")
                    else:
                        sl = input("Stop Loss (optionnel, Entrée pour ignorer): ").strip()
                        tp = input("Take Profit (optionnel, Entrée pour ignorer): ").strip()
                        
                        sl_value = float(sl) if sl else None
                        tp_value = float(tp) if tp else None
                        
                        result = place_sell_order(SYMBOL, sl_value, tp_value)
                        if result:
                            print("✅ Ordre de vente traité")
                
                elif choice == "5":
                    price = float(input("Prix pour BUY LIMIT: "))
                    sl_price = float(input("Stop Loss: "))
                    result = place_buy_limit(SYMBOL, price, sl_price)
                    print(result)
                
                elif choice == "6":
                    price = float(input("Prix pour SELL LIMIT: "))
                    sl_price = float(input("Stop Loss: "))
                    result = place_sell_limit(SYMBOL, price, sl_price)
                    print(result)
                
                elif choice == "7":
                    confirm = input("⚠️ Clôturer TOUTES les positions ? (oui/non): ").lower()
                    if confirm in ['oui', 'o', 'yes', 'y']:
                        close_all_orders(SYMBOL)
                        print("✅ Toutes les positions ont été clôturées")
                
                elif choice == "8":
                    show_positions()
                
                elif choice == "9":
                    show_candles()
                
                else:
                    print("❌ Option invalide")
                
                # Petite pause pour éviter de surcharger
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n🛑 Interruption détectée...")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
                print("Continuons...")
    
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
    
    finally:
        # Déconnexion propre
        print("🔌 Déconnexion de MT5...")
        disconnect_from_mt5()
        print("✅ Déconnexion terminée")

if __name__ == "__main__":
    main()
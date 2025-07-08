# Envoi et gestion des ordres

import MetaTrader5 as mt5
from config import VOLUME
import uuid
import time

import requests



def ensure_connection():
    """Vérifie si MT5 est connecté."""
    if not mt5.terminal_info():
        raise RuntimeError("MT5 n'est pas connecté. Veuillez vérifier votre connexion.")

def generate_order_code():
    """Génère un code unique pour chaque ordre."""
    return str(uuid.uuid4())[:8]

def place_buy_order(symbol , sl = None , tp = None):
    """Passe plusieurs ordres d'achat avec des volumes spécifiés."""
    ensure_connection()
    symbol_info_tick = mt5.symbol_info_tick(symbol)
    if symbol_info_tick is None:
        print(f"⚠️ Impossible d'obtenir les informations pour {symbol}")
        return None

    results = []
    
    order_code = generate_order_code()
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": VOLUME,
        "type": mt5.ORDER_TYPE_BUY,
        "price": symbol_info_tick.ask,
        "deviation": 10,
        "magic": 234000,
        "comment": f"order:{order_code}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    if sl is not None:
        request["sl"] = sl
    if tp is not None:
        request["tp"] = tp

    result = mt5.order_send(request)
    results.append({"result": result, "order_code": order_code, "volume": VOLUME})
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"💰 Achat effectué : volume {VOLUME}, code : {order_code}, prix: {result.price}")
    else:
        print(f"❗ Erreur pour l'achat avec volume {VOLUME} : {result.retcode}")

    return results

def close_buy_order(symbol, order_code):
    """Clôture une position d'achat spécifique par son code d'ordre."""
    ensure_connection()
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        print(f"🔍 Aucune position d'achat ouverte pour {symbol}")
        return

    for pos in positions:
        if pos.type == mt5.ORDER_TYPE_BUY and f"order:{order_code}" in pos.comment:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": pos.volume,
                "type": mt5.ORDER_TYPE_SELL,
                "position": pos.ticket,
                "price": mt5.symbol_info_tick(symbol).bid,
                "deviation": 10,
                "magic": 234000,
                "comment": "Clôture d'achat",
            }
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ Position d'achat clôturée : volume {pos.volume}, code : {order_code}")
            else:
                print(f"❗ Erreur lors de la clôture : {result.retcode}")

def place_sell_order(symbol, sl = None , tp = None):
    """Passe plusieurs ordres de vente avec des volumes spécifiés."""
    ensure_connection()
    symbol_info_tick = mt5.symbol_info_tick(symbol)
    if symbol_info_tick is None:
        raise ValueError(f"⚠️ Impossible d'obtenir les informations pour {symbol}")

    results = []
    
    order_code = generate_order_code()
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": VOLUME,
        "type": mt5.ORDER_TYPE_SELL,
        "price": symbol_info_tick.bid,
        "deviation": 10,
        "magic": 234000,
        "comment": f"order:{order_code}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    if sl is not None:
        request["sl"] = sl
    if tp is not None:
        request["tp"] = tp
        

    result = mt5.order_send(request)
    results.append({"result": result, "order_code": order_code, "volume": VOLUME})
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"💰 Vente effectuée : volume {VOLUME}, code : {order_code}, prix: {result.price}")
    else:
        print(f"❗ Erreur pour la vente avec volume {VOLUME} : {result.retcode}")

    return results

def close_buy_order(symbol, order_code):
    """Clôture une position d'achat spécifique par son code d'ordre."""
    ensure_connection()
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        print(f"🔍 Aucune position d'achat ouverte pour {symbol}")
        return

    for pos in positions:
        if pos.type == mt5.ORDER_TYPE_BUY and f"order:{order_code}" in pos.comment:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": pos.volume,
                "type": mt5.ORDER_TYPE_SELL,
                "position": pos.ticket,
                "price": mt5.symbol_info_tick(symbol).bid,
                "deviation": 10,
                "magic": 234000,
                "comment": "Clôture d'achat",
            }
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ Position d'achat clôturée : volume {pos.volume}, code : {order_code}")
            else:
                print(f"❗ Erreur lors de la clôture : {result.retcode}")

def close_sell_order(symbol, order_code):
    """Clôture une position de vente spécifique par son code d'ordre."""
    ensure_connection()
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        print(f"🔍 Aucune position de vente ouverte pour {symbol}")
        return

    for pos in positions:
        if pos.type == mt5.ORDER_TYPE_SELL and f"order:{order_code}" in pos.comment:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": pos.volume,
                "type": mt5.ORDER_TYPE_BUY,
                "position": pos.ticket,
                "price": mt5.symbol_info_tick(symbol).ask,
                "deviation": 10,
                "magic": 234000,
                "comment": "Clôture de vente",
            }
            result = mt5.order_send(request)
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ Position de vente clôturée : volume {pos.volume}, code : {order_code}")
            else:
                print(f"❗ Erreur lors de la clôture : {result.retcode}")

def close_all_orders(symbol):
    """Clôture toutes les positions (achat/vente) pour un symbole donné sans se baser sur un commentaire spécifique."""
    ensure_connection()
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        print(f"🔍 Aucune position ouverte pour {symbol}")
        return

    print(f"🔍 {len(positions)} positions ouvertes pour {symbol}")
    for pos in positions:
        if pos.type == mt5.ORDER_TYPE_BUY:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": pos.volume,
                "type": mt5.ORDER_TYPE_SELL,
                "position": pos.ticket,
                "price": mt5.symbol_info_tick(symbol).bid,
                "deviation": 10,
                "magic": 234000,
                "comment": "Clôture totale d'achat",
            }
        elif pos.type == mt5.ORDER_TYPE_SELL:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": pos.volume,
                "type": mt5.ORDER_TYPE_BUY,
                "position": pos.ticket,
                "price": mt5.symbol_info_tick(symbol).ask,
                "deviation": 10,
                "magic": 234000,
                "comment": "Clôture totale de vente",
            }
        else:
            continue

        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"✅ Position clôturée : ticket {pos.ticket}, volume {pos.volume}")
        else:
            print(f"❗ Erreur lors de la clôture : ticket {pos.ticket}, code {result.retcode}")




def get_price(symbol):
    """Obtient le prix actuel d'un symbole."""
    ensure_connection()
    time.sleep(0.6)
    # current_bid = price["bid"]
    # current_ask = price["ask"]
    symbol_info_tick = mt5.symbol_info_tick(symbol)
    if symbol_info_tick is None:
        print(f"⚠️ Impossible d'obtenir les informations pour {symbol}")
        return None
    return symbol_info_tick.bid , symbol_info_tick.ask

def order_exists(level , SYMBOL):
    ensure_connection()
    orders = mt5.orders_get()
    if orders:
        for order in orders:
            if order.symbol == SYMBOL and abs(order.price - level) < 0.01:
                return True
    return False

# Placer un ordre limite avec SL
def place_buy_limit(symbol, price, sl_price):
    if order_exists(price , symbol):
        return "Ordre BUY LIMIT déjà existant pour le niveau {price}"
    ensure_connection()
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": VOLUME,
        "type": mt5.ORDER_TYPE_BUY_LIMIT,
        "price": price,
        "sl": sl_price,
        "deviation": 10,
        "magic": 123456,
        "comment": "Buy Limit with SL",
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return "Erreur lors de l'ordre BUY LIMIT : {result.retcode}"
    else:
        return "Ordre BUY LIMIT placé à {price} avec SL à {sl_price}"

def place_sell_limit(symbol, price, sl_price):
    if order_exists(price , symbol):
        return
    ensure_connection()
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": VOLUME,
        "type": mt5.ORDER_TYPE_SELL_LIMIT,
        "price": price,
        "sl": sl_price,
        "deviation": 10,
        "magic": 123456,
        "comment": "Sell Limit with SL",
    }
    result = mt5.order_send(request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return "Erreur lors de l'ordre SELL LIMIT : {result.retcode}"
    else:
        return "Ordre SELL LIMIT placé à {price} avec SL à {sl_price}"
    


def get_balance():
    """Obtient le solde actuel du compte."""
    ensure_connection()
    account_info = mt5.account_info()
    return account_info.balance

def has_open_position(symbol, direction):
    """
    Vérifie s'il existe déjà une position ouverte sur le symbole dans la direction donnée.
    direction: 'buy' ou 'sell'
    """
    import MetaTrader5 as mt5
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        return False
    for pos in positions:
        if direction == 'buy' and pos.type == mt5.ORDER_TYPE_BUY:
            return True
        if direction == 'sell' and pos.type == mt5.ORDER_TYPE_SELL:
            return True
    return False
import logging
import os
import sys
import traceback

MINUTEFRAME = 1
MAX_POS = 10

sys.path.append("./live_tools")
import ta
from utilities.perp_bitget import PerpBitget
from datetime import datetime
import json
import pandas as pd

data_directory = "./data"
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

now = datetime.now()
current_time = now.strftime("%d/%m/%Y %H:%M:%S")
print("--- Start Execution Time :", current_time, "---")
#
# f = open(
#     "../../secret.json",
# )
f = open(
    "./live_tools/secret.json",
)

# Ajustez le chemin si nécessaire
secret = json.load(f)
f.close()

account_to_select = "bitget_exemple"
production = True
timeframe = "1m"
type = ["long"]  # Spécifiez "short" si vous voulez également prendre des positions courtes
leverage = 5
max_var = 5
max_side_exposition = 1.55

margin_mode = "fixed"  # fixed or crossed
exchange_leverage = 5

params_coin = {

    "AAVE/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,  # Tolérance pour la pente de la MA 20
        "bb_width_tolerance": 5.0,  # Tolérance pour la largeur des BB en %
        "rsi_threshold": 50,  # Seuil RSI pour l'entrée en position
        "rsi_exit_threshold": 70,  # Seuil RSI pour la sortie de position
        "macd_exit": True,  # Activation de la sortie basée sur le MACD
        "trailing_stop_percentage": 2.0  # Pourcentage pour le trailing stop-loss
    },
    "LDO/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "KAS/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "SOL/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "BGB/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "AVAX/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "DOGE/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },

    "FLOKI/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "PYTH/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "PEPE/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "SUI/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "NEAR/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "ICP/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "POL/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "XRP/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "APE/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "EOS/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "GALA/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "ETH/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "UXLINK/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "POPCAT/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "1000BONK/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    "1000000MOG/USDT:USDT": {
        "wallet_exposure": 0.1,
        "bb_window": 50,
        "bb_std": 2,
        "long_ma_window": 98,
        "ma_slope_tolerance": 0.05,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 2.0
    },
    # Ajoutez d'autres actifs avec les mêmes paramètres
}


def open_long(row, pair):
    params = params_coin[pair]
    ma_slope_tolerance = params["ma_slope_tolerance"]
    bb_width_tolerance = params["bb_width_tolerance"]
    rsi_threshold = params["rsi_threshold"]



    if (
            row['n1_close'] < row['n1_higher_band']
            and row['close'] > row['long_ma']
            and row['close'] > row['higher_band']
            and row['close'] > row['long_ma']
            and abs(row['ma_20_slope_pct']) < ma_slope_tolerance
            and row['bb_width_pct'] < bb_width_tolerance
            and row['rsi'] > rsi_threshold
    ):
        print(
            f"Check open_long for {pair}: long_ma={row['long_ma']}, close={row['close']}, "
            f"n1_close={row['n1_close']}, higher_band={row['higher_band']}, "
            f"n1_higher_band={row['n1_higher_band']}, ma_band={row['ma_band']}, "
            f"ma_20_slope_pct={row['ma_20_slope_pct']}, bb_width_pct={row['bb_width_pct']}, rsi={row['rsi']}"
            f"long_ma={row['long_ma']}"
        )
        print(f"Open long on {pair}")
        return True
    else:
        print(f"Skip long on {pair}")
        return False


def close_long(row, position, pair, df):
    params = params_coin[pair]
    rsi_exit_threshold = params.get('rsi_exit_threshold', 70)
    macd_exit = params.get('macd_exit', True)
    trailing_stop_percentage = params.get('trailing_stop_percentage', 2.0)

    # Mise à jour du plus haut atteint pour le trailing stop-loss en se basant sur l'historique
    open_time = position.get('open_time')
    df_since_open = df[df.index >= open_time]
    highest_price = df_since_open['high'].max()
    position['highest_price'] = highest_price
    trailing_stop_price = highest_price * (1 - trailing_stop_percentage / 100)


    # Conditions de sortie
    condition1 = row['close'] < row['ma_band']
    condition2 = row['rsi'] > rsi_exit_threshold
    condition3 = macd_exit and (row['macd'] < row['macd_signal'])
    condition4 = row['close'] <= trailing_stop_price

    if condition1 or condition2 or condition3 or condition4:
        print(f"Close long on {pair}")

        conditions_met = []
        if condition1:
            conditions_met.append("Close below MA Band")
        if condition2:
            conditions_met.append(f"RSI above {rsi_exit_threshold}")
        if condition3:
            conditions_met.append("MACD crossover down")
        if condition4:
            conditions_met.append("Trailing stop-loss hit")
        print(f"Close long on {pair} due to: {', '.join(conditions_met)}")

        return True
    else:
        return False


print(f"--- Bollinger Trend on {len(params_coin)} tokens {timeframe} Leverage x{leverage} ---")

bitget = PerpBitget(
    apiKey=secret[account_to_select]["apiKey"],
    secret=secret[account_to_select]["secret"],
    password=secret[account_to_select]["password"],
)

# Récupération des données
df_list = {}

for pair in params_coin:
    filename = f"{data_directory}/{pair.replace('/', '_').replace(':', '_')}_{timeframe}.csv"

    # Vérifier si le fichier de données existe
    if os.path.isfile(filename):
        # Charger les données existantes depuis le fichier
        df_existing = pd.read_csv(filename, index_col='timestamp', parse_dates=True)

        # Récupérer le dernier timestamp dans les données existantes
        # last_timestamp = df_existing.index[-1]

        # Calculer le nombre de nouvelles bougies à récupérer
        # Supposons que le timeframe est en minutes, vous pouvez ajuster en fonction
        # time_diff = datetime.utcnow() - last_timestamp
        # minutes_diff = int(time_diff.total_seconds() / 60)
        # limit = max(1, minutes_diff)

        # Récupérer les nouvelles données manquantes
        new_data = bitget.get_more_last_historical_async(pair, timeframe, 10, MINUTEFRAME)

        # Fusionner les nouvelles données avec les données existantes
        df_new = new_data.copy()
        df_new = df_new[~df_new.index.isin(df_existing.index)]  # Éviter les doublons
        df_pair = pd.concat([df_existing, df_new])

        # Limiter le DataFrame aux 1000 dernières lignes
        df_pair = df_pair.tail(1000)

        # Sauvegarder le DataFrame mis à jour dans le fichier
        df_pair.to_csv(filename, index=True)

        # Ajouter le DataFrame au dictionnaire
        df_list[pair] = df_pair
    else:
        # Le fichier n'existe pas, récupérer les données initiales (par exemple, 1000 bougies)
        initial_data = bitget.get_more_last_historical_async(pair, timeframe, 100, MINUTEFRAME)
        df_pair = initial_data.copy()

        # Sauvegarder le DataFrame dans le fichier
        df_pair.to_csv(filename, index=True)

        # Ajouter le DataFrame au dictionnaire
        df_list[pair] = df_pair

print("Data OHLCV loaded 100%")


def setExchangeLeverage(pair):
    try:
        print(f"Setting {margin_mode} x{exchange_leverage} on {pair} pair...")
        bitget.set_margin_mode_and_leverage(
            pair, margin_mode, exchange_leverage
        )
    except Exception as e:
        print(e)


for pair in df_list:
    df = df_list[pair]
    params = params_coin[pair]
    bol_band = ta.volatility.BollingerBands(close=df["close"], window=params["bb_window"], window_dev=params["bb_std"])
    df["lower_band"] = bol_band.bollinger_lband()
    df["higher_band"] = bol_band.bollinger_hband()
    df["ma_band"] = bol_band.bollinger_mavg()
    df['long_ma'] = ta.trend.sma_indicator(close=df['close'], window=params["long_ma_window"])
    df["n1_close"] = df["close"].shift(1)
    df["n1_lower_band"] = df["lower_band"].shift(1)
    df["n1_higher_band"] = df["higher_band"].shift(1)
    df['iloc'] = range(len(df))

    # Calcul de la MA 20 et de sa pente en pourcentage
    df['ma_20'] = ta.trend.sma_indicator(close=df['close'], window=20)
    df['ma_20_slope_pct'] = df['ma_20'].pct_change() * 100

    # Calcul de la largeur des BB en pourcentage
    df['bb_width'] = df['higher_band'] - df['lower_band']
    df['bb_width_pct'] = (df['bb_width'] / df['ma_band']) * 100

    # Calcul du RSI
    df['rsi'] = ta.momentum.rsi(close=df['close'], window=14)

    # Calcul du MACD
    macd = ta.trend.MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()

print("Indicators loaded 100%")

usd_balance = float(bitget.get_usdt_equity())
print("USD balance :", round(usd_balance, 2), "$")

positions_data = bitget.get_open_position()
position_list = [
    {
        "pair": d["symbol"],
        "side": d["side"],
        "size": float(d["contracts"]) * float(d["contractSize"]),
        "market_price": d["info"]["marketPrice"],
        "usd_size": float(d["contracts"]) * float(d["contractSize"]) * float(d["info"]["marketPrice"]),
        "open_price": d["entryPrice"],
        "highest_price": float(d["entryPrice"]),  # Initialisation du highest_price
        "open_time": df_list[d["symbol"]].iloc[-1].name  # En supposant que la position vient d'être ouverte
    }
    for d in positions_data if d["symbol"] in df_list
]

positions = {}
for pos in position_list:
    positions[pos["pair"]] = {
        "side": pos["side"],
        "size": pos["size"],
        "market_price": pos["market_price"],
        "usd_size": pos["usd_size"],
        "open_price": pos["open_price"],
        "highest_price": pos["highest_price"],
        "open_time": pos["open_time"]
    }

print(f"{len(positions)} active positions ({list(positions.keys())})")

# Vérification des positions à fermer
positions_to_delete = []

for pair in positions:
    df = df_list[pair]
    row = df.iloc[-2]
    last_price = float(df.iloc[-1]["close"])
    position = positions[pair]

    if position["side"] == "long":
        if close_long(row, position, pair, df):
            close_long_market_price = last_price
            close_long_quantity = float(
                bitget.convert_amount_to_precision(pair, position["size"])
            )
            exchange_close_long_quantity = close_long_quantity * close_long_market_price
            print(
                f"Place Close Long Market Order: {close_long_quantity} {pair[:-5]} at the price of {close_long_market_price}$ ~{round(exchange_close_long_quantity, 2)}$"
            )

            if production:
                setExchangeLeverage(pair)
                bitget.place_market_order(pair, "sell", close_long_quantity, reduce=True)
                positions_to_delete.append(pair)
        else:
            # Mise à jour du plus haut prix atteint
            positions[pair]['highest_price'] = position['highest_price']

for pair in positions_to_delete:
    del positions[pair]

# Vérification de l'exposition actuelle
positions_exposition = {}
long_exposition = 0
short_exposition = 0
for pair in df_list:
    positions_exposition[pair] = {"long": 0, "short": 0}

positions_data = bitget.get_open_position()
for pos in positions_data:
    if pos["symbol"] in df_list and pos["side"] == "long":
        pct_exposition = (float(pos["contracts"]) * float(pos["contractSize"]) * float(
            pos["info"]["marketPrice"])) / usd_balance
        positions_exposition[pos["symbol"]]["long"] += pct_exposition
        long_exposition += pct_exposition
    elif pos["symbol"] in df_list and pos["side"] == "short":
        pct_exposition = (float(pos["contracts"]) * float(pos["contractSize"]) * float(
            pos["info"]["marketPrice"])) / usd_balance
        positions_exposition[pos["symbol"]]["short"] += pct_exposition
        short_exposition += pct_exposition

pct_sizing = 1 / MAX_POS

if len(positions) < MAX_POS:
    for pair in df_list:
        if pair not in positions:
            try:
                df = df_list[pair]
                row = df.iloc[-2]
                last_price = float(df.iloc[-1]["close"])
                if open_long(row, pair) and "long" in type:
                    long_market_price = last_price
                    long_quantity_in_usd = usd_balance * pct_sizing * leverage
                    long_quantity = float(bitget.convert_amount_to_precision(pair, float(
                        bitget.convert_amount_to_precision(pair, long_quantity_in_usd / long_market_price)
                    )))
                    exchange_long_quantity = long_quantity * long_market_price
                    print(
                        f"Place Open Long Market Order: {long_quantity} {pair[:-5]} at the price of {long_market_price}$ ~{round(exchange_long_quantity, 2)}$"
                    )
                    if production:
                        setExchangeLeverage(pair)
                        bitget.place_market_order(pair, "buy", long_quantity, reduce=False)
                        positions_exposition[pair]["long"] += (long_quantity_in_usd / usd_balance)
                        long_exposition += (long_quantity_in_usd / usd_balance)
                        # Initialiser le plus haut prix atteint et l'horodatage d'ouverture
                        positions[pair] = {
                            "side": "long",
                            "size": long_quantity,
                            "market_price": long_market_price,
                            "usd_size": exchange_long_quantity,
                            "open_price": long_market_price,
                            "highest_price": long_market_price,
                            "open_time": df.iloc[-1].name  # Horodatage d'ouverture
                        }
                # Ajoutez la gestion des positions courtes si nécessaire
            except Exception as e:
                print(traceback.format_exc())
                print(f"Error on {pair} ({e}), skip {pair}")
else:
    print(f"{len(positions)} positions already opened")

now = datetime.now()
current_time = now.strftime("%d/%m/%Y %H:%M:%S")
print("--- End Execution Time :", current_time, "---")

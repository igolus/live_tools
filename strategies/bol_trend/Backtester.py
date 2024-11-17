import pandas as pd
import numpy as np
import ccxt
import ta
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from tabulate import tabulate


class Backtester:
    def __init__(self, params_coin, timeframe='1m', start_date=None, end_date=None, leverage=1, taker_fee=0.0006):
        self.params_coin = params_coin
        self.timeframe = timeframe
        self.start_date = start_date
        self.end_date = end_date
        self.leverage = leverage  # Levier
        self.taker_fee = taker_fee  # Frais de taker
        self.exchange = ccxt.binance()  # Vous pouvez changer d'échange si nécessaire
        self.data = {}
        self.results = {}
        self.initial_balance = 1000  # Capital initial en USDT
        self.balance = self.initial_balance
        self.total_fees = 0  # Total des frais payés

    def fetch_data(self):
        print("Fetching historical data...")
        for pair in self.params_coin:
            symbol = pair.replace(':', '')
            data = []
            since = self.exchange.parse8601(self.start_date.isoformat())
            end_timestamp = self.exchange.parse8601(self.end_date.isoformat())
            while since < end_timestamp:
                try:
                    ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=self.timeframe, since=since, limit=1000)
                    if not ohlcv:
                        break
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    since = ohlcv[-1][0] + 1
                    data.append(df)
                except Exception as e:
                    print(f"Error fetching data for {pair}: {e}")
                    break
            if data:
                df_pair = pd.concat(data)
                df_pair['timestamp'] = pd.to_datetime(df_pair['timestamp'], unit='ms')
                df_pair.set_index('timestamp', inplace=True)
                self.data[pair] = df_pair
            else:
                print(f"No data fetched for {pair}")

    def calculate_indicators(self):
        print("Calculating indicators...")
        for pair in self.data:
            df = self.data[pair]
            params = self.params_coin[pair]

            # Bandes de Bollinger
            bol_band = ta.volatility.BollingerBands(close=df["close"], window=params["bb_window"], window_dev=params["bb_std"])
            df["lower_band"] = bol_band.bollinger_lband()
            df["higher_band"] = bol_band.bollinger_hband()
            df["ma_band"] = bol_band.bollinger_mavg()

            # EMA 20 et sa pente
            df['ema_20'] = ta.trend.ema_indicator(close=df['close'], window=20)
            df['ema_20_slope_pct'] = df['ema_20'].pct_change() * 100

            # EMA à long terme
            df['long_ema'] = ta.trend.ema_indicator(close=df['close'], window=params["long_ma_window"])
            df['long_ma'] = ta.trend.sma_indicator(close=df['close'], window=params["long_ma_window"])

            # Décalage des valeurs pour la condition sur n-1
            df["n1_close"] = df["close"].shift(1)
            df["n1_higher_band"] = df["higher_band"].shift(1)

            # Calcul du RSI
            df['rsi'] = ta.momentum.rsi(close=df['close'], window=14)

            # Calcul du MACD
            macd = ta.trend.MACD(close=df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()

            # Calcul de la largeur des Bandes de Bollinger en pourcentage
            df['bb_width'] = df['higher_band'] - df['lower_band']
            df['bb_width_pct'] = (df['bb_width'] / df['ma_band']) * 100

            # Calcul de la moyenne mobile du volume
            df['volume_mean'] = df['volume'].rolling(window=20).mean()

            # Supprimer les lignes avec des valeurs manquantes
            df.dropna(inplace=True)

            # Enregistrer les données avec les indicateurs
            self.data[pair] = df

    def open_long(self, row, params):
        ema_slope_tolerance = params["ema_slope_tolerance"]
        bb_width_tolerance = params["bb_width_tolerance"]
        rsi_threshold = params["rsi_threshold"]

        if (row['n1_close'] < row['n1_higher_band']
                and row['volume'] > row['volume_mean']
                # and row['close'] > row['ema_20']
                and row['close'] > row['higher_band']
                and row['close'] > row['long_ma']
                # and row['ema_20_slope_pct'] > -ema_slope_tolerance
                # and row['bb_width_pct'] < bb_width_tolerance
                and row['rsi'] > rsi_threshold
        ):
            return True
        else:
            return False

    def close_long(self, row, position, params):
        rsi_exit_threshold = params.get('rsi_exit_threshold', 70)
        macd_exit = params.get('macd_exit', True)
        trailing_stop_percentage = params.get('trailing_stop_percentage', 2.0)

        # Mise à jour du plus haut atteint pour le trailing stop-loss
        highest_price = max(position['highest_price'], row['high'])
        position['highest_price'] = highest_price
        trailing_stop_price = highest_price * (1 - trailing_stop_percentage / 100)

        condition1 = row['close'] < row['ma_band']
        condition2 = row['rsi'] > rsi_exit_threshold
        condition3 = macd_exit and (row['macd'] < row['macd_signal'])
        condition4 = row['close'] <= trailing_stop_price

        if condition1 or condition2 or condition3 or condition4:
            return True
        else:
            return False

    def run_backtest(self):
        print("Running backtest...")
        self.positions = {}
        self.trades = []
        for pair in self.data:
            df = self.data[pair]
            params = self.params_coin[pair]
            wallet_exposure = params["wallet_exposure"]
            position = None

            for index, row in df.iterrows():
                # Vérifier si une position est ouverte
                if position is None:
                    # Vérifier les conditions d'ouverture
                    if self.open_long(row, params):
                        # Ouvrir une position
                        position_size_usd = self.balance * wallet_exposure * self.leverage  # Appliquer le levier
                        required_margin = position_size_usd / self.leverage  # Marge nécessaire
                        # Calcul des frais d'ouverture
                        opening_fee = position_size_usd * self.taker_fee
                        total_cost = required_margin + opening_fee
                        if total_cost > self.balance:
                            print(f"Insufficient balance to open position on {pair}")
                            continue
                        position_size = position_size_usd / row['close']
                        position = {
                            'entry_price': row['close'],
                            'entry_time': index,
                            'size': position_size,
                            'highest_price': row['high']
                        }
                        # Calcul du prix de liquidation
                        position['liquidation_price'] = position['entry_price'] * (1 - 1 / self.leverage)
                        self.balance -= total_cost  # Déduire la marge et les frais du solde
                        self.total_fees += opening_fee
                        print(f"Opened position on {pair} at {index} price {row['close']} with leverage {self.leverage}")
                else:
                    # Vérifier si la position est liquidée
                    if row['low'] <= position['liquidation_price']:
                        # La position est liquidée
                        required_margin = position['size'] * position['entry_price'] / self.leverage
                        pnl = -required_margin  # Perte égale à la marge initiale
                        self.total_fees += 0  # Pas de frais supplémentaires en cas de liquidation (ou ajouter si applicable)
                        self.trades.append({
                            'pair': pair,
                            'entry_time': position['entry_time'],
                            'exit_time': index,
                            'entry_price': position['entry_price'],
                            'exit_price': position['liquidation_price'],
                            'pnl': pnl,
                            'result': 'Liquidation'
                        })
                        print(f"Position liquidée sur {pair} à {index} au prix {position['liquidation_price']} PnL: {pnl:.2f} USDT")
                        position = None
                        continue  # Passer à la prochaine itération

                    # Vérifier les conditions de clôture
                    if self.close_long(row, position, params):
                        # Fermer la position
                        exit_price = row['close']
                        required_margin = position['size'] * position['entry_price'] / self.leverage
                        # Calcul des frais de clôture
                        closing_fee = (position['size'] * exit_price * self.leverage) * self.taker_fee
                        price_difference = (exit_price - position['entry_price'])
                        gross_pnl = price_difference * position['size'] * self.leverage  # PnL brut avant frais
                        pnl = gross_pnl - closing_fee  # PnL net après frais de clôture
                        self.balance += required_margin  # Récupérer la marge initiale
                        self.balance += pnl  # Ajouter le profit ou la perte net(te)
                        self.total_fees += closing_fee
                        # Déterminer si le trade est gagnant ou perdant
                        if pnl > 0:
                            trade_result = "Gagnant"
                        else:
                            trade_result = "Perdant"
                        self.trades.append({
                            'pair': pair,
                            'entry_time': position['entry_time'],
                            'exit_time': index,
                            'entry_price': position['entry_price'],
                            'exit_price': exit_price,
                            'pnl': pnl,
                            'result': trade_result  # Ajouter le résultat du trade
                        })
                        print(f"Closed {trade_result} position on {pair} at {index} price {row['close']} PnL: {pnl:.2f} USDT")
                        position = None  # Réinitialiser la position

            # Si une position est encore ouverte à la fin des données
            if position is not None:
                exit_price = df.iloc[-1]['close']
                required_margin = position['size'] * position['entry_price'] / self.leverage
                # Vérifier si la position est liquidée
                if df.iloc[-1]['low'] <= position['liquidation_price']:
                    # La position est liquidée
                    pnl = -required_margin  # Perte égale à la marge initiale
                    self.total_fees += 0  # Pas de frais supplémentaires en cas de liquidation (ou ajouter si applicable)
                    self.trades.append({
                        'pair': pair,
                        'entry_time': position['entry_time'],
                        'exit_time': df.iloc[-1].name,
                        'entry_price': position['entry_price'],
                        'exit_price': position['liquidation_price'],
                        'pnl': pnl,
                        'result': 'Liquidation'
                    })
                    print(f"Position liquidée sur {pair} à {df.iloc[-1].name} au prix {position['liquidation_price']} PnL: {pnl:.2f} USDT")
                else:
                    # Fermer la position normalement
                    # Calcul des frais de clôture
                    closing_fee = (position['size'] * exit_price * self.leverage) * self.taker_fee
                    price_difference = (exit_price - position['entry_price'])
                    gross_pnl = price_difference * position['size'] * self.leverage  # PnL brut avant frais
                    pnl = gross_pnl - closing_fee  # PnL net après frais de clôture
                    self.balance += required_margin  # Récupérer la marge initiale
                    self.balance += pnl  # Ajouter le profit ou la perte net(te)
                    self.total_fees += closing_fee
                    # Déterminer si le trade est gagnant ou perdant
                    if pnl > 0:
                        trade_result = "Gagnant"
                    else:
                        trade_result = "Perdant"
                    self.trades.append({
                        'pair': pair,
                        'entry_time': position['entry_time'],
                        'exit_time': df.iloc[-1].name,
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'pnl': pnl,
                        'result': trade_result  # Ajouter le résultat du trade
                    })
                    print(f"Closed remaining {trade_result} position on {pair} at {df.iloc[-1].name} price {exit_price} PnL: {pnl:.2f} USDT")
                position = None  # Réinitialiser la position

        self.final_balance = self.balance
        self.results = {
            'initial_balance': self.initial_balance,
            'final_balance': self.final_balance,
            'profit': self.final_balance - self.initial_balance,
            'trades': self.trades
        }

    def calculate_hold_profit(self):
        self.hold_profits = {}
        for pair in self.data:
            df = self.data[pair]
            start_price = df.iloc[0]['close']
            end_price = df.iloc[-1]['close']
            price_change = (end_price - start_price) / start_price * 100
            self.hold_profits[pair] = price_change
            print(f"Hold profit for {pair}: {price_change:.2f}%")

    def print_results(self):
        print("\nBacktest Results:")
        print(f"Initial Balance: {self.initial_balance:.2f} USDT")
        print(f"Final Balance: {self.final_balance:.2f} USDT")
        net_profit = self.final_balance - self.initial_balance
        profit_percentage = net_profit / self.initial_balance * 100
        print(f"Net Profit: {net_profit:.2f} USDT ({profit_percentage:.2f}%)")
        print(f"Total Fees Paid: {self.total_fees:.2f} USDT")
        print(f"Total Trades: {len(self.trades)}")

        wins = [t for t in self.trades if t['result'] == 'Gagnant']
        losses = [t for t in self.trades if t['result'] == 'Perdant']
        liquidations = [t for t in self.trades if t['result'] == 'Liquidation']
        total_win_pnl = sum(t['pnl'] for t in wins)
        total_loss_pnl = sum(t['pnl'] for t in losses)
        total_liq_pnl = sum(t['pnl'] for t in liquidations)

        print(f"Winning Trades: {len(wins)}")
        print(f"Losing Trades: {len(losses)}")
        print(f"Liquidated Trades: {len(liquidations)}")
        print(f"Total Winning PnL: {total_win_pnl:.2f} USDT")
        print(f"Total Losing PnL: {total_loss_pnl:.2f} USDT")
        print(f"Total Liquidation PnL: {total_liq_pnl:.2f} USDT")
        if len(self.trades) > 0:
            win_rate = len(wins) / len(self.trades) * 100
            print(f"Win Rate: {win_rate:.2f}%")
        else:
            win_rate = 0
            print("No trades executed.")

        # Afficher les profits du holding
        print("\nHold Profits:")
        for pair in self.hold_profits:
            print(f"{pair}: {self.hold_profits[pair]:.2f}%")

        # Comparaison globale
        avg_hold_profit = sum(self.hold_profits.values()) / len(self.hold_profits)
        print(f"\nAverage Hold Profit: {avg_hold_profit:.2f}%")
        print(f"Strategy Profit: {profit_percentage:.2f}%")


        table = [
            ["Initial Balance", f"{self.initial_balance:.2f} USDT"],
            ["Final Balance", f"{self.final_balance:.2f} USDT"],
            ["Net Profit", f"{net_profit:.2f} USDT ({profit_percentage:.2f}%)"],
            ["Total Fees Paid", f"{self.total_fees:.2f} USDT"],
            ["Total Trades", f"{len(self.trades)}"],
            ["Winning Trades", f"{len(wins)}"],
            ["Losing Trades", f"{len(losses)}"],
            ["Liquidated Trades", f"{len(liquidations)}"],
            ["Total Winning PnL", f"{total_win_pnl:.2f} USDT"],
            ["Total Losing PnL", f"{total_loss_pnl:.2f} USDT"],
            ["Total Liquidation PnL", f"{total_liq_pnl:.2f} USDT"],
            ["Win Rate", f"{win_rate:.2f}%"],
            # ["Max Drawdown", f"{self.max_drawdown:.2f}%"],
            ["Average Hold Profit", f"{avg_hold_profit:.2f}%"],
            ["Strategy Profit", f"{profit_percentage:.2f}%"]
        ]

        # Affichage du tableau
        print("\nBacktest Results:")
        print(tabulate(table, headers=["Metric", "Value"], tablefmt="grid"))

    def plot_equity_curve(self):
        equity = [self.initial_balance]
        for trade in self.trades:
            equity.append(equity[-1] + trade['pnl'])
        plt.plot(equity)
        plt.title('Equity Curve')
        plt.xlabel('Trades')
        plt.ylabel('Balance (USDT)')
        plt.show()

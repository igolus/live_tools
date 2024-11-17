from datetime import datetime, timedelta

from strategies.bol_trend.Backtester import Backtester

params_coin = {
    "SOL/USDT": {
        "wallet_exposure": 0.99,
        "bb_window": 50,
        "bb_std": 2.25,
        "long_ma_window": 100,
        "ema_slope_tolerance": 0.0,
        "bb_width_tolerance": 5.0,
        "rsi_threshold": 50,
        "rsi_exit_threshold": 70,
        "macd_exit": True,
        "trailing_stop_percentage": 100
    },
    # Ajoutez d'autres paires si nécessaire
}

start_date = datetime.now() - timedelta(days=120)  # 4 mois (~30 jours par mois)
end_date = datetime.now()

backtester = Backtester(
    params_coin=params_coin,
    timeframe='1h',
    start_date=start_date,
    end_date=end_date,
    leverage=4,
    taker_fee=0.0006  # Frais de taker de 0.06%
)
backtester.fetch_data()
backtester.calculate_indicators()
backtester.run_backtest()
backtester.calculate_hold_profit()
backtester.print_results()
backtester.plot_equity_curve()
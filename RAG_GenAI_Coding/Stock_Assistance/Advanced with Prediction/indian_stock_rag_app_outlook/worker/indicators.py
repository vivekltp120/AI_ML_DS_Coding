import pandas as pd
import pandas_ta as ta

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if 'Close' not in df.columns and 'close' in df.columns:
        df = df.rename(columns={'close': 'Close'})
    df['rsi14'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    df = pd.concat([df, macd], axis=1)
    bb = ta.bbands(df['Close'], length=20, std=2)
    df = pd.concat([df, bb], axis=1)
    df['sma20'] = ta.sma(df['Close'], length=20)
    df['sma50'] = ta.sma(df['Close'], length=50)
    return df

def compute_signal_for_row(row) -> dict:
    sig = {"signal": "HOLD", "reason": []}
    try:
        rsi = float(row.get('rsi14', float('nan')))
        if rsi and rsi > 70:
            sig["reason"].append("RSI>70 (overbought)")
            sig["signal"] = "SELL"
        elif rsi and rsi < 30:
            sig["reason"].append("RSI<30 (oversold)")
            sig["signal"] = "BUY"
    except Exception:
        pass

    if pd.notna(row.get('sma20')) and pd.notna(row.get('sma50')):
        if row['sma20'] > row['sma50']:
            if sig["signal"] == "SELL":
                sig["reason"].append("SMA20 > SMA50 (bullish tilt) - conflicting")
            else:
                sig["reason"].append("SMA20 > SMA50 (bullish)")
                sig["signal"] = "BUY" if sig["signal"] != "SELL" else sig["signal"]
        elif row['sma20'] < row['sma50']:
            if sig["signal"] == "BUY":
                sig["reason"].append("SMA20 < SMA50 (bearish tilt) - conflicting")
            else:
                sig["reason"].append("SMA20 < SMA50 (bearish)")
                sig["signal"] = "SELL" if sig["signal"] != "BUY" else sig["signal"]

    macd_val = row.get('MACD_12_26_9') if 'MACD_12_26_9' in row.index else None
    macds_val = row.get('MACDs_12_26_9') if 'MACDs_12_26_9' in row.index else None
    try:
        if macd_val is not None and macds_val is not None:
            if macd_val > macds_val:
                sig["reason"].append("MACD above signal (bullish)")
                if sig["signal"] == "HOLD":
                    sig["signal"] = "BUY"
            elif macd_val < macds_val:
                sig["reason"].append("MACD below signal (bearish)")
                if sig["signal"] == "HOLD":
                    sig["signal"] = "SELL"
    except Exception:
        pass

    summary = f"Signal: {sig['signal']}. Reasons: " + "; ".join(sig["reason"]) if sig["reason"] else f"Signal: {sig['signal']}. No strong indicator."
    sig["summary"] = summary
    return sig

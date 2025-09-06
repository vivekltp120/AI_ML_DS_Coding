import pandas as pd
import pandas_ta as ta

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Ensure standard column names (yfinance uses 'Close' etc.)
    if 'Close' not in df.columns and 'close' in df.columns:
        df = df.rename(columns={'close':'Close'})
    # Basic TA set (extend as needed)
    df['rsi14'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    df = pd.concat([df, macd], axis=1)
    bb = ta.bbands(df['Close'], length=20, std=2)
    df = pd.concat([df, bb], axis=1)
    df['sma20'] = ta.sma(df['Close'], length=20)
    df['sma50'] = ta.sma(df['Close'], length=50)
    return df

def row_to_summary(ticker: str, row) -> str:
    fields = [
        f"Close={row.Close:.2f}",
        f"RSI14={row.rsi14:.2f}" if pd.notna(row.rsi14) else "RSI14=NA",
    ]
    # MACD fields safe access
    if 'MACD_12_26_9' in row.index:
        fields.append(f"MACD={row.MACD_12_26_9:.2f}")
    else:
        fields.append("MACD=NA")
    if 'MACDs_12_26_9' in row.index:
        fields.append(f"Signal={row.MACDs_12_26_9:.2f}")
    else:
        fields.append("Signal=NA")
    if 'BBANDS_U_20_2.0' in row.index:
        fields.append(f"UpperBB={row.BBANDS_U_20_2.0:.2f}")
    else:
        fields.append("UpperBB=NA")
    if 'BBANDS_L_20_2.0' in row.index:
        fields.append(f"LowerBB={row.BBANDS_L_20_2.0:.2f}")
    else:
        fields.append("LowerBB=NA")
    fields.append(f"SMA20={row.sma20:.2f}" if pd.notna(row.sma20) else "SMA20=NA")
    fields.append(f"SMA50={row.sma50:.2f}" if pd.notna(row.sma50) else "SMA50=NA")
    return (
        f"Daily technical snapshot for {ticker}: " + ", ".join(fields) + ". " +
        "Interpret cautiously; not investment advice."
    )

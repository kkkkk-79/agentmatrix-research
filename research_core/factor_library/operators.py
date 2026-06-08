# ============================================================
# Factor Operators - 因子基础操作函数（已修复版）
# ============================================================

import numpy as np
import pandas as pd


def cross_sectional_rank(df: pd.DataFrame, date_col: str, value_col: str) -> pd.Series:
    """Return percentile rank of ``value_col`` within each ``date_col`` cross-section."""
    return df.groupby(date_col)[value_col].rank(pct=True)


def rank_cross_section(df, col):
    """RANK: 截面百分位排名"""
    return cross_sectional_rank(df, 'date', col)


def ts_rank(series: pd.Series, window: int) -> pd.Series:
    """Return rolling percentile rank of the last value in each window."""
    def _rank_last(x):
        return pd.Series(x).rank(method="average", pct=True).iloc[-1]
    return series.rolling(window).apply(_rank_last, raw=True)


def tsrank(series, n):
    """Ts_Rank / TSRANK: 末位值在过去n天的百分位排名"""
    return ts_rank(series, n)


def ts_corr(x, y=None, window=None, n=None, 
            symbol_col: str = 'symbol', date_col: str = 'date') -> pd.Series:
    """【关键修复】CORR / 滚动相关系数 - 严格按每个股票自己的过去N天时序计算
       原实现容易把不同股票数据混在一起（横截面错误），现已修复。
    """
    corr_window = n if n is not None else window
    if corr_window is None:
        raise ValueError("必须提供 window 或 n 参数")

    # 支持长格式 DataFrame（最常用）
    if isinstance(x, pd.DataFrame):
        df = x.copy()
        if symbol_col in df.columns and date_col in df.columns:
            df = df.sort_values([symbol_col, date_col])
            # 自动处理 col_a / col_b（兼容不同调用方式）
            col_a = y if isinstance(y, str) else df.columns[0]
            col_b = window if isinstance(window, str) else df.columns[1]
            def _corr_group(g):
                return g[col_a].rolling(window=corr_window, min_periods=1).corr(g[col_b])
            result = df.groupby(symbol_col).apply(_corr_group)
            return result.reset_index(level=0, drop=True)
        else:
            # fallback：宽格式或简单两列
            col_a = df.columns[0]
            col_b = df.columns[1] if len(df.columns) > 1 else y
            return df[col_a].rolling(corr_window).corr(df[col_b] if isinstance(col_b, str) else col_b)

    # 普通 Series（单股票）
    return x.rolling(corr_window).corr(y)


def delta(series: pd.Series, period: int) -> pd.Series:
    """DELTA: n阶差分"""
    return series.diff(period)


def delay(series: pd.Series, period: int) -> pd.Series:
    """DELAY: n期滞后"""
    return series.shift(period)


def ts_sum(series: pd.Series, window: int) -> pd.Series:
    """Return rolling sum."""
    return series.rolling(window).sum()


def ts_mean(series: pd.Series, window: int) -> pd.Series:
    """Return rolling mean."""
    return series.rolling(window).mean()


def ts_std(series: pd.Series, window: int) -> pd.Series:
    """Return rolling standard deviation."""
    return series.rolling(window).std()


def ts_min(series: pd.Series, window: int) -> pd.Series:
    """Return rolling minimum."""
    return series.rolling(window).min()


def ts_max(series: pd.Series, window: int) -> pd.Series:
    """Return rolling maximum."""
    return series.rolling(window).max()


def tsmax(series, n):
    """ts_max / TSMAX: 滚动最大值"""
    return ts_max(series, n)


def tsmin(series, n):
    """ts_min / TSMIN: 滚动最小值"""
    return ts_min(series, n)


def ts_argmax(series, n):
    """Ts_ArgMax: 过去n天最大值所在位置(0-based)"""
    return series.rolling(n).apply(np.argmax, raw=True)


def signed_power(series: pd.Series, power: float) -> pd.Series:
    """Return sign-preserving power transform."""
    return np.sign(series) * (np.abs(series) ** power)


def safe_vwap(
    amount: pd.Series,
    volume: pd.Series,
    open_: pd.Series,
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
) -> pd.Series:
    """Return VWAP as amount / volume, falling back to OHLC mean when invalid."""
    vwap = amount / volume
    vwap = vwap.replace([np.inf, -np.inf], np.nan)
    ohlc_mean = (open_ + high + low + close) / 4
    vwap = vwap.fillna(ohlc_mean)
    mask_zero_vol = (volume == 0) | volume.isna()
    vwap[mask_zero_vol] = ohlc_mean[mask_zero_vol]
    return vwap


def compute_vwap(close, high, low, open_, amount, volume):
    """计算VWAP: amount/volume，零值用OHLC均值填充"""
    return safe_vwap(amount, volume, open_, high, low, close)


def sma_gtja(series, n, m):
    """GTJA191 SMA: Y_{i+1} = (A_i * m + Y_i * (n - m)) / n"""
    values = series.values.astype(float)
    result = np.full(len(values), np.nan)
    start_idx = 0
    for i in range(len(values)):
        if not np.isnan(values[i]):
            result[i] = values[i]
            start_idx = i
            break
    for i in range(start_idx + 1, len(values)):
        if np.isnan(values[i]):
            result[i] = result[i - 1]
        else:
            result[i] = (values[i] * m + result[i - 1] * (n - m)) / n
    return pd.Series(result, index=series.index)


# 新增 helper（推荐使用）
def adv_amount(series: pd.Series, window: int) -> pd.Series:
    """adv20 使用 amount（成交额）计算，保证与 alpha7 单位一致"""
    return ts_mean(series, window)

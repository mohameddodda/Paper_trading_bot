import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from core.db_manager import db_manager
from core.data_fetcher import fetch_all_prices
from bots.cli_bot import portfolio  # Global portfolio
import time

st.set_page_config(page_title="Paper Trading Bot Dashboard", layout="wide")

st.title("📈 Paper Trading Bot - Live Dashboard")
st.markdown("**Real-time PnL, equity curve, open positions from SQLite DB**")

# Sidebar
st.sidebar.title("Controls")
auto_refresh = st.sidebar.checkbox("Auto refresh (30s)", value=True)
refresh_interval = 30 if auto_refresh else None

# Metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    stats = db_manager.get_trade_stats()
    st.metric("Total Trades", stats.get('total_trades', 0))
with col2:
    st.metric("Win Rate", f"{stats.get('win_rate_pct', 0):.1f}%")
with col3:
    st.metric("Avg PnL", f"{stats.get('avg_pnl_pct', 0):.2f}%")
with col4:
    st.metric("Daily PnL", f"{stats.get('daily_pnl_pct', 0):.2f}%")

# Live prices
st.subheader("💰 Live Prices & Portfolio")
prices = fetch_all_prices()
portfolio_col1, portfolio_col2 = st.columns(2)
with portfolio_col1:
    st.write("**Current Prices**")
    for sym, price in list(prices.items())[:8]:
        st.metric(sym, f"${price:.4f}" if price else "N/A")
with portfolio_col2:
    st.write("**Open Positions**")
    open_pos = {k: v for k, v in portfolio.portfolio.items() if v > 0}
    for sym, qty in list(open_pos.items())[:8]:
        price = prices.get(sym, 0)
        val = qty * price
        st.metric(f"{sym} ({qty:.4f})", f"${val:.2f}")

# Equity curve
st.subheader("📊 Equity Curve")
trades_df = db_manager.get_trades(limit=1000)
if not trades_df.empty:
    trades_df['cumulative_pnl'] = trades_df['pnl'].cumsum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trades_df['timestamp'], y=trades_df['cumulative_pnl'], 
                            mode='lines+markers', name='Cumulative PnL'))
    fig.update_layout(title="Portfolio Equity Over Time", xaxis_title="Time", yaxis_title="PnL ($)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No trades yet. Run the bot to see equity curve!")

# Recent trades table
st.subheader("📋 Recent Trades")
recent_trades = db_manager.get_trades(limit=20)
if not recent_trades.empty:
    st.dataframe(recent_trades[['timestamp', 'symbol', 'type', 'price', 'pnl_pct', 'reason']])
else:
    st.info("No trades in database yet.")

# Performance stats
st.subheader("🏆 Performance Metrics")
stats_df = pd.DataFrame([db_manager.get_trade_stats()])
st.dataframe(stats_df.T, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("*Paper Trading Bot v1.0 - Educational simulation only*")

if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()


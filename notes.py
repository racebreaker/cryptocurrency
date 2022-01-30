# app7.py - Module Introduction
import streamlit as st
import pandas as pd


def app():
    st.title('Release Notes')
    st.write("""
        - 2022.01.15 First version 1.0 go online!
        - 2022.01.16 v1.1 - Fixed some minor issues in Algorithmic Trading module

        - Algorithmic Trading
            1. Candlestick and Analysis Chart
            2. Add Technical Indicators
                - Available Indicators: SMA 20, 60, 120, EMA 20, 60, 120, RSI, Bollinger Band
                - Can define two types of custom indicators 
                    - SMA
                    - EMA
            3. Define Buy/Sell Strategy
                - Momentum Indicators (Eg. RSI < 30)
                - Volatility Indicators (Eg. Close < Lower)
                - Trend Indicators vs. Indictors (Eg. EMA20 crossup/crossdown EMA120)
                - Price vs. Indicators (Eg. Close > EMA120)
            4. Backtesting Strategy
                - Initial Invested Amount
                - Buy only when there is no position
                - Sell only when there is no position
            """)

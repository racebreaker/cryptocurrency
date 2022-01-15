# app7.py - Module Introduction
import streamlit as st
import pandas as pd


def app():
    st.title('Release Notes')
    st.write("""
        - 2022.01.15 First version 1.0 go online! 

        - Cryptocurrency
            1. Candlestick and Analysis Chart
            2. Add Technical Indicators
                - Can define custom indicators 
                    - SMA
                    - EMA
            3. Define Buy/Sell Strategy
                - Momentum Indicators (Eg. RSI < 30)
                - Volatility Indicators (Eg. Close < Lower)
                - Trend Indicators (Eg. EMA20 > EMA120, Close crossover EMA10)
                - Candle price comparison (Eg. Close > High (1 day ago))
            4. Backtesting Strategy
            """)

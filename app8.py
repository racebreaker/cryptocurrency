# app8.py - Cryptocurrency
import streamlit as st
import pandas as pd
import yfinance as yf
import talib
from talib import abstract
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib
import datetime
import operator

import backtrader as bt
# from strategies import TestStrategy
import matplotlib.pyplot as plt

import backtesting
from backtesting import Strategy, Backtest
from backtesting.lib import crossover


def app():
    # st.title('Cryptocurrency')
    st.title('Algorithmic trading strategies and Backtesting')
    st.markdown("***")

    # st.text("")
    st.write('\n')
    st.subheader('1. Candlestick and Analysis Chart')

    expander_candlestick = st.expander(
        label='Select Candlestick Chart Parameters')
    with expander_candlestick:
        with st.form(key='crypto_selection'):
            # st.subheader("Plot Candlestick")
            dropdown = st.text_input(
                'Please key in Crypto Quote:', value='BTC-USD')
            # st.write('Dropdown is', dropdown)
            interval = st.multiselect('Time Interval is:', ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk',
                                                            '1mo', '3mo'], default='1d')
            start = st.date_input(
                'Start Date:', value=pd.to_datetime('2021-01-01'))
            now = datetime.datetime.now()
            end = st.date_input('End Date:', value=pd.to_datetime('now'))

            # (optional, default is '1d')

            submit = st.form_submit_button(label='Submit')

        # @st.cache
    if len(dropdown) > 0:
        # st.write('Dropdown is', dropdown)
        # st.write('Start date is', start)
        # st.write('End date is', end)
        # st.write('Interval is', interval[0])
        #!This created for Backtrader module, Adj Close is merged into Close
        data_raw = yf.download(dropdown, start, now,
                               interval=interval[0], auto_adjust=True)

        # ! Choose different interval will give different default index column name
        data = data_raw
        # st.write('DataFrame is:', data)

        # data = data.reset_index()
        # data = data.rename(columns={'Date': 'Datetime'})

        # data.index.names = ['Datetime']
        # st.write('Data Raw temp is', data_raw)
        # data.reset_index(inplace=True)
        # st.write('Data processed', data_raw)
        # st.write('Actual Data', data)

    #     dfprice = pd.DataFrame()
    #     dfprice = yf.download(dropdown,start,end)['Close']

    #     dfnew = dfprice.pct_change() + 1
    #     cumret = dfnew.cumprod() - 1
    #     cumret = cumret.fillna(0)
    #     st.line_chart(cumret)

    # Plot Candlestick Chart
    fig = make_subplots(
        rows=1, cols=1,
        #    subplot_titles=("Pricing and Volume Chart",""),
        specs=[[{"secondary_y": True}]])

    # fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            low=data['Low'],
            high=data['High'],
            close=data['Close'],
            open=data['Open'],
            increasing_line_color='green',
            decreasing_line_color='red',
            name=dropdown),
        row=1, col=1,
        secondary_y=False
    )

    # Chart 2 - Volume (Secondary Y)
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['Volume'],
            name='Volume'
        ),
        row=1, col=1,
        secondary_y=True
    )

    ################################################################################################################
    st.subheader('2. Choose Technical Indicators or Define Custom Indicators')

    # Initialization of session variable
    if 'trend_indicator' not in st.session_state:
        st.session_state.trend_indicator = ''
        # st.write('Session initial value is', st.session_state.trend_indicator)
    if 'trend_period' not in st.session_state:
        st.session_state.trend_period = 0
        # st.write('Trend intial value is', st.session_state.trend_period)

    ta_list = ['EMA20', 'EMA60', 'EMA120', 'SMA20', 'SMA60',
               'SMA120', 'RSI', 'Upper', 'Lower', 'Custom']
    if len(st.session_state.trend_indicator) > 0:
        ta_list.insert(
            0, f'{st.session_state.trend_indicator}{st.session_state.trend_period}')
        data[st.session_state.trend_indicator+str(st.session_state.trend_period)] = eval(
            "getattr(abstract, f'{st.session_state.trend_indicator}')")(data.Close, st.session_state.trend_period)

    dropdown_ta = st.multiselect(
        'Please add Indicator:', ta_list, default=None)

    if 'Custom' in dropdown_ta:
        with st.form(key='custom_indicator'):
            col1, col2 = st.columns(2)
            with col1:
                trend_indicator = st.selectbox(
                    'Please Select Indicators:', ['SMA', 'EMA'])
                trend_period = st.number_input('Period', value=10)
            submit = st.form_submit_button('Submit')

        if submit:
            # st.write(trend_indicator)
            # st.write(str(trend_period))
            # data[trend_indicator+str(trend_period)] = getattr(
            #     talib, trend_indicator(data['Close'], trend_period))
            # data[trend_indicator+str(trend_period)] = getattr(talib,
            # st.write(trend_indicator)
            # st.write(trend_period)

            # if 'trend_indicator' not in st.session_state:
            st.session_state.trend_indicator = trend_indicator
            st.write('Session value is', st.session_state.trend_indicator)

            # if 'trend_period' not in st.session_state:
            st.session_state.trend_period = trend_period
            st.write('Trend Period is', st.session_state.trend_period)

            # st.write(st.session_state.trend_indicator)
            # st.write(st.session_state.trend_period)
            #! data[SMA10] needs to be defined first regardless of operator
            data[st.session_state.trend_indicator+str(st.session_state.trend_period)] = eval(
                "getattr(abstract, f'{st.session_state.trend_indicator}')")(data.Close, st.session_state.trend_period)
            # st.session_state.data[st.session_state.trend_indicator+str(
            #     st.session_state.trend_period)] = data[st.session_state.trend_indicator+str(st.session_state.trend_period)]
            st.write('Customer indicator is writen in memory')
            st.write(
                f'Custom indicator {trend_indicator}{trend_period} has been created successfully', data[st.session_state.trend_indicator+str(st.session_state.trend_period)])
            ta_list = ta_list.insert(
                0, f'{st.session_state.trend_indicator}{st.session_state.trend_period}')
            # st.write(ta_list)
            # ta_list.insert(0, trend_indicator+str(trend_period))

    data['SMA20'] = talib.SMA(data['Close'], 20)
    data['SMA60'] = talib.SMA(data['Close'], 60)
    data['SMA120'] = talib.SMA(data['Close'], 120)
    data['EMA20'] = talib.EMA(data['Close'], 20)
    data['EMA60'] = talib.EMA(data['Close'], 60)
    data['EMA120'] = talib.EMA(data['Close'], 120)
    data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
    data['Upper'], data['Middle'], data['Lower'] = talib.BBANDS(
        data['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    # st.write('Close length', len(data['Close']))
    # st.write('Lower length', len(data['Lower']))

    if 'Custom' not in dropdown_ta:
        for select_indicator in dropdown_ta:
            # st.write("Selected Indicator is " + select_indicator)
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data[select_indicator],
                    name=select_indicator
                )
            )
  ################################################################################################################
    st.subheader('3. Define Algorithmic Trading Strategy')
    ops = {
        '>': operator.gt,
        '<': operator.lt,
        '==': operator.eq,
        '>=': operator.ge,
        '<=': operator.le,
    }

    expander_criteria = st.expander(label='Buy/Sell Criteria Details')
    with expander_criteria:
        with st.form(key='indicator_selection_buy'):
            # Buy Criteria
            container1 = st.container()
            with container1:
                st.write('Please Define Buy Criteria (Container 1)')
                col1, col2, col3 = st.columns(3)

                with col1:
                    # Momentum indicator selection
                    # momentum_buy = st.multiselect(
                    #     'Momentum Indicators:', talib.get_function_groups()['Momentum Indicators'])
                    momentum_buy = st.multiselect(
                        'Momentum Indicators:', ['RSI'])
                    price_buy = st.multiselect('Price:', [
                        'Close', 'Open', 'High', 'Low'])
                    # Define buy list and insert the custom indicator if there is any
                    trend1_buy_list = ['EMA20', 'EMA60',
                                       'EMA120', 'SMA20', 'SMA60', 'SMA120']
                    if len(st.session_state.trend_indicator) > 0:
                        trend1_buy_list.insert(
                            0, f'{st.session_state.trend_indicator}{st.session_state.trend_period}')
                    trend1_buy = st.multiselect(
                        'Trend Indicators:', trend1_buy_list, key='Trend1')
                    # price1_comp_buy = st.multiselect('Price:', [
                    #     'Close', 'Open', 'High', 'Low'], key='Price1 Compare Buy')
                    price1_buy = st.multiselect('Price:', [
                        'Close', 'Open', 'High', 'Low'], key='Price 1 Buy')

                with col2:
                    # Momentum indicator selection
                    operator1_buy = st.multiselect(
                        'Operator:', ['>', '<', '==', '>=', '<='], key='Operator 1')
                    operator2_buy = st.multiselect(
                        'Operator:', ['>', '<', '==', '>=', '<='], key='Operator 2')
                    operator3_buy = st.multiselect(
                        'Operator:', ['>', '<', '==', '>=', '<=', 'crossup'], key='Operator 3')
                    operator4_buy = st.multiselect(
                        'Operator:', ['>', '<', '==', '>=', '<=', 'crossup'], key='Operator 4')

                with col3:
                    # Momentum indicator selection
                    value_buy = st.text_input(
                        'Value:')
                    # value1 = st.text_input('Please enter the value:', key='Value1')
                    # indicator_volatility_list = talib.get_function_groups()[
                    #     'Volatility Indicators']
                    # indicator_volatility_list.insert(1, 'BB-Lower')
                    # indicator_volatility_list.insert(1, 'BB-Upper')
                    volatility_buy = st.multiselect(
                        'Volatility Indicators:', ['Upper', 'Lower'])
                    trend2_buy_list = ['EMA20', 'EMA60',
                                       'EMA120', 'SMA20', 'SMA60', 'SMA120']
                    # if len(st.session_state.trend_indicator) > 0:
                    #     trend2_buy_list = trend2_buy_list.insert(
                    #         0, f'{st.session_state.trend_indicator}{st.session_state.trend_period}')
                    # st.write('trend2_buy_list', trend2_buy_list)
                    trend2_buy = st.multiselect(
                        'Trend Indicators:', trend1_buy_list, key='Trend2')

                    trend3_buy = st.multiselect(
                        'Trend Indicators:', trend1_buy_list, key='Trend3')
                    # price2_comp_buy = st.multiselect('Previous price (1 day ago):', [
                    #     'Close', 'Open', 'High', 'Low'], key='Price2 Compare Buy')

            #---------------------------------------------------------------------------------------------------#
            # Sell Criteria
            container2 = st.container()
            with container2:
                st.write('Please Define Sell Criteria (Container 2)')
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Momentum indicator selection
                    momentum_sell = st.multiselect(
                        'Momentum Indicators:', ['RSI'], key='Sell')
                    # Volatility indicator selection
                    price_sell = st.multiselect('Price:', [
                        'Close', 'Open', 'High', 'Low'], key='Sell')

                    # Define sell list and buy list are the same, and insert the custom indicator if there is any
                    trend1_sell_list = ['EMA20', 'EMA60',
                                        'EMA120', 'SMA20', 'SMA60', 'SMA120']
                    if len(st.session_state.trend_indicator) > 0:
                        trend1_sell_list.insert(
                            0, f'{st.session_state.trend_indicator}{st.session_state.trend_period}')
                    trend1_sell = st.multiselect(
                        'Trend Indicators:', trend1_sell_list, key='Trend1_sell')
                    # price1_comp_sell = st.multiselect('Price:', [
                    #     'Close', 'Open', 'High', 'Low'], key='Price1 Compare Sell')
                    price1_sell = st.multiselect('Price:', [
                        'Close', 'Open', 'High', 'Low'], key='Price 1 Sell')

                with col2:
                    # Momentum indicator selection
                    operator1_sell = st.multiselect(
                        'Operator:', ['>', '<', '==', '>=', '<='], key='Operator 1_sell')
                    # Volatility indicator selection
                    operator2_sell = st.multiselect(
                        'Operator:', ['>', '<', '==', '>=', '<='], key='Operator 2_sell')
                    operator3_sell = st.multiselect(
                        'Operator:', ['>', '<', '==', '>=', '<=', 'crossdown'], key='Operator 3_sell')
                    operator4_sell = st.multiselect(
                        'Operator:', ['>', '<', '==', '>=', '<=', 'crossdown'], key='Operator 4_sell')

                with col3:
                    # Momentum indicator selection
                    value_sell = st.text_input(
                        'Value:', key='Sell')

                    # value1 = st.text_input('Please enter the value:', key='Value1')
                    # indicator_volatility_list = talib.get_function_groups()[
                    #     'Volatility Indicators']
                    # indicator_volatility_list.insert(1, 'BB-Lower')
                    # indicator_volatility_list.insert(1, 'BB-Upper')
                    # Volatility indicator selection
                    volatility_sell = st.multiselect(
                        'Volatility Indicators:', ['Upper', 'Lower'], key='Sell')
                    # if len(st.session_state.trend_indicator) > 0:
                    #     trend2_buy_list = trend2_buy_list.insert(
                    #         0, f'{st.session_state.trend_indicator}{st.session_state.trend_period}')
                    trend2_sell = st.multiselect(
                        'Trend Indicators:', trend1_sell_list, key='Trend2_sell')
                    # price2_comp_sell = st.multiselect('Previous price (1 day before):', [
                    #     'Close', 'Open', 'High', 'Low'], key='Price2 Compare Sell')
                    trend3_sell = st.multiselect(
                        'Trend Indicators:', trend1_sell_list, key='Trend3_sell')
            # st.write('Outside the container2')
            submit = st.form_submit_button('Submit')

        if submit:
            #! Assign the custom indicator in the criteria
            if len(st.session_state.trend_indicator) > 0:
                data[st.session_state.trend_indicator+str(st.session_state.trend_period)] = eval(
                    "getattr(abstract, f'{st.session_state.trend_indicator}')")(data.Close, st.session_state.trend_period)

            # Buy criteria
            if len(operator1_buy) == 0 or len(momentum_buy) == 0:
                data.condition1_buy = True
            else:
                data.condition1_buy = ops[operator1_buy[0]](
                    data[momentum_buy[0]], float(value_buy))
                # st.write('Condition1', data.condition1_buy)

            if len(operator2_buy) == 0 or len(price_buy) == 0 or len(volatility_buy) == 0:
                data.condition2_buy = True
            else:
                data.condition2_buy = ops[operator2_buy[0]](
                    data[price_buy[0]], data[volatility_buy[0]])
                # condition2_buy_bt = eval(
                #     f'self.data.{price_buy[0]} {operator2_buy[0]} self.{volatility_buy[0]}')

            if len(operator3_buy) == 0 or len(trend1_buy) == 0 or len(trend2_buy) == 0:
                data.condition3_buy = True
            else:
                if operator3_buy[0] == 'crossup':
                    # st.write('st.session_state.trend_indicator',
                    #          st.session_state.trend_indicator)
                    # st.write('trend1_buy[0]', trend1_buy[0])
                    # st.write('trend2_buy[0]', trend2_buy[0])
                    # st.write(eval(f'data.{trend1_buy[0]}'))
                    data['condition3_buy'] = ''
                    for i in range(len(data)-1, 0, -1):
                        data['condition3_buy'].iloc[i] = eval(
                            f'data.{trend1_buy[0]}.iloc[{i}] > data.{trend2_buy[0]}.iloc[{i}] and data.{trend1_buy[0]}.iloc[{i-1}] < data.{trend2_buy[0]}.iloc[{i-1}]').astype(str)
                    # # data.condition3_buy = data['test']
                    d = {'True': True, 'False': False}
                    data['condition3_buy'] = data['condition3_buy'].map(d)
                    # st.write('Condition3', data.condition3_buy)
                    # st.write('Check data frame', data)
                else:
                    data.condition3_buy = ops[operator3_buy[0]](
                        getattr(data, trend1_buy[0]), getattr(data, trend2_buy[0]))
                    # st.write('trend1_buy[0] is', trend1_buy[0])
                    # st.write('trend2_buy[0] is', trend2_buy[0])
                    # st.write('Condition 3 is satisfied', data.condition3_buy)

            if len(operator4_buy) == 0 or len(price1_buy) == 0 or len(trend3_buy) == 0:
                data.condition4_buy = True
            else:
                if operator4_buy[0] == 'crossup':
                    # st.write('price1_buy[0]', price1_buy[0])
                    # st.write('trend3_buy[0]', trend3_buy[0])
                    data['condition4_buy'] = ''
                    for i in range(len(data)-1, 0, -1):
                        data['condition4_buy'].iloc[i] = eval(
                            f'data.{price1_buy[0]}.iloc[{i}] > data.{trend3_buy[0]}.iloc[{i}] and data.{price1_buy[0]}.iloc[{i-1}] < data.{trend3_buy[0]}.iloc[{i-1}]').astype(str)
                    # # data.condition3_buy = data['test']
                    d = {'True': True, 'False': False}
                    data['condition4_buy'] = data['condition4_buy'].map(d)
                    # st.write('Condition3', data.condition3_buy)
                    # st.write('Check data frame', data)
                else:
                    data.condition4_buy = ops[operator4_buy[0]](
                        getattr(data, price1_buy[0]), getattr(data, trend3_buy[0]))
                    # st.write('trend1_buy[0] is', trend1_buy[0])
                    # st.write('trend2_buy[0] is', trend2_buy[0])
                    # st.write('Condition 3 is satisfied', data.condition3_buy)

            # if len(operator4_buy) == 0 or len(price1_comp_buy) == 0 or len(price2_comp_buy) == 0:
            #     data.condition4_buy = True
            # else:
            #     for i in range(len(data)-1, 0, -1):
            #         data.condition4_buy = eval(
            #             f'data.{price1_comp_buy[0]}.iloc[{i}] {operator4_buy[0]} data.{price2_comp_buy[0]}.iloc[{i-1}]')

            #! This is to cater for the situation that nothing is selected
            empty_buy = type(data.condition1_buy) == bool and type(data.condition2_buy) == bool and type(
                data.condition3_buy) == bool and type(data.condition4_buy) == bool
            if empty_buy == True:
                st.write('No Buy Criteria is selected!')
            else:
                # st.write('Condition 1 is', data.condition1_buy)
                # st.write('Condition 2 is', data.condition2_buy)
                # st.write('Condition 3 is', data.condition3_buy)
                # st.write('Condition 4 is', data.condition4_buy)
                data_buy = data.loc[data.condition1_buy &
                                    data.condition2_buy & data.condition3_buy & data.condition4_buy]
                st.write(
                    f'There are total {len(data_buy)} days meet Buy Criteria, they are:', data_buy)

                # Chart 2 - Buy Signal
                fig.add_trace(
                    go.Scatter(
                        x=data_buy.index,
                        y=data_buy['Low']*0.80,
                        mode='markers',
                        name='Buy Singal',
                        marker=go.Marker(size=8,
                                         symbol="triangle-up",
                                         color="green")),
                    row=1, col=1,
                    secondary_y=False)
            #----------------------------------------------------------------------------------------------#
            # Sell Criteria
            if len(operator1_sell) == 0 or len(momentum_sell) == 0:
                data.condition1_sell = True
            else:
                data.condition1_sell = ops[operator1_sell[0]](
                    data[momentum_sell[0]], float(value_sell))

            if len(operator2_sell) == 0 or len(price_sell) == 0 or len(volatility_sell) == 0:
                data.condition2_sell = True
            else:
                data.condition2_sell = ops[operator2_sell[0]](
                    data[price_sell[0]], data[volatility_sell[0]])

            if len(operator3_sell) == 0 or len(trend1_sell) == 0 or len(trend2_sell) == 0:
                data.condition3_sell = True
            else:
                if operator3_sell[0] == 'crossdown':
                    data['condition3_sell'] = ''
                    for i in range(len(data)-1, 0, -1):
                        data['condition3_sell'].iloc[i] = eval(
                            f'data.{trend1_sell[0]}.iloc[{i}] < data.{trend2_sell[0]}.iloc[{i}] and data.{trend1_sell[0]}.iloc[{i-1}] > data.{trend2_sell[0]}.iloc[{i-1}]').astype(str)
                    # st.write('Check data frame', data)
                    d = {'True': True, 'False': False}
                    data['condition3_sell'] = data['condition3_sell'].map(d)
                    # st.write('Condition3', data.condition3_sell)
                    # st.write('Check data frame', data)
                else:
                    data.condition3_sell = ops[operator3_sell[0]](
                        getattr(data, trend1_sell[0]), getattr(data, trend2_sell[0]))
                    # st.write('trend1_buy[0] is', trend1_buy[0])
                    # st.write('trend2_buy[0] is', trend2_buy[0])
                    # st.write('Condition 3 is satisfied', data.condition3_buy)

            if len(operator4_sell) == 0 or len(price1_sell) == 0 or len(trend3_sell) == 0:
                data.condition4_sell = True
            else:
                if operator4_sell[0] == 'crossdown':
                    data['condition4_sell'] = ''
                    for i in range(len(data)-1, 0, -1):
                        data['condition4_sell'].iloc[i] = eval(
                            f'data.{price1_sell[0]}.iloc[{i}] < data.{trend3_sell[0]}.iloc[{i}] and data.{price1_sell[0]}.iloc[{i-1}] > data.{trend3_sell[0]}.iloc[{i-1}]').astype(str)
                    # st.write('Check data frame', data)
                    d = {'True': True, 'False': False}
                    data['condition4_sell'] = data['condition4_sell'].map(d)
                    # st.write('Condition3', data.condition3_sell)
                    # st.write('Check data frame', data)
                else:
                    data.condition4_sell = ops[operator4_sell[0]](
                        getattr(data, price1_sell[0]), getattr(data, trend3_sell[0]))

            # if len(operator4_sell) == 0 or len(price1_comp_sell) == 0 or len(price2_comp_sell) == 0:
            #     data.condition4_sell = True
            # else:
            #     for i in range(len(data)-1, 0, -1):
            #         data.condition4_sell = eval(
            #             f'data.{price1_comp_sell[0]}.iloc[{i}] {operator4_sell[0]} data.{price2_comp_sell[0]}.iloc[{i-1}]')

            empty_sell = type(data.condition1_sell) == bool and type(data.condition2_sell) == bool and type(
                data.condition3_sell) == bool and type(data.condition4_sell) == bool

            if empty_sell == True:
                st.write('No Sell Criteria is selected!')
            else:
                data_sell = data.loc[data.condition1_sell &
                                     data.condition2_sell & data.condition3_sell & data.condition4_sell]
                st.write(
                    f'There are total {len(data_sell)} days meet Sell Criteria, they are:', data_sell)

                # Chart 2 - Sell Signal
                fig.add_trace(
                    go.Scatter(
                        x=data_sell.index,
                        y=data_sell['High']*1.10,
                        mode='markers',
                        name='Sell Singal',
                        marker=go.Marker(size=8,
                                         symbol="triangle-down",
                                         color="red")),
                    row=1, col=1,
                    secondary_y=False)

    fig.update_layout(
        # legend=dict(
        # yanchor="top",
        # y=0.99,
        # xanchor="left",
        # x=0.01),
        title='Pricing and Volume Chart',
        title_x=0.5)
    st.plotly_chart(fig)
    st.write(
        f'There are total {len(data)} trading days in the selected time period')

    # import os
    # st.write(os.getcwd())
    #################################################################################################################
    st.header('4. Conduct Backtesting')

    matplotlib.use('Agg')

    # Create Data Feed
    # data = bt.feeds.YahooFinanceCSVData(
    #    dataname='TSLA.csv',
    # Do not pass values before this date
    #    fromdate=datetime.datetime(2018, 1, 1),
    # Do not pass values after this date
    #    todate=datetime.datetime(2021, 10, 2),
    #    reverse=False)

    # data = yf.download('TSLA', '2018-01-01', '2021-12-29', auto_adjust=True)
    # data.reset_index(inplace=True) #! Need to leave the date as index, otherwise, won't be able to see date
    # data = bt.feeds.PandasData(dataname=yf.download('TSLA', '2018-01-01', '2021-10-02', auto_adjust=True))

    class Custom(Strategy):
        n1 = 20
        n2 = 120
        n3 = 14
        n4 = st.session_state.trend_period

        # def log(self, txt, dt=None):
        #     ''' Logging function for this strategy'''
        #     dt = dt or self.datas[0].datetime.date(0)
        #     print('%s, %s' % (dt.isoformat(), txt))
        # st.write('Variable is', trend1_buy[0])

        def init(self):
            # self.__dict__[momentum_buy[0]] = self.I(
            #     getattr(talib, momentum_buy[0]), self.data.Close, timeperiod=self.n3)
            #--------------------------------------------------------------------------------------------#
            # Define indicators
            self.SMA20 = self.I(talib.SMA, self.data.Close, self.n1)
            self.SMA60 = self.I(talib.SMA, self.data.Close, 60)
            self.SMA120 = self.I(talib.SMA, self.data.Close, self.n2)
            self.EMA20 = self.I(talib.EMA, self.data.Close, self.n1)
            self.EMA60 = self.I(talib.EMA, self.data.Close, 60)
            self.EMA120 = self.I(talib.EMA, self.data.Close, self.n2)
            self.RSI = self.I(talib.RSI, self.data.Close, timeperiod=self.n3)

            # st.write('Total Data Length is', len(self.data.Close))
            self.Upper, self.Middle, self.Lower = self.I(
                talib.BBANDS, self.data.Close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
            self.Close = self.data.Close
            self.High = self.data.High
            indicator_name = st.session_state.trend_indicator + \
                str(st.session_state.trend_period)
            # st.write('Name of custom Indicator', indicator_name)
            if len(st.session_state.trend_indicator) > 0:
                setattr(self, indicator_name, self.I(getattr(
                    talib, f'{st.session_state.trend_indicator}'), self.data.Close, self.n4))
                # st.write(
                #     f'Custom Indicator {indicator_name} has been instantiated successfully')

            #--------------------------------------------------------------------------------------------#
            # Define Buy Criteria for Backtest.py
            if len(operator1_buy) == 0 or len(momentum_buy) == 0:
                self.condition1_buy_bt = True
            else:
                self.condition1_buy_bt = eval(
                    f'self.{momentum_buy[0]} {operator1_buy[0]} {value_buy}')
                # self.condition1_buy_bt = ops[operator1_buy[0]](
                #     getattr(self, momentum_buy[0]), float(value_buy))
                # st.write('momentum_buy[0] value is', momentum_buy[0])
                # st.write('Value_buy is', float(value_buy))
                # st.write('Condition1 Operator1_buy', operator1_buy[0])
                # st.write('Condition 1', self.condition1_buy_bt)
                # st.write('Condition 1 length', len(self.condition1_buy_bt))

            if len(operator2_buy) == 0 or len(price_buy) == 0 or len(volatility_buy) == 0:
                self.condition2_buy_bt = True
            else:
                self.condition2_buy_bt = eval(
                    f'self.data.{price_buy[0]} {operator2_buy[0]} self.{volatility_buy[0]}')
                # st.write('Operator is', operator2_buy[0])
                # # st.write('Type of the Operator is',
                #          type(operator2_buy[0]))
                #! working one on operator!
                # self.condition2_buy_bt = eval(
                #     f'self.data.Close {operator2_buy[0]} self.Upper')
                # st.write('Condition 2', self.condition2_buy_bt)
                # st.write('Condition 2 length', len(self.condition2_buy_bt))
                # self.condition2_buy_bt = eval(
                #     'getattr(self, price_buy[0]) operator2_buy[0] getattr(self, volatility_buy[0])')

                # st.write(getattr(self, price_buy[0]))
                # st.write('Close length', len(getattr(self, price_buy[0])))
                # st.write(getattr(self, volatility_buy[0]))

                # st.write('Lower length', len(
                #     getattr(self, volatility_buy[0])))
                # st.write('Volatility input is', volatility_buy[0])
                # st.write('Lower length direct', len(self.Lower))
                # st.write(ops[operator2_buy[0]])
                # self.condition2_buy_bt = ops[operator2_buy[0]](
                #     getattr(self, price_buy[0]), getattr(self, volatility_buy[0]))

            if len(operator3_buy) == 0 or len(trend1_buy) == 0 or len(trend2_buy) == 0:
                self.condition3_buy_bt = True
            else:
                if operator3_buy[0] == 'crossup':
                    self.condition3_buy_bt = eval(
                        f'crossover(self.{trend1_buy[0]}, self.{trend2_buy[0]})')
                    #! Alternative statement
                    # setattr(self, 'condition3_buy_bt', eval(
                    #         f'self.{trend1_buy[0]}[-1] > self.{trend2_buy[0]}[-2] and self.{trend1_buy[0]}[-2] < self.{trend2_buy[0]}[-3]'))
                    # st.write('Condition3', self.condition3_buy_bt)

                    # st.write('Choose Crossover')
                    # st.write(
                    #     'Eval string is', f'{operator3_buy[0]}(self.{trend1_buy[0]}, self.{trend2_buy[0]})')
                    # st.write('Condition3 operator3_buy', operator3_buy[0])
                    # st.write('Condition3 trend1_buy', trend1_buy[0])
                    # # st.write('Condition3 self.SMA20', self.SMA20)
                    # # st.write('Condition3 self.SMA120', self.SMA120)
                    # st.write('Crossover function',
                    #          crossover(self.SMA20, self.SMA120))
                    # st.write('Condition3 trend2_buy', trend2_buy[0])
                    # st.write('Condition3 condition3_buy_bt',
                    #          eval(f'{operator3_buy[0]}(self.{trend1_buy[0]}, self.{trend2_buy[0]})'))
                else:
                    self.condition3_buy_bt = eval(
                        f'self.{trend1_buy[0]} {operator3_buy[0]} self.{trend2_buy[0]}')
                    # st.write('Condition 3', self.condition3_buy_bt)
                    # self.condition3_buy_bt = ops[operator3_buy[0]](
                    #     getattr(self, trend1_buy[0]), getattr(self, trend2_buy[0]))
                    # st.write('Condition3 trend1_buy', trend1_buy[0])
                    # st.write('Condition3 trend2_buy', trend2_buy[0])
                    # st.write('Condition3 Operator3_buy', operator3_buy[0])
                    # st.write('Self.Close direct', self.Close)
                    # st.write('Self.Close direct length', len(self.Close))
                    # st.write('Self.Close', getattr(self, trend1_buy[0]))
                    # st.write('Self.Close length', len(
                    #     getattr(self, trend1_buy[0])))
                    # st.write('Self.SMA10', getattr(self, trend2_buy[0]))
                    # st.write('Self.SMA10 length', len(
                    #     getattr(self, trend2_buy[0])))
                    # st.write('operator3_buy', operator3_buy[0])
                    # st.write('self.trend1_buy', getattr(self, trend1_buy[0]))
                    # st.write('self.trend1_buy length', len(
                    #     getattr(self, trend1_buy[0])))
                    # st.write('self.trend2_buy', getattr(self, trend2_buy[0]))
                    # st.write('self.trend2_buy length', len(
                    #     getattr(self, trend2_buy[0])))

                    # st.write('Condition 3 length', len(self.condition3_buy_bt))
                    # self.condition3_buy_bt = ops[operator3_buy[0]](
                    #     getattr(self, trend1_buy[0]), getattr(self, trend2_buy[0]))

            if len(operator4_buy) == 0 or len(price1_buy) == 0 or len(trend3_buy) == 0:
                self.condition4_buy_bt = True
            else:
                if operator4_buy[0] == 'crossup':
                    self.condition4_buy_bt = eval(
                        f'crossover(self.data.{price1_buy[0]}, self.{trend3_buy[0]})')
                else:
                    self.condition4_buy_bt = eval(
                        f'self.data.{price1_buy[0]} {operator4_buy[0]} self.{trend3_buy[0]}')

            # if len(operator4_buy) == 0 or len(price1_comp_buy) == 0 or len(price2_comp_buy) == 0:
            #     self.condition4_buy_bt = True
            # else:
            #     self.condition4_buy_bt = eval(
            #         f'self.{price1_comp_buy[0]}[-1] {operator4_buy[0]} self.{price2_comp_buy[0]}[-2]')
            #     st.write('Condition 4', self.condition4_buy_bt)
            #     st.write('Condition 4 length', len(self.condition4_buy_bt))

            #------------------------------------------------------------------------------------------------#
            # Define Sell Condition
            if len(operator1_sell) == 0 or len(momentum_sell) == 0:
                self.condition1_sell_bt = True
            else:
                self.condition1_sell_bt = eval(
                    f'self.{momentum_sell[0]} {operator1_sell[0]} {value_sell}')
                # self.condition1_sell_bt = ops[operator1_sell[0]](
                #     getattr(self, momentum_sell[0]), float(value_sell))

            if len(operator2_sell) == 0 or len(price_sell) == 0 or len(volatility_sell) == 0:
                self.condition2_sell_bt = True
            else:
                self.condition2_sell_bt = eval(
                    f'self.data.{price_sell[0]} {operator2_sell[0]} self.{volatility_sell[0]}')
                # st.write('Operator is', operator2_buy[0])
                # # st.write('Type of the Operator is',
                #          type(operator2_buy[0]))
                #! working one on operator!
                # self.condition2_buy_bt = eval(
                #     f'self.data.Close {operator2_buy[0]} self.Upper')

            if len(operator3_sell) == 0 or len(trend1_sell) == 0 or len(trend2_sell) == 0:
                self.condition3_sell_bt = True
            else:
                if operator3_sell[0] == 'crossdown':
                    self.condition3_sell_bt = eval(
                        f'crossover (self.{trend2_sell[0]}, self.{trend1_sell[0]})')
                else:
                    self.condition3_sell_bt = eval(
                        f'self.data.{trend1_sell[0]} {operator3_sell[0]} self.{trend2_sell[0]}')

            if len(operator4_sell) == 0 or len(price1_sell) == 0 or len(trend3_sell) == 0:
                self.condition4_sell_bt = True
            else:
                if operator4_sell[0] == 'crossdown':
                    self.condition4_sell_bt = eval(
                        f'crossover (self.data.{price1_sell[0]}, self.{trend3_sell[0]})')
                else:
                    self.condition4_sell_bt = eval(
                        f'self.data.{price1_sell[0]} {operator4_sell[0]} self.{trend3_sell[0]}')

            # self.condition4_sell_bt = True
            # if len(operator4_sell) == 0 or len(price1_comp_sell) == 0 or len(price2_comp_sell) == 0:
            #     self.condition4_sell_bt = True
            # else:
            #     self.condition4_sell_bt = eval(
            #         f'self.{price1_comp_buy[0]}[-1] {operator4_sell[0]} self.{price2_comp_sell[0]}[-2]')

           #--------------------------------------------------------------------------------------------#
            # Define whether there is no input
            self.empty_buy = type(self.condition1_buy_bt) == bool and type(self.condition2_buy_bt) == bool and type(
                self.condition3_buy_bt) == bool and type(self.condition4_buy_bt) == bool

            if self.empty_buy == True:
                st.write('No Buy Criteria is selected!')

            self.empty_sell = type(self.condition1_sell_bt) == bool and type(self.condition2_sell_bt) == bool and type(
                self.condition3_sell_bt) == bool and type(self.condition4_sell_bt) == bool

            if self.empty_sell == True:
                st.write('No Sell Criteria is selected!')

           #--------------------------------------------------------------------------------------------#
            # Define criteria and holding
            st.write(
                'The default behaivor is system will Buy/Sell whenever the criteria is met, regardless position status.')
            agree_buy = st.checkbox(
                'Buy only when there is no position', key='check_buy')
            if agree_buy:
                self.decision_buy = 'not self.position'  # Not in a position
                # st.write('Not self.position value', self.decision_buy)
            else:
                self.decision_buy = 'True'

            agree_sell = st.checkbox(
                'Sell only when there is a position', key='check_sell')
            if agree_sell:
                self.decision_sell = 'self.position'
                # st.write('Self.position value', self.decision_sell)
            else:  # Default value
                self.decision_sell = 'True'

        def next(self):
            #! Put in condition3 inside one more time is for the 'crossover' function
            if len(operator3_buy) == 0 or len(trend1_buy) == 0 or len(trend2_buy) == 0:
                self.condition3_buy_bt = True
            else:
                if operator3_buy[0] == 'crossup':
                    self.condition3_buy_bt = eval(
                        f'crossover(self.{trend1_buy[0]}, self.{trend2_buy[0]})')
                else:
                    self.condition3_buy_bt = eval(
                        f'self.{trend1_buy[0]} {operator3_buy[0]} self.{trend2_buy[0]}')
                    # st.write('Condition 3', self.condition3_buy_bt)

            if len(operator4_buy) == 0 or len(price1_buy) == 0 or len(trend3_buy) == 0:
                self.condition4_buy_bt = True
            else:
                if operator4_buy[0] == 'crossup':
                    self.condition4_buy_bt = eval(
                        f'crossover(self.data.{price1_buy[0]}, self.{trend3_buy[0]})')
                else:
                    self.condition4_buy_bt = eval(
                        f'self.data.{price1_buy[0]} {operator4_buy[0]} self.{trend3_buy[0]}')

            if len(operator3_sell) == 0 or len(trend1_sell) == 0 or len(trend2_sell) == 0:
                self.condition3_sell_bt = True
            else:
                if operator3_sell[0] == 'crossdown':
                    self.condition3_sell_bt = eval(
                        f'crossover (self.{trend2_sell[0]}, self.{trend1_sell[0]})')
                else:
                    self.condition3_sell_bt = eval(
                        f'self.{trend1_sell[0]} {operator3_sell[0]} self.{trend2_sell[0]}')

            if len(operator4_sell) == 0 or len(price1_sell) == 0 or len(trend3_sell) == 0:
                self.condition4_sell_bt = True
            else:
                if operator4_sell[0] == 'crossdown':
                    self.condition4_sell_bt = eval(
                        f'crossover (self.data.{price1_sell[0]}, self.{trend3_sell[0]})')
                else:
                    self.condition4_sell_bt = eval(
                        f'self.data.{price1_sell[0]} {operator4_sell[0]} self.{trend3_sell[0]}')

            if self.empty_buy != True and self.condition1_buy_bt and self.condition2_buy_bt and self.condition3_buy_bt and self.condition4_buy_bt and eval(self.decision_buy):
                # if self.RSI <= 25:
                # if ops[operator3_buy[0]](self.__dict__[trend1_buy[0]], self.__dict__[trend2_buy[0]]):
                self.buy()
                # if not self.position:
                #     # print('No position and I will buy now')
                #     # print('met criteria', not self.position)
                #     self.buy()

            if self.empty_sell != True and self.condition1_sell_bt and self.condition2_sell_bt and self.condition3_sell_bt and self.condition4_sell_bt and eval(self.decision_sell):
                # if self.RSI <= 25:
                # if ops[operator3_buy[0]](self.__dict__[trend1_buy[0]], self.__dict__[trend2_buy[0]]):
                self.sell()

            # if self.condition1_sell_bt and self.condition2_sell_bt and self.condition3_sell_bt and self.condition4_sell_bt:
            #     # if ops[operator3_buy[0]](self.__dict__[trend1_buy[0]], self.__dict__[trend2_buy[0]]):
            #     self.position.close()
                # if not self.position:
                #     # print('No position and I will buy now')
                #     # print('met criteria', not self.position)
                #     self.buy()

            # if self.rsi < 30:
            #     self.buy()

            # elif self.rsi > 70:
            #     self.position.close()

            # if crossover(self.sma1, self.sma2):
            #     self.buy()

            # elif crossover(self.sma2, self.sma1):
            #     self.position.close()

            #--------------------------------------------------------------------------------------------#
            # Define Trading related parameters
    amount = st.number_input('Initial Invested Amount', value=100000)
    bt = Backtest(data, Custom, cash=amount,
                  commission=0, exclusive_orders=True)
    output = bt.run()
    output.to_csv('temp.csv')
    temp = pd.read_csv('temp.csv')
    temp.rename(columns={'Unnamed: 0': 'Item', '0': 'Value'}, inplace=True)
    # temp.Value.iloc[3:14] = temp.Value.iloc[3:14].astype(
    #     float).map('{:,.2f}'.format)
    # temp.Value.iloc[18:21] = temp.Value.iloc[18:21].astype(
    #     float).map('{:,.2f}'.format)
    # temp.Value.iloc[24:26] = temp.Value.iloc[24:26].astype(
    #     float).map('{:,.2f}'.format)
    temp.Value.iloc[pd.np.r_[3:14, 18:21, 24:26]] = temp.Value.iloc[pd.np.r_[3:14, 18:21, 24:26]].astype(
        float).map('{:,.2f}'.format)
    # temp.Value[ temp.Value[3:3].astype(float).map('{:,.2f}%'.format)
    # # temp.Value[18:21].astype(float).map('{:,.2f}'.format)
    # temp.Value[24:26].astype(float).map('{:,.2f}'.format)
    # st.write('Backtest Result', output.to_frame())
    st.subheader('Backtest Result')
    # temp.iloc[3:14]
    st.write(temp)
    # st.write('Trade Details', output.stats['_trades'])

    bt.plot(open_browser=False)

    # figure = bt.plot()
    # # show the plot in Streamlit
    # st.pyplot(figure)

    import streamlit.components.v1 as components

    # >>> import plotly.express as px
    # >>> fig = px.box(range(10))
    # >>> fig.write_html('test.html')

    st.subheader("Backtest Chart")

    HtmlFile = open("Custom.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    # st.write(source_code)
    components.html(source_code, height=800)

    # figure = bt.plot()[0][0]
    # #     figure = cerebro.plot(style='candle')[0][0]
    # #     # show the plot in Streamlit
    # st.pyplot(figure)
    # # %matplotlib widget
    # cerebro = bt.Cerebro()

    # # Create Data Feed
    # # data_bt = bt.feeds.YahooFinanceCSVData(
    # #    dataname='TSLA.csv',
    # # Do not pass values before this date
    # #    fromdate=datetime.datetime(2018, 1, 1),
    # # Do not pass values after this date
    # #    todate=datetime.datetime(2021, 10, 2),
    # #    reverse=False)

    # # # Use a backend that doesn't display the plot to the user
    # # we want only to display inside the Streamlit page

    # # data_temp = yf.download(
    # #     'TSLA', '2019-01-01', '2021-12-28', auto_adjust=True)
    # data_bt = bt.feeds.PandasData(dataname=data_raw)

    # # st.write('Data Temp is', data_temp)
    # # st.write('Data Raw is', data_raw)
    # # Add Data Feed
    # st.write('Data Feed is', data_bt)
    # cerebro.adddata(data_bt)

    # with st.form(key='backtest_selection'):
    #     cash = st.number_input('Initial Fund', value=100000)
    #     cerebro.broker.setcash(cash)
    #     submit = st.form_submit_button('Backtest!')

    # if submit:
    #     class MyStrategy(bt.Strategy):

    #         def log(self, txt, dt=None):
    #             ''' Logging function for this strategy'''
    #             dt = dt or self.datas[0].datetime.date(0)
    #             st.write('%s, %s' % (dt.isoformat(), txt))

    #         def __init__(self):
    #             self.rsi = bt.indicators.RelativeStrengthIndex()
    #             self.bb = bt.indicators.BollingerBands()
    #             self.ema_20 = bt.indicators.ExponentialMovingAverage(
    #                 self.data.close, period=20)
    #             self.ema_120 = bt.indicators.ExponentialMovingAverage(
    #                 self.data.close, period=120)

    #         #   self.order = None
    #         #   self.buy_signal

    #         def next(self):

    #             if self.data.close[0] < self.bb.lines.bot and self.rsi[0] < 35 and self.ema_20 > self.ema_120:
    #                 self.order = self.buy()
    #                 self.log('BUY CREATE, %.2f' % self.data.close[0])

    #             if self.data.close[0] > self.bb.lines.top and self.rsi[0] > 65 and self.ema_20 < self.ema_120 and self.position:
    #                 self.order = self.close(percents=100)
    #                 self.log('Close, %.2f' % self.data.close[0])

    #     # Add Strategy
    #     cerebro.addstrategy(MyStrategy)
    #     cerebro.addsizer(bt.sizers.PercentSizer, percents=30)

    #     before_value = cerebro.broker.getvalue()
    #     st.write('Starting Portfilo Value: ' '{0:,.2f}'.format(before_value))

    #     cerebro.run()

    #     after_value = cerebro.broker.getvalue()
    #     st.write('Final Portfilo Value: ' '{0:,.2f}'.format(after_value))
    #     profit = after_value - before_value
    #     profit_rate = (after_value - before_value)/before_value
    #     st.write('Profit amount is: '+'{0:,.2f}'.format(profit))
    #     st.write('Profit Rate is: ' + '{0:,.2f}%'.format((profit_rate)*100))

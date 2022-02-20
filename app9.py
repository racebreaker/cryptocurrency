# app9.py - Valuation
import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial
import yahoo_fin.stock_info as si
import yfinance as yf


def app():
    st.title('Fundamental Analysis - Company Valuation (DCF)')
    st.markdown("***")
    # new_title = '<p style="font-size: 20px;">**Valuation - DCF Calculation**</p>'
    # st.markdown(new_title, unsafe_allow_html=True)
    st.write("""
        - Assumptions
            1. Usd FCF number to calculate Enterprise value. It will minus the debt number to get equity intrinsic value
            2. FCF number will be derived from Cash flow statement directly
            3. Forecast FCF directly (using analyst forecast) rather than forecast the financial statement
            """)

    quote_input = st.text_input('Please Input Stock Quote:', value='AAPL')
    # st.write("Quote Input value is", quote_input == '')

    # Take the first value in Dropdown_dcf list
    # for quote_dcf in dropdown_dcf:
    #     if quote_dcf != '':
    #         fcfe = overview_info.loc[overview_info.Quote ==
    #                                  dropdown_dcf[0]]['FCFE (ttm)'].values[0]
    #         st.write('Quote is: ' + dropdown_dcf[0])
    # fcfe_input = st.text_input('FCFE (Levered Free Cash Flow) Value is:', value = fcfe if dropdown_radar !='' else 0)
    # st.write('FCFE (Levered Free Cash Flow) Value is:', value = fcfe if dropdown_radar !='' else 0)
    #------------------------------------------------------------------------------------------#

    # fcfe_real = float(fcfe[:-1])
    # st.write('FCFE Value is', fcfe_real)

    # Calculate FCF from Cash Flow statement
    if quote_input != '':
        st.subheader('Step 1 - Retrieve and Forecast FCF')
        ticker = yf.Ticker(quote_input)
        fcf = ticker.quarterly_cashflow.loc['Total Cash From Operating Activities'] + \
            ticker.quarterly_cashflow.loc['Capital Expenditures']
        st.write('FCF (TTM) Value is', sum(fcf)/1000000000)
        st.write('FCF Date is', fcf.index[0])

        FCF = {}
        FCF[0] = float(st.text_input(
            'Please Enter FCF (TTM) Value:', value=sum(fcf)/1000000000))
        # FCF[0] = fcfe_real
        # st.write('FCFE is ', fcfe)

        # st.caption('Key Number Reference')
        # dcf_fcfe = overview_info.loc[overview_info.Quote == dropdown_dcf[0]][[
        #     'Quote', 'Rev (ttm)', 'Net Income (ttm)', 'FCFE (ttm)']]
        # st.write(dcf_fcfe)

        # st.caption('Key Growth Number Reference')
        # dcf_growth = overview_info[overview_info.Quote == dropdown_dcf[0]][['Quote', 'Qtr Rev Growth',
        #                                                                     'Cur Yr Est', 'Next Yr Est', 'Past 5 Yr', 'Next 5 Yr Est']]
        # st.write(dcf_growth)
        # st.write(float(overview_info[overview_info.Quote ==
        #          dropdown_dcf[0]]['Next 5 Yr Est'].iloc[0][:-1])/100)
        import yahoo_fin.stock_info as si
        yahoo_growth = si.get_analysts_info(quote_input)['Growth Estimates']
        growth_est = float(yahoo_growth.loc[yahoo_growth['Growth Estimates']
                                            == 'Next 5 Years (per annum)'][quote_input].values[0][:-1])/100

        # growth_est = float(overview_info[overview_info.Quote ==
        #                                  dropdown_dcf[0]]['Next 5 Yr Est'].values[0][:-1])/100
        growth_5y = st.text_input(
            'Please Enter FCF Growth Rate (First 5 years):', value=growth_est)

        # Calculate the 5-year FCFE number
        # if growth_rate_input != '':
        growth_5y_real = float(growth_5y)
        st.write('Growth Rate (First 5 year) is', growth_5y_real)

        growth_10y = st.text_input(
            'Please Enter FCF Growth Rate (5-10 years):', value=growth_est*0.75)
        growth_10y_real = float(growth_10y)
        st.write('Growth Rate (5-10 years) is', growth_10y_real)

        growth_20y_real = 0.0418

        for i in range(1, 6):
            print(i)
            FCF[i] = FCF[i-1]*(1+growth_5y_real)
            st.write(f'Year {i} - FCF value {FCF[i]:.2f}')

        FCF[0] = 0
        FCF_list_5y = list(FCF.values())
        st.write('FCF 10-year length is', len(FCF_list_5y))

        for i in range(6, 11):
            print(i)
            FCF[i] = FCF[i-1]*(1+growth_10y_real)
            st.write(f'Year {i} - FCF value {FCF[i]:.2f}')

        FCF[0] = 0
        FCF_list_10y = list(FCF.values())
        st.write('FCF 10-year length is', len(FCF_list_10y))

        for i in range(11, 21):
            print(i)
            FCF[i] = FCF[i-1]*(1+growth_20y_real)
            st.write(f'Year {i} - FCF value {FCF[i]:.2f}')
        FCF_list_20y = list(FCF.values())
        st.write('FCF 20-year length is', len(FCF_list_20y))

        #------------------------------------------------------------------------------------------#
        st.subheader(
            'Step 2 - Calculate WACC, Formula: WACC = E/(D+E)*rE + (D/(D+E))*rD*(1-t), rE = rF + (rM - rF)*Beta')

        ticker = yf.Ticker(quote_input)
        if 'Long Term Debt' in ticker.balance_sheet.index and 'Short Long Term Debt' in ticker.balance_sheet.index:
            if not ticker.balance_sheet.loc['Short Long Term Debt'][0] > 0:
                ticker.balance_sheet.loc['Short Long Term Debt'][0] = 0
                # st.write('Short Long Term Debt value is 0')
            elif not ticker.balance_sheet.loc['Long Term Debt'][0] > 0:
                ticker.balance_sheet.loc['Long Term Debt'][0] = 0
                # st.write('Long Term Debt value is 0')

            D = ticker.balance_sheet.loc['Long Term Debt'] + \
                ticker.balance_sheet.loc['Short Long Term Debt']
            rD = -ticker.financials.loc['Interest Expense'] / D
            st.write('Long Term Debt is',
                     ticker.balance_sheet.loc['Long Term Debt'][0])
            st.write('Short Long Term Debt',
                     ticker.balance_sheet.loc['Short Long Term Debt'][0])
            st.write('Total Debt Value is', D[0])
            # print('Debt Value is', D[0])
        else:
            rD = [0]
            D = [0]
            st.write(
                'There are No Long Term Debt and No Short Long Term Debt items in the Balance Sheet')
        # print('Cost of Debt, rD is', rD[0])
        st.write('Cost of Debt, rD is', rD[0])
        st.write('Debt Value is', D[0])

        t = ticker.financials.loc['Income Tax Expense'] / \
            ticker.financials.loc['Income Before Tax']
        # print('Tax Rate is', t[0])
        st.write('Tax Rate is', t[0])

        import yahoo_fin.stock_info as si
        quote_table = si.get_quote_table(
            quote_input, dict_result=False)

        market_cap = quote_table.loc[quote_table.attribute ==
                                     'Market Cap'].value.values[0]
        if market_cap[-1] == 'T':
            E = float(market_cap[:-1])*1000000000000
        elif market_cap[-1] == 'B':
            E = float(market_cap[:-1])*1000000000
        # print('Equity Value is', E)
        st.write('Equity Value is', E)

        # (D[0]/(D[0]+E))*rD[0]*(1-t[0])

        if si.get_live_price('^TNX')/100 > 0:  # rF sometimes will get nan
            rF = si.get_live_price('^TNX')/100
        else:
            rF = 0.015
            st.write(
                'Can not retrieve rF value and use pre-define value instead')

        # print('10 Year Bond Yield Rate is', rF)
        st.write('10 Year Bond Yield Rate is', rF)
        rM = 0.0745
        # print('Market Return Rate is', rM)
        st.write('Market Return Rate is', rM)

        Beta = quote_table.loc[quote_table.attribute ==
                               'Beta (5Y Monthly)'].value.values[0]
        # print('Beta Value is', Beta)
        st.write('Beta Value is', Beta)
        beta_input = st.number_input('Please Enter Beta Rate:', value=Beta)

        rE = rF + (rM - rF)*beta_input
        # print('Cost of Equity, rE is', rE)
        st.write('Cost of Equity, rE is', rE)

        st.write(f'Cost of Equity weightage is {E/(D[0]+E)*100:.2f}%')

        WACC = E/(D[0]+E)*rE + (D[0]/(D[0]+E))*rD[0]*(1-t[0])
        # print('WACC Value is', WACC)
        st.write('WACC Value is', WACC)

        wacc_input = st.text_input('Please Enter WACC Rate:', value=WACC)
        wacc_input_real = float(wacc_input)

        #------------------------------------------------------------------------------------------#
        st.subheader(
            'Step 3 - Calculate Terminal Value, Formula: TV = FCFn*(1+g)/(WACC-g)')
        ltgrowth_rate_input = st.text_input(
            'Please Enter Long Term Growth Rate:', value=0.02)
        ltgrowth_rate_input_real = float(ltgrowth_rate_input)

        terminal_value_5y = (FCF[5] * (1 + ltgrowth_rate_input_real)) / \
            (wacc_input_real - ltgrowth_rate_input_real)
        st.write('Terminal Value 5-year is', terminal_value_5y)

        terminal_value_10y = (FCF[10] * (1 + ltgrowth_rate_input_real)) / \
            (wacc_input_real - ltgrowth_rate_input_real)
        st.write('Terminal Value 10-year is', terminal_value_10y)

        #------------------------------------------------------------------------------------------#
        st.subheader(
            'Step 4 - Calculate Discount NPV and Terminal Value, Formula: NPV = CF1/(1+r)^1 + CF2/(1+r)^2 +...+ CFn/(1+r)^n')
        npv_5y = numpy_financial.npv(wacc_input_real, FCF_list_5y)
        # If future cashflows are used, the first cashflow values[0] must be zeroed and added to the net present value of the future cashflows
        st.write('Net Present Value 5-year is', npv_5y)
        terminal_value_discounted_5y = terminal_value_5y / \
            (1+wacc_input_real)**6  # Start from the 11th year
        st.write('Discounted Terminal Value 5-year is',
                 terminal_value_discounted_5y)
        st.write(
            f'Terminal value weightage is {terminal_value_discounted_5y/(terminal_value_discounted_5y + npv_5y)*100:.2f}%')

        npv_10y = numpy_financial.npv(wacc_input_real, FCF_list_10y)
        st.write('Net Present Value 10-year is', npv_10y)
        terminal_value_discounted_10y = terminal_value_10y / \
            (1+wacc_input_real)**11  # Start from the 11th year
        st.write('Discounted Terminal Value 10-year is',
                 terminal_value_discounted_10y)
        st.write(
            f'Terminal value weightage is {terminal_value_discounted_10y/(terminal_value_discounted_10y + npv_10y)*100:.2f}%')

        npv_20y = numpy_financial.npv(wacc_input_real, FCF_list_20y)
        st.write('Net Present Value 10-year is', npv_10y)
        # npvnew = numpy_financial.npv(wacc_input_real, FCF_list)
        # st.write('New Net Present Value is', npvnew)
        st.write('Discounted 11-20 year Value is', npv_20y-npv_10y)
        st.write(
            f'Discounted 11-20 year Value weightage is {(npv_20y-npv_10y)/npv_20y*100:.2f}%')
        #------------------------------------------------------------------------------------------#
        st.subheader(
            'Step 5 - Calculate Intrinsic Value per Share, Formula: Intrinsic_Value = NPV + Terminal_Discounted_Value, Equity Value = Enterprise Value - Debt Value + Cash')
        intrinsic_5y = npv_5y + terminal_value_discounted_5y
        intrinsic_10y = npv_10y + terminal_value_discounted_10y
        # st.write('Intrinsic Value 5-year is', intrinsic_5y)
        # st.write('Intrinsic Value 10-year is', intrinsic_10y)
        # st.write('Intrinsic Value 20-year is', npv_20y)

        if type(si.get_stats(quote_input).loc[si.get_stats(quote_input)[
                'Attribute'] == 'Implied Shares Outstanding 6']['Value'].values[0]) == float:
            share_ost = si.get_stats(quote_input).loc[si.get_stats(quote_input)[
                'Attribute'] == 'Shares Outstanding 5']['Value'].values[0]
        else:
            share_ost = si.get_stats(quote_input).loc[si.get_stats(quote_input)[
                'Attribute'] == 'Implied Shares Outstanding 6']['Value'].values[0]
        # share_ost = overview_info.loc[overview_info.Quote ==
        #                                 dropdown_dcf[0]]['Shares Outstanding'].values[0]
        share_ost_input = st.text_input(
            'Please Enter Number of Share Outstanding:', value=share_ost)

        if share_ost_input[-1] == 'B':
            share_ost_real = float(share_ost_input[:-1]) * 1000000000
        elif share_ost_input[-1] == 'M':
            share_ost_real = float(share_ost_input[:-1]) * 1000000

        st.write('Share Oustanding Value is', share_ost_real)
        debt_pershare = D[0] / share_ost_real
        st.write('Debt Per Share is', debt_pershare)
        cash = ticker.balance_sheet.loc['Cash']
        cash_pershare = cash[0] / share_ost_real
        st.write('Cash Per Share is', cash_pershare)

        intrinsic_pershare_5y = intrinsic_5y * \
            1000000000 / share_ost_real - debt_pershare + cash_pershare
        intrinsic_pershare_10y = intrinsic_10y * \
            1000000000 / share_ost_real - debt_pershare + cash_pershare
        intrinsic_pershare_20y = npv_20y * 1000000000 / \
            share_ost_real - debt_pershare + cash_pershare

        st.write('Intrinsic Value 5-year Per Share is',
                 intrinsic_pershare_5y)
        st.write('Intrinsic Value 10-year Per Share is',
                 intrinsic_pershare_10y)
        st.write('Intrinsic Value 20-year Per Share is',
                 intrinsic_pershare_20y)

        price = si.get_live_price(quote_input)
        st.write('Current Stock price is', price)

        ratio = price/intrinsic_pershare_5y

        st.write('Compared with 5-year DCF result: ')
        if ratio <= 1:
            st.write(
                f'Currently the Stock is Under Value {(1-float(ratio))*100:.2f}%')
        if ratio > 1:
            st.write(
                f'Currently the Stock is Overvalue Value {(float(ratio)-1)*100:.2f}%')

# app1.py
import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot
import yahoo_fin.stock_info as si
import datetime  # This it to add timestamp in the filename
# datestamp = datetime.datetime.today().strftime ('%Y-%m-%d')
from PIL import Image


def app():
    st.title('Fundamental Analysis')

    import sqlite3
    conn = sqlite3.connect(r'C:\Temp\Streamlit\WebData.db',
                           check_same_thread=False)
    # print("Database has connected successfully")
    c = conn.cursor()

    # Create Table based on Schema - Create once is enough
    # c.execute("""CREATE TABLE IF NOT EXISTS overview \
    # (Quote TEXT primary key, "Sector" TEXT, 'Mkt Cap' TEXT, 'Rev (ttm)' TEXT, 'Net Income (ttm)' TEXT\
    # 'Qtr Rev Growth' TEXT, 'Qtr Earning Growth' TEXT, 'Cur Qtr Est' TEXT, 'Next Qtr Est' TEXT, 'Cur Yr Est' TEXT, 'Next Yr Est' TEXT, \
    # 'ROE (ttm)' TEXT, 'ROA (ttm)' TEXT, 'Gross Margin (ttm)' TEXT, 'Operating Margin (ttm)' TEXT, 'Profit Margin' TEXT, \
    # 'Trailing P/E' TEXT, 'Forward P/E' TEXT, 'Price/Sales (ttm)' TEXT, 'PEG Ratio (5 yr expected)' TEXT, \
    # 'Total Debt/Equity (mrq)' TEXT, 'Current Ratio (mrq)' TEXT, 'Beta (5Y Monthly)' REAL, \
    # 'Asset Turnover' TEXT)""")
    # conn.commit()
    # Debug
    # st.write("Datebase and table has been created successfully!")

    ###############################################################################################################
    # Section 1 - Company Scoring - Radar Chart
    overview_info = pd.read_sql("""SELECT * FROM overview""", conn)
    quote_exist = overview_info['Quote'].sort_values().values.tolist()

    st.header('1. Company Scoring - Radar Chart')

    fig = go.Figure()
    categories = ['Valuation', 'Growth', 'Profitability',
                  'Safety', 'Operational Efficiency']

    radar_display_column = {'Quote': [], 'Trailing P/E': [], 'Qtr Rev Growth': [],
                            'Gross Margin (ttm)': [], 'Current Ratio (mrq)': [], 'Asset Turnover': []}
    radar_display = pd.DataFrame(radar_display_column)
    radar_display = radar_display.set_index('Quote')

    # quote_exist = overview_info['Quote'].values.tolist().sort_values()
    # ! sort_values first, then convert to a list
    # quote_exist = overview_info['Quote'].sort_values().values.tolist()

    # ! No need to resign to quote_exist
    quote_exist.insert(0, 'Not in the list')

    expander_criteria = st.expander(
        label='Please select Stock Quote and Valuation Ratio:')
    with expander_criteria:
        quote_select = st.multiselect(
            '', quote_exist, default='AAPL', key='Quote Selection')  # -- Take the input from above multi-select
        col1, col2 = st.columns(2)
        with col1:
            val_option = st.selectbox('Choose Valuation Ratio:', ('PE', 'PS'))
            st.write('You selected:', val_option)
        with col2:
            growth_option = st.selectbox(
                'Choose Growth Ratio:', ('Qtr Earning Growth', 'Qtr Rev Growth'))
            st.write('You selected:', growth_option)

        image = Image.open('PE.jpg')
        st.image(image, caption='When to use Valuation Ratio such as PE or PS')

    if quote_select != []:
        if 'Not in the list' in quote_select:  # ! Just in case 'Not in the list' is not the first one
            string = st.text_input(
                'Please key in list of Stock Quote you want to search, separated by Comma and No space:')
            # st.write('String value is', string)
            if string != '':
                quotes = string.split(",")  # Remove the comma, if there is any
                for quote in quotes:
                    st.write('The quote keyed in is', quote)
                    analysts_info = si.get_analysts_info(quote)
                    company_info = si.get_company_info(quote)
                    company_info.reset_index(inplace=True)

                    stats = si.get_stats(quote)
                    stats_valuation = si.get_stats_valuation(quote)
                    quote_table = si.get_quote_table(quote, dict_result=False)

                    sector = company_info.loc[company_info.Breakdown ==
                                              'sector'].Value.values[0]
                    market_cap = quote_table.loc[quote_table.attribute ==
                                                 'Market Cap'].value.values[0]
                    revenue = stats.loc[stats.Attribute ==
                                        'Revenue (ttm)'].Value.values[0]
                    fcfe = stats.loc[stats.Attribute ==
                                     'Levered Free Cash Flow (ttm)'].Value.values[0]

                    # Valuation
                    trailing_pe = stats_valuation.loc[stats_valuation[0]
                                                      == 'Trailing P/E'][1].values[0]
                    trailing_pe_real = float(trailing_pe)
                    # forward_pe = stats_valuation.loc[stats_valuation[0] == 'Forward P/E 1'][1].values[0]
                    forward_pe = stats_valuation.loc[stats_valuation[0]
                                                     == 'Forward P/E'][1].values[0]
                    ps = stats_valuation.loc[stats_valuation[0]
                                             == 'Price/Sales (ttm)'][1].values[0]
                    # peg = stats_valuation.loc[stats_valuation[0] == 'PEG Ratio (5 yr expected) 1'][1].values[0]
                    peg = stats_valuation.loc[stats_valuation[0]
                                              == 'PEG Ratio (5 yr expected)'][1].values[0]

                    # Growth
                    rev_growth_q = stats.loc[stats.Attribute ==
                                             'Quarterly Revenue Growth (yoy)'].Value.values[0]
                    rev_growth_q_real = float(rev_growth_q[:-1])
                    earning_growth_q = stats.loc[stats.Attribute ==
                                                 'Quarterly Earnings Growth (yoy)'].Value.values[0]

                    # Reveun Growth Estimate - their columns values is not fixed
                    rev_est = analysts_info['Revenue Estimate']
                    for item in rev_est.columns[1:]:
                        # print(item)
                        if item.startswith('Current Qtr'):
                            column1 = item
                        elif item.startswith('Next Qtr'):
                            column2 = item
                        elif item.startswith('Current Year'):
                            column3 = item
                        elif item.startswith('Next Year'):
                            column4 = item

                    # print(column1, column2, column3, column4)
                    cqsg = rev_est.loc[rev_est['Revenue Estimate'] ==
                                       'Sales Growth (year/est)'][column1].values[0]
                    nqsg = rev_est.loc[rev_est['Revenue Estimate'] ==
                                       'Sales Growth (year/est)'][column2].values[0]
                    cysg = rev_est.loc[rev_est['Revenue Estimate'] ==
                                       'Sales Growth (year/est)'][column3].values[0]
                    nysg = rev_est.loc[rev_est['Revenue Estimate'] ==
                                       'Sales Growth (year/est)'][column4].values[0]

                    growth_est = analysts_info['Growth Estimates']
                    past_5y = growth_est.loc[growth_est['Growth Estimates']
                                             == 'Past 5 Years (per annum)'][quote].values[0]
                    next_5y = growth_est.loc[growth_est['Growth Estimates']
                                             == 'Next 5 Years (per annum)'][quote].values[0]

                    # Profitability
                    roe = stats.loc[stats.Attribute ==
                                    'Return on Equity (ttm)'].Value.values[0]

                    revenue_real = float(revenue[:-1])
                    gross_real = float(
                        stats.loc[stats.Attribute == 'Gross Profit (ttm)'].Value.values[0][:-1])
                    gross_margin = "{:.2f}".format(
                        gross_real/revenue_real*100)+'%'
                    gross_margin_real = float(gross_margin[:-1])

                    profit_margin = stats.loc[stats.Attribute ==
                                              'Profit Margin'].Value.values[0]
                    operating_margin = stats.loc[stats.Attribute ==
                                                 'Operating Margin (ttm)'].Value.values[0]

                    # Safety
                    debt_equity_ratio = stats.loc[stats.Attribute ==
                                                  'Total Debt/Equity (mrq)'].Value.values[0]
                    current_ratio = stats.loc[stats.Attribute ==
                                              'Current Ratio (mrq)'].Value.values[0]
                    current_ratio_real = float(current_ratio)*10
                    beta = quote_table.loc[quote_table.attribute ==
                                           'Beta (5Y Monthly)'].value.values[0]

                    # Operational Efficiency
                    roa = stats.loc[stats.Attribute ==
                                    'Return on Assets (ttm)'].Value.values[0]
                    roa_real = float(roa[:-1])
                    netincome = stats.loc[stats.Attribute ==
                                          'Net Income Avi to Common (ttm)'].Value.values[0]
                    netincome_real = float(netincome[:-1])
                    totalasset = netincome_real / roa_real * 100
                    asset_turnover = "{:.2f}".format(revenue_real/totalasset)
                    asset_turnover_real = float(asset_turnover)*100

                    # Others
                    share_ost = stats.loc[stats.Attribute ==
                                          'Shares Outstanding 5'].Value.values[0]

                    # position = len(overview)
                    # st.write('Current Row number is', position)
                    # overview.loc[position] = [quote, market_cap, revenue, rev_growth_q, roe, gross_margin, beta]

                    insert_sql = """REPLACE INTO overview (Quote, Sector, 'Mkt Cap', 'Rev (ttm)', 'Net Income (ttm)', 'FCFE (ttm)', \
                    'Qtr Rev Growth', 'Qtr Earning Growth', 'Cur Qtr Est', 'Next Qtr Est', 'Cur Yr Est', 'Next Yr Est', 'Past 5 Yr', 'Next 5 Yr Est',\
                    'ROE (ttm)', 'ROA (ttm)', 'Gross Margin (ttm)', 'Operating Margin (ttm)', 'Profit Margin', \
                    'Trailing P/E', 'Forward P/E', 'Price/Sales (ttm)', 'PEG Ratio (5 yr expected)', \
                    'Total Debt/Equity (mrq)', 'Current Ratio (mrq)', 'Beta (5Y Monthly)', \
                    'Asset Turnover', \
                    'Shares Outstanding')
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """
                    c.execute(insert_sql, (quote, sector, market_cap, revenue, netincome, fcfe,
                                           rev_growth_q, earning_growth_q, cqsg, nqsg, cysg, nysg, past_5y, next_5y,
                                           roe, roa, gross_margin, operating_margin, profit_margin,
                                           trailing_pe, forward_pe, ps, peg,
                                           debt_equity_ratio, current_ratio, beta,
                                           asset_turnover,
                                           share_ost))
                    conn.commit()
                    # Only after Database is refreshed, then update the Database
            overview_info = pd.read_sql("""SELECT * FROM overview""", conn)
            st.write(
                'Database is refreshed, please select the stock quote from dropdown list again')
        else:
            for quote in quote_select:
                # st.write(overview_info)
                trailing_pe = overview_info.loc[overview_info.Quote ==
                                                quote]['Trailing P/E'].values[0]
                if trailing_pe == None:
                    trailing_pe_real = 0
                else:
                    trailing_pe_real = float(trailing_pe)
                trailing_ps = overview_info.loc[overview_info.Quote ==
                                                quote]['Price/Sales (ttm)'].values[0]
                rev_growth_q = overview_info.loc[overview_info.Quote ==
                                                 quote]['Qtr Rev Growth'].values[0]
                rev_growth_q_real = float(rev_growth_q[:-1])
                earning_growth_q = overview_info.loc[overview_info.Quote ==
                                                     quote]['Qtr Earning Growth'].values[0]
                earning_growth_q_real = float(earning_growth_q[:-1])
                operating_margin = overview_info.loc[overview_info.Quote ==
                                                     quote]['Operating Margin (ttm)'].values[0]
                operating_margin_real = float(operating_margin[:-1])
                gross_margin = overview_info.loc[overview_info.Quote ==
                                                 quote]['Gross Margin (ttm)'].values[0]
                gross_margin_real = float(gross_margin[:-1])
                ps = overview_info.loc[overview_info.Quote ==
                                       quote]['Price/Sales (ttm)'].values[0]
                ps_real = float(ps)

                current_ratio = overview_info.loc[overview_info.Quote ==
                                                  quote]['Current Ratio (mrq)'].values[0]
                current_ratio_real = float(current_ratio)*10
                asset_turnover = overview_info.loc[overview_info.Quote ==
                                                   quote]['Asset Turnover'].values[0]
                asset_turnover_real = float(asset_turnover)*100

                radar_display.loc[quote] = [trailing_pe, rev_growth_q,
                                            gross_margin, current_ratio, asset_turnover]

                if val_option == 'PE':
                    val_real = trailing_pe_real
                elif val_option == 'PS':
                    val_real = trailing_ps

                if growth_option == 'Qtr Rev Growth':
                    growth_real = rev_growth_q_real
                if growth_option == 'Qtr Earning Growth':
                    growth_real = earning_growth_q_real

                fig.add_trace(go.Scatterpolar(
                    r=[val_real, growth_real, gross_margin_real,
                       current_ratio_real, asset_turnover_real],
                    theta=categories,
                    fill='toself',
                    name=quote))

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100])),
                    title={
                        'text': 'Revenue Quarterly - '+quote,
                        'y': 0.9,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                    showlegend=True
                )

            st.plotly_chart(fig)
            st.write(radar_display)
  # Scenario 1 - if quote exists in the Database, will retrieve data from Database
#     st.write('Quotes are', quotes)
#    for quote in quotes:
#         if quote != '':
#             if quote in quote_exist:
#                 st.write('The quote keyed in is', quote +
#                          ' and it is in the Database')
#                 trailing_pe = overview_info.loc[overview_info.Quote ==
#                                                 quote]['Trailing P/E'].values[0]
#                 if trailing_pe == None:
#                     trailing_pe_real = 0
#                 else:
#                     trailing_pe_real = float(trailing_pe)
#                 rev_growth_q = overview_info.loc[overview_info.Quote ==
#                                                  quote]['Qtr Rev Growth'].values[0]
#                 rev_growth_q_real = float(rev_growth_q[:-1])
#                 operating_margin = overview_info.loc[overview_info.Quote ==
#                                                      quote]['Operating Margin (ttm)'].values[0]
#                 operating_margin_real = float(operating_margin[:-1])
#                 gross_margin = overview_info.loc[overview_info.Quote ==
#                                                  quote]['Gross Margin (ttm)'].values[0]
#                 gross_margin_real = float(gross_margin[:-1])
#                 ps = overview_info.loc[overview_info.Quote ==
#                                        quote]['Price/Sales (ttm)'].values[0]
#                 ps_real = float(ps)

#                 current_ratio = overview_info.loc[overview_info.Quote ==
#                                                   quote]['Current Ratio (mrq)'].values[0]
#                 current_ratio_real = float(current_ratio)*10
#                 asset_turnover = overview_info.loc[overview_info.Quote ==
#                                                    quote]['Asset Turnover'].values[0]
#                 asset_turnover_real = float(asset_turnover)*100

#             else:
#                 st.write('The quote keyed in is', quote +
#                          ' and it is NOT in the Database')
#                 analysts_info = si.get_analysts_info(quote)
#                 company_info = si.get_company_info(quote)
#                 company_info.reset_index(inplace=True)

#                 stats = si.get_stats(quote)
#                 stats_valuation = si.get_stats_valuation(quote)
#                 quote_table = si.get_quote_table(quote, dict_result=False)

#                 sector = company_info.loc[company_info.Breakdown ==
#                                           'sector'].Value.values[0]
#                 market_cap = quote_table.loc[quote_table.attribute ==
#                                              'Market Cap'].value.values[0]
#                 revenue = stats.loc[stats.Attribute ==
#                                     'Revenue (ttm)'].Value.values[0]
#                 fcfe = stats.loc[stats.Attribute ==
#                                  'Levered Free Cash Flow (ttm)'].Value.values[0]

#                 # Valuation
#                 trailing_pe = stats_valuation.loc[stats_valuation[0]
#                                                   == 'Trailing P/E'][1].values[0]
#                 trailing_pe_real = float(trailing_pe)
#                 # forward_pe = stats_valuation.loc[stats_valuation[0] == 'Forward P/E 1'][1].values[0]
#                 forward_pe = stats_valuation.loc[stats_valuation[0]
#                                                  == 'Forward P/E'][1].values[0]
#                 ps = stats_valuation.loc[stats_valuation[0]
#                                          == 'Price/Sales (ttm)'][1].values[0]
#                 # peg = stats_valuation.loc[stats_valuation[0] == 'PEG Ratio (5 yr expected) 1'][1].values[0]
#                 peg = stats_valuation.loc[stats_valuation[0]
#                                           == 'PEG Ratio (5 yr expected)'][1].values[0]

#                 # Growth
#                 rev_growth_q = stats.loc[stats.Attribute ==
#                                          'Quarterly Revenue Growth (yoy)'].Value.values[0]
#                 rev_growth_q_real = float(rev_growth_q[:-1])
#                 earning_growth_q = stats.loc[stats.Attribute ==
#                                              'Quarterly Earnings Growth (yoy)'].Value.values[0]

#                 # Reveun Growth Estimate - their columns values is not fixed
#                 rev_est = analysts_info['Revenue Estimate']
#                 for item in rev_est.columns[1:]:
#                     # print(item)
#                     if item.startswith('Current Qtr'):
#                         column1 = item
#                     elif item.startswith('Next Qtr'):
#                         column2 = item
#                     elif item.startswith('Current Year'):
#                         column3 = item
#                     elif item.startswith('Next Year'):
#                         column4 = item

#                 # print(column1, column2, column3, column4)
#                 cqsg = rev_est.loc[rev_est['Revenue Estimate'] ==
#                                    'Sales Growth (year/est)'][column1].values[0]
#                 nqsg = rev_est.loc[rev_est['Revenue Estimate'] ==
#                                    'Sales Growth (year/est)'][column2].values[0]
#                 cysg = rev_est.loc[rev_est['Revenue Estimate'] ==
#                                    'Sales Growth (year/est)'][column3].values[0]
#                 nysg = rev_est.loc[rev_est['Revenue Estimate'] ==
#                                    'Sales Growth (year/est)'][column4].values[0]

#                 # Profitability
#                 roe = stats.loc[stats.Attribute ==
#                                 'Return on Equity (ttm)'].Value.values[0]

#                 revenue_real = float(revenue[:-1])
#                 gross_real = float(
#                     stats.loc[stats.Attribute == 'Gross Profit (ttm)'].Value.values[0][:-1])
#                 gross_margin = "{:.2f}".format(gross_real/revenue_real*100)+'%'
#                 gross_margin_real = float(gross_margin[:-1])

#                 profit_margin = stats.loc[stats.Attribute ==
#                                           'Profit Margin'].Value.values[0]
#                 operating_margin = stats.loc[stats.Attribute ==
#                                              'Operating Margin (ttm)'].Value.values[0]

#                 # Safety
#                 debt_equity_ratio = stats.loc[stats.Attribute ==
#                                               'Total Debt/Equity (mrq)'].Value.values[0]
#                 current_ratio = stats.loc[stats.Attribute ==
#                                           'Current Ratio (mrq)'].Value.values[0]
#                 current_ratio_real = float(current_ratio)*10
#                 beta = quote_table.loc[quote_table.attribute ==
#                                        'Beta (5Y Monthly)'].value.values[0]

#                 # Operational Efficiency
#                 roa = stats.loc[stats.Attribute ==
#                                 'Return on Assets (ttm)'].Value.values[0]
#                 roa_real = float(roa[:-1])
#                 netincome = stats.loc[stats.Attribute ==
#                                       'Net Income Avi to Common (ttm)'].Value.values[0]
#                 netincome_real = float(netincome[:-1])
#                 totalasset = netincome_real / roa_real * 100
#                 asset_turnover = "{:.2f}".format(revenue_real/totalasset)
#                 asset_turnover_real = float(asset_turnover)*100

#                 # Others
#                 share_ost = stats.loc[stats.Attribute ==
#                                       'Shares Outstanding 5'].Value.values[0]

#                 # position = len(overview)
#                 # st.write('Current Row number is', position)
#                 # overview.loc[position] = [quote, market_cap, revenue, rev_growth_q, roe, gross_margin, beta]

#                 insert_sql = """REPLACE INTO overview (Quote, Sector, 'Mkt Cap', 'Rev (ttm)', 'Net Income (ttm)', 'FCFE (ttm)', \
#                 'Qtr Rev Growth', 'Qtr Earning Growth', 'Cur Qtr Est', 'Next Qtr Est', 'Cur Yr Est', 'Next Yr Est', \
#                 'ROE (ttm)', 'ROA (ttm)', 'Gross Margin (ttm)', 'Operating Margin (ttm)', 'Profit Margin', \
#                 'Trailing P/E', 'Forward P/E', 'Price/Sales (ttm)', 'PEG Ratio (5 yr expected)', \
#                 'Total Debt/Equity (mrq)', 'Current Ratio (mrq)', 'Beta (5Y Monthly)', \
#                 'Asset Turnover', \
#                 'Shares Outstanding')
#                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """
#                 c.execute(insert_sql, (quote, sector, market_cap, revenue, netincome, fcfe,
#                                        rev_growth_q, earning_growth_q, cqsg, nqsg, cysg, nysg,
#                                        roe, roa, gross_margin, operating_margin, profit_margin,
#                                        trailing_pe, forward_pe, ps, peg,
#                                        debt_equity_ratio, current_ratio, beta,
#                                        asset_turnover,
#                                        share_ost))
#                 conn.commit()
#                 # Only after Database is refreshed, then update the Database
#                 overview_info = pd.read_sql("""SELECT * FROM overview""", conn)

#             radar_display.loc[quote] = [trailing_pe, rev_growth_q,
#                                         gross_margin, current_ratio, asset_turnover]

#         fig.add_trace(go.Scatterpolar(
#             r=[trailing_pe_real, rev_growth_q_real, gross_margin_real,
#                 current_ratio_real, asset_turnover_real],
#             theta=categories,
#             fill='toself',
#             name=quote))

#         fig.update_layout(
#             polar=dict(
#                 radialaxis=dict(
#                     visible=True,
#                     range=[0, 100])),
#             title={
#                 'text': 'Revenue Quarterly - '+quote,
#                 'y': 0.9,
#                 'x': 0.5,
#                 'xanchor': 'center',
#                 'yanchor': 'top'},
#             showlegend=True
#         )

#     st.plotly_chart(fig)
#     st.write(radar_display)

    # new_title1 = '<p style="font-size: 12px; text-align: center;">Figure 1 - Company Radar Chart</p>'
    # st.markdown(new_title1, unsafe_allow_html=True)
    # st.caption('Figure 1 - Company Radar Chart')

    #--------------------------------------------------------------------------------------------------------------#
    ###############################################################################################################
    # Section 2 - Company Fundamental Overview (Display Data Frame Details)
    st.header('2. Company Fundamental Overview - Most Recent Quarter')
    overview_fund = pd.DataFrame(columns=overview_info.columns)
    # overview_fund = overview_fund.set_index('Quote')
    # st.write('Index is set')

    # st.write('quote_selet value is', quote_select)
    # st.write('Not in the list' == quote_select)
    # st.write('Not in the list' in quote_select)
    # st.write(quote_select != [])
    # st.write('Dropdown Fund value', dropdown_fund)
    if ('Not in the list' not in quote_select) and quote_select != []:
        dropdown_fund = st.multiselect(
            'Please select Stock Quote:', quote_exist, default=quote_select)  # -- Take the input from above multi-select

        for quote_fund in dropdown_fund:
            # st.write('Quote Value', quote_fund)

            # -- write all the rows into DataFrame
            overview_fund.loc[len(
                overview_fund)] = overview_info.loc[overview_info.Quote == quote_fund].values[0]

        st.write("Company Fundamental", overview_fund)

        overview_valuation = overview_fund[[
            'Quote', 'Trailing P/E', 'Forward P/E', 'Price/Sales (ttm)', 'PEG Ratio (5 yr expected)']]
        st.write("Key Indicators - Valuation", overview_valuation)

        overview_growth = overview_fund[['Quote', 'Qtr Rev Growth', 'Qtr Earning Growth', 'Cur Qtr Est',
                                        'Next Qtr Est', 'Cur Yr Est', 'Next Yr Est', 'Past 5 Yr', 'Next 5 Yr Est']]
        st.write("Key Indicators - Growth", overview_growth)
        # st.write('Next 5 Year Growth Rate is', next_5y)
        # st.write('Past 5 Year Growth Rate is', past_5y)

        overview_profitability = overview_fund[[
            'Quote', 'ROE (ttm)', 'ROA (ttm)', 'Gross Margin (ttm)', 'Operating Margin (ttm)', 'Profit Margin']]
        st.write("Key Indicators - Profitability ",
                 overview_profitability)

        overview_safety = overview_fund[[
            'Quote', 'Total Debt/Equity (mrq)', 'Current Ratio (mrq)', 'Beta (5Y Monthly)']]
        st.write("Key Indicators - Safety", overview_safety)

        overview_operation = overview_fund[['Quote', 'Asset Turnover']]
        st.write("Key Indicators - Operational Efficiency",
                 overview_operation)
    # c.close
    # conn.close

    # Define the DataFrame and columns
    # string = st.text_input('Please key in list of Stock Quote, separated by Comma and No space:')
    # quotes = string.split(",") #Remove the comma, if there is any

    # for quote in quotes:
    #     if quote != '':
    #         st.write('The quote keyed in is', quote)

    #         analysts_info = si.get_analysts_info(quote)
    #         company_info = si.get_company_info(quote)
    #         company_info.reset_index(inplace=True)

    #         stats = si.get_stats(quote)
    #         stats_valuation = si.get_stats_valuation(quote)
    #         quote_table = si.get_quote_table(quote, dict_result = False)

    #         sector = company_info.loc[company_info.Breakdown == 'sector'].Value.values[0]
    #         market_cap = quote_table.loc[quote_table.attribute == 'Market Cap'].value.values[0]
    #         revenue = stats.loc[stats.Attribute == 'Revenue (ttm)'].Value.values[0]
    #         fcfe = stats.loc[stats.Attribute == 'Levered Free Cash Flow (ttm)'].Value.values[0]

    #         #Valuation
    #         trailing_pe = stats_valuation.loc[stats_valuation[0] == 'Trailing P/E'][1].values[0]
    #         forward_pe = stats_valuation.loc[stats_valuation[0] == 'Forward P/E 1'][1].values[0]
    #         ps = stats_valuation.loc[stats_valuation[0] == 'Price/Sales (ttm)'][1].values[0]
    #         peg = stats_valuation.loc[stats_valuation[0] == 'PEG Ratio (5 yr expected) 1'][1].values[0]

    #         #Growth
    #         rev_growth_q = stats.loc[stats.Attribute == 'Quarterly Revenue Growth (yoy)'].Value.values[0]
    #         earning_growth_q = stats.loc[stats.Attribute == 'Quarterly Earnings Growth (yoy)'].Value.values[0]

    #         #Reveun Growth Estimate - their columns values is not fixed
    #         rev_est = analysts_info['Revenue Estimate']
    #         for item in rev_est.columns[1:]:
    #             print(item)
    #             if item.startswith('Current Qtr'):
    #                 column1 = item
    #             elif item.startswith('Next Qtr'):
    #                 column2 = item
    #             elif item.startswith('Current Year'):
    #                 column3 = item
    #             elif item.startswith('Next Year'):
    #                 column4 = item

    #         print(column1, column2, column3, column4)

    #         cqsg = rev_est.loc[rev_est['Revenue Estimate'] == 'Sales Growth (year/est)'][column1].values[0]
    #         nqsg = rev_est.loc[rev_est['Revenue Estimate'] == 'Sales Growth (year/est)'][column2].values[0]
    #         cysg = rev_est.loc[rev_est['Revenue Estimate'] == 'Sales Growth (year/est)'][column3].values[0]
    #         nysg = rev_est.loc[rev_est['Revenue Estimate'] == 'Sales Growth (year/est)'][column4].values[0]

    #         #Profitability
    #         roe = stats.loc[stats.Attribute == 'Return on Equity (ttm)'].Value.values[0]

    #         revenue_real = float(revenue[:-1])
    #         gross_real = float(stats.loc[stats.Attribute == 'Gross Profit (ttm)'].Value.values[0][:-1])
    #         gross_margin = "{:.2f}".format(gross_real/revenue_real*100)+'%'

    #         profit_margin = stats.loc[stats.Attribute == 'Profit Margin'].Value.values[0]
    #         operating_margin = stats.loc[stats.Attribute == 'Operating Margin (ttm)'].Value.values[0]

    #         #Safety
    #         debt_equity_ratio = stats.loc[stats.Attribute == 'Total Debt/Equity (mrq)'].Value.values[0]
    #         current_ratio = stats.loc[stats.Attribute == 'Current Ratio (mrq)'].Value.values[0]
    #         beta = quote_table.loc[quote_table.attribute == 'Beta (5Y Monthly)'].value.values[0]

    #         #Operational Efficiency
    #         roa = stats.loc[stats.Attribute == 'Return on Assets (ttm)'].Value.values[0]
    #         roa_real = float(roa[:-1])
    #         netincome = stats.loc[stats.Attribute == 'Net Income Avi to Common (ttm)'].Value.values[0]
    #         netincome_real = float(netincome[:-1])
    #         totalasset = netincome_real / roa_real * 100
    #         asset_turnover = "{:.2f}".format(revenue_real/totalasset)

    #         #Others
    #         share_ost = stats.loc[stats.Attribute == 'Shares Outstanding 5'].Value.values[0]

    #         # position = len(overview)
    #         # st.write('Current Row number is', position)
    #         # overview.loc[position] = [quote, market_cap, revenue, rev_growth_q, roe, gross_margin, beta]

    #         insert_sql = """REPLACE INTO overview (Quote, Sector, 'Mkt Cap', 'Rev (ttm)', 'Net Income (ttm)', 'FCFE (ttm)', \
    #         'Qtr Rev Growth', 'Qtr Earning Growth', 'Cur Qtr Est', 'Next Qtr Est', 'Cur Yr Est', 'Next Yr Est', \
    #         'ROE (ttm)', 'ROA (ttm)', 'Gross Margin (ttm)', 'Operating Margin (ttm)', 'Profit Margin', \
    #         'Trailing P/E', 'Forward P/E', 'Price/Sales (ttm)', 'PEG Ratio (5 yr expected)', \
    #         'Total Debt/Equity (mrq)', 'Current Ratio (mrq)', 'Beta (5Y Monthly)', \
    #         'Asset Turnover', \
    #         'Shares Outstanding')
    #         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """
    #         c.execute(insert_sql, (quote, sector, market_cap, revenue, netincome, fcfe,
    #                        rev_growth_q, earning_growth_q, cqsg, nqsg, cysg, nysg,
    #                        roe, roa, gross_margin, operating_margin, profit_margin,
    #                        trailing_pe, forward_pe, ps, peg,
    #                        debt_equity_ratio, current_ratio, beta,
    #                        asset_turnover,
    #                       share_ost))
    #         conn.commit()

    # overview_info = pd.read_sql("""SELECT * FROM overview""", conn)

    # Debug
    # st.write("Web Date has been written to the Database successfully!")


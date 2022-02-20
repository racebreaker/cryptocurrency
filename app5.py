# app5.py
import streamlit as st
import pandas as pd
from PIL import Image


def app():
    st.title('Microeconomics Data')

    st.header('US Fed Reserve')
    url = 'https://www.cmegroup.com/trading/interest-rates/countdown-to-fomc.html'
    st.write(f' - CME FedWatch Tool ({url})')

    st.write(' - Prob. of Fed Rate Hike Calculator')
    expander = st.expander(label='Calculator Details')
    with expander:
        future_price = st.number_input(
            'Future Price: refer to the link below', value=99.905)
        url = 'https://www.cmegroup.com/markets/interest-rates/stirs/30-day-federal-fund.quotes.html'
        st.write(f'{url}')

        future_yield = st.number_input(
            'Future Implied Yield (%) = 100 - Future Price', value=100 - future_price)
        current_rate = st.number_input(
            'Current Fed Rate (%): refer to the link below', value=0.08)
        url = 'https://fred.stlouisfed.org/series/FEDFUNDS'
        st.write(f'{url}')

        rate_hike = st.number_input('Estimated Fed Rate Hike (%)', value=0.25)
        new_rate = st.number_input(
            'New Fed Rate (%)', value=current_rate + rate_hike)
        st.write(
            f'Prob. of Rate Hike = (Future Yield - Current Rate)/(New Rate - Current Rate) is {(future_yield - current_rate)/(new_rate - current_rate)*100:.2f}%')

    url = 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'
    st.write(
        f' - Meeting calendars, statements, and minutes (2017-2022) ({url})')

    url = 'https://www.federalreserve.gov/aboutthefed/boardmeetings/meetingdates.htm'
    st.write(f' - Board Meetings ({url})')

################################################################################################################
    st.header('US Interest Rate')
    url = "https://fred.stlouisfed.org/series/FEDFUNDS"
    st.write("Federal Funds Effective Rate (FEDFUNDS) (%s)" % url)

    st.subheader('10-Year 2-Year Yield Spread')
    url = "https://fred.stlouisfed.org/series/T10Y2Y"
    st.write(
        "10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity (%s)" % url)

################################################################################################################
    st.header('US Inflation Rate (CPI)')
    url = "https://tradingeconomics.com/united-states/inflation-cpi"
    st.write(f' - United States Inflation Rate2022 ({url})')
    # https://www.statista.com/statistics/273418/unadjusted-monthly-inflation-rate-in-the-us/

    url = 'https://www.federalreserve.gov/faqs/economy_14419.htm'
    st.write(
        f' - What is inflation and how does the Federal Reserve evaluate changes in the rate of inflation? ({url})')

    st.subheader('US PPI Index')
    st.subheader('US Employment Cost Index')
    url = "https://tradingeconomics.com/united-states/employment-cost-index"
    st.write(
        "United States Employment Cost Index QoQ - the salary increment (%s)" % url)

################################################################################################################
    st.header('Fed Balance Sheet')
    url = "https://www.federalreserve.gov/monetarypolicy/bst_recenttrends.htm"
    st.write("Credit and Liquidity Programs and the Balance Sheet (%s)" % url)

    url = 'https://fred.stlouisfed.org/series/EXCSRESNS'
    st.write("Excess Reserves of Depository Institutions (DISCONTINUED) (%s)" % url)

    url = 'https://fred.stlouisfed.org/series/GFDEBTN'
    st.write(f'Federal Debt: Total Public Debt ({url})')

    # st.write(
    #     "check out this [link](https://share.streamlit.io/mesmith027/streamlit_webapps/main/MC_pi/streamlit_app.py)")

    # link = 'check out this [link](https://retailscope.africa/)'
    # st.markdown(link, unsafe_allow_html=True)
    # st.markdown("Credit and Liquidity Programs and the Balance Sheet(%s)" % url)

################################################################################################################
    st.header('US Unemployment Rate')
    url = "https://fred.stlouisfed.org/series/UNRATE"
    st.write("Unemployment Rate (UNRATE) (%s)" % url)

    url = "https://www.bls.gov/charts/employment-situation/employment-by-industry-monthly-changes.htm"
    st.write(f"Employment by industry, monthly changes ({url})")

    url = 'https://fred.stlouisfed.org/series/CIVPART'
    st.write(f'Labor Force Participation Rate ({url})')

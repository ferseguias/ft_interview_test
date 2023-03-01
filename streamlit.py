# to initialize streamlit go to folder with terminal and run: streamlit run streamlit.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests

plt.style.use('dark_background')

# imports cc_deposits
cc_deposits = pd.read_excel('excel_files/Recruiting Task Dataset _ abridged version.xlsx')
columns = ['tx_approved?', 'customer_id', 'cc_processing_co', 'cc_bank', 'amount', 'datetime']
cc_deposits.columns = columns
cc_deposits = cc_deposits.set_index('datetime')

# question 1 cc_deposits
quarterly_approval_rate = cc_deposits.groupby(cc_deposits.index.to_period('Q'))['tx_approved?'].agg({'sum', 'count'})
quarterly_approval_rate['failed_tx'] = quarterly_approval_rate['count'] - quarterly_approval_rate['sum']
quarterly_approval_rate['approval_rate_%'] = (quarterly_approval_rate['sum'] / quarterly_approval_rate['count'] * 100).round(2)
quarterly_approval_rate = quarterly_approval_rate.reset_index().rename(columns={'count':'total_tx', 'sum':'approved_tx'})
quarterly_approval_rate['datetime'] = list(quarterly_approval_rate.datetime.astype(str))

fig, ax = plt.subplots(figsize = (10, 5))
x = list(quarterly_approval_rate.datetime.astype(str))
y1 = quarterly_approval_rate['approved_tx']
y2 = quarterly_approval_rate['failed_tx']
ax.bar(x, y1, width=0.4, align='center', label='Approved transactions')
ax.bar(x, y2, width=0.4, align='center', bottom=y1, label='Failed transactions')
ax.set_xlabel('Quarters')
ax.set_ylabel('Number of transactions')
ax.set_title('Total transactions separated by its approval status')
ax.legend()

# question 2 cc_deposits
cc_processing_co_failure = cc_deposits.groupby([cc_deposits.index.to_period('Q'), 'cc_processing_co'])['tx_approved?'].value_counts().unstack().replace(np.nan, 0)
cc_processing_co_failure = cc_processing_co_failure.loc[cc_processing_co_failure[1] == 0].reset_index()
cc_processing_co_failure = cc_processing_co_failure.groupby('datetime')['cc_processing_co'].count().reset_index().rename(columns={'cc_processing_co':'cc_processing_co_failed_any'})
cc_processing_co_failure['datetime'] = list(cc_processing_co_failure.datetime.astype(str))

# question 3 cc_deposits
cc_bank_failure_analysis = cc_deposits.groupby('cc_bank')['tx_approved?'].value_counts().unstack().replace(np.nan, 0)
cc_bank_failure_analysis['total_tx'] = cc_bank_failure_analysis[0] + cc_bank_failure_analysis[1]
cc_bank_failure_analysis['failure_rate'] = cc_bank_failure_analysis[0] / cc_bank_failure_analysis['total_tx'] * 100
cc_bank_failure_analysis = cc_bank_failure_analysis.sort_values(by=['failure_rate', 'total_tx'], ascending=False).reset_index().rename(columns={0:'n_failed_tx', 1:'n_approved_tx'})

cc_processing_co_failure_analysis = cc_deposits.groupby('cc_processing_co')['tx_approved?'].value_counts().unstack().replace(np.nan, 0)
cc_processing_co_failure_analysis['total_tx'] = cc_processing_co_failure_analysis[0] + cc_processing_co_failure_analysis[1]
cc_processing_co_failure_analysis['failure_rate'] = cc_processing_co_failure_analysis[0] / cc_processing_co_failure_analysis['total_tx'] * 100
cc_processing_co_failure_analysis = cc_processing_co_failure_analysis.sort_values(by=['failure_rate', 'total_tx'], ascending=False).reset_index().rename(columns={0:'n_failed_tx', 1:'n_approved_tx'})

# imports crypto_deposits
btc_deposits = pd.read_excel('excel_files/Crypto_Sample_BTC.xlsx')
eth_deposits = pd.read_excel('excel_files/Crypto_Sample_ETH.xlsx')
crypto_deposits = pd.concat([btc_deposits, eth_deposits])
columns = ['tx_id', 'datetime', 'usd_amount', 'currency', 'status', 'tx_type', 'fee', 'symbol', 'crypto_amount', 'buy_rate']
crypto_deposits.columns = columns
crypto_deposits = crypto_deposits.set_index('datetime').sort_values(by=['datetime'], ascending=True)
crypto_deposits.loc[crypto_deposits['tx_type'] == 'PAYOUT', ['usd_amount', 'crypto_amount']] *= -1

# question 1 crypto_deposits
crypto_balance_dec22 = {'symbol':['BTC', 'ETH'],
                        'crypto_balance_dec22':[30.88890835, 62.29934006],
                        'usd_balance_dec22':[714194.50, 98633.66]}
crypto_balance_dec22 = pd.DataFrame(crypto_balance_dec22)
crypto_balance_dec22['avg_tx_rate_dec22'] = crypto_balance_dec22['usd_balance_dec22'] / crypto_balance_dec22['crypto_balance_dec22']

crypto_tx_jan23 = crypto_deposits.groupby('symbol')[['crypto_amount', 'usd_amount']].sum()
crypto_tx_jan23 = crypto_tx_jan23.reset_index().rename(columns={'crypto_amount':'crypto_tx_jan23', 'usd_amount':'usd_tx_jan23'})
crypto_tx_jan23['avg_tx_rate_jan23'] = crypto_tx_jan23['usd_tx_jan23'] / crypto_tx_jan23['crypto_tx_jan23']

crypto_balance_jan23 = crypto_balance_dec22.copy()
crypto_balance_jan23['crypto_balance_jan23'] = crypto_balance_dec22['crypto_balance_dec22'] + crypto_tx_jan23['crypto_tx_jan23']
crypto_balance_jan23['usd_balance_jan23'] = crypto_balance_dec22['usd_balance_dec22'] + crypto_tx_jan23['usd_tx_jan23']
crypto_balance_jan23['avg_tx_rate_jan23'] = crypto_balance_jan23['usd_balance_jan23'] / crypto_balance_jan23['crypto_balance_jan23']
crypto_balance_jan23 = crypto_balance_jan23.drop(columns=['crypto_balance_dec22', 'usd_balance_dec22', 'avg_tx_rate_dec22'])

# question 2 crypto_deposits
url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin%2Cethereum&vs_currencies=usd"
response = requests.get(url)
btc_price = response.json()["bitcoin"]["usd"]
eth_price = response.json()["ethereum"]["usd"]

url = "https://api.coingecko.com/api/v3/coins/bitcoin/history?date=31-12-2022"
response = requests.get(url)
btc_price_dec22 = response.json()["market_data"]["current_price"]["usd"]
url = "https://api.coingecko.com/api/v3/coins/ethereum/history?date=31-12-2022"
response = requests.get(url)
eth_price_dec22 = response.json()["market_data"]["current_price"]["usd"]

crypto_balance_dec22_fx = crypto_balance_dec22.copy()
crypto_balance_dec22_fx['avg_tx_rate_dec22'] = crypto_balance_dec22_fx['usd_balance_dec22'] / crypto_balance_dec22_fx['crypto_balance_dec22']
crypto_balance_dec22_fx['close_price_dec22'] = [btc_price_dec22, eth_price_dec22]
crypto_balance_dec22_fx['fx_loss_(gain)_dec22'] = crypto_balance_dec22_fx['usd_balance_dec22'] - (crypto_balance_dec22_fx['crypto_balance_dec22'] * crypto_balance_dec22_fx['close_price_dec22'])

crypto_balance_jan23_fx = crypto_balance_jan23.copy()
crypto_balance_jan23_fx['close_price_today'] = [btc_price, eth_price]
crypto_balance_jan23_fx['usd_balance_jan23'] = crypto_balance_jan23_fx['usd_balance_jan23'] - crypto_balance_dec22_fx['fx_loss_(gain)_dec22']
crypto_balance_jan23_fx['avg_tx_rate_jan23'] = crypto_balance_jan23_fx['usd_balance_jan23'] / crypto_balance_jan23_fx['crypto_balance_jan23']
crypto_balance_jan23_fx['fx_loss_(gain)_23'] = crypto_balance_jan23_fx['usd_balance_jan23'] - (crypto_balance_jan23_fx['crypto_balance_jan23'] * crypto_balance_jan23_fx['close_price_today'])

# question 3 crypto_deposits
btc = crypto_deposits.loc[crypto_deposits['symbol'] == 'BTC']
eth = crypto_deposits.loc[crypto_deposits['symbol'] == 'ETH']
btc = btc.groupby(btc.index.to_period('D'))[['crypto_amount', 'buy_rate']].agg({'crypto_amount':'sum', 'buy_rate':'mean'})
btc = btc.reset_index()
btc['crypto_amount_accum'] = btc['crypto_amount'].cumsum()
btc['datetime'] = btc['datetime'].astype(str)
eth = eth.groupby(eth.index.to_period('D'))[['crypto_amount', 'buy_rate']].agg({'crypto_amount':'sum', 'buy_rate':'mean'})
eth = eth.reset_index()
eth['crypto_amount_accum'] = eth['crypto_amount'].cumsum()
eth['datetime'] = eth['datetime'].astype(str)

fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(20,15))
btc_x = btc['datetime']
btc_y1 = btc['crypto_amount_accum']
btc_y2 = btc['buy_rate']
ax1_ = ax1.twinx()
ax1.plot(btc_x, btc_y1, 'w-', label='Net Volume Accumulated')
ax1.set_xlabel('Date')
ax1.set_ylabel('Daily net volumn accumulated', color='w')
ax1.tick_params('y', colors='w')
ax1_.plot(btc_x, btc_y2, 'r-', label='Average Conversion Rate')
ax1_.set_ylabel('Daily average conversion rate', color='r')
ax1_.tick_params('y', colors='r')
ax1.set_title('BTC daily volumes accumulated and average conversion rates per day')
eth_x = eth['datetime']
eth_y1 = eth['crypto_amount_accum']
eth_y2 = eth['buy_rate']
ax2_ = ax2.twinx()
ax2.plot(eth_x, eth_y1, 'w-', label='Net Volume Accumulated')
ax2.set_xlabel('Date')
ax2.set_ylabel('Daily net volumn accumulated', color='w')
ax2.tick_params('y', colors='w')
ax2_.plot(eth_x, eth_y2, 'r-', label='Average Conversion Rate')
ax2_.set_ylabel('Daily average conversion rate', color='r')
ax2_.tick_params('y', colors='r')
ax2.set_title('ETH daily volumes accumulated and average conversion rates per day')
plt.setp(ax1.get_xticklabels(), rotation=45)
plt.setp(ax2.get_xticklabels(), rotation=45)
ax1.legend(loc='upper left')
ax1_.legend(loc='lower right')
ax2.legend(loc='upper left')
ax2_.legend(loc='lower right')
plt.tight_layout()

gen_options = st.sidebar.selectbox("What file would you like to work with?", ["CREDIT CARD DEPOSITS", "CRYPTO WALLETS"])

if gen_options == "CREDIT CARD DEPOSITS":
    st.sidebar.title("""CREDIT CARD DEPOSITS""")
    options = st.sidebar.selectbox("Choose question", ["Dataframe preview", "Question 1", "Question 2", "Question 3"])
    if options == 'Dataframe preview':
        st.header('Dataframe preview (first 5 rows) and columns information')
        st.table(cc_deposits.head(5))
        st.write(f'#### Columns description:')
        st.write('- Index: indicates the date and time of the deposit attempt.')
        st.write('- Deposit attempts have a "tx_approved?" value of 1 or 0 signifying whether they have been approved or declined.')
        st.write('- "customer_id" identifies the customer account attempting to deposit.')
        st.write('- "cc_processing_co" indicates the credit card processing company that is processing the transaction for the business.')
        st.write('- "cc_bank" indicates the bank that has issued the customers credit card.')
        st.write('- "amount" indicates the amount that the customer is attempting to deposit.')
    elif options == 'Question 1':
        st.header('Q1: What is the datasets approval rate by quarter?')
        st.write(f'#### Below table with approval rates per quarter:')
        st.table(quarterly_approval_rate)
        st.write(f'#### Plot total transactions separated by its approval status:')
        st.pyplot(fig)
    elif options == 'Question 2':
        st.header('Q2: How many Processing COs failed to approve any deposit attempts in each of the four quarters?')
        st.write(f'#### Below table with number of Processing COs that failed to approve any deposit attempt per quarter:')
        st.table(cc_processing_co_failure)
    elif options == 'Question 3':
        st.header('Q3: Identify any factors likely to have played a causal role for the decline in approval rates seen in Q3 2021 vs Q4 2020?')
        st.write(f'#### Below list of top 5 banks that failed 100% of their transactions:')
        st.table(cc_bank_failure_analysis.head(5))
        st.write(f'#### Below list of top 5 processing companies that failed 100% of their transactions:')
        st.table(cc_processing_co_failure_analysis.head(5))

if gen_options == "CRYPTO WALLETS":
    st.sidebar.title("""CRYPTO WALLETS""")
    options = st.sidebar.selectbox("Choose question", ["Dataframe preview", "Question 1", "Question 2", "Question 3"])
    if options == 'Dataframe preview':
        st.header('Dataframe preview (first 5 rows) and columns information')
        st.table(crypto_deposits.head(5))
        st.write(f'#### Columns description:')
        st.write('- Index: indicates the date and time of the transaction.')
        st.write('- "tx_id": identifies the unique transaction.')
        st.write('- "usd_amount" transaction amount credited to the customer in USD.')
        st.write('- "currency" currency of the transaction credited to the customer (all customer credits are in USD).')
        st.write('- "status" status of the transaction – all should be approved.')
        st.write('- "tx_type" indicates whether the transaction is a deposit or payout.')
        st.write('- "fee" indicates any applicable fees on the transaction.')
        st.write('- "symbol" indicates Crypto coin type.')
        st.write('- "crypto_amount" indicates the crypto value at time of transaction.')
        st.write('- "buy_rate" indicates the conversion rate used at the time of transaction.')
    elif options == 'Question 1':
        st.header('Q1: Calculated Balance of each wallet as at Jan.31, 2023')
        st.write(f'#### Step 1 - table with crypto balance at the end of 2022 (info provided in the challenge):')
        st.table(crypto_balance_dec22)
        st.write(f'#### Step 2 - table with crypto transactions during January 2023:')
        st.table(crypto_tx_jan23)
        st.write(f'#### Step 3 - table with crypto balance YTD 2023 (table 1 + table 2):')
        st.table(crypto_balance_jan23)
    elif options == 'Question 2':
        st.header('Q2: Calculate the revaluation of the USD balance of each wallet (FX loss or gain)')
        st.write(f'#### FX loss or gain 2022:')
        st.table(crypto_balance_dec22_fx.round(2))
        st.write(f'#### FX loss or gain 2023:')
        st.table(crypto_balance_jan23_fx.round(2))
        st.write(f'##### Crypto prices current and previous year closing:')
        st.write(f'BTC current price: {round(btc_price, 2)}')
        st.write(f'ETH current price: {round(eth_price, 2)}')
        st.write(f'BTC 2022 closing price: {round(btc_price_dec22, 2)}')
        st.write(f'ETH 2022 closing price: {round(eth_price_dec22, 2)}')
    elif options == 'Question 3':
        st.header('Q3: Prepare a graph to show the daily volumes and average conversion rates per day for each coin type')
        st.write(f'#### Plot daily volumes accumulated and average conversion rates per day and coin:')
        st.pyplot(fig1)
        st.write('Left Y axis represents accumulated volume')
        st.write('Right Y axis represents average conversion rate')
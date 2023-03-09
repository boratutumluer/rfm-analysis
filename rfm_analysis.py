import pandas as pd
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
import sys

sys.path.append("rfm_cltv/")
from helpers.pandas_options import set_pandas_options
from helpers.eda import check_df
from helpers.data_prep import outlier_threshold
from helpers.segment_map import get_segmentation_map

set_pandas_options(width=300, precision=3)

customer = pd.read_csv("rfm_cltv/datasets/olist_customers_dataset.csv")
order_items = pd.read_csv("rfm_cltv/datasets/olist_order_items_dataset.csv")
order_payments = pd.read_csv("rfm_cltv/datasets/olist_order_payments_dataset.csv")
order_reviews = pd.read_csv("rfm_cltv/datasets/olist_order_reviews_dataset.csv")
orders = pd.read_csv("rfm_cltv/datasets/olist_orders_dataset.csv")
products = pd.read_csv("rfm_cltv/datasets/olist_products_dataset.csv")

#######################################################
# ORDER ANALYSIS
#######################################################
check_df(orders)
check_df(order_items)
check_df(order_payments)

# There is more than one product in an order.
order_items.groupby("order_id").size().sort_values(ascending=False).head()
# order_id
# 8272b63d03f5f79c56e9e4120aec44ef    21
# 1b15974a0141d54e36626dca3fdc731a    20
# ab14fdcfbe524636d65ee38360e22ce8    20
# 9ef13efd6949e4573a18964dd1bbe7f5    15
# 428a2f660dc84138d969ccd69a0ab6d5    15

# We need to group the order ids by taking the sum of the prices and freight values.
order_price_freight = order_items.groupby("order_id").agg({"price": "sum", "freight_value": "sum"}).reset_index()

# --> distribution_of_orders_price_freight.png
sns.scatterplot(x="price", y="freight_value", data=order_price_freight)

# As we can see, there are some outliers in these variables.
price_min_limit, price_max_limit = outlier_threshold(order_price_freight, "price", q1=0.01, q3=0.99)
freight_value_min_limit, freight_value_max_limit = outlier_threshold(order_price_freight,
                                                                     "freight_value",
                                                                     q1=0.01,
                                                                     q3=0.99)
# for price --> min. limit: -1468.40875, max. limit: 2479.28525
# for freight_value --> min. limit: -139.0002500000001, max. limit: 251.37375000000014

order_price_freight.describe().T
#                   count    mean     std   min    25%    50%     75%       max
# price         98666.000 137.754 210.645 0.850 45.900 86.900 149.900 13440.000
# freight_value 98666.000  22.824  21.651 0.000 13.850 17.170  24.040  1794.960

# we can remove outliers in dataframe
order_price_freight = order_price_freight[
    ~(((order_price_freight["price"] < price_min_limit) | (order_price_freight["price"] > price_max_limit))
      | ((order_price_freight["freight_value"] < freight_value_min_limit) | (
                    order_price_freight["freight_value"] > freight_value_max_limit)))]

# after remove
#                   count    mean     std   min    25%    50%     75%      max
# price         98508.000 134.386 181.047 0.850 45.900 86.500 149.900 2470.500
# freight_value 98508.000  22.491  18.388 0.000 13.840 17.160  23.980  251.360

# --> density_of_price_freight.png
sns.set_style("darkgrid")
fig, ax = plt.subplots(1, 2, figsize=(20, 5))
sns.distplot(order_price_freight["price"], color="teal", ax=ax[0])
sns.distplot(order_price_freight["freight_value"], color="olive", ax=ax[1])
plt.show
# --> distribution_of_orders_price_freight_after_remove_outliers.png
sns.scatterplot(x="price", y="freight_value", data=order_price_freight)

#######################################################
# CUSTOMER ANALYSIS
#######################################################

# peyment methods
order_payments["payment_type"].value_counts()
# --> peyment_methods.png
sns.countplot(data=order_payments, x="payment_type")

# combine customers and orders dataset
orders = orders.merge(order_price_freight, on="order_id")
customer_order = customer.merge(orders, on="customer_id")
customer_order.head()

# peyments per order
paid = order_payments.groupby("order_id").agg({"payment_value": "sum"}).sort_values("payment_value",
                                                                                    ascending=False).reset_index()
paid.head()

# combine customers, orders and payments dataset
customer_order_payment = customer_order.merge(paid, on="order_id")
drop_columns = ["customer_id", "customer_zip_code_prefix", "customer_city", "order_status", "order_approved_at",
                "order_delivered_carrier_date"]
customer_order_payment.drop(drop_columns, inplace=True, axis=1)

# --> customer_order_states.png
sns.catplot(data=customer_order_payment, x="customer_state", kind="count",
            palette="ch:.25")
customer_order_payment.head()

#######################################################
# ORDER DELIVERY TIME ANALYSIS
#######################################################

customer_order_payment.isnull().sum()  # order_delivered_customer_date    2182
customer_order_payment.dropna(subset=["order_delivered_customer_date"], how="all", inplace=True)

# string to date
for col in ["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"]:
    customer_order_payment[col] = customer_order_payment[col].apply(
        lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))

customer_order_payment.info()  # check

order_time = customer_order_payment.groupby(["customer_unique_id", "customer_state"]).agg(
    {"order_estimated_delivery_date": "max",
     "order_delivered_customer_date": "max"}).reset_index()

order_time["diff_delivery_days"] = (order_time["order_estimated_delivery_date"] -
                                    order_time["order_delivered_customer_date"]).dt.days
# the rate of delays in all orders
print('%' + '%.2f' % float(
    order_time.loc[order_time["diff_delivery_days"] < 0, "diff_delivery_days"].count() / len(order_time) * 100))
# %8.18

# the regional rate of delayed orders
delayed_order_state = order_time.loc[order_time["diff_delivery_days"] < 0, :]. \
    groupby("customer_state").size().sort_values(ascending=False).reset_index(name="count")

pd.DataFrame({"state": delayed_order_state["customer_state"],
              "RATE(%)": delayed_order_state["count"] / delayed_order_state["count"].sum() * 100}).head()
#   state  RATE(%)
# 0    SP   30.492
# 1    RJ   21.180
# 2    MG    8.223
# 3    BA    5.836
# 4    RS    4.839

#######################################################
# CUSTOMER SEGMENTATION WITH RFM ANALYSIS
#######################################################

# Recency - number of days since the last purchase
# Frequency - number of transactions made over a given period
# Monetary - amount spent over a given period of time

customer_order_payment.head()
# we should define anaylsis day in order to calculate the recency of the purchase
analysis_date = customer_order_payment["order_purchase_timestamp"].max() + dt.timedelta(2)

# rfm metrics per customer
rfm = customer_order_payment.groupby("customer_unique_id").agg(
    {"order_purchase_timestamp": lambda x: (analysis_date - x.max()).days,
     "order_id": lambda x: x.nunique(),
     "payment_value": lambda x: x.sum()}).rename(columns={"order_purchase_timestamp": "recency",
                                                          "order_id": "frequency",
                                                          "payment_value": "monetary"}).reset_index()

rfm[rfm["frequency"] > 1].shape[0] / rfm.shape[0] * 100
# We can see that around 97% of customers are one time customers and only 3% where recurring customers.
# This is a problem for customer segmentation.
# We can continue analyze in 3% of customers, but in this project, I'm going to continue analyze with all customers.

rfm["r_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])
rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["m_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])
rfm["rfm_score"] = rfm["r_score"].astype(str) + rfm["f_score"].astype(str)

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm["segment"] = rfm["rfm_score"].replace(seg_map, regex=True)

rfm.head()
#                  customer_unique_id  recency  frequency  monetary r_score f_score m_score rfm_score      segment
# 0  0000366f3b9a7992bf8c76cfdf3221e2      113          1   141.900       4       1       4        41    promising
# 1  0000b849f77a49e4a4ce2b2a4ca5be3f      116          1    27.190       4       1       1        41    promising
# 2  0000f46a3911fa3c0805444483337064      538          1    86.220       1       1       2        11  hibernating
# 3  0000f6ccb0745a6a4b88665a16c9f078      322          1    43.620       2       1       1        21  hibernating
# 4  0004aac84e0df4da2b147fca70cf8255      289          1   196.890       2       1       4        21  hibernating

rfm.describe().T
#               count    mean     std   min     25%     50%     75%      max
# recency   93209.000 238.971 152.591 2.000 115.000 220.000 347.000  696.000
# frequency 93209.000   1.033   0.209 1.000   1.000   1.000   1.000   15.000
# monetary  93209.000 161.441 194.697 9.590  63.000 107.780 181.790 4655.910

rfm["segment"].value_counts()
# loyal_customers        14983
# hibernating            14965
# potential_loyalists    14964
# at_Risk                14911
# champions               7519
# about_to_sleep          7369
# cant_loose              7281
# need_attention          3754
# promising               3751
# new_customers           3712

# --> segmentation_map.png
get_segmentation_map(df_rfm=rfm, col_name="segment", seg_map=seg_map)

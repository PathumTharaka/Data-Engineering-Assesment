import pandas as pd
import streamlit as st
import altair as alt


st.set_page_config(layout="wide")


data = pd.read_csv('C:/Users/pathu/Downloads/order.csv')


print(data.head()) 


data['created_at'] = pd.to_datetime(data['created_at'])


data['created_at'] = data['created_at'].dt.normalize()


data['customer_id'] = data['customer_id'].fillna(0).astype(int)


data = data.dropna()


st.sidebar.header("Filters")


st.sidebar.markdown('<div style="background-color: #ffffff; border-radius: 15px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"><h4 style="color: #2980b9; text-align: center;">Date Range</h4>', unsafe_allow_html=True)

start_date, end_date = st.sidebar.date_input("Order Date Range", [data['created_at'].min(), data['created_at'].max()])
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown('<div style="background-color: #ffffff; border-radius: 15px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"><h4 style="color: #2980b9; text-align: center;">Total Amount Spent</h4>', unsafe_allow_html=True)

total_amount_spent = st.sidebar.slider('Filter customers by total amount spent', 
                                         min_value=0, 
                                         max_value=int(data['total_amount'].max()), 
                                         value=1000)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown('<div style="background-color: #ffffff; border-radius: 15px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"><h4 style="color: #2980b9; text-align: center;">Number of Orders</h4>', unsafe_allow_html=True)

num_orders = st.sidebar.selectbox('Customers with more than X orders', [1, 5, 10, 20], index=1)
st.sidebar.markdown('</div>', unsafe_allow_html=True)


filtered_data = data[(data['created_at'] >= pd.to_datetime(start_date)) & (data['created_at'] <= pd.to_datetime(end_date))]
filtered_data = filtered_data.groupby('customer_id').filter(lambda x: x['total_amount'].sum() > total_amount_spent)
filtered_data = filtered_data.groupby('customer_id').filter(lambda x: len(x) > num_orders)


print("Data after preprocessing:")
print(data.head())

#
st.markdown("""
    <h1 style="text-align: center; color: #2980b9; font-size: 40px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
        Order Analytics Dashboard
    </h1>
""", unsafe_allow_html=True)


st.subheader("Summary Metrics")  


total_revenue = filtered_data['total_amount'].sum()
unique_customers = filtered_data['customer_id'].nunique()
total_orders = len(filtered_data)


col1, col2, col3 = st.columns(3)


card_style = """
<div style='background-color: #f0f2f5; border-radius: 10px; padding: 20px; height: 150px; display: flex; flex-direction: column; justify-content: center; align-items: center;'>
    <h4 style="margin: 0; color: #2c3e50; font-size: 14px; text-align: center;">{label}</h4>
    <h3 style="margin: 0; color: #2c3e50; font-size: 24px; text-align: center;">{value}</h3>
</div>
"""

with col1:
    st.markdown(card_style.format(label="Total Revenue", value=f"${total_revenue:,.2f}"), unsafe_allow_html=True)

with col2:
    st.markdown(card_style.format(label="Number of Unique Customers", value=unique_customers), unsafe_allow_html=True)

with col3:
    st.markdown(card_style.format(label="Total Orders", value=total_orders), unsafe_allow_html=True)


st.subheader("Filtered Data") 
st.dataframe(filtered_data, use_container_width=True) 


top_customers = filtered_data.groupby('customer_id')['total_amount'].sum().sort_values(ascending=False).head(10).reset_index()
st.subheader("Top 10 Customers by Total Revenue") 


bar_chart = alt.Chart(top_customers).mark_bar().encode(
    x=alt.X('customer_id:O', title='Customer ID'),
    y=alt.Y('total_amount:Q', title='Total Revenue'),
    tooltip=['customer_id', 'total_amount']
).properties(
    width=800,  
    height=400
)
st.altair_chart(bar_chart, use_container_width=True)


revenue_over_time = filtered_data.resample('W', on='created_at')['total_amount'].sum().reset_index()
st.subheader("Total Revenue Over Time")  


line_chart = alt.Chart(revenue_over_time).mark_line().encode(
    x=alt.X('created_at:T', title='Date'),
    y=alt.Y('total_amount:Q', title='Total Revenue'),
    tooltip=['created_at', 'total_amount']
).properties(
    width=800, 
    height=400
)
st.altair_chart(line_chart, use_container_width=True)


print(f"*Total Revenue:* ${total_revenue}")
print(f"*Number of Unique Customers:* {unique_customers}")
print(f"*Number of Orders:* {total_orders}")
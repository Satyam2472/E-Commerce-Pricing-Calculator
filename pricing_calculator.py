import streamlit as st
import pandas as pd
import numpy as np
# from streamlit_lottie import st_lottie
import requests

# Load data for flipakrt
df_comm_flipkart = pd.read_excel(r"Rate card.xlsx", sheet_name="All Commission")
df_shipping_flipkart = pd.read_excel(r"Rate card.xlsx", sheet_name="All Shipping fee")
df_reverse_flipkart = pd.read_excel(r"Rate card.xlsx", sheet_name="Reverse shipping fee")
df_pick_pack_flipkart = pd.read_excel(r"Rate card.xlsx", sheet_name="Pick and Pack fee")
df_fixed_flipkart = pd.read_excel(r"Rate card.xlsx", sheet_name="Fixed fee")

# Load data for Amazon
df_pick_pack_amazon = pd.read_excel(r"Rate card.xlsx", sheet_name="Pick and Pack Amazon")
df_shipping_amazon = pd.read_excel(r"Rate card.xlsx", sheet_name="Shipping Amazon")
df_referral_amazon = pd.read_excel(r"Rate card.xlsx", sheet_name="Referral fee Amazon")
df_closing_amazon = pd.read_excel(r"Rate card.xlsx", sheet_name="Closing fee Amazon")

# Load data for Jiomart
df_fixed_jiomart = pd.read_excel(r"Rate card.xlsx", sheet_name="Jiomart Fixed fee")
df_shipping_jiomart = pd.read_excel(r"Rate card.xlsx", sheet_name="Jiomart Shipping fee")
df_commission_jiomart = pd.read_excel(r"Rate card.xlsx", sheet_name="Jiomart Commission fee")



# Define functions for Flipkart

# Make sure to return 1 in case of not found for those functions which are being multiplied and 0 for those functions which are added
# Fixed fee depends upon the Seller account the product or Category (So I need the details of all sellers)
def fixed_fee_flipkart(fullfillment_type, seller_tier):
    row = df_fixed_flipkart[(df_fixed_flipkart['Fullfillment Type'] == fullfillment_type) & (df_fixed_flipkart['Seller Tier'] == seller_tier)]
    if not row.empty:
        return row['Price'].iloc[0]
    else:
        return 0
    
# Check whether the file contains an updated list of all the vertical and price buckets
def commission_fee_flipkart(platform, vertical, fullfillment, price):
    row = df_comm_flipkart[(df_comm_flipkart['Platform'] == platform) & (df_comm_flipkart['Vertical'] == vertical) & (df_comm_flipkart['Fullfillment Type'] == fullfillment) & (df_comm_flipkart['Lower ASP'] <= price) & ((df_comm_flipkart['Upper ASP'] >= price) | (df_comm_flipkart['Upper ASP'] == 0))]
    if not row.empty:
        return row['Commission'].iloc[0] * price
    else:
        return 0

# Does Shipping fee depends upon the Seller Tier as well as the weight of the product, or its just the weight ?
# Ans = Seller Tier as well as the weight of the product
def shipping_fee_flipkart(local, zonal, national, weight, platform, seller_tier, fullfillment_type):
    row = df_shipping_flipkart[(df_shipping_flipkart['Platform'] == platform) & (df_shipping_flipkart['Seller Tier'] == seller_tier) & (df_shipping_flipkart['Fullfillment Type'] == fullfillment_type) & (df_shipping_flipkart['Lower weight'] <= weight) & (df_shipping_flipkart['Upper weight'] >= weight)]
    if not row.empty:
        return row['Local'].iloc[0] * local + row['Zonal'].iloc[0] * zonal + row['National'].iloc[0] * national
    else:
        return 0
    
# Is this applicable for Non-FBF or FBF ? Ans: It is applicable to FBF only
def pick_pack_fee_flipkart(fullfillment_type, local, zonal, national, weight):
    row = df_pick_pack_flipkart[(df_pick_pack_flipkart['Fullfillment Type'] == fullfillment_type) & (df_pick_pack_flipkart['Lower weight'] <= weight) & (df_pick_pack_flipkart['Upper weight'] >= weight)]
    if not row.empty:
        return row['Local'].iloc[0] * local + row['Zonal'].iloc[0] * zonal + row['National'].iloc[0] * national
    else:
        return 0
    
# Is this only dependent on weight of the product or it also depends upon the Seller Tier ?
# Ans = weight of the product
def reverse_ship_fee_flipkart(local, zonal, national, weight):
    row = df_reverse_flipkart[(df_reverse_flipkart['Lower weight'] <= weight) & (df_reverse_flipkart['Upper weight'] >= weight)]
    if not row.empty:
        return row['Local'].iloc[0] * local + row['Zonal'].iloc[0] * zonal + row['National'].iloc[0] * national
    else:
        return 0

# Define functions for Amazon

def pick_pack_fee_amazon(fullfillment_type, size_brand):
    if (fullfillment_type == "FBA"):
        if (size_brand == "Standard"):
            return 14
        else:
            return 26
    else:
        return 0

def referal_fee_amazon(vertical, price):
    row = df_referral_amazon[
        df_referral_amazon['Vertical'].apply(lambda x: vertical in map(str.strip, x.split(','))) &
        (df_referral_amazon['Lower price'] <= price) &
        (df_referral_amazon['Upper price'] >= price)]
    
    if not row.empty:
        return row['Commission'].iloc[0] * price
    else:
        return 0


def closing_fee_amazon(fullfillment_type, price, vertical):
    if ((fullfillment_type == "Easy Ship" or fullfillment_type == "Easy Ship Prime") and (price <= 250)):
        return 4
    elif ((fullfillment_type == "Easy Ship" or fullfillment_type == "Easy Ship Prime") and (price >= 251 and price <=500)):
        return 9
    elif ((fullfillment_type == "Easy Ship" or fullfillment_type == "Easy Ship Prime") and (price >= 501 and price <=1000)):
        return 30
    elif ((fullfillment_type == "Easy Ship" or fullfillment_type == "Easy Ship Prime") and (price >= 1001)):
        return 61
    elif ((fullfillment_type == "FBA") and (price <=250)):
        row = df_closing_amazon[
        df_closing_amazon['Single_star_product'].apply(lambda x: vertical in map(str.strip, x.split(',')))]
        if not row.empty:
            return 12
        else:
            return 25
        
    elif ((fullfillment_type == "FBA") and (price >= 251 and price <=500)):
        row = df_closing_amazon[
        df_closing_amazon['Two_star_product'].apply(lambda x: vertical in map(str.strip, x.split(',')))]
        if not row.empty:
            return 12
        else:
            return 20

    elif ((fullfillment_type == "FBA") and (price >= 501 and price <= 1000)):
        return 25
    elif ((fullfillment_type == "FBA") and (price > 1000)):
        row = df_closing_amazon[
        df_closing_amazon['Three_star_product'].apply(lambda x: vertical in map(str.strip, x.split(',')))]
        if not row.empty:
            return 70
        else:
            return 50
    

def shipping_fee_amazon(platform, size_brand, seller_tier, fullfillment_type, local, zonal, national, weight):
    row = df_shipping_amazon[(df_shipping_amazon['Platform'] == platform) & (df_shipping_amazon['Size brand'] == size_brand) & (df_shipping_amazon['Seller Tier'] == seller_tier) & (df_shipping_amazon['Fullfillment Type'] == fullfillment_type) & (df_shipping_amazon['Lower weight'] <= weight) & (df_shipping_amazon['Upper weight'] >= weight)]
    if not row.empty:
        return row['Local'].iloc[0] * local + row['Zonal'].iloc[0] * zonal + row['National'].iloc[0] * national
    else:
        return 0
    


# Define functions for Jiomart
def fixed_fee_jiomart(price):
    row = df_fixed_jiomart[(df_fixed_jiomart['Lower bound'] <= price) & (df_fixed_jiomart['Upper bound'] >= price)]

    if not row.empty:
        return row['Price'].iloc[0]
    else:
        return 0

def commission_fee_jiomart(department, category, sub_category, product_type, price):
    row = df_commission_jiomart[(df_commission_jiomart['Department'] == department) & (df_commission_jiomart['Category'] == category) & (df_commission_jiomart['Sub-Category'] == sub_category) & (df_commission_jiomart['Lower bound'] <= price) & (df_commission_jiomart['Upper bound'] >= price)]
    if not row.empty:
        return row['Commission Fee'].iloc[0]*price
    else:
        return 0

def shipping_fee_jiomart(local, zonal, national, weight):
    row = df_shipping_jiomart[(df_shipping_jiomart['Lower weight'] <= weight) & (df_shipping_jiomart['Upper weight'] >= weight)]
    if not row.empty:
        return row['Local'].iloc[0]*local + row['Zonal'].iloc[0]*zonal + row['National'].iloc[0]*national
    else: 
        return 0


def collection_fee_jiomart():
    # As of now the collection fee on Jiomart is zero
    pass

# def reverse_ship_fee_jiomart(local, zonal, national, weight):
#     pass

# def pick_pack_fee_jiomart():
#     pass

    


# Calculate SP function
def calculate_sp(row, platform):

    # For Flipkart
    if platform == 'Flipkart':

        current_sp = row['MRP']
        temp = row['MRP']
        mop_one = row['MOP']
        mop = mop_one

        net_sp = current_sp * (1 - row['RTO'] - row['RVP']) / (1 + row['GST'])
        abs_ads = current_sp * row['Ads']
        pre_set = 1e9
        moq = 1
        moq_flag = False

        dead_weight = row['Length']*row['Breadth']*row['Height']/5000
        weight = max(dead_weight, row['Weight'])

        commission_fee = 0
        shipping_fee = 0
        reverse_shipping_fee = 0
        fixed_fee = 0
        pick_and_pack_fee = 0

        i = 0


        while (pre_set > row['Settlement Asked']*moq or moq > 1) and abs(pre_set - row['Settlement Asked']*moq) > 0.2 and i <= 90:
            i = i + 1
            if (temp > mop):


                if moq_flag == True:
                    temp = row['MRP']
                    mop = mop_one
                    temp = temp*moq
                    mop = mop*moq
                    moq_flag = False
        
                current_sp = temp
                abs_ads = current_sp * row['Ads']
                net_sp = current_sp * (1 - row['RTO'] - row['RVP']) / (1 + row['GST'])
                
                commission_fee = commission_fee_flipkart(row['Platform'], row['Vertical'], row['Fullfillment Type'], current_sp)
                fixed_fee = fixed_fee_flipkart(row['Fullfillment Type'], row['Seller Tier'])
                shipping_fee = shipping_fee_flipkart(row['Local'], row['Zonal'], row['National'], weight*moq, row['Platform'], row['Seller Tier'], row['Fullfillment Type'])
                reverse_shipping_fee = reverse_ship_fee_flipkart(row['Local'], row['Zonal'], row['National'], weight*moq)
                pick_and_pack_fee = pick_pack_fee_flipkart(row['Fullfillment Type'], row['Local'], row['Zonal'], row['National'], weight*moq)


                pre_set = (net_sp - (1 - row['RTO'] - row['RVP']) * commission_fee_flipkart(row['Platform'], row['Vertical'], row['Fullfillment Type'], current_sp) - 
                        (1 - row['RTO']) * (fixed_fee_flipkart(row['Fullfillment Type'], row['Seller Tier']) + shipping_fee_flipkart(row['Local'], row['Zonal'], row['National'], weight*moq, row['Platform'], row['Seller Tier'], row['Fullfillment Type'])) - 
                        reverse_ship_fee_flipkart(row['Local'], row['Zonal'], row['National'], weight*moq) * row['RVP'] - 
                        abs_ads * (1 - row['RTO'] - row['RVP']) - pick_pack_fee_flipkart(row['Fullfillment Type'], row['Local'], row['Zonal'], row['National'], weight*moq)) / (1 - row['RTO'] - row['RVP'])

                if (pre_set < row['Settlement Asked']*moq):
                    moq = moq+1
                    moq_flag = True
                    continue

            else:
                break
            temp = current_sp - (pre_set - row['Settlement Asked']*moq)/5


        return current_sp/moq, net_sp/moq, pre_set/moq, moq, commission_fee/moq, fixed_fee/moq, shipping_fee/moq, reverse_shipping_fee*row['RVP']/moq, pick_and_pack_fee/moq, abs_ads/moq
    
    # For Amazon
    elif platform == 'Amazon':

        current_sp = row['MRP']
        temp = row['MRP']
        mop_one = row['MOP']
        mop = mop_one

        net_sp = current_sp * (1 - row['RTO'] - row['RVP']) / (1 + row['GST'])
        abs_ads = current_sp * row['Ads']
        pre_set = 1e9
        moq = 1
        moq_flag = False

        dead_weight = row['Length']*row['Breadth']*row['Height']/5000
        weight = max(dead_weight, row['Weight'])

        referal_fee = 0
        shipping_fee = 0
        closing_fee = 0
        pick_and_pack_fee = 0

        i = 0

        while (pre_set > row['Settlement Asked']*moq or moq > 1) and abs(pre_set - row['Settlement Asked']*moq) > 0.2 and i < 90:
            
            i = i + 1
            if (temp > mop):


                if moq_flag == True:
                    temp = row['MRP']
                    mop = mop_one
                    temp = temp*moq
                    mop = mop*moq
                    moq_flag = False
        
                current_sp = temp
                abs_ads = current_sp * row['Ads']
                net_sp = current_sp * (1 - row['RTO'] - row['RVP']) / (1 + row['GST'])

                referal_fee = referal_fee_amazon(row['Vertical'], current_sp)
                closing_fee = closing_fee_amazon(row['Fullfillment Type'], current_sp, row['Vertical'])
                shipping_fee = shipping_fee_amazon(row['Platform'], row['Size brand'], row['Seller Tier'], row['Fullfillment Type'], row['Local'], row['Zonal'], row['National'], weight*moq)
                pick_and_pack_fee = pick_pack_fee_amazon(row['Fullfillment Type'], row['Size brand'])

                pre_set = (net_sp - (1 - row['RTO'] - row['RVP'])*referal_fee_amazon(row['Vertical'], current_sp) - 
                       (1 - row['RTO'])*(closing_fee_amazon(row['Fullfillment Type'], current_sp, row['Vertical']) + shipping_fee_amazon(row['Platform'], row['Size brand'], row['Seller Tier'], row['Fullfillment Type'], row['Local'], row['Zonal'], row['National'], weight*moq)) - 
                       abs_ads*(1 - row['RTO'] - row['RVP']) - pick_pack_fee_amazon(row['Fullfillment Type'], row['Size brand'])) / (1 - row['RTO'] - row['RVP'])
            
            
                if (pre_set < row['Settlement Asked']*moq):
                    moq = moq+1
                    moq_flag = True
                    continue

            else:
                break
            temp = current_sp - (pre_set - row['Settlement Asked']*moq)/5

        return current_sp/moq, net_sp/moq, pre_set/moq, moq, referal_fee/moq, closing_fee/moq, shipping_fee/moq, pick_and_pack_fee/moq, abs_ads/moq

    # For JioMart 
    elif platform == 'Jiomart':

    # Fields that are required in the excel file are :- 
    # Department, Category, Sub-Category, Product Type, MRP, Length, Breadth, Height, Weight, RTO, RVP, 
    # GST(in %), Ads(in %), MOP, Expected Settlement, Local, Zonal and National

        current_sp = row['MRP']
        temp = row['MRP']
        mop_one = row['MOP']
        mop = mop_one

        net_sp = current_sp * (1 - row['RTO'] - row['RVP']) / (1 + row['GST'])
        abs_ads = current_sp * row['Ads']
        pre_set = 1e9
        moq = 1
        moq_flag = False

        dead_weight = row['Length']*row['Breadth']*row['Height']/5000
        weight = max(dead_weight, row['Weight'])

        commission_fee = 0
        fixed_fee = 0
        shipping_fee = 0

        i = 0

        while (pre_set > row['Settlement Asked']*moq or moq > 1) and abs(pre_set - row['Settlement Asked']*moq) > 0.2 and i < 90:
            
            i = i + 1
            if (temp > mop):


                if moq_flag == True:
                    temp = row['MRP']
                    mop = mop_one
                    temp = temp*moq
                    mop = mop*moq
                    moq_flag = False
        
                current_sp = temp
                abs_ads = current_sp * row['Ads']
                net_sp = current_sp * (1 - row['RTO'] - row['RVP']) / (1 + row['GST'])
            
                commission_fee = commission_fee_jiomart(row['Department'], row['Category'], row['Sub-Category'], row['Product Type'], current_sp)
                fixed_fee = fixed_fee_jiomart(current_sp)
                shipping_fee = shipping_fee_jiomart(row['Local'], row['Zonal'], row['National'], weight)

                pre_set = (net_sp - (1 - row['RTO'] - row['RVP']) * commission_fee_jiomart(row['Department'], row['Category'], row['Sub-Category'], row['Product Type'], current_sp) - 
                        (1 - row['RTO']) * (fixed_fee_jiomart(current_sp) + shipping_fee_jiomart(row['Local'], row['Zonal'], row['National'], weight)) -  
                        abs_ads * (1 - row['RTO'] - row['RVP'])) / (1 - row['RTO'] - row['RVP'])
                
                if (pre_set < row['Settlement Asked']*moq):
                    moq = moq+1
                    moq_flag = True
                    continue
            
            else:
                break
            temp = current_sp - (pre_set - row['Settlement Asked']*moq)/5
            
        return current_sp/moq, net_sp/moq, pre_set/moq, moq, shipping_fee/moq, commission_fee/moq, fixed_fee/moq, abs_ads/moq
    
    
    # For Meesho
    elif platform == 'Meesho':

        temp = row['MRP'] + row['Shipping']
        mop_one = row['MOP']
        mop = mop_one

        current_sp = row['MRP'] + row['Shipping']
        net_sp = current_sp * (1 - row['RTO'] - row['RVP']) / (1 + row['GST'])
        abs_ads = current_sp * row['Ads']
        pre_set = 1e9
        
        i = 0
        moq = 1
        moq_flag = False

        if (row['Platform'] == "Mall"):
        # What I need in the excel sheet ?
        # MRP, Shipping, RTO, RVP, Ops, Ads(%), GST, Expected Settlement

            while (pre_set > row['Settlement Asked']*moq or moq > 1) and abs(pre_set - row['Settlement Asked']*moq) > 0.2 and i <= 90:
                
                i = i + 1
                if (temp > mop):

                    if moq_flag == True:
                        temp = row['MRP'] + row['Shipping']
                        mop = mop_one
                        temp = temp*moq
                        mop = mop*moq
                        moq_flag = False
                        
                    current_sp = temp
                    abs_ads = current_sp * row['Ads']
                    net_sp = current_sp * (1 - row['RTO'] - row['RVP']) / (1 + row['GST'])

# present settlement = (SP + shipping)/product tax - shipping/shipping tax - commission - ads - ops
                    pre_set = (net_sp - row['Shipping']/1.18 - current_sp*0.05 - abs_ads - row['Ops'])
                        
                    if (pre_set < row['Settlement Asked']*moq):
                        moq = moq+1
                        moq_flag = True
                        continue
                
                else:
                    break
                temp = current_sp - (pre_set - row['Settlement Asked']*moq)/5


        elif (row['Platform'] == "MP"):

            while (pre_set > row['Settlement Asked']*moq or moq > 1) and abs(pre_set - row['Settlement Asked']*moq) > 0.2 and i <= 90:
                
                i = i + 1
                if (temp > mop):

                    if moq_flag == True:
                        temp = row['MRP'] + row['Shipping']
                        mop = mop_one
                        temp = temp*moq
                        mop = mop*moq
                        moq_flag = False
                        
                    current_sp = temp
                    abs_ads = current_sp * row['Ads']
                    net_sp = current_sp * (1 - row['RTO'] - row['RVP']) / (1 + row['GST'])

# present settlement = (SP + shipping)/product tax - shipping/shipping tax - commission - ads - ops
                    pre_set = (net_sp - row['Shipping']/1.18 - current_sp*0.00 - abs_ads - row['Ops'])
                        
                    if (pre_set < row['Settlement Asked']*moq):
                        moq = moq+1
                        moq_flag = True
                        continue
                
                else:
                    break
                temp = current_sp - (pre_set - row['Settlement Asked']*moq)/5

        return current_sp/moq, net_sp/moq, pre_set/moq, moq, abs_ads/moq

# Streamlit UI
st.set_page_config(page_title="Nexten Pricing Calculator", page_icon=":moneybag:", layout="wide")

with st.container():
    st.image("nexten.png", width=100)  # Nexten Logo

    st.title("Nexten Pricing Calculator")



# with st.container():
#     left_column, right_column = st.columns((2, 1))

#     with left_column:
#         platform = st.selectbox("Select Platform", ["Flipkart", "Amazon", "Jiomart", "Meesho"])

#         uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

#         if uploaded_file:
#             df_input = pd.read_excel(uploaded_file)
#             st.write("Input Data", df_input)
            
#             # The file must have 'Category', 'Local', 'Zonal', 'National', 'Weight', 'Ads', 'MRP', 'RVP', 'RTO', 'GST', 'Expected Settlement'
#             df_input[['SP', 'Present settlement', 'MOQ']] = df_input.apply(lambda row: pd.Series(calculate_sp(row, platform)), axis=1)
            
#             st.write("Output Data with SP", df_input)
            
#             output = "output_with_sp.xlsx"
#             df_input.to_excel(output, index=False)

#             # Download link for the Excel file
#             with open(output, "rb") as file:
#                 btn = st.download_button(
#                     label="Download Output Excel",
#                     data=file,
#                     file_name=output,
#                     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#                 )

#     with right_column:
#         st.image('ecom.jpg')  # Display an image from a file


def add_platform_specific_columns(df, platform):
    if platform == "Flipkart":
        df[['Final SP', 'Net SP', 'Present settlement', 'MOQ', 'Commission fee', 'Fixed fee',
            'Shipping fee', 'Reverse shipping fee', 'Pick and pack fee', 'Ads fee']] = df.apply(
            lambda row: pd.Series(calculate_sp(row, platform)), axis=1)
    elif platform == "Amazon":
        df[['Final SP', 'Net SP', 'Present settlement', 'MOQ', 'Referal fee', 'Closing fee',
            'Shipping fee', 'Pick and Pack fee', 'Ads fee']] = df.apply(
            lambda row: pd.Series(calculate_sp(row, platform)), axis=1)
    elif platform == "Jiomart":
        df[['Final SP', 'Net SP', 'Present settlement', 'MOQ', 'Shipping fee', 'Commission fee',
            'Fixed fee', 'Ads fee']] = df.apply(
            lambda row: pd.Series(calculate_sp(row, platform)), axis=1)
    elif platform == "Meesho":
        df[['Final SP', 'Net SP', 'Present settlement', 'MOQ', 'Ads fee']] = df.apply(
            lambda row: pd.Series(calculate_sp(row, platform)), axis=1)
    return df

with st.container():
    left_column, right_column = st.columns((2, 1))

    with left_column:
        platform = st.selectbox("Select Platform", ["Flipkart", "Amazon", "Jiomart", "Meesho"])

        uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

        st.write("Note: In the output Excel file whatever parameters you will get as an output e.g. Final SP, Net SP, Present Settlement etc is per unit, please consider multiplying with MOQ to get the final picture.")

        if uploaded_file:
            df_input = pd.read_excel(uploaded_file)
            st.write("Input Data", df_input)
            
            # Add platform-specific columns
            df_input = add_platform_specific_columns(df_input, platform)
            
            st.write("Output Data with SP", df_input)
            
            output = "output_with_sp.xlsx"
            df_input.to_excel(output, index=False)

            # Download link for the Excel file
            with open(output, "rb") as file:
                btn = st.download_button(
                    label="Download Output Excel",
                    data=file,
                    file_name=output,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    with right_column:
        st.image('ecom.jpg')  # Display an image from a file

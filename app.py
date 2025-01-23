from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

class Details(BaseModel):
    category: str
    price: float
    weight: float
    shipping_mode: str
    service_level: str
    product_size: str
    location: str

@app.get("/")
def read_root():
    return {"message": "Welcome to API home"}

@app.post("/api/v1/profitability-calculator")
def read_item(detail: Details):
    res={}
    response_final={}
    res['referralFee']=getReferralFee(detail)
    res['closingFee']=getClosingFee(detail)
    res['pickAndPackFee']=getPickFee(detail)
    res['weightHandlingFee']=getWeightHandlingFee(detail)
    response_final['totalFees']=res['referralFee']+res['closingFee']+res['pickAndPackFee']+res['weightHandlingFee']
    response_final['netEarnings']=detail.price-response_final['totalFees']
    response_final['breakdown']=res
    return response_final


def getReferralFee(detail):
    fee_data=json.load(open('brackets.json'))
    applicable_fees=fee_data[detail.category]
    fee_percent=0
    for i in applicable_fees.keys():
        if detail.price<=float(i):
            fee_percent=i
            break
    
    return detail.price*applicable_fees[fee_percent]

def getClosingFee(detail):
    fee_data=json.load(open('closing.json'))
    applicable_fees={}
    for i in fee_data.keys():
        if float(i)<=detail.price:
            applicable_fees=fee_data[i]
            break
    
    fee=0

    for idx in applicable_fees.keys():
        if detail.shipping_mode in idx:
            fee=applicable_fees[idx]
    
    return fee

def getPickFee(detail):
    if detail.product_size=='Standard':
        return 14
    elif detail.product_size=='Heavy & Bulky':
        return 26
    
    return 0

def getWeightHandlingFee(detail):
    fee_data=pd.read_csv('Amazon marketplace - Weight handling fees.csv')
    net_fee=0
    if detail.weight<=0.5:
        if detail.product_size!='Standard':
            net_fee+=0
        else:
            relevant_fee=fee_data[fee_data['Service Level'].str.contains(detail.service_level)]
            relevant_fee=relevant_fee[relevant_fee['Weight Range']=='First 500g']
            relevant_fee=relevant_fee[relevant_fee['Service Level'].str.contains(detail.product_size)]
            relevant_fee=relevant_fee[relevant_fee['Service Level'].str.contains(detail.shipping_mode)]
            relevant_fee=list(relevant_fee[detail.location])[0]
            if relevant_fee!="NA" and relevant_fee!="-":
                net_fee+=float(relevant_fee[1:])
    
    if detail.weight>=0.5:
        if detail.product_size!='Standard':
            net_fee+=0
        else:
            relevant_fee=fee_data[fee_data['Service Level'].str.contains('All')]
            relevant_fee=relevant_fee[relevant_fee['Weight Range'].str.contains('Additional 500g')]
            relevant_fee=relevant_fee[relevant_fee['Service Level'].str.contains(detail.product_size)]
            relevant_fee=relevant_fee[relevant_fee['Service Level'].str.contains(detail.shipping_mode)]
            relevant_fee=list(relevant_fee[detail.location])[0]
            if relevant_fee!="NA" and relevant_fee!="-":
                net_fee+=float(relevant_fee[1:])
    
    if detail.weight>=1:
        if detail.product_size!='Standard':
            net_fee+=0
        else:
            net_mult=min(4,detail.weight-1)
            relevant_fee=fee_data[fee_data['Service Level'].str.contains('All')]
            relevant_fee=relevant_fee[relevant_fee['Weight Range'].str.contains('Additional kg after 1kg')]
            relevant_fee=relevant_fee[relevant_fee['Service Level'].str.contains(detail.product_size)]
            relevant_fee=relevant_fee[relevant_fee['Service Level'].str.contains(detail.shipping_mode)]
            relevant_fee=list(relevant_fee[detail.location])[0]
            if relevant_fee!="NA" and relevant_fee!="-":
                net_fee+=float(relevant_fee[1:])*net_mult
    
    if detail.weight>=5:
        if detail.product_size=='Standard':
            net_mult=detail.weight-5
            relevant_fee=fee_data[fee_data['Service Level'].str.contains('All')]
            relevant_fee=relevant_fee[relevant_fee['Weight Range'].str.contains('Additional kg after 5kg')]
            relevant_fee=relevant_fee[relevant_fee['Service Level'].str.contains(detail.product_size)]
            relevant_fee=relevant_fee[relevant_fee['Service Level'].str.contains(detail.shipping_mode)]
            relevant_fee=list(relevant_fee[detail.location])[0]
            if relevant_fee!="NA" and relevant_fee!="-":
                net_fee+=float(relevant_fee[1:])*net_mult
    
    if detail.weight<=12 and detail.product_size!='Standard':
        relevant_fee=fee_data[fee_data['Service Level'].str.contains(detail.service_level)]
        relevant_fee=relevant_fee[relevant_fee['Weight Range']=='First 12kg']
        relevant_fee=relevant_fee[relevant_fee['Service Level'].str.contains(detail.product_size)]
        relevant_fee=relevant_fee[relevant_fee['Service Level'].str.contains(detail.shipping_mode)]
        relevant_fee=list(relevant_fee[detail.location])[0]
        if relevant_fee!="NA" and relevant_fee!="-":
            net_fee+=float(relevant_fee[1:])
    
    if detail.weight>12 and detail.product_size!='Standard':
        net_mult=detail.weight-12
        relevant_fee=fee_data[fee_data['Service Level'].str.contains('All')]
        relevant_fee=relevant_fee[relevant_fee['Weight Range'].str.contains('additional kg after 12kg')]
        relevant_fee=relevant_fee[relevant_fee['Service Level'].str.contains(detail.product_size)]
        relevant_fee=relevant_fee[relevant_fee['Service Level'].str.contains(detail.shipping_mode)]
        relevant_fee=list(relevant_fee[detail.location])[0]
        if relevant_fee!="NA" and relevant_fee!="-":
            net_fee+=float(relevant_fee[1:])*net_mult
    
    return net_fee
            

    
    

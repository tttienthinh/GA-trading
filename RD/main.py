#!/usr/bin/env python
# coding: utf-8

# In[30]:


import numpy as np
import pandas as pd

import ta, pickle


# In[31]:


df = pd.read_csv("../data/train.csv",
                 names=['date', 'open', 'high', 'low', 'close', 'volume'])
df


# In[32]:


def get_features(df):
    df_ = df[["open", "high", "low", "close"]]
    # adding RSI
    df_["rsi"] = ta.momentum.rsi(df.close, fillna=True)/100
    # adding StochasticOscillator
    stoch = ta.momentum.StochasticOscillator(high=df.high, low=df.low, close=df.close, fillna=True)
    df_["stoch"] = stoch.stoch() / 100
    df_["stoch_signal"] = stoch.stoch_signal() / 100
    # adding Aroon
    aroon = ta.trend.AroonIndicator(df.close, fillna=True)
    df_["aroon"] = (aroon.aroon_indicator() + 100) / 200
    df_["aroon_down"] = aroon.aroon_down() / 100
    df_["aroon_up"] = aroon.aroon_up() / 100
    
    return df_


# # GA

# ## Create Population

# In[33]:


# indiv shape (6, 2, 2)
n_indicator = 6 # 6 indicators + stoploss take profit
n_action = 2
n_borne = 2
def conform_indiv(indiv):
    for indicator in range(n_indicator+1): # 6 indicators + stoploss take profit
        for action in range(n_action):
            inf_index = (indicator, action, 0)
            sup_index = (indicator, action, 1)
            if indiv[inf_index] > indiv[sup_index]:
                indiv[inf_index], indiv[sup_index] = indiv[sup_index], indiv[inf_index]
    for borne in range(n_borne):
        for action in range(n_action):
            index = (-1, action, borne)
            indiv[index] = (indiv[index] + borne)/2
    return indiv

def create_indiv():
    indiv = np.random.random((7, 2, 2))
    indiv = conform_indiv(indiv)
    return indiv


# In[34]:


def create_pop(size=100):
    pop = [(None, create_indiv(), 0) for i in range(size)]
    return pop
        


# ##  Evaluation

# In[35]:


spread = 30
indicators = ['rsi', 'stoch', 'stoch_signal', 'aroon', 'aroon_down', 'aroon_up']

def match_condition(indiv, df):
    for i in range(n_indicator):
        inf = indiv[i, 0]
        sup = indiv[i, 1]
        value = df[indicators[i]]
        if value < inf or value > sup:
            return False
    return True

def trade(df, low, high, start):
    ls = df.values.tolist()
    n = len(ls)
    for i in range(n):
        if ls[i][0] > high: # test high
            return high, i
        if ls[i][1] < low: # test low
            return low, i
    return start, n

def eval_indiv(indiv, df):
    n = len(df)
    score = 0
    i = 15
    while i < n-15:
        df_indicators = df.iloc[i][indicators]
        price = df.iloc[i]["close"]
        if match_condition(indiv[:, 0], df_indicators): # Test achat
            out, d = trade(df.iloc[i:][["high", "low"]], 
                            price * (indiv[-1, 0, 0]+.5),
                            price * (indiv[-1, 0, 1]+.5),
                            price
                           )
            score += (out-price) - spread
            i += d
        if match_condition(indiv[:, 1], df_indicators): # Test vente
            out, d = trade(df.iloc[i:][["high", "low"]], 
                            price * (indiv[-1, 1, 0]+.5),
                            price * (indiv[-1, 1, 1]+.5),
                            price
                           )
            score += (price-out) - spread
            i += d
        i+=1
    return score


# # Selection

# In[36]:


def crossover(indiv1, indiv2, rate=.5):
    indiv1 = indiv1.reshape((((n_indicator+1)*n_action, n_borne)))
    indiv2 = indiv2.reshape((((n_indicator+1)*n_action, n_borne)))
    indiv = []
    for i in range((n_indicator+1)*n_action):
        if np.random.random() > rate:
            indiv.append(indiv1[i])
        else:
            indiv.append(indiv2[i])
    indiv = np.array(indiv).reshape((n_indicator+1, n_action, n_borne))
    return indiv
    
def create_cross_pop(ls, size):
    ls_ = []
    n = len(ls)
    for i in range(size):
        a, b = np.random.randint(n, size=2)
        ls_.append((None, crossover(ls[a][1], ls[b][1]), 0))
    return ls_
    
def mutation(ls, rate=.3):
    for i in range(len(ls)):
        indiv = ls[i][1]
        indiv_ = create_indiv()
        indiv = crossover(indiv, indiv_, rate)
        ls[i] = (None, indiv, 0)
    return ls

def new_gen(ls):
    ls_ = []
    best_times = 0
    for (score, indiv, times) in ls[:10]: # taille 10
        if score > 0:
            times += 1
        best_times = max(best_times, times)
        ls_.append((score, indiv, times+1))
    ls_ = ls_ + mutation(ls_) # taille 10+10 = 20
    ls_ = ls_ + create_cross_pop(ls[:30], 50) # taille 20+50 = 70
    ls_ = ls_ + create_pop(30) # taille 70+30 = 100
    return ls_, best_times


# # Processus

# In[37]:


df = get_features(df)
df


# In[38]:


list_df = []
delta = 2120
for i in range(40):
    list_df.append(df.iloc[80+i*delta:80+(i+1)*delta:])
len(list_df)


# In[43]:


import time
best_score = -1
best_times = 0
gen = 1
population = create_pop()
while best_times < 40:
    df_ = list_df[gen%40]
    for i in range(len(population)):
        population[i] = (eval_indiv(population[i][1], df_), population[i][1], population[i][2])
    population.sort(key=lambda x: x[0], reverse=True)
    best_score = population[0][0]
    lowest_score = population[-1][0]
    liste_best.append(best_score)
    with open(f"record/{gen}", "wb") as fp:   #Pickling
        pickle.dump(population[0], fp)
        fp.close
    with open(f"record/actual", "wb") as fp:   #Pickling
        pickle.dump(population, fp)
    population, best_times = new_gen(population)
    print(f"Generation {gen} best_score : {best_score}")
    print(f"Times : {best_times}")
    print(f"lowest_score : {lowest_score}")
    gen += 1
    time.sleep(60)






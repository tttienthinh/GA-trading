#!/usr/bin/env python
# coding: utf-8

# In[264]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import ta, pickle


# In[273]:


df = pd.read_csv("data/train.csv", 
                 names=['date', 'open', 'high', 'low', 'close', 'volume'])
df


# In[62]:


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

# In[215]:


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
    return indiv

def create_indiv():
    indiv = np.random.random((7, 2, 2))
    indiv = conform_indiv(indiv)
    return indiv


# In[216]:


def create_pop(size=100):
    pop = [(None, create_indiv()) for i in range(size)]
    return pop
        


# ##  Evaluation

# In[279]:


spread = 15
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
    for i in range(len(ls)):
        if ls[i][0] > high: # test high
            return high
        if ls[i][1] < low: # test low
            return low
    return start

def eval_indiv(indiv, df):
    n = len(df)
    score = 0
    for i in range(15, n-15):
        df_indicators = df.iloc[i][indicators]
        if match_condition(indiv[:, 0], df_indicators): # Test achat
            price = df.iloc[i]["close"]
            out = trade(df.iloc[i:][["high", "low"]], 
                        price * (indiv[-1, 0, 0]+.5),
                        price * (indiv[-1, 0, 1]+.5),
                        price
                       )
            score += (out-price) - spread
        
        if match_condition(indiv[:, 1], df_indicators): # Test vente
            price = df.iloc[i]["close"]
            out = trade(df.iloc[i:][["high", "low"]], 
                        price * (indiv[-1, 1, 0]+.5),
                        price * (indiv[-1, 1, 1]+.5),
                        price
                       )
            score += (price-out) - spread
    return score


# # Selection

# In[233]:


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
        ls_.append((None, crossover(ls[a][1], ls[b][1])))
    return ls_
    
def mutation(ls, rate=.2):
    n = len(ls)
    for i in range(int(n*rate)):
        a = np.random.randint(n)
        indiv = ls[a][1]
        indiv_ = create_indiv()
        indiv = crossover(indiv, indiv_, rate)
        ls[a] = (None, indiv)
    return ls

def new_gen(ls):
    ls_ = ls[:10]
    ls_ = ls_ + create_cross_pop(ls[:30], 60)
    ls_ = mutation(ls_)
    ls_ = ls_ + create_pop(30)
    return ls_


# # Processus

# In[286]:


df = get_features(df)
df


# In[289]:


list_df = []
delta = 2120
for i in range(40):
    list_df.append(df.iloc[80+i*delta:80+(i+1)*delta:])
len(list_df)


# In[ ]:


best_score = -1
gen = 1
population = create_pop()
liste_best = [0]*40
while sum(np.array(liste_best[-40:]) > 0) < 40:
    df_ = list_df[gen%40]
    for i in range(len(population)):
        population[i] = (eval_indiv(population[i][1], df_), population[i][1])
    population.sort(key=lambda x: x[0], reverse=True)
    best_score = population[0][0]
    liste_best.append(best_score)
    with open(f"record/{gen}", "wb") as fp:   #Pickling
        pickle.dump(population[0], fp)
        fp.close
    with open(f"record/actual", "wb") as fp:   #Pickling
        pickle.dump(population, fp)
    print(f"Generation {gen} best_score : {best_score}")
    print(f"lowest_score : {population[-1][0]}")
    population = new_gen(population)
    gen += 1


# # Testing result

# In[260]:


with open(f"record/1", "rb") as fp:   #Pickling
    population = pickle.load(fp)
population


# In[270]:


def eval_indiv_test(indiv, df):
    n = len(df)
    score = 0
    ordre = [[], []]
    for i in range(15, n-15):
        df_indicators = df.iloc[i][indicators]
        if match_condition(indiv[:, 0], df_indicators): # Test achat
            print("ACHAT")
            price = df.iloc[i]["close"]
            ordre[0].append(i)
            ordre[1].append(price)
            out = trade(df.iloc[i:][["high", "low"]], 
                        price * (indiv[-1, 0, 0]+.5),
                        price * (indiv[-1, 0, 1]+.5),
                        price
                       )
            score += (out-price) - spread
        
        if match_condition(indiv[:, 1], df_indicators): # Test vente
            print("VENTE")
            price = df.iloc[i]["close"]
            ordre[0].append(i)
            ordre[1].append(price)
            out = trade(df.iloc[i:][["high", "low"]], 
                        price * (indiv[-1, 1, 0]+.5),
                        price * (indiv[-1, 1, 1]+.5),
                        price
                       )
            score += (price-out) - spread
    return score, ordre
score, ordre = eval_indiv_test(population[1], test)
score


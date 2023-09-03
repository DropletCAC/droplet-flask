import firebase_admin
from firebase_admin import credentials, firestore 
import json 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from datetime import datetime 

today = datetime.today()
cred = credentials.Certificate("credentials.json")
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

def prepare_data(monthly_usage):
    data = []

    for month, value in monthly_usage.items():
        for day, daily_usage in value.items():
            x = 0
            for hour in daily_usage:
                data.append([month, day, x, int(hour)])
                x += 1         
    return data


def graph_lof(X, radius):
    plt.scatter(X[:, 0], X[:, 1], color="k", s=3.0, label="Data points")


    scatter = plt.scatter(
        X[:, 0],
        X[:, 1],
        s=1000 * radius,
        edgecolors="r",
        facecolors="none",
        label="Outlier scores",
    )
    
    plt.axis("tight")
    plt.xlim((-5, 30))
    plt.ylim((0, 100))
    plt.title("Local Outlier Factor (LOF)")
    plt.show()
    

def detect_leak(user, section, *, month, day):
    #user = BwyZV2GQN0O1DVDsGl4BAj9W5q92
    monthly_usage = db.collection("users").document(user).collection("meters").document(section).collection("usage").document("2023").get().to_dict()
    data = prepare_data(monthly_usage)
    
    df = pd.DataFrame(data, columns=["Month", "Day", "Hour", "Usage"])
    df_array = df.to_numpy()

    X = df[["Hour", "Usage"]].to_numpy()

    clf = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
    y_pred = clf.fit_predict(X)
    X_scores = clf.negative_outlier_factor_
    radius = (X_scores.max() - X_scores) / (X_scores.max() - X_scores.min())

    graph_lof(X, radius)
    
    indices = (np.where(radius > 0.7))

    print(df_array[indices])
    print(radius[indices])    
   
    response = {
            "success": True,
            "leaks": None,
    }
        
    if df_array[indices].size > 0:
  
        for leak in df_array[indices]:
            print(leak)
            leak_data = {
                "month": int(leak[0]),
                "day": int(leak[1]),
                "hour": int(leak[2]),
                "usage": int(leak[3])
            }
            
            if (leak_data['month'] == month) and (leak_data['day'] == day):
                print(leak_data)    
                print("leaking out the bazoonkies")
                response['leaks'] = leak_data   
    print(response)
    return response

if __name__ == '__main__':
    detect_leak("BwyZV2GQN0O1DVDsGl4BAj9W5q92", "bathroom", month=9, day=3)
    
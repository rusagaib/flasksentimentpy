from flask import Flask, render_template
import pandas as pd
import numpy as np
import json
import plotly
import plotly.express as px
from wordcloud import WordCloud
import os
import base64
import io

def newLegend(fig, newNames):
    newLabels = []
    for item in newNames:
        for i, elem in enumerate(fig.data[0].labels):
            if elem == item:
                #fig.data[0].labels[i] = newNames[item]
                newLabels.append(newNames[item])
    fig.data[0].labels = np.array(newLabels)
    return(fig)

def barchart(kamusall):
    df3 = pd.DataFrame(kamusall, columns=["term","df"])
    short_df3 = df3.sort_values(by='df', ascending=False)
    # print(short_df3.head(100))
    fig = px.bar(short_df3.head(100), x='term', y='df')
    barJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return barJSON

def piechart(dataset):
    df2 = pd.DataFrame(dataset, columns=["label"])
    grup = df2.groupby('label').size().reset_index(name='size')
    # fig = px.pie(grup, values='size' , names='label')
    fig = px.pie(grup, values='size' , names='label')
    fig=newLegend(fig, {0:"0 - Negatif",
                        1:"1 - Positif"})
    pieJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return pieJSON

def get_wordcloud(dataframe):
    pil_img = WordCloud(width=700, height=300)
    wordCloud=pil_img.generate_from_frequencies(dataframe).to_image()
    img= io.BytesIO()
    wordCloud.save(img,"PNG")
    img.seek(0)
    img_b64=base64.b64encode(img.getvalue()).decode()
    return img_b64

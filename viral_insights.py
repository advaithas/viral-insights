import tkinter as tk
from tkinter import ttk
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from pandastable import Table, TableModel


def get_covid_data(country):
    url = f"https://api.covid19api.com/total/dayone/country/{country}"
    response = requests.get(url)
    response_json = response.json()
    covid_data = []
    for data in response_json:
        covid_data.append((data["Confirmed"], data["Deaths"], data["Recovered"], data["Active"], data["Date"]))
    return covid_data

def create_graph(covid_data):
    figure = plt.Figure(figsize=(6, 5), dpi=100)
    ax = figure.add_subplot(111)
    dates = [data[4] for data in covid_data]
    confirmed_cases = [data[0] for data in covid_data]
    ax.plot(dates, confirmed_cases)
    ax.set_title("Confirmed Cases Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Cases")
    return figure

def update_graph():
    country = selected_country.get()
    covid_data = get_covid_data(country)
    figure = create_graph(covid_data)
    canvas = FigureCanvasTkAgg(figure, root)
    canvas.get_tk_widget().grid(row=1, column=1)
    predict_future(covid_data)
    show_table(covid_data)
    

def create_table(covid_data, future_dates, future_cases):
    table = ttk.Treeview(root)
    table["columns"] = ("confirmed", "deaths", "recovered", "active", "date", "predicted")
    table.heading("confirmed", text="Confirmed Cases")
    table.heading("deaths", text="Deaths")
    table.heading("recovered", text="Recovered")
    table.heading("active", text="Active Cases")
    table.heading("date", text="Date")
    table.heading("predicted", text="Predicted Cases")
    for data in covid_data:
        table.insert("", "end", text="", values=data)
    for i in range(len(future_dates)):
        table.insert("", "end", text="", values=("", "", "", "", future_dates[i].strftime("%Y-%m-%d"), future_cases[i]))
    return table


def predict_future(covid_data, days_in_future=30):
    last_date = covid_data[-1][4]
    future_dates = pd.date_range(start=last_date, periods=days_in_future+1)
    future_cases = []
    for i in range(len(future_dates)):
        future_cases.append(np.nan)
    for i in range(len(covid_data)-1):
        days_diff = (pd.to_datetime(covid_data[i+1][4]) - pd.to_datetime(covid_data[i][4])).days
        daily_increase = (covid_data[i+1][0] - covid_data[i][0]) / days_diff
        for j in range(days_diff):
            index = (pd.to_datetime(covid_data[i][4]) + pd.DateOffset(days=j+1))
            if index in future_dates:
                future_cases[future_dates.get_loc(index)] = round(covid_data[i][0] + daily_increase * (j+1))
    future_cases[-1] = round(covid_data[-1][0] + daily_increase * days_in_future)
    return future_dates, future_cases


def show_table(covid_data):
    table_frame = tk.Frame(root)
    table_frame.grid(row=2, column=0, columnspan=2)
    pt = Table(table_frame, dataframe=pd.DataFrame(covid_data, columns=["Confirmed", "Deaths", "Recovered", "Active", "Date"]), showtoolbar=True, showstatusbar=True)
    pt.show()


root = tk.Tk()
root.title("COVID-19 Data Visualization")

selected_country = tk.StringVar()
country_dropdown = ttk.Combobox(root, textvariable=selected_country)
country_dropdown['values'] = ('USA', 'India', 'Brazil', 'Russia', 'UK')
country_dropdown.grid(row=0, column=0)

button = tk.Button(root, text="Get Data", command=update_graph)
button.grid(row=0, column=1)

root.mainloop()



import tkinter as tk
import webbrowser
from newsapi import NewsApiClient

# Initialize News API client
newsapi = NewsApiClient(api_key='c2f1dcde50c448c08a2c2b6b9c0bc580')

# Define function to retrieve top headlines for a given country
def get_top_headlines(country_code):
    top_headlines = newsapi.get_top_headlines(q='covid', country=country_code)
    articles = top_headlines['articles']
    return articles

# Define function to display news headlines for a given country
def display_news(country_code):
    # Retrieve top headlines for selected country
    articles = get_top_headlines(country_code)
    
    # Clear any existing news headlines
    for widget in news_frame.winfo_children():
        widget.destroy()
    
    # Display news headlines for selected country
    for article in articles:
        # Create label for news headline
        label = tk.Label(news_frame, text=article['title'], cursor='hand2', font=('Arial', 12, 'bold'), fg='blue', wraplength=700)
        label.pack(pady=5)
        
        # Open news article in browser when label is clicked
        def callback(event, url=article['url']):
            webbrowser.open_new(url)
        label.bind("<Button-1>", callback)

# Create Tkinter window
window = tk.Tk()
window.title('COVID-19 News')
window.geometry('800x600')

# Create frame for country dropdown menu
country_frame = tk.Frame(window)
country_frame.pack(pady=20)

# Create label for country dropdown menu
country_label = tk.Label(country_frame, text='Select a country:', font=('Arial', 14))
country_label.pack(side=tk.LEFT, padx=10)

# Create list of country codes and names
countries = [
    ('au', 'Australia'),
    ('ca', 'Canada'),
    ('cn', 'China'),
    ('fr', 'France'),
    ('de', 'Germany'),
    ('in', 'India'),
    ('jp', 'Japan'),
    ('nz', 'New Zealand'),
    ('sg', 'Singapore'),
    ('gb', 'United Kingdom'),
    ('us', 'United States')
]

# Create dictionary to map country names to country codes
country_dict = {name: code for code, name in countries}

# Create StringVar to hold selected country name
country_var = tk.StringVar()

# Set default country to first country in list
country_var.set(countries[0][1])

# Create dropdown menu for selecting country
country_dropdown = tk.OptionMenu(country_frame, country_var, *list(country_dict.keys()), command=lambda value: display_news(country_dict[value]))
country_dropdown.pack(side=tk.LEFT)

# Create frame for news headlines
news_frame = tk.Frame(window)
news_frame.pack(pady=20)

# Call display_news function to display initial news headlines
display_news(country_dict[country_var.get()])

# Run Tkinter event loop
window.mainloop()

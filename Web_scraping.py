from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import json
import matplotlib.pyplot as plt
import re

# Loading the webpage with the list of Marvel movies and conversion into a beautiful soup object

marvel = requests.get('https://en.wikipedia.org/wiki/List_of_Marvel_Cinematic_Universe_films').text

soup = bs(marvel)

# print(soup.prettify())

# find the movie links

links = soup.find_all('i')


def get_links(lin):

    m_links = []

    for link in lin:
        a = link.find('a')
        if a is not  None:

            wiki = a.get('href')

            m_links.append(wiki)

    return m_links


movie_links = get_links(links)

# Save and load all links


def save_links(title, data):

    with open(title, 'w', encoding="utf-8") as f:

        json.dump(data, f, ensure_ascii=False, indent=2)


def load_links(title, data):

    with open(title, encoding="utf-8") as f:

        return json.load(f)


save_links("movie_links.json",movie_links)

# Find all the Marvel movies that were produced

tables = soup.find_all("table", attrs={"class": "wikitable"})

# print("Number of tables: ", len(tables))


# Create a function that takes a web table and returns a dataframe

def table_to_df(table):

# Scrape first table

    table1 = table
    body = table1.find_all("tr")
    head = body[0]  # 0th item is the header row
    body_rows = body[1:]  # All other items becomes the rest of the rows


# Titles of the first table

    headings = []
    for item in head.find_all("th"):
        item = (item.text).rstrip("\n")
        headings.append(item)

    all_rows = []

    for row_num in range(len(body_rows)):
        row = []

        for row_item in body_rows[row_num].find_all("th"):
            r = re.sub("(\xa0)|(\n)|,", "", row_item.text)
            row.append(r)

        for row_item in body_rows[row_num].find_all("td"):

            r = re.sub("(\xa0)|(\n)|,", "", row_item.text)
            row.append(r)
        all_rows.append(row)

    df = pd.DataFrame(data=all_rows, columns=headings)

# remove all square brackets and parenthesis

    for column in df.columns:

        df[column] = df[column].str.replace(r"\(.*\)", "")
        df[column] = df[column].str.replace(r"\[.*\]", "")

    return df

# Create a function that takes all the tables and store their content into dataframes

# def multi_dfs(tables):

#     fd = {str(x): pd.DataFrame() for x in range(0, len(tables))}

#     for i in range(0, len(tables)):

#          fd[str(i)] = table_to_df(tables[i])


df = table_to_df(tables[0])
df.drop([0, 7, 14], 0, inplace=True)
df.reset_index(drop=True, inplace=True)
# df.to_csv('marvel_movies.csv')


# Counting how many movies were produced each year

pd.to_datetime(df['U.S. release date'])
df['year'] = pd.DatetimeIndex(df['U.S. release date']).year
df1 = df.groupby(['year']).count()
# print(df1)


# Plot our results in a histogram

plot_m = plt.hist(df.year, bins=range(2008, 2020), edgecolor='white', linewidth=1, color='r')

plt.xticks(range(2008, 2020))
plt.xlabel('U.S release date')
plt.ylabel('Number of movies')

# plt.show()


# Find how many films were produced by Kevin Feige

df['Kevin Feige'] = df['Producer(s)'].str.contains('Kevin Feige')
print(df['Kevin Feige'].count())

# importing libraries
import requests
import pandas as pd
from bs4 import BeautifulSoup

# http headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

# take the url for the first df
world_url = "https://restcountries.com/v3.1/all?fields=name,languages,area,capital,currencies,latlng,languages,region,borders,subregion"

# reponse
world_response = requests.get(world_url)
# convert to json
world_response = world_response.json()

# convert to dataframe
df1 = pd.DataFrame(world_response)

# cleaning
df1["name"] = df1["name"].apply(lambda x:x["common"])
df1["currency"] = df1["currencies"].apply(lambda x: list(x.values())[0]["name"] if isinstance(x, dict) and len(x) > 0 else None)
df1["capital"] = df1["capital"].apply(lambda x: x[0] if isinstance(x,list) and len(x) > 0 else None)
df1["languages"] = df1["languages"].apply(lambda x: list(x.values())[0] if isinstance(x, dict) and len(x) > 0 else None)
df1["latitude"] = df1["latlng"].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
df1["longitude"] = df1["latlng"].apply(lambda x: x[1] if isinstance(x, list) and len(x) > 0 else None)
df1["borders"] = df1["borders"].apply(lambda x: x if len(x) > 0 else None)
df1 = df1[["name", "currency", "capital", "languages", "latitude", "longitude", "area", "region", "subregion", "borders"]]

# take the url for the second df
economic_url = "https://tradingeconomics.com/matrix"

# send request and parsing
economic_response = requests.get(economic_url, headers=headers)
soup = BeautifulSoup(economic_response.text, "html.parser")

# find all the elements
table = soup.find("table", class_="table table-hover sortable-theme-minimal table-heatmap")
header = [th.get_text(strip=True) for th in table.find("thead").find("tr").find_all("th")]

rows = []
for tr in table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        if cols:
            rows.append(cols)

# to dataframe
df2 = pd.DataFrame(rows, columns=header)

# merging the dataframe
df_merged = pd.merge(
      df1,
      df2,
      left_on= "name",
      right_on= "Country",
      how= "inner"
)

# dropping the country column 
df_merged = df_merged.drop("Country", axis=1)

# storing to csv
df_merged.to_csv("world_economics.csv", index=False, encoding="utf-8")
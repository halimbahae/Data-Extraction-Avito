# Cellule 1 - Importation des bibliothèques :
# Cette cellule importe les bibliothèques nécessaires pour exécuter le code.
# Les bibliothèques requests, BeautifulSoup, js2py et pandas sont importées.

import requests
from bs4 import BeautifulSoup
import js2py
import pandas as pd

# Lists to store the scraped data
# Cellule 2 - Initialisation des listes :
# Cette cellule initialise les listes qui seront utilisées pour stocker les données extraites du site Web.
# Chaque liste correspond à une catégorie de données spécifique.

addressLocality = []
addressRegion = []
categorys = []
product_id = []
telephones = []
publicationType = []
names = []
prices = []
pages = [str(i) for i in range(2, 10000)]

# Cellule 4 - Extraction des données pour chaque produit :
# Cette cellule extrait les données pour chaque produit en envoyant une requête HTTP pour chaque URL de produit.
# Les données extraites sont stockées dans les listes correspondantes.


for page in pages:
    url = "https://www.avito.ma/fr/maroc/%C3%A0_vendre?o=" + page
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=30)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    pg = session.get(url)
   
    if pg.status_code != 200:
        break
    
    html_soup = BeautifulSoup(pg.text, 'html.parser')
    
    #  Extraction des données si elles ne sont pas vides
    items_list = html_soup.find(class_="listing listing-thumbs").findAll("div", class_="item-info ctext1 mls")
    items_urls = [i.find('a', href=True)['href'] for i in items_list] 
    
    for url in items_urls:
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        response = session.get(url)
        data = {}
        
        if response.status_code != 200:
            break
        
        html_soup = BeautifulSoup(response.text, "html.parser")
        price = html_soup.find("div", class_="panel-body").span.string
        
        script = html_soup.find("div", class_="container mbm").find_all("script", {"type": "text/javascript"})[-1]
        context = js2py.EvalJs()
        context.execute(script.string)
        
        if context.data:
            data = dict(context.data.to_dict())
        
        # If the data is not empty, extract:
        if data:
            prices.append(price)  # The price
            addressLocality.append(data.get("addressLocality", ""))  # Local address
            addressRegion.append(data.get("addressRegion", ""))  # Region address
            categorys.append(data.get("category", ""))  # Category
            telephones.append(data.get("telephone", ""))  # Telephone
            publicationType.append(data.get("publisherType", ""))  # Publication type
            names.append(data.get("name", ""))  # Product name
            product_id.append(data.get("id", ""))  # Product ID


# Cellule 5 - Sauvegarde des données dans un fichier Excel :
# Cette cellule crée un DataFrame à partir des listes de données extraites et le sauvegarde dans un fichier Excel nommé "Avito_Dataset.xlsx".
# Les colonnes du DataFrame correspondent aux différentes catégories de données.


# Save the data in an Excel file:
dataset = pd.DataFrame({
    "Product_name": names,
    "Product_id": product_id,
    "Product_Category": categorys,
    "price": prices,
    "Phone_number": telephones,
    "Professional_Publication": publicationType,
    "Region_address": addressRegion,
    "Local_address": addressLocality
})
dataset.to_excel("Avito_Dataset2.xlsx")

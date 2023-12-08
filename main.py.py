import httpx
from selectolax.parser import HTMLParser
import time
from urllib.parse import urljoin
from dataclasses import asdict, dataclass , fields
import csv



@dataclass
class Item:
    name:str | None
    item_num:str | None
    rating:float | None
    price:str | None
    


#getting html function

def get_html(url,**kwargs):
    
   
    headers= {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
      
    if kwargs.get("page"):
        
        response = httpx.get(url+str(kwargs.get("page")),headers=headers,follow_redirects=True)
    else:
        response = httpx.get(url,headers=headers,follow_redirects=True)
   
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}. PAGE LIMIT EXCEEDED")
        return False
    #print(response.status_code)
    html = HTMLParser(response.text)
     
    return html


def extract_text(html,sel):
    try:
        return html.css_first(sel).text()
    except AttributeError:
        return None
  
    
def parse_page(html): 
        products = html.css("li.VcGDfKKy_dvNbxUqm29K")
        
        for product in  products:
            yield urljoin("https://www.rei.com",product.css_first('a').attributes['href'])
            
            
def parse_item_page(html):
    
    new_item =Item(
        name=extract_text(html, "h1#product-page-title"),
        item_num=extract_text(html, "span#product-item-number"),
        rating=extract_text(html, "span.cdr-rating__number_13-5-3"),
        price=extract_text(html, "span#buy-box-product-price")
        )
    return asdict(new_item)

def export_to_json(products):
    with open ("products.json","w",encoding="utf-8") as f:
        json.dump(products,f, ensure_ascii=False,indent=4)

def export_to_csv(data_list, filename='products.csv'):
    # Extract keys from the first dictionary to use as header in CSV
    if data_list:
        keys = data_list[0].keys()
    else:
        return  # No data to write
    
    # Write data to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data_list)
    print("SAVED TO CSV") 

def main():
    products = []
    baseUrl="https://www.rei.com/c/camping-and-hiking/f/scd-deals?page="
    for i in range(1,20):
        print(f"Gathering Page {i}")
        html=get_html(baseUrl,page=i)
        time.sleep(1)
        if html is False:
            break
        products_urls=parse_page(html)
        for url in products_urls:
            print(url)
            html=get_html(url, page=i)
            products.append(parse_item_page(html))
            time.sleep(0.5)
            
    
    for product in products:
        print(product)
    
    #export_to_json(products)
    export_to_csv(products)

if __name__ == "__main__":
    main()            
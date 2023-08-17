from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode, parse_qs,quote
import re
import requests
import asyncio
import aiohttp
import json


def last_entry(x):
    return x[-1]

def does_exist(x):
    return len(x) > 1

def make_thumbnails(location_array):
    thumbnails = []
    for i in range(1, len(location_array)):
        try:
            thumbnail_details = location_array[i].split('</div>')[0].split('background-image:url(')[1].split(')')[0]
            thumbnails.append(thumbnail_details)
        except IndexError:
            pass
    return thumbnails

def clean_url(url):
    # delete unnecessary parameters from product page url
    url = urlparse(url)
    params = dict(parse_qsl(url.query))
    params.pop('_appId', None)
    params.pop('pid', None)
    params.pop('_refId', None)
    params.pop('cmpid', None)
    url = urlunparse((url.scheme, url.netloc, url.path, url.params, urlencode(params), url.fragment))
    return url

def extract_product_name(webPageContents):
    try:
        product_name=None
        if '<h1' in webPageContents:
            product_name = webPageContents.split('<h1')[1].split('</span>')[0].split('">')[2].replace('<!-- -->', '').replace('<!-- --', '')
            try:
                sub_name = webPageContents.split('class="B_NuCI')[1].split('</span>')[0].split('>')[1].replace('<!-- -->', '').replace('<!-- --', '')
                product_name += sub_name
            except Exception:
                pass
        else:
            product_name = webPageContents.split('class="B_NuCI')[1].split('</span>')[0].split('>')[1].replace('<!-- -->', '')

        return product_name

    except Exception:
        return None

def calculate_discount(webPageContents):
    currentPrice=None
    originalPrice=None
    discountDetailsArray=[]

    try:
        currentPrice = webPageContents.split('<h1')[1].split(">₹")[1].split("</div>")[0]
        currentPrice = int(currentPrice.replace(",", ""))
        product_id = webPageContents.split('productId":"')[1].split('","')[0]
        discountDetailsArray = webPageContents.split('<h1')[1].split(">₹")[2].split("</div>")[0].split('<!-- -->')
        originalPrice = int(discountDetailsArray[1].replace(",", ""))
    except Exception as e:
        originalPrice = currentPrice

    try:
        if currentPrice is None or currentPrice == "undefined" or currentPrice == "NaN" or int(currentPrice) < 1:
            currentPrice = int(webPageContents.split('_30jeq3 _16Jk6d')[1].split('</div>')[0].split('>')[1].replace('₹', '').replace(',', ''))
    except Exception as e:
        pass

    try:
        if originalPrice is None or originalPrice == "undefined" or originalPrice == "NaN" or int(originalPrice) < 1:
            originalPrice = int(webPageContents.split('_3I9_wc _2p6lqe')[1].split('</div>')[0].split('>')[1].replace('₹', '').replace(',', ''))
    except Exception as e:
        pass

    discount_percent =int(100 * (1 - currentPrice / originalPrice))

    return {"discount_percent":discount_percent, "currentPrice":currentPrice, "originalPrice":originalPrice}




def extract_thumbnails(webPageContents, productName):
    thumbnailDetailsArray = webPageContents.split('height:64px')
    thumbnails = []

    if does_exist(thumbnailDetailsArray):
        thumbnails = make_thumbnails(thumbnailDetailsArray)
    else:
        thumbnailDetailsArray = webPageContents.split('_20Gt85 _1Y')
        if does_exist(thumbnailDetailsArray):
            thumbnails = make_thumbnails(thumbnailDetailsArray)
        else:
            thumbnailDetailsArray = webPageContents.split('_2r_T1I')
            if does_exist(thumbnailDetailsArray):
                thumbnails = make_thumbnails(thumbnailDetailsArray)

    if len(thumbnails) == 0:
        try:
            thumbnailDetailsUsingName = productName.split('(')[0].strip()
            thumb = webPageContents.split(f'alt="{thumbnailDetailsUsingName}')
            if len(thumb) == 1:
                thumb = webPageContents.split(f'alt="{thumbnailDetailsUsingName[:5]}')
            thumb = thumb[1].split('src="')[1].split('"')[0]
            thumbnails.append(thumb)
        except Exception as e:
            pass

    try:
        imgArray = webPageContents.split('<img src="')
        imgArray.pop(0)
        for img in imgArray:
            img = img.split('"')[0]
            if 'promos' not in img and img[-2:].isdigit() and int(img[-2:]) >= 50:
                if img not in thumbnails:
                    thumbnails.append(img)
    except Exception as e:
        pass

    return thumbnails
    
def extract_fassured_status(webPageContents):
    fAssuredDetails = None
    fassured = False
    try:
        fAssuredDetails = webPageContents.split('<h1')[1].split('Product Description')[0].split('fk-cp-zion/img/fa_62673a.png')
        fassured = does_exist(fAssuredDetails)
    except Exception as e:
        fassured = does_exist(webPageContents.split('Product Description')[0].split('fk-cp-zion/img/fa_62673a.png'))

    return {"fassured":fassured, "fAssuredDetails":fAssuredDetails}


def extract_proper_uri(webPageContents, uri):
    result_dict = {}
    proper_uri = None

    try:
        small_uri = webPageContents.split('product.share.pp"')
        if does_exist(small_uri):
            small_uri = last_entry(small_uri[-2].split('"')) + 'product.share.pp'
            proper_uri = small_uri
        
        if proper_uri[0] == '/':
            proper_uri = 'https://www.flipkart.com' + proper_uri
        
        x = 0
        if uri.split('/')[0] == '':
            x = 1
        
        proper_uri2 = f"https://www.flipkart.com/{uri}"
        if uri.split('/')[x] == 's' or uri.split('/')[x] == 'dl':
            proper_uri2 = f"https://dl.flipkart.com/{uri}"
        
        proper_uri2 = clean_url(proper_uri2)
        proper_uri = clean_url(proper_uri)
        
        if len(proper_uri2) < len(proper_uri) or does_exist(str(proper_uri).lower().split('login')):
            proper_uri = proper_uri2

    except Exception as e:
        proper_uri = clean_url(f"https://www.flipkart.com/{uri}")
        if uri.split('/')[0] == 's' or uri.split('/')[0] == 'dl':
            proper_uri = clean_url(f"https://dl.flipkart.com/{uri}")
    
    result_dict['proper_uri'] = proper_uri
    return result_dict


def extract_highlights(webPageContents):
    highlights = []

    try:
        highlights_details = webPageContents.split('Highlights')[1].split('</ul>')[0].replace('</li>', '').split('<li')
        if does_exist(highlights_details):
            for i in range(1, len(highlights_details)):
                try:
                    highlights.append(highlights_details[i].split('>')[1])
                except Exception as e:
                    pass
    except Exception as e:
        highlights = []

    return highlights



async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


async def product(link, type='detailed'):
    star = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMyIgaGVpZ2h0PSIxMiI+PHBhdGggZmlsbD0iI0ZGRiIgZD0iTTYuNSA5LjQzOWwtMy42NzQgMi4yMy45NC00LjI2LTMuMjEtMi44ODMgNC4yNTQtLjQwNEw2LjUuMTEybDEuNjkgNC4wMSA0LjI1NC40MDQtMy4yMSAyLjg4Mi45NCA0LjI2eiIvPjwvc3ZnPg=='
    if type == 'compact':
        compactResult = True
        minimumResult = False
    elif type == 'minimum':
        compactResult = False
        minimumResult = True
    else:
        compactResult = False
        minimumResult = False

    try:
        # uri = quote(link)
        uri=link
        print("Product initiated:", uri)

        webPageContents=None
        comingSoon=0
        inStock=0

        try:
            webPageContents = await fetch_data(uri)
            webPageContents = webPageContents.replace('&amp;', '&')
            webPageContents = webPageContents.replace('&nbsp;', '')
            webPageContents = webPageContents.replace('&#...;', '')
            
            comingSoon = does_exist(webPageContents.split('Coming Soon</div>'))
            inStock = not does_exist(webPageContents.split('This item is currently out of stock</div>')) or comingSoon
            
            if 'for has been moved or deleted' in webPageContents:
                raise Exception("Link provided doesn't correspond to any product")
            
        except Exception as e:
            return {
                "error_message": str(e),
                "possible_solution": "Validate your link and try removing https://www.flipkart.com from your product link",
                "bug_report": "https://github.com/aryan2002"
            }
        
        rating = None 
        currentPrice = None 
        properURI = None 
        productName = None 
        originalPrice = None
        highlights = [] 
        product_id = None
        discountPercent=None
        thumbnails=[]
        fAssured=False
        fAssuredDetails=None
    
    
        # productName
        
        productName=extract_product_name(webPageContents)

        # product price

        refPriceTemp= calculate_discount(webPageContents)
        currentPrice=refPriceTemp["currentPrice"]
        originalPrice=refPriceTemp["originalPrice"]
        discountPercent=refPriceTemp["discount_percent"]        
        
        #tumbnails
        thumbnails=extract_thumbnails(webPageContents, productName)

        #fAssured
        refAssuredTemp=extract_fassured_status(webPageContents)
        fAssured=refAssuredTemp["fassured"]
        fAssuredDetails=refAssuredTemp["fAssuredDetails"]

        #properUri
        refProperUriTemp=extract_proper_uri(webPageContents, uri)
        properURI=refProperUriTemp["proper_uri"]

        #highlights
        highlights=extract_highlights(webPageContents)

        #rating
        
        isRated = fAssuredDetails[0].split(star)
        if comingSoon:
            # products not released, so will not be rated
            rating = None
        else:
            if does_exist(isRated):
                ratingDetails = isRated[0].split('">')
                rating = last_entry(ratingDetails).split('<')[0]
            else:
                try:
                    rating = webPageContents.split('_3LWZlK')[1].split('<')[0].split('>')[1].strip()
                except Exception as e:
                    pass

        try:
            # final changes
            productName = productName.replace('&#x27;', "'").strip()
            properURI = properURI.replace('http://', 'https://')
        except Exception as e:
            pass

        
        #product specifications
            #not need right now

        resultJson = {
            "name": productName,
            "current_price": currentPrice,
            "original_price": originalPrice,
            "discounted": originalPrice != currentPrice,
            "discount_percent":discountPercent,
            "rating": float(rating) if rating is not None else None,
            "in_stock": inStock,
            "f_assured": fAssured,
            "share_url": properURI,
            "seller": {
                "seller_name": None,
                "seller_rating": None
            },
            "thumbnails": thumbnails,
            "highlights": highlights,
            "product_id": product_id
        }

        if inStock:
            try:
                seller = webPageContents.split('sellerName')[1]
                sellerName = last_entry(seller.split('</span>')[0].split('<span>'))
                try:
                    seller_rating = last_entry(seller.split(star)[0].split('>')).split('<')[0]
                    if len(seller_rating) <= 3:
                        resultJson["seller"]["seller_rating"] = float(seller_rating)
                except Exception as e:
                    pass
                resultJson["seller"]["seller_name"] = sellerName
            except Exception as e:
                pass
        
        return resultJson
    except Exception as e:
        print(e)
        return { "error": "Couldn't fetch information : " + str(e),
            "possible_solution": "Don't lose hope, contact the support",}
 

def main():
    result=asyncio.run(product('https://www.flipkart.com/entwino-f-1-gaming-mouse-wired-compute-optical/p/itma5e4346710327?pid=ACCG7TYKWZ457HJF&lid=LSTACCG7TYKWZ457HJFB7IZTZ&marketplace=FLIPKART&q=gamingMouse&store=6bo%2Fai3%2F2ay&srno=s_1_1&otracker=search&fm=organic&iid=8677a6f2-10c0-4059-a48f-99d65c2836f2.ACCG7TYKWZ457HJF.SEARCH&ppt=sp&ppn=sp&ssid=eg8h9ncprk0000001692276151289&qH=80cf3858d5cf3c14'))

    result=json.dumps(result)

    with open('product.json', 'w') as f:
        f.write(result)
    # print(result)

main()
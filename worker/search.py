import re
import requests
import asyncio
import aiohttp
import json
from urllib.parse import urlparse, urlencode, parse_qs


def nameClear(
    name: str, productLink
):  # helper function to clear the name of the product
    if name.__contains__("<sp"):
        product_part = re.search(r"/([^/]+)/p/", productLink).group(1)
        # Replace hyphens with spaces and capitalize first character after each hyphen
        product_name = " ".join(word.capitalize() for word in product_part.split("-"))
        return product_name
    return name


async def search(q, host):
    searchURL = f"https://www.flipkart.com/search?marketplace=FLIPKART&q={q}"
    print("Search initiated:", searchURL)

    #  webPageContents = requests.get(searchURL).text //for sync requests

    webPageContents = None  # for async requests
    async with aiohttp.ClientSession() as session:
        async with session.get(searchURL) as response:
            webPageContents = await response.text()
            # webPageContents=webPageContents.text

    webPageContents = webPageContents.replace(
        'style="color:#000000;font-size:14px;font-style:normal;font-weight:700">₹',
        ">Rs. ",
    )
    webPageContents = re.sub("&#x27;", "'", webPageContents)
    webPageContents = re.sub("&#...;", "", webPageContents)
    products = webPageContents.split(">₹")
    result = []
    method = None
    reversion = False

    i = 1
    while i < len(products):
        try:
            currentPrice = None
            originalPrice = None
            productLink = None
            productName = None
            isDiscounted = False
            thumbnail = None
            linkDetails = None
            lastLinkIndex = None
            linkDetailsFinder = None

            priceCheck = products[i].split("</div>")[0].replace(",", "")
            # print("\n",products[i],"--> products\n")
            # print(priceCheck)
            # return
            currentPrice = int(priceCheck)
            originalPrice = int(currentPrice)

            if priceCheck.split("</option>"):
                try:
                    linkDetails = products[i - 1].split("</a>")
                    try:
                        thumbnails_arr = products[i - 1].split('src="https')
                        for thumb in thumbnails_arr:
                            possible_thumbnail = thumb.split('"')[0]
                            if (
                                "jpeg" in possible_thumbnail
                                or "image" in possible_thumbnail
                            ):
                                thumbnail = "https" + possible_thumbnail
                                break
                    except Exception:
                        pass
                    lastLinkIndex = len(linkDetails) - 2
                    linkDetailsFinder = linkDetails[lastLinkIndex].split(
                        'target="_blank"'
                    )
                    if len(linkDetailsFinder) > 1:
                        productLink = (
                            "https://www.flipkart.com"
                            + linkDetailsFinder[1].split('href="')[1].split('"')[0]
                        )
                        productName = (
                            linkDetailsFinder[1]
                            .split('href="')[1]
                            .split('"')[1]
                            .split(">")[1]
                        )
                        method = "A"
                except Exception:
                    print("Failed to obtain product name and link from Method A")

                if productName in ("", None):
                    try:
                        if method == "C" or method == "D":
                            i += 1
                            reversion = True
                        linkDetails = products[i - 2].split("<a")
                        method = "B"
                        if len(linkDetails) == 1:
                            linkDetails = products[i - 1].split("<a")
                            method = "C"
                        else:
                            print(
                                "Failed to obtain product name and link from Method B"
                            )
                        lastLinkIndex = len(linkDetails) - 1
                        linkDetailsFinder = linkDetails[lastLinkIndex].split(
                            'target="_blank"'
                        )
                        if len(linkDetailsFinder) > 1:
                            productLink = (
                                "https://www.flipkart.com"
                                + linkDetailsFinder[1].split('href="')[1].split('"')[0]
                            )
                            productName = (
                                linkDetailsFinder[1]
                                .split('href="')[1]
                                .split('"col col-7-12">')[1]
                                .split("</div>")[0]
                                .split(">")[1]
                            )
                        if reversion:
                            i -= 1
                            reversion = False
                            method = "D"
                            print(
                                "Failed to obtain product name and link from Method C"
                            )
                    except Exception as e:
                        print(e)
                    if productName in ("", None):
                        print(
                            "Failed to obtain product name and link from known methods"
                        )
                    else:
                        print(
                            "Successfully obtained product name and link from known methods"
                        )
                        try:
                            if thumbnail is None:
                                thumbnail = (
                                    webPageContents.split(f'alt="{productName}"')[1]
                                    .split('src="')[1]
                                    .split('"')[0]
                                )
                        except Exception:
                            thumbnail = None
                        if i + 1 != len(products):
                            nextItem = (
                                products[i + 1]
                                .split("</div>")[0]
                                .replace(",", "")
                                .split("<!-- -->")
                            )
                            isDiscounted = len(nextItem) > 1
                            if isDiscounted:
                                i += 1
                                originalPrice = int(nextItem[1])

                        result.append(
                            {
                                # "name": productName.replace('&#x27;', "'"),
                                "name": nameClear(
                                    productName.replace("&#x27;", "'"),
                                    clean(productLink),
                                ),
                                "link": clean(productLink),
                                "current_price": currentPrice,
                                "original_price": originalPrice,
                                "discounted": isDiscounted,
                                "thumbnail": thumbnail,
                                "query_url": clean(productLink)
                                .replace("www.flipkart.com", f"{host}/product?query=")
                                .replace("dl.flipkart.com", f"{host}/product?query="),
                            }
                        )
                else:
                    try:
                        if thumbnail is None:
                            thumbnail = webPageContents.split(f'alt="{productName}"')
                            if len(thumbnail) == 1:
                                thumbnail = webPageContents.split(
                                    f'alt="{productName[:5]}'
                                )
                            thumbnail = thumbnail[1].split('src="')[1].split('"')[0]
                    except Exception:
                        thumbnail = None
                    if i + 1 != len(products):
                        nextItem = (
                            products[i + 1]
                            .split("</div>")[0]
                            .replace(",", "")
                            .split("<!-- -->")
                        )
                        isDiscounted = len(nextItem) > 1
                        if isDiscounted:
                            i += 1
                            originalPrice = int(nextItem[1])

                    result.append(
                        {
                            # "name": productName.strip(),
                            "name": nameClear(
                                productName.strip(),
                                clean(productLink).replace("http://", "https://"),
                            ),
                            "link": clean(productLink).replace("http://", "https://"),
                            "current_price": currentPrice,
                            "original_price": originalPrice,
                            "discounted": isDiscounted,
                            "thumbnail": thumbnail,
                            "query_url": clean(productLink)
                            .replace("www.flipkart.com", f"{host}/product?query=")
                            .replace("dl.flipkart.com", f"{host}/product?query="),
                        }
                    )
            else:
                webPageContents = webPageContents.replace("₹", "Rs.")
                print(
                    "Ignoring amount",
                    currentPrice,
                    ": Suspected to be dropdown menu item",
                )

        except Exception as e:
            print(e)

        i += 1

    return {
        "total_result": len(result),
        "query": q,
        "fetch_from": searchURL,
        "result": result,
    }


def clean(link):
    url = urlparse(link.replace("amp;", ""))
    query_params = parse_qs(url.query)
    query_params.pop("_appId", None)
    query_params.pop("_refId", None)
    query_params.pop("cmpid", None)
    query_params.pop("pid", None)
    query_params.pop("marketplace", None)
    query_params.pop("ppt", None)
    query_params.pop("lid", None)
    query_params.pop("store", None)
    query_params.pop("spotlightTagId", None)
    query_params.pop("q", None)
    query_params.pop("srno", None)
    query_params.pop("otracker", None)
    query_params.pop("fm", None)
    query_params.pop("iid", None)
    query_params.pop("ppn", None)
    query_params.pop("ssid", None)
    query_params.pop("qH", None)
    new_query = urlencode(query_params, doseq=True)
    return f"{url.scheme}://{url.netloc}{url.path}?{new_query}"


# debugging tool
# convert the result into json format and write it in a file
# result = asyncio.run(search("laptop", 'flipkart.com'))
# result = json.dumps(result)
# with open('result.json', 'w') as f:
#     f.write(result)
# print(result)

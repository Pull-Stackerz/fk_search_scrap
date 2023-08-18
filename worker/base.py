def base(hostName):
    data = {
        "name": "flipkartScrapperAPI",
        "description": "do scrapping form flipkart.com and return data in json format",
        "version": "1.0.0",
        "author": "aryan",
        "email": "aryan20022003@gmail.com",
        "usage": {
            "search_api": "https://${hostName}/search/<product_name>",
            "product_api": "https://${hostName}/product/<product_link_argument>",
            "product_min_api": "https://${hostName}/product/min/<product_link_argument>",
        },
        "examples": {
            "search_api": "https://${hostName}/search/gamingMouse",
            "product_api": "https://${hostName}/product/dl/huami-amazfit-bip-u-smartwatch/p/itmc6ae7a0e9f440?pid=SMWFY7PPGQTEH2BZ",
            "product_min_api": "https://${hostName}/product/min/dl/logitech-g102-light-sync-adj-dpi-upto-8000-6-programmable-buttons-rgb-wired-optical-gaming-mouse/p/itmc44c10000ad95?pid=ACCFUJC6YG3MWYQ5&lid=LSTACCFUJC6YG3MWYQ5ISPJ3X&marketplace=FLIPKART&",
            
        },
    }
    return data



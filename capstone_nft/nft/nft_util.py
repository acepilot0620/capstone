import requests


def get_my_token(address):
    url = f'https://deep-index.moralis.io/api/v2/{address}/nft?chain=rinkeby&format=decimal'
    headers = {
        "accept": "application/json",
        "X-API-Key": "wvthmDqYNaHvYE7e0G6AOmkDBI5JzzhcP0BPAoirhGUh05uJleYdMspcZcyKOIWh"
    }
    response = requests.get(url, headers=headers).json()
    res_dict = {
        'tokens' : response['result']
    }
    return res_dict
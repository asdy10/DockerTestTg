import requests


def get_cards(api_token):
    url = 'https://suppliers-api.wildberries.ru/content/v1/cards/cursor/list'
    headers = {'Authorization': api_token}
    params = {'dateFrom': '2018-06-20'}# str(datetime.datetime.today()).split(' ')[0]}
    params =   {
          "sort": {
              "cursor": {
                  "limit": 1000
              },
              "filter": {
                  "withPhoto": -1
              }
          }
        }
    res = requests.post(url=url, headers=headers, json=params)
    print(res)
    return res.json()['data']['cards']


def get_card_by_article(api_token, articles):
    url = 'https://suppliers-api.wildberries.ru/content/v1/cards/filter'
    data = {'vendorCodes': articles,
            'allowedCategoriesOnly': True}
    headers = {'Authorization': api_token}
    res = requests.post(url=url, headers=headers, json=data)
    print(res, res.text)
    result = []
    for i in res.json()['data']:
        if i['vendorCode'] in articles:
            result.append(i)
    return result


if __name__ == '__main__':
    api_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6ImEzNzAzZDMyLWI5NDEtNDY3My1iNGQ2LTZkMWE3YzJlNzM5MyJ9.KfY8uJae2LG4LNaRJ2bnsNU1UowMgUWq5ip7_Eosnl8'

    res = get_card_by_article(api_token, ['230510', '230414'])
    for i in res:
        for j in i['sizes']:
            print(j)
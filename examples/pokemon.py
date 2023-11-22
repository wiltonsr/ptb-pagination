from urllib.request import urlopen, Request
import json


class Pokemon():
    def __init__(self, name: str, url: str):
        self.name = name.capitalize()
        self.url = url

    def _read_info(self) -> list:
        req = Request(
            url=self.url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )

        response = urlopen(req)
        data_json = json.loads(response.read())

        return data_json

    def poke_html_msg(self) -> str:
        info = self._read_info()

        type_msg = '<b>Type(s): </b>'
        types_list = []
        for t in info['types']:
            types_list.append(t['type']['name'])
        type_msg = type_msg + ', '.join(types_list)

        return (
            f"<b>Name</b>: {self.name} #{info['id']}\n"
            f"{type_msg}\n"
            f"<b>Weight</b>: {info['weight']}\n"
            f"<b>Height</b>: {info['height']}\n"
            f"\n"
            f"{info['sprites']['front_default']}"
        )

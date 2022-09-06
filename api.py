import json
import requests
import base64
import concurrent.futures


class MathPixAPI:
    stroke_url = 'https://api.mathpix.com/v3/strokes'
    header = {
        "content-type": "application/json",
        "app_id": "xxxxxxxxxxx",
        "app_key": "xxxxxxxxxxx"            # censored
    }

    @staticmethod
    def format_data(file_name: str):
        return "data:image/png;base64," + base64.b64encode(open(file_name, "rb").read()).decode()

    def _send_request(self, data: str):
        r = requests.post("https://api.mathpix.com/v3/text",
                          data=json.dumps({'src': data}),
                          headers=self.header)
        return json.loads(r.text)

    def post_data(self, payload: dict):
        result = dict(payload)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            keys = []
            data = []
            for location, _data in payload.items():
                if isinstance(_data, str):
                    if _data.startswith('data:image'):
                        keys.append(location)
                        data.append(_data)
            futures = executor.map(self._send_request, data)
            for key, value in zip(keys, futures):
                result[key] = value
        return result

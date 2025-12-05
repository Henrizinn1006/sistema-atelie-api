import requests

# 🚨 IMPORTANTE:
# Troque pela URL da sua API na Hostinger/VPS
BASE_URL = "https://SEU_DOMINIO_OU_IP/api"


class APIClient:

    def get(self, endpoint, params=None):
        try:
            r = requests.get(BASE_URL + endpoint, params=params, timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def post(self, endpoint, data=None, files=None):
        try:
            r = requests.post(BASE_URL + endpoint, data=data, files=files, timeout=15)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def put(self, endpoint, data=None, files=None):
        try:
            r = requests.put(BASE_URL + endpoint, data=data, files=files, timeout=15)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def delete(self, endpoint):
        try:
            r = requests.delete(BASE_URL + endpoint, timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}


api = APIClient()

TOKEN_NAME = "Emilio Ziniades"
API_ENDPOINT = "https://vrmapi.victronenergy.com/v2/"
AUTH_ENDPOINT = API_ENDPOINT + "auth/login"
TOKEN_ENDPOINT = API_ENDPOINT + "users/{user_id}/accesstokens/create"
TOKEN_REVOKE_ENDPOINT = API_ENDPOINT + "users/{user_id}/accesstokens/{token_id}/revoke"
TOKEN_LIST_ENDPOINT = API_ENDPOINT + "users/{user_id}/accesstokens/list"
INSTALLATIONS_ENDPOINT = API_ENDPOINT + "users/{user_id}/installations"
STATS_ENDPOINT = API_ENDPOINT + "installations/{site_id}/stats"
WIDGET_ENDPOINT = API_ENDPOINT + "installations/{site_id}/widgets/{widget}"

"""Client minimale per Microsoft Graph API: elenco/download/upload/spostamento
file su OneDrive. Usa il percorso della cartella (es. "Audio") invece di ID,
per semplicità lato utente.
"""

import os

import requests

GRAPH_ROOT = "https://graph.microsoft.com/v1.0"
SIMPLE_UPLOAD_LIMIT = 4 * 1024 * 1024  # 4MB, limite Graph API per upload semplice
UPLOAD_CHUNK_SIZE = 10 * 1024 * 1024  # multiplo di 320KB richiesto dalle upload session


class OneDriveError(RuntimeError):
    pass


def _headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}


def _raise_for_status(resp):
    if resp.status_code >= 400:
        raise OneDriveError(f"Graph API error {resp.status_code}: {resp.text}")


def _item_by_path_url(folder_path):
    folder_path = folder_path.strip("/")
    if not folder_path:
        return f"{GRAPH_ROOT}/me/drive/root"
    return f"{GRAPH_ROOT}/me/drive/root:/{folder_path}"


def list_folder_children(access_token, folder_path):
    url = f"{_item_by_path_url(folder_path)}:/children" if folder_path.strip("/") else f"{_item_by_path_url('')}/children"
    items = []
    while url:
        resp = requests.get(url, headers=_headers(access_token))
        _raise_for_status(resp)
        data = resp.json()
        items.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
    return items


def list_wav_files(access_token, folder_path):
    children = list_folder_children(access_token, folder_path)
    return [
        item for item in children
        if "file" in item and item["name"].lower().endswith(".wav")
    ]


def ensure_subfolder(access_token, folder_path, subfolder_name):
    """Ritorna l'item della sottocartella, creandola se non esiste."""
    children = list_folder_children(access_token, folder_path)
    for item in children:
        if "folder" in item and item["name"] == subfolder_name:
            return item

    url = f"{_item_by_path_url(folder_path)}:/children" if folder_path.strip("/") else f"{_item_by_path_url('')}/children"
    resp = requests.post(url, headers=_headers(access_token), json={
        "name": subfolder_name,
        "folder": {},
        "@microsoft.graph.conflictBehavior": "rename",
    })
    _raise_for_status(resp)
    return resp.json()


def download_file(access_token, item_id, local_path):
    url = f"{GRAPH_ROOT}/me/drive/items/{item_id}/content"
    with requests.get(url, headers=_headers(access_token), stream=True) as resp:
        _raise_for_status(resp)
        with open(local_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)


def upload_file(access_token, folder_path, filename, local_path):
    """Carica local_path come folder_path/filename, ritorna l'item creato."""
    size = os.path.getsize(local_path)
    dest = f"{folder_path.strip('/')}/{filename}" if folder_path.strip("/") else filename

    if size <= SIMPLE_UPLOAD_LIMIT:
        url = f"{GRAPH_ROOT}/me/drive/root:/{dest}:/content"
        with open(local_path, "rb") as f:
            resp = requests.put(url, headers=_headers(access_token), data=f)
        _raise_for_status(resp)
        return resp.json()

    session_url = f"{GRAPH_ROOT}/me/drive/root:/{dest}:/createUploadSession"
    resp = requests.post(session_url, headers=_headers(access_token), json={
        "item": {"@microsoft.graph.conflictBehavior": "rename"}
    })
    _raise_for_status(resp)
    upload_url = resp.json()["uploadUrl"]

    with open(local_path, "rb") as f:
        offset = 0
        while offset < size:
            chunk = f.read(UPLOAD_CHUNK_SIZE)
            chunk_end = offset + len(chunk) - 1
            headers = {
                "Content-Length": str(len(chunk)),
                "Content-Range": f"bytes {offset}-{chunk_end}/{size}",
            }
            put_resp = requests.put(upload_url, headers=headers, data=chunk)
            _raise_for_status(put_resp)
            offset += len(chunk)

    return put_resp.json()


def move_item(access_token, item_id, destination_folder_id, new_name=None):
    url = f"{GRAPH_ROOT}/me/drive/items/{item_id}"
    body = {"parentReference": {"id": destination_folder_id}}
    if new_name:
        body["name"] = new_name
    resp = requests.patch(url, headers=_headers(access_token), json=body)
    _raise_for_status(resp)
    return resp.json()

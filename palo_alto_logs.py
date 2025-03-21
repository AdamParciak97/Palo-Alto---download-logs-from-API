import requests
import xmltodict
import time
import pandas as pd
import urllib3

# Wyłącz ostrzeżenia o SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Konfiguracja Palo Alto
PA_IP = "Adres IP"
API_KEY = "Wygenerowany API KEY"
BASE_URL = f"https://{PA_IP}/api/"


def get_job_id():
    """Wysyła zapytanie o logi i pobiera job ID"""
    params = {
        "type": "log",
        "log-type": "threat",
        "nlogs": "5000",
        "key": API_KEY
    }

    response = requests.get(BASE_URL, params=params, verify=False)
    log_data = xmltodict.parse(response.text)

    # Pobranie job ID
    job_id = log_data.get("response", {}).get("result", {}).get("job", None)

    if job_id:
        print(f"Zapytanie zakolejkowane. Job ID: {job_id}")
        return job_id
    else:
        print("Błąd: Nie udało się pobrać Job ID.")
        return None


def wait_for_job_completion(job_id):
    """Sprawdza status joba i czeka na zakończenie"""
    params = {
        "type": "log",
        "action": "get",
        "job-id": job_id,
        "key": API_KEY
    }

    while True:
        response = requests.get(BASE_URL, params=params, verify=False)
        job_status = xmltodict.parse(response.text)

        status = job_status.get("response", {}).get("result", {}).get("job", {}).get("status", "")
        if status == "FIN":
            print("Job zakończony. Pobieram logi...")
            return job_status
        else:
            print(f"Job w trakcie ({status})... Czekam 5 sekund.")
            time.sleep(5)


def save_logs_to_csv(log_data, filename="logs.csv"):
    """Zapisuje logi do pliku CSV"""
    logs = log_data.get("response", {}).get("result", {}).get("log", {}).get("logs", {}).get("entry", [])

    if not logs:
        print("Nie znaleziono logów w strukturze.")
        return

    df = pd.DataFrame(logs)
    df.to_csv(filename, index=False)
    print(f"Logi zapisane do: {filename}")


# Pobieranie logów
job_id = get_job_id()
if job_id:
    logs = wait_for_job_completion(job_id)
    save_logs_to_csv(logs)

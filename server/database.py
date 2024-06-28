import os
import pickle
import requests
import argparse
from urllib.parse import urlparse
from datetime import datetime, timezone
from typing import Tuple, List, Dict, Optional
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.pickle"


def get_google_sheets_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    service = build("sheets", "v4", credentials=creds)
    return service


def parse_url(job_url: str) -> Tuple[str, str, str]:
    parsed = urlparse(job_url)
    ats = parsed.netloc

    ats_list = ["bamboohr.com", "breezy.hr", "recruitee.com"]
    if any(substring in ats for substring in ats_list):
        breezy_parts = ats.split(".")
        company_name = breezy_parts[0]
        ats = f"{breezy_parts[1]}.{breezy_parts[-1]}"
        path_parts = parsed.path.split("/")
        if len(path_parts) < 3:
            raise ValueError("Invalid URL format")
        job_id = path_parts[-1]
        return company_name, job_id, ats

    if "personio.com" in ats:
        personio_parts = ats.split(".")
        company_name = personio_parts[0]
        ats = f"{personio_parts[1]}.{personio_parts[2]}.{personio_parts[3]}"
        path_parts = parsed.path.split("/")
        if len(path_parts) < 3:
            raise ValueError("Invalid URL format")
        job_id = path_parts[-1].replace("\\", "")
        return company_name, job_id, ats

    if ats == "jobs.lever.co":
        path_parts = parsed.path.split("/")
        if len(path_parts) < 3:
            raise ValueError("Invalid Lever URL format")
        return path_parts[1], path_parts[2], ats
    elif ats == "boards.greenhouse.io":
        path_parts = parsed.path.split("/")
        if len(path_parts) < 4:
            raise ValueError("Invalid Greenhouse URL format")
        company_name = path_parts[1]
        job_id = path_parts[-1]
        return company_name, job_id, ats
    elif ats == "jobs.smartrecruiters.com":
        path_parts = parsed.path.split("/")
        if len(path_parts) < 3:
            raise ValueError("Invalid SmartRecruiters URL format")
        company_name = path_parts[1]
        job_id = path_parts[-1].split("-")[0]
        return company_name, job_id, ats
    elif ats == "jobs.personio.com":
        path_parts = parsed.path.split("/")
        if len(path_parts) < 3:
            raise ValueError("Invalid Personio URL format")
        company_name = path_parts[1]
        job_id = path_parts[-1]
        return company_name, job_id, ats
    else:
        raise ValueError("Unsupported ATS")


def get_jobs(ats: str, company_name: str) -> List[Dict[str, any]]:
    urls = {
        "greenhouse": f"https://boards-api.greenhouse.io/v1/boards/{company_name}/jobs?content=true",
        "lever": f"https://api.lever.co/v0/postings/{company_name}",
        "smartrecruiters": f"https://api.smartrecruiters.com/v1/companies/{company_name}/postings",
        "personio": f"https://{company_name}.jobs.personio.com/search.json",
        "breezy": f"https://{company_name}.breezy.hr/json",
        "bamboohr": f"https://{company_name}.bamboohr.com/careers/list",
        "recruitee": f"https://{company_name}.recruitee.com/api/offers",
    }
    url = ""

    if ats == "boards.greenhouse.io":
        url = urls["greenhouse"]
    elif ats == "jobs.lever.co":
        url = urls["lever"]
    elif ats == "jobs.smartrecruiters.com":
        url = urls["smartrecruiters"]
    elif ats == "jobs.personio.com":
        url = urls["personio"]
    elif ats == "breezy.hr":
        url = urls["breezy"]
    elif ats == "bamboohr.com":
        url = urls["bamboohr"]
    elif ats == "recruitee.com":
        url = urls["recruitee"]
    else:
        raise ValueError("Unsupported ATS")
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def convert_timestamp(timestamp):
    """Convert Unix timestamp (milliseconds) or ISO 8601 date string to datetime object."""
    if isinstance(timestamp, (int, float)):
        # Handle Unix timestamp (milliseconds)
        return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
    elif isinstance(timestamp, str):
        # Handle ISO 8601 date string
        return timestamp[:10]
    else:
        raise ValueError(f"Unsupported timestamp format: {timestamp}")


def calculate_days_open(created_at: datetime) -> int:
    """Calculate the number of days between the job creation date and today."""
    now = datetime.now(timezone.utc)
    days_open = (now - created_at).days
    return max(days_open, 0)


def get_job(ats: str, company_name: str, job_id: str) -> Optional[Dict[str, any]]:
    jobs = get_jobs(ats, company_name)
    if ats == "boards.greenhouse.io":
        for job in jobs.get("jobs", []):
            if str(job["id"]) == str(job_id):
                created_at = datetime.strptime(job["updated_at"], "%Y-%m-%dT%H:%M:%S%z")
                return {
                    "id": job["id"],
                    "company": company_name.capitalize(),
                    "title": job["title"],
                    "posted_date": created_at.strftime("%Y-%m-%d"),
                    "url": job["absolute_url"],
                }
    elif ats == "jobs.lever.co":
        for job in jobs:
            if str(job["id"]) == job_id:
                created_at = convert_timestamp(job["createdAt"])
                return {
                    "id": job["id"],
                    "company": company_name.capitalize(),
                    "title": job["text"],
                    "posted_date": created_at.strftime("%Y-%m-%d"),
                    "url": job["hostedUrl"],
                }
    elif ats == "jobs.smartrecruiters.com":
        for job in jobs.get("content", []):
            if str(job["id"]) == job_id:
                created_at = convert_timestamp(job["releasedDate"])
                return {
                    "id": job["id"],
                    "company": company_name.capitalize(),
                    "title": job["name"],
                    "posted_date": created_at,
                    "url": f"https://jobs.smartrecruiters.com/{company_name}/{job['id']}",
                }
    elif ats == "breezy.hr":
        for job in jobs:
            if str(job["id"]) == job_id:
                created_at = convert_timestamp(job["published_date"])
                return {
                    "id": job["id"],
                    "company": company_name.capitalize(),
                    "title": job["name"],
                    "posted_date": created_at,
                    "url": job["url"],
                }
    elif ats == "bamboohr.com":
        for job in jobs.get("result", []):
            if str(job["id"]) == job_id:
                return {
                    "id": job["id"],
                    "company": company_name.capitalize(),
                    "title": job["jobOpeningName"],
                    "posted_date": "-",
                    "url": f"https://{company_name}.bamboohr.com/careers/{job['id']}",
                }
    elif ats == "recruitee.com":
        for job in jobs.get("offers", []):
            if job["slug"] == job_id:
                created_at = convert_timestamp(job["created_at"])
                return {
                    "id": job["id"],
                    "company": company_name.capitalize(),
                    "title": job["title"],
                    "posted_date": created_at,
                    "url": f"https://{company_name}.recruitee.com/o/{job['id']}",
                }
    elif ats == "jobs.personio.com":
        for job in jobs:
            if str(job["id"]) == job_id:
                return {
                    "id": job["id"],
                    "company": company_name.capitalize(),
                    "title": job["name"],
                    "posted_date": "-",
                    "url": f"https://{company_name}.jobs.personio.com/job/{job['id']}?language=en&display=en",
                }
    return None


def update_sheet(
    service, spreadsheet_id: str, sheet_name: str, job_data: Dict[str, any]
):
    sheet = service.spreadsheets()

    # Get sheet ID (keep this part as it was)
    sheet_metadata = sheet.get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get("sheets", "")
    sheet_id = None
    available_sheets = []
    for s in sheets:
        available_sheets.append(s["properties"]["title"])
        if s["properties"]["title"] == sheet_name:
            sheet_id = s["properties"]["sheetId"]
            break

    if sheet_id is None:
        print(f"Sheet '{sheet_name}' not found in the spreadsheet.")
        print(f"Available sheets: {', '.join(available_sheets)}")
        raise ValueError(f"Sheet '{sheet_name}' not found in the spreadsheet.")

    # Create formulas
    job_url = job_data["url"]
    ats_name = urlparse(job_url).netloc.split(".")[1].capitalize()
    url_formula = f'=HYPERLINK("{job_url}", "{ats_name}")'
    days_open_formula = f'=DAYS_SINCE("{job_data["posted_date"]}")'

    values = [
        [
            job_data["id"],
            job_data["company"],
            job_data["title"],
            job_data["posted_date"],
            days_open_formula,
            url_formula,
            "Applied",
        ]
    ]
    body = {"values": values}
    try:
        result = (
            sheet.values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1",
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )
        print(
            f"{result.get('updates').get('updatedCells')} cells appended to sheet '{sheet_name}'."
        )
    except Exception as e:
        print(f"Error updating sheet: {e}")
        print(f"Spreadsheet ID: {spreadsheet_id}")
        print(f"Sheet name: {sheet_name}")
        print(f"Values to be inserted: {values}")
        raise


def main(job_url: str, spreadsheet_id: str, sheet_name: str):
    try:
        company_name, job_id, ats = parse_url(job_url)
        job = get_job(ats, company_name, job_id)
        if job:
            service = get_google_sheets_service()
            update_sheet(service, spreadsheet_id, sheet_name, job)
        else:
            print(f"Job with ID {job_id} not found for company {company_name}")
    except Exception as e:
        print(f"An error occurred: {e}")


# if __name__ == "__main__":
#     """
#     https://boards.greenhouse.io/ezcaterinc/jobs/4412685007
#     https://jobs.lever.co/supportninja/93c183b9-5ddd-4822-977a-83808623e314
#     https://jobs.smartrecruiters.com/Square/743999996482830-firmware-engineering-manager
#     https://jarvis-ml.breezy.hr/p/10b6f47186e8
#     https://acculynx.bamboohr.com/careers/196
#     https://valorsoftware.recruitee.com/o/marketing-manager-generalist
#     https://taktile-gmbh-1.jobs.personio.com/job/781173?language=en
#     """
#     parser = argparse.ArgumentParser(
#         description="Scrape job information from Lever.co and update Google Sheet"
#     )
#     parser.add_argument("job_url", help="The URL of the job posting to scrape")
#     parser.add_argument(
#         "sheet_name",
#         help="The name of the specific sheet to update within the Google Sheet",
#     )
#     args = parser.parse_args()
#     main(args.job_url, "1HZY0Q3NvM4NG_sFIjY2eWJ3UXpGjgKTC6cdEXN-zhUg", args.sheet_name)

from pathlib import Path
import json
import datetime
from linkedin_api import Linkedin

from consultant_info_generator.config import cfg
from consultant_info_generator.model import Consultant, Industry, Company, Experience, Skill


def extract_profile(profile: str) -> dict:
    api = Linkedin(cfg.linkedin_user, cfg.linkedin_password)
    return api.get_profile(profile)


def profile_to_file(profile: str, target: Path) -> Path:
    profile_data = extract_profile(profile)
    target.write_text(json.dumps(profile_data), encoding="utf-8")
    return target


def extract_consultant(profile: str) -> Consultant:
    profile_data: dict = extract_profile(profile)
    industries: list[Industry] = []
    companies: list[Company] = []
    skills: list[Skill] = []
    experiences: list[Experience] = []
    cv = profile_data["summary"]
    given_name = profile_data["firstName"]
    surname = profile_data["lastName"]
    email = ""
    industry_name: str = profile_data["industryName"]
    geo_location: str = profile_data["geoLocationName"]
    linkedin_profile_url = f"https://www.linkedin.com/in/{profile}"
    for experience in profile_data["experience"]:
        add_experience(experiences, experience)
    for skill in profile_data["skills"]:
        if "name" in skill:
            skills.append(Skill(name=skill["name"]))
    return Consultant(
        given_name=given_name,
        surname=surname,
        email=email,
        cv=cv,
        industry_name=industry_name,
        geo_location=geo_location,
        linkedin_profile_url=linkedin_profile_url,
        experiences=experiences,
        skills=skills
    )


def add_experience(experiences, experience):
    location = experience.get("locationName", "")
    time_period = experience["timePeriod"]
    if time_period:
        if "startDate" in time_period:
            start_date = time_period["startDate"]
            start_date_month = int(start_date.get("month", "1"))
            start_date_year = int(start_date["year"]) if start_date["year"] else 1
            start_date = datetime.datetime(start_date_year, start_date_month, 1)
            end_date = None
            if "endDate" in time_period:
                end_date = time_period["endDate"]
                end_date_month = int(end_date.get("month", "12"))
                if "year" in end_date:
                    end_date_year = int(end_date["year"])
                    end_date = datetime.datetime(end_date_year, end_date_month, 1)
            company_name = experience["companyName"] or ""
            company: Company = Company(name=company_name)
            experience: Experience = Experience(
                    location=location, start=start_date, end=end_date, company=company
                )
            experiences.append(experience)


if __name__ == "__main__":
    profile_name = "alexander-polev-cto"
    output_file = Path(f"{profile_name}-consultant.json")
    consultant = extract_consultant(profile_name)
    output_file.write_text(consultant.model_dump_json(), encoding="utf-8")

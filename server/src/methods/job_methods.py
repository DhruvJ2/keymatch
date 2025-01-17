from sqlalchemy.orm import Session
from fastapi import HTTPException
from src import schemas, models
from rake_nltk import Rake
import docx2txt as dxt

FILE_LOCATION = './static/resume.docx'

def get_job():
    pass

def add_job(job: schemas.JobCreate, db: Session):
    try:
        resume_text = dxt.process(FILE_LOCATION)
    except Exception as e:
        raise HTTPException(404, "Resume not found, please upload a resume!")
    else:
        new_job = models.Job(**job.model_dump())
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        extract_common_keywords(new_job.id, new_job.description, resume_text, db)
        return new_job
    

def delete_job(jobId: int, db: Session):
    job = db.query(models.Job).filter(models.Job.id == jobId).first()
    if(job):
        db.delete(job)
        db.commit()
        return "Job Deleted Successfully"
    else:
        raise HTTPException(404, "Job Does Not Exist")

def update_job():
    pass

def get_all_jobs(db: Session):
    return db.query(models.Job).all()
    

# def extract_keywords(desc: str, jobId: int, db: Session):
#     r = Rake()
#     r.extract_keywords_from_text(desc)
#     for i in r.frequency_dist:
#         keyword = models.Keywords(**schemas.KeywordCreate(keyword=i, job_id=jobId).model_dump())
#         db.add(keyword)
#         db.commit()
#         db.refresh(keyword)

def extract_keywords_from_docx_text(resume_text: str):
    r = Rake()
    r.extract_keywords_from_text(resume_text)
    keywords = set()
    for i in r.frequency_dist:
        keywords.add(i)
    return keywords

def extract_keywords_from_job_desc_text(text: str):
    r = Rake()
    r.extract_keywords_from_text(text=text)
    keywords = set()
    for i in r.frequency_dist:
        keywords.add(i)
    
    print(keywords)
    return keywords

def extract_common_keywords(jobId: int, job_desc: str, resume_text: str, db: Session):
    resume_keywords = extract_keywords_from_docx_text(resume_text)
    job_desc_keywords = extract_keywords_from_job_desc_text(job_desc)
    extracted_keywords = set()

    for i in resume_keywords:
        if i in job_desc_keywords:
            extracted_keywords.add(i)
    
    print(extracted_keywords)
    for i in extracted_keywords:
        common_keyword = models.Keywords(**schemas.KeywordCreate(keyword=i, job_id=jobId).model_dump())
        db.add(common_keyword)
        db.commit()
        db.refresh(common_keyword)
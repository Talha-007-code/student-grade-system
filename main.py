from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal, get_db
import pandas as pd

app = FastAPI()

models.Base.metadata.create_all(bind=engine)



@app.post("/students/")
def create_student(name: str, db: Session = Depends(get_db)):
    student = models.Student(name=name)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student



@app.get("/students/")
def get_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()



@app.post("/grades/")
def assign_grade(student_id: int, subject: str, grade: str, db: Session = Depends(get_db)): 
    student = db.query(models.Student).filter(models.Student.id == student_id).first() 
    if not student:
        raise HTTPException(status_code=404, detail="student not found")

    # import pdb; pdb.set_trace()
    grade_entry = models.Grade(student_id=student_id, subject=subject, grade=grade)
    db.add(grade_entry)
    db.commit()
    db.refresh(grade_entry)
    return grade_entry



@app.get("/grades/")
def get_grades(db: Session = Depends(get_db)):
    return db.query(models.Grade).all()



@app.get("/students/{student_id}/grades/")
def get_student_grades(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail = "student not found")
    return student.grades



@app.get("/reports/average_grades/")
def average_grades(db: Session = Depends(get_db)):
    grades = db.query(models.Grade).all()
    data = [{"student_id":g.student_id, "grade":g.grade}for g in grades]
    df = pd.DataFrame(data)

    if df.empty:
        return {"message": "No grades available"}

# Map letter grades to numeric values
    grade_map = {
        "A": 95,
        "B": 85,
        "C": 75,
        "D": 65,
        "F": 50
    }

    df["numeric_grade"] = df["grade"].map(grade_map)

    avg_grades = df.groupby("student_id")["numeric_grade"].mean().reset_index()
    return avg_grades.to_dict(orient="records")

    return avg_grades.to_dict(orient="records")


@app.get("/reports/top-students/")
def top_students(db: Session = Depends(get_db)):
    # Fetch all grades from the database
    grades = db.query(models.Grade).all()
    data = [{"student_id": g.student_id, "grade": g.grade} for g in grades]
    df = pd.DataFrame(data)

    # Check if there are no grades
    if df.empty:
        return {"message": "No grades available"}

    # Map letter grades to numeric values
    grade_map = {
        "A": 95,
        "B": 85,
        "C": 75,
        "D": 65,
        "F": 50
    }

    # Map grades in the dataframe to numeric values
    df["numeric_grade"] = df["grade"].map(grade_map)

    # Calculate average grades per student
    avg_grades = df.groupby("student_id")["numeric_grade"].mean().reset_index()

    # Sort students by average grade in descending order and pick top 3
    top_students = avg_grades.sort_values("numeric_grade", ascending=False).head(3)

    # Optionally: Map numeric grade back to letter grade (for user-friendly output)
    top_students["letter_grade"] = top_students["numeric_grade"].apply(
        lambda x: "A" if x >= 90 else "B" if x >= 80 else "C" if x >= 70 else "D" if x >= 60 else "F"
    )

    # Return the top students with their average numeric and letter grades
    return top_students[["student_id", "numeric_grade", "letter_grade"]].to_dict(orient="records")



@app.get("/reports/grade-distribution/")
def grade_distribution(db: Session = Depends(get_db)):
    grades = db.query(models.Grade).all()
    data = [{"grade": g.grade} for g in grades]
    df = pd.DataFrame(data)

    if df.empty:
        return {"message": "No grades available"}

    # Map letter grades to numeric values
    grade_map = {
        "A": 95,
        "B": 85,
        "C": 75,
        "D": 65,
        "F": 50
    }

    # Map grades to numeric values
    df["numeric_grade"] = df["grade"].map(grade_map)

    # Define bins for numeric grades
    bins = [0, 60, 70, 80, 90, 100]
    labels = ["F", "D", "C", "B", "A"]
    
    # Categorize numeric grades into grade categories
    df["grade_category"] = pd.cut(df["numeric_grade"], bins=bins, labels=labels, include_lowest=True)

    # Get the distribution of grade categories
    distribution = df["grade_category"].value_counts().to_dict()
    
    return distribution





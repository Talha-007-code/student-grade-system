from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base


class Student(Base):
    __tablename__= "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    grades = relationship("Grade", back_populates="student")

class Grade(Base):
    __tablename__ = "grades"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject = Column(String, index=True)
    grade = Column(String, index=True)
    student = relationship("Student", back_populates="grades")
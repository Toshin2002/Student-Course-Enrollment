# import os
from flask import Flask, redirect , render_template , request
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
# current_dir = os.path.abspath(os.path.dirname(__file__)) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
db = SQLAlchemy(app)

class Enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer , primary_key=True)
    estudent_id = db.Column(db.Integer , db.ForeignKey("student.student_id") , nullable=False)
    ecourse_id = db.Column(db.Integer , db.ForeignKey("course.course_id") ,nullable=False)    

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer , autoincrement=True , primary_key=True)
    course_code = db.Column(db.Text , unique=True , nullable=False)
    course_name = db.Column(db.Text , nullable=False)
    course_description = db.Column(db.Text)

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer , autoincrement=True , primary_key=True)
    roll_number = db.Column(db.Text , unique=True , nullable=False)
    first_name = db.Column(db.Text , nullable=False)
    last_name = db.Column(db.Text)   
    chosen_subs = db.relationship("Course" , secondary='enrollments' , backref='subjects')

##################     NOW COME THE CRUD OPERATIONS FOR STUDENTS      #################################

@app.route("/",methods=["GET","POST"])
def Checking() :
    if request.method == "GET":
        students = Student.query.all()
        return render_template("index.html",students=students)

@app.route("/student/create",methods=["GET","POST"])
def create():
    if request.method == "GET":
        return render_template("create.html")

    if request.method == "POST":
        new_student = request.form
        search = Student.query.filter_by(roll_number = new_student["roll"]).first()
        if search is None:
            ns = Student(roll_number=new_student["roll"],first_name=new_student["f_name"],last_name=new_student["l_name"])
            db.session.add(ns)
            db.session.commit()
            
            students = Student.query.all()
            return render_template("index.html",students=students)
        else:
            return render_template("/already_exists.html")

        # return new_student    
@app.route("/student/<stud_id>/update",methods=["GET","POST"])       
def update(stud_id):
    if request.method == "GET":
        search = Student.query.filter_by(student_id = stud_id).first()
        courses = Course.query.all()
        return render_template("update.html",stud=search,courses=courses)
        
    if request.method == "POST":    
        search = Student.query.filter_by(student_id = stud_id).first()
        updates = request.form
        search.first_name=updates["f_name"]
        search.last_name=updates["l_name"]  
        db.session.commit()
        
        for i in search.chosen_subs:
            search.chosen_subs.remove(i)

        cou = Course.query.filter_by(course_id=updates['course']).first()
        search.chosen_subs.append(cou)
        # up_subs=[]
        # for key in updates:
        #     if key != 'f_name' and key!='l_name':
        #         up_subs.append(key)
        
        # while search.chosen_subs:
        #        
        #         db.session.commit()

        # for new_subs in up_subs:
        #     
        #     search.chosen_subs.append(cou)
        #     db.session.commit()

        db.session.commit()
        students = Student.query.all()
        return render_template("index.html",students=students)

@app.route("/student/<stud_id>/delete")
def delete(stud_id):
    search = Student.query.filter_by(student_id = stud_id).first()
    db.session.delete(search)
    db.session.commit()
    students = Student.query.all()
    return render_template("index.html",students=students)

@app.route("/student/<stud_id>") 
def info(stud_id):
    student = Student.query.filter_by(student_id=stud_id).first()    
    return render_template("student_info.html",student=student,courses=student.chosen_subs)   

##################     NOW COME THE CRUD OPERATIONS FOR COURSES      #################################

@app.route("/courses")
def show_course():
    courses=Course.query.all()
    return render_template("courses.html",courses=courses)

@app.route("/course/create",methods=["GET","POST"])
def create_course():
    if request.method == "GET":
        return render_template("create_course.html")
    else:
        nc=request.form
        search = Course.query.filter_by(course_code = nc["code"]).first()
        if search is None:
            cou = Course(course_code=nc["code"],course_name=nc["c_name"],course_description=nc["desc"])
            db.session.add(cou)
            db.session.commit()
            courses=Course.query.all()
            return render_template("courses.html",courses=courses)
        else:
            return render_template("course_exists.html")

@app.route("/course/<cour_id>/update",methods=["GET","POST"])
def up_course(cour_id):
    if request.method=="GET":
        up = Course.query.filter_by(course_id=cour_id).first()
        return render_template("course_update.html",course=up)
    else:
        nc=request.form
        up = Course.query.filter_by(course_id=cour_id).first()
        up.course_name=nc["c_name"]
        up.course_description=nc["desc"]
        db.session.commit()
        courses=Course.query.all()
        return render_template("courses.html",courses=courses)

@app.route("/course/<cour_id>/delete")
def del_course(cour_id):
    target=Course.query.filter_by(course_id=cour_id).first()       
    db.session.delete(target)
    db.session.commit()
    courses=Course.query.all()
    return render_template("courses.html",courses=courses)

@app.route("/course/<cour_id>")
def course_info(cour_id):
    target=Course.query.filter_by(course_id=cour_id).first()
    return render_template("course_info.html",course=target,students=target.subjects)

@app.route("/student/<stud_id>/withdraw/<cour_id>")
def withdraw(stud_id,cour_id):
    stud = Student.query.filter_by(student_id=stud_id).first()    
    cour = Course.query.filter_by(course_id=cour_id).first()
    stud.chosen_subs.remove(cour)
    db.session.commit()    
    students = Student.query.all()
    return render_template("index.html",students=students)

if __name__ == '__main__':
    app.run(
        debug=True,
        host="0.0.0.0",
        port=8080
    )


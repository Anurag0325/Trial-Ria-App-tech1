import psycopg2
import csv
from flask import Flask, jsonify, request, send_file
from models import *
from flask_cors import CORS
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from io import BytesIO
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import pandas as pd
from werkzeug.security import generate_password_hash
import jwt
from sqlalchemy import func
from dotenv import load_dotenv
import time
import psutil
import gc
from flask_caching import Cache
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import threading
from time import sleep
from sqlalchemy.orm import load_only

load_dotenv()

app = Flask(__name__)

app.config['CACHE_TYPE'] = 'simple'  # In-memory cache
cache = Cache(app)

CORS(app)


# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite3"
# app.config['SECRET_KEY'] = "anuragiitmadras"

# DATABASE_URL = 'sqlite:///database.sqlite3'  # Replace with your actual DB URL
# engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL')  # Use full URL from Render
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
#     'DATABASE_URL')  # Use full URL from Render
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:qwerty@localhost:5432/kvqadatabase"
# app.config['SECRET_KEY'] = "anuragiitmadras"


db.init_app(app)


# def create_database():
#     connection = psycopg2.connect(
#     user="postgres", password="qwerty", host="127.0.0.1", port="5432")
#     connection.autocommit = True
#     cursor = connection.cursor()
#     try:
#         cursor.execute("CREATE DATABASE kvqadatabase")
#         print("Database created successfully")
#     except psycopg2.errors.DuplicateDatabase:
#         print("Database already exists")
#     finally:
#         cursor.close()
#         connection.close()


def insert_dummy_data():
    colleagues_data = [
        {'name': 'Maswood Alam', 'email': 'maswood.alam@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Mayank Jaiswal', 'email': 'mayank.jaiswal@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Mayank Pendke', 'email': 'mayank.pendke@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Mayur Sanjayrao Salunke', 'email': 'mayur.salunke@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Mayuri Pandit', 'email': 'mayuri.pandit@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Meera KM', 'email': 'meera.m@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},       
        {'name': 'Megh Shah', 'email': 'megh.shah@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Megha Ajayan', 'email': 'megha.ajayan@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Melissa Klein', 'email': 'melissa.klein@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Michael Norton', 'email': 'manorton@brasstacksconsulting.com', 'department': 'Developer', 'designation': 'Contractor'},
        {'name': 'Michael Surface', 'email': 'michael.surface@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},        
        {'name': 'Miguel Diman Tan', 'email': 'migs.tan@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Principal Consultant'},       
        {'name': 'Miheeka Khair', 'email': 'miheeka.khair@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Mihir Milind Shahane', 'email': 'mihir.shahane@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Minakshi Kumari', 'email': 'minakshi.kumari@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant  QA'},
        {'name': 'Minal Rajendra Mishra', 'email': 'minal.mishra@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},        
        {'name': 'Mitali Milind Hulbatte', 'email': 'mitali.hulbatte@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},    
        {'name': 'Mitali Naik', 'email': 'mitali.naik@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Mitesh Anil Agrawal', 'email': 'mitesh.agrawal@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},     
        {'name': 'Mitesh Buddhdev', 'email': 'mitesh.buddhdev@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Director'},
        {'name': 'Mohan Pachpande', 'email': 'mohan.pachpande@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'SHAHRUKH SHAIKH', 'email': 'mohd.shaikh@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Mohd Shaqib Anwar', 'email': 'mohd.anwar@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Mohini Sachar', 'email': 'mohini.sachar@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Mona Ranpise', 'email': 'mona.ranpise@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Monika Prashant Dipke', 'email': 'monika.dipke@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Monika Injamuri', 'email': 'monika.injamuri@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Mugdha Mayuresh Pujari', 'email': 'mugdha.pujari@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},   
        {'name': 'Nahush Dalvi', 'email': 'nahush.dalvi@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Principal Consultant'},       
        {'name': 'Namrata Chougule', 'email': 'namrata.chougule@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},      
        {'name': 'Naveen Nair', 'email': 'naveen.nair@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Navnit Raj', 'email': 'navnit.raj@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Neel Desai', 'email': 'neel.desai@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Technical Manager'},
        {'name': 'Neeraj Arora', 'email': 'neeraj.arora@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Neeraja Krishnakumar', 'email': 'neeraja.krishnakumar@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'}, 
        {'name': 'Neha Jain', 'email': 'neha.jain@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Neha Pawar', 'email': 'neha.pawar@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Neha Krunal Tidke', 'email': 'neha.tidke@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Nikhil Bhutada', 'email': 'nikhil.bhutada@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Nikhil Anil Sawant', 'email': 'nikhil.sawant@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Nikhil Sharma', 'email': 'nikhil.sharma@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Nikita Borgaonkar', 'email': 'nikita.borgaonkar@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Nikita Ubale', 'email': 'nikita.ubale@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Nilakshi Shirish Badave', 'email': 'nilakshi.badave@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Director'}, 
        {'name': 'Nilesh Laxmanrao Bidwai', 'email': 'nilesh.bidwai@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},     
        {'name': 'Nilesh Sanjay Marathe', 'email': 'nilesh.marathe@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},   
        {'name': 'Nilima Dash', 'email': 'nilima.dash@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Nirmal Rathod', 'email': 'nirmal.rathod@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Nisha Kakade', 'email': 'nisha.kakade@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Nishanth M', 'email': 'nishanth.m@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Nishitha Padamati', 'email': 'nishitha.padamati@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},    
        {'name': 'Nithin Gowda', 'email': 'nithin.gowda@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Director'},
        {'name': 'Nithya Ananth', 'email': 'nithya.ananth@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Director'},
        {'name': 'Nitin Karande', 'email': 'nitin.karande@riaadvisory.com', 'department': 'Developer', 'designation': 'Technical Consulting Senior Manager'},
        {'name': 'Nitish Kumar', 'email': 'nitish.kumar@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Nityanand Kankipati', 'email': 'nity.kankipati@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Director'},
        {'name': 'Om Sudhanshu', 'email': 'om.sudhanshu@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Omkar Dinkar Ghorpade', 'email': 'omkar.ghorpade@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},   
        {'name': 'Onkar Pradip Gupte', 'email': 'onkar.gupte@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Software Engineer (SDE4)'},
        {'name': 'Onkar Joshi', 'email': 'onkar.joshi@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Onkar Navinchandra Ravan', 'email': 'onkar.ravan@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},   
        {'name': 'Onkar Gajanan Shinde', 'email': 'onkar.shinde@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Onkareshwar Sanjaykuar Kinhalkar', 'email': 'onkareshwar.kinhalkar@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Oscar Velazquez', 'email': 'oscar.velazquez@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Pallavi Arun Birdawade', 'email': 'pallavi.birdawade@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Pallavi Tanaji Kopnar', 'email': 'pallavi.kopnar@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},   
        {'name': 'Pallavi Pramod Marathe', 'email': 'pallavi.marathe@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},    
        {'name': 'Pallavi Tonpe', 'email': 'pallavi.tonpe@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Director'},
        {'name': 'Pankaj Babaji Dukare', 'email': 'pankaj.dukare@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},     
        {'name': 'Pankaj Maurya', 'email': 'pankaj.morya@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Paridhi Jain', 'email': 'paridhi.jain@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Parikrama Lokare', 'email': 'parikrama.lokare@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Parth Apamarjane', 'email': 'parth.apamarjane@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},      
        {'name': 'Paushal PA', 'email': 'paushal.a@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Pawan Venkateswarlu Bandla', 'email': 'pawan.bandla@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Piyush Milind Kale', 'email': 'piyush.kale@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Pooja Gulshan .', 'email': 'pooja.tuteja@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Pooja DN', 'email': 'pooja.revoor@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Pooja Gogate', 'email': 'pooja.gogate@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Poonam Kiran Tembhekar', 'email': 'poonam.tembhekar@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},   
        {'name': 'Pornima Kakade', 'email': 'pornima.kakade@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Pragati Alone', 'email': 'pragati.alone@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Pragun Khanna', 'email': 'pragunkhanna@riaadvisory.com', 'department': 'Developer', 'designation': 'Intern'},
        {'name': 'Pranali Ghanghav', 'email': 'pranali.ghanghav@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'PRANAV PRASADKUMAR KULKARNI', 'email': 'pranav.kulkarni@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Prasad Vijay Sapkal', 'email': 'prasad.sapkal@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},      
        {'name': 'Prashant RANGARAO Pawar', 'email': 'prashant.pawar@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Software Development Engineer (SDE4)'},
        {'name': 'Prateek Bansal', 'email': 'prateek.bansal@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Prathamesh Mangesh Bhosale', 'email': 'prathamesh.bhosale@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Developer (SD3)'},
        {'name': 'Prathamesh Chougule', 'email': 'prathamesh.chougule@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Prathmesh Nandaram Gabhale', 'email': 'prathmesh.gabhale@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Pratibha Rathore', 'email': 'pratibha.rathore@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},      
        {'name': 'Pratik Chaudhari', 'email': 'pratik.chaudhari@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},      
        {'name': 'Pratik Anil Jain', 'email': 'pratik.jain@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Pratik Sabale', 'email': 'pratik.sabale@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Pratik Sharma', 'email': 'pratik.sharma@astcorporation.com', 'department': 'Developer', 'designation': 'Contractor'},
        {'name': 'Pratik Thorve', 'email': 'pratik.thorve@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Pratiksha B Bhavle', 'email': 'pratiksha.bhavle@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Pratiksha Kokare', 'email': 'pratiksha.kokare@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Pratiksha Harshal Unhale', 'email': 'pratiksha.unhale@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},        
        {'name': 'PRAVEEN SATHE', 'email': 'praveen.sathe@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Pravin Ranganath Garad', 'email': 'pravin.garad@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},    
        {'name': 'Pravin Kumar Singh', 'email': 'pravinkumar.singh@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},      
        {'name': 'Preeti Tiwari', 'email': 'preeti.tiwari@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Solution Architect'},       
        {'name': 'Preeti Rajan Velhal', 'email': 'preeti.velhal@riaadvisory.com', 'department': 'Developer', 'designation': 'Business Analyst'},
        {'name': 'Prerana Jugalkishor Holani', 'email': 'prerana.holani@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'}, 
        {'name': 'Prince Singh', 'email': 'prince.singh@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Pritam Sunil Chaudhari', 'email': 'pritam.chaudhari@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Priti Gopale', 'email': 'priti.gopale@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Priya Marathe', 'email': 'priya.marathe@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Priya Mendonca', 'email': 'priya.mendonca@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Priyanka Vinod Kanoi', 'email': 'priyanka.kanoi@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Software Engineer (SDE4)'},
        {'name': 'Priyanka Nandkumar Shirore', 'email': 'priyanka.shirore@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Priyata Sinha', 'email': 'priyata.sinha@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Pushkar Vasant Dasgaonkar', 'email': 'pushkar.dasgaonkar@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Queency Fernandes', 'email': 'queency.fernandes@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},    
        {'name': 'Raajan Narayanan', 'email': 'raajan.narayanan@riaadvisory.com', 'department': 'Developer', 'designation': 'Solution Architect'},        
        {'name': 'Raghvendra Purohit', 'email': 'raghvendra.purohit@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},     
        {'name': 'Rahul Kumar', 'email': 'rahul.kumar@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Software Engineer (SDE4)'},  
        {'name': 'Rahul Nehare', 'email': 'rahul.nehare@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Rais M Naik', 'email': 'rais.naik@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Rajat Saxena', 'email': 'rajat.saxena@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Rajesh Ramdas Ingulkar', 'email': 'rajesh.ingulkar@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Rakesh Chaubey', 'email': 'rakesh.chaubey@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Rakesh Sahoo', 'email': 'rakesh.sahoo@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Rakhi Jadhav', 'email': 'rakhi.jadhav@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Rakhi Nilkanth Kshirsagar', 'email': 'rakhi.kshirsagar@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},       
        {'name': 'Rakshit Gopakumar Nair', 'email': 'rakshit.nair@riaadvisory.com', 'department': 'Developer', 'designation': 'Intern'},
        {'name': 'Ramachandran Ananthapadmanabhan', 'email': 'ramachandran.ananthapadmanabhan@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Director'},
        {'name': 'Ranjeev Nair', 'email': 'ranjeev.nair@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Director'},
        {'name': 'Raveena Arora', 'email': 'raveena.arora@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Ravi Sahitya', 'email': 'ravi.sahitya@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Ravikumar Garuku', 'email': 'ravikumar.garuku@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Ravinandan Rohila', 'email': 'ravinandan.rohila@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Principal Consultant'},
        {'name': 'Ravsaheb K Shelake', 'email': 'ravsaheb.shelake@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},       
        {'name': 'Reema Kuwar', 'email': 'reema.kuwar@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Renuka Patil', 'email': 'renuka.patil@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Richa Thakur', 'email': 'richa.thakur@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Richard Francis Dsouza', 'email': 'richard.desouza@riaadvisory.com', 'department': 'Developer', 'designation': 'Project Manager'},      
        {'name': 'Rishabh Rai', 'email': 'rishabh.rai@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Ritesh Paratane', 'email': 'ritesh.paratane@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},        
        {'name': 'Ritik Ashok Manghani', 'email': 'ritik.manghani@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'RIYA BISHT', 'email': 'riya.bisht@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Robert Stanislaw Radziszewski', 'email': 'robert.radziszewski@riaadvisory.com', 'department': 'Developer', 'designation': 'Technical Architect'},
        {'name': 'Rohan Deshpande', 'email': 'rohan.deshpande@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Rohan Sukhdev Gaikwad', 'email': 'rohan.gaikwad@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Rohan Jain', 'email': 'rohan.jain@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Manager'},
        {'name': 'Rohit Kulkarni', 'email': 'rohit.kulkarni@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Rohit Prabhakar Shelar', 'email': 'rohit.shelar@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},    
        {'name': 'Rohith S K', 'email': 'rohith.sk@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Roshani Patil', 'email': 'roshani.patil@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Ruchi Bhardwaj', 'email': 'ruchi.bhardwaj@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Director'},
        {'name': 'Ruchi Jain', 'email': 'ruchi.jain@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},  
        {'name': 'Rupal Mittal', 'email': 'rupal.mittal@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Technical Manager'},      
        {'name': 'Rupesh Kachiraju', 'email': 'rupesh.kachiraju@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Rupesh Kumar', 'email': 'rupesh.kumar@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Rushibha Suresh Adlak', 'email': 'rushibha.adlak@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Rushikesh Kinikar', 'email': 'rushikesh.kinikar@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Rushikesh Bhojling Pawar', 'email': 'rushikesh.pawar@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Rutuja Vijay Khedekar', 'email': 'rutuja.khedekar@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Sachin Macwan', 'email': 'sachin.macwan@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consulting Manager'},       
        {'name': 'Sachin More', 'email': 'sachin.more@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Project Manager'},
        {'name': 'Sagar Ghate', 'email': 'sagar.ghate@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Sagar Khachane', 'email': 'sagar.khachane@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Sagar Gunwantrao Umathe', 'email': 'sagar.umathe@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Sahadeo Pandit Bhogil', 'email': 'sahadeo.bhogil@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Saher Jamadar', 'email': 'saher.jamadar@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Sahil Patil', 'email': 'sahil.patil@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Sahil Shaikh', 'email': 'sahil.shaikh@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Sai Ramsagar', 'email': 'sai.ramsagar@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Consultant'},
        {'name': 'Sai Sahaja Badvel', 'email': 'sahaja.badvel@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Business Analyst'},  
        {'name': 'Sai Vinod Thiruveedhula', 'email': 'saivinod.thiruveedhula@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Saikat Das', 'email': 'saikat.das@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Sakshi Verma', 'email': 'sakshi.verma@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Salil Ray', 'email': 'salil.ray@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Salini Bhimireddy', 'email': 'salini.bhimireddy@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},    
        {'name': 'Samatha Kusuma', 'email': 'samatha.kusuma@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Samik Bhattacharjee', 'email': 'samik.bhattacharjee@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},   
        {'name': 'Samir Batta', 'email': 'samir.batta@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Sanjay Gupta', 'email': 'sanjay.gupta@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Senior Project Manager'}, 
        {'name': 'Sanjay Khandelwal', 'email': 'sanjay.khandelwal@riaadvisory.com', 'department': 'Developer', 'designation': 'Director - Managed Support Services'},
        {'name': 'Sanjna Sudhir Pawar', 'email': 'sanjna.pawar@riaadvisory.com', 'department': 'Developer', 'designation': 'Contractor'},
        {'name': 'Sanket Suresh Vaidya', 'email': 'sanket.vaidya@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},     
        {'name': 'Sanskar Saxena', 'email': 'sanskar.saxena@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Santini Pecaoco', 'email': 'santini.pecaoco@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Solution Architect'},   
        {'name': 'Santosh Prakash Saste', 'email': 'santosh.saste@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Principal Engineer'},
        {'name': 'Saravana Kumar Jagadeesan', 'email': 'saravanakumar.jagadeesan@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Technical Director'},
        {'name': 'Sathwika Baddam', 'email': 'sathwika.baddam@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Sawarin Kishore Patel', 'email': 'sawarin.patel@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Sayali Musande', 'email': 'sayali.musande@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Sayali Rajeev Sapre', 'email': 'sayali.sapre@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Seenivasan Kaliyamoorthy', 'email': 'seenivasan.kaliyamoorthy@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Seershika Majeti', 'email': 'seershika.majeti@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},      
        {'name': 'Senthilkumar Ayyaswamy', 'email': 'senthil.ayyaswamy@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Technical Consulting Manager'},
        {'name': 'Sesha Shayan Nandyal', 'email': 'sesha.nandyal@riaadvisory.com', 'department': 'Developer', 'designation': 'Director Consultant'},      
        {'name': 'Shafiuddin Aminuddin Kazi', 'email': 'shafiuddin.kazi@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Manager'},
        {'name': 'Shailaja Parelley', 'email': 'shailaja.parelley@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},    
        {'name': 'Shalu Balakrishnan', 'email': 'shalu.balakrishnan@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Shantanu Shivaji Shinde', 'email': 'shantanu.shinde@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Sharayu Ganoo', 'email': 'sharayu.ganoo@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Shashank Pandey', 'email': 'shashank.pandey@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Shashank Rastogi', 'email': 'shashank.rastogi@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Technical Manager'},
        {'name': 'Shilpa Narayanan Chitbone', 'email': 'shilpa.chitbone@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Shina Bajaj', 'email': 'shina.bajaj@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Shini Cherian', 'email': 'shini.cherian@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Shirish Manik Jadhav', 'email': 'shirish.jadhav@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},    
        {'name': 'Shivani Kulkarni', 'email': 'shivani.kulkarni@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Shraddha Kakad', 'email': 'shraddha.kakad@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Shray Arora', 'email': 'shray.arora@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Shreshtha Mehrotra', 'email': 'shreshtha.mehrotra@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Shreya Ingolikar', 'email': 'shreya.ingolikar@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},      
        {'name': 'Shreya Patil', 'email': 'shreya.patil@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Shreyas Sapre', 'email': 'shreyas.sapre@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Shrihas Devalekar', 'email': 'shrihas.devalekar@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Shrinivas Anil Kottawar', 'email': 'shrinivas.kottawar@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Shriniwas Madhav Hirave', 'email': 'shriniwas.hirave@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Manager- Test Automation'},
        {'name': 'Shriram Mandara', 'email': 'shriram.mandara@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Shruti Bhagat', 'email': 'shruti.bhagat@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Shrutika Anarthe', 'email': 'shrutika.anarthe@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Shubham Patil', 'email': 'shubham.patil@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Shubham Kakad', 'email': 'shubham.kakad@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Shubham Sanjay Kulkarni', 'email': 'shubham.kulkarni@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Shweta Hasija', 'email': 'shweta.hasija@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Principal Consultant'},     
        {'name': 'Shwetha Patil', 'email': 'shwetha.patil@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Shyam Vilas Kawale', 'email': 'shyam.kawale@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},        
        {'name': 'Shyamkant Barve', 'email': 'shyamkant.barve@riaadvisory.com', 'department': 'Developer', 'designation': 'Contractor'},
        {'name': 'Siddharth Lasure', 'email': 'siddharth.lasure@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Siddharth Rajendra Navgire', 'email': 'siddharth.navgire@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Siva Sundaresan', 'email': 'siva.sundaresan@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Sivani Sagi', 'email': 'sivani.sagi@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Sneha Yewankar', 'email': 'sneha.yewankar@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Snehal Dhok', 'email': 'snehal.dhok@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consulting Manager'},
        {'name': 'Snehal Eknath Rajas', 'email': 'snehal.rajas@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Project Manager'},     
        {'name': 'Snehali Nandurkar', 'email': 'snehali.nandurkar@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},       
        {'name': 'Snigdha Sumukh Rajwade', 'email': 'snigdha.rajwade@riaadvisory.com', 'department': 'Developer', 'designation': 'Contractor'},
        {'name': 'Somya Sahani', 'email': 'somya.sahani@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Sonaji Prakash Talade', 'email': 'sonaji.talade@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Sonal Namdev', 'email': 'sonal.namdev@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Sonal Suresh Renuse', 'email': 'sonal.renuse@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Sonali Chavan', 'email': 'sonali.chavan@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Sonali Desai', 'email': 'sonali.desai@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Sonali Dubey', 'email': 'sonali.dubey@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Sonia Chandhok', 'email': 'sonia.chandhok@riaadvisory.com', 'department': 'Developer', 'designation': 'Manager - Production Support'},  
        {'name': 'Sravanthi Bandi', 'email': 'sravanthi.bandi@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Sreejith R', 'email': 'sreejith.r@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Sreeraj S', 'email': 'sreeraj.s@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},    
        {'name': 'Srilakshmi Gogula', 'email': 'srilakshmi.gogula@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Srilaxmi Mogulla', 'email': 'mogulla.srilaxmi@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Srinivas Gunda', 'email': 'srinivas.gunda@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Subodh Salve', 'email': 'subodh.salve@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Sudhanshu Patki', 'email': 'sudhanshu.patki@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Director'},
        {'name': 'Sudhir Yadav', 'email': 'sudhir.yadav@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Sudipta Banerjee', 'email': 'sudipta.banerjee@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Director'},
        {'name': 'Sujith Varghese', 'email': 'sujith.varghese@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Director'},
        {'name': 'Suraj Yashwant Ahire', 'email': 'suraj.ahire@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},       
        {'name': 'Suraj Rajesh Anasune', 'email': 'suraj.anasune@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},        
        {'name': 'Surbhi Bhatnagar', 'email': 'surbhi.bhatnagar@riaadvisory.com', 'department': 'Developer', 'designation': 'Project Manager'},
        {'name': 'Sushmi Mukherjee', 'email': 'sushmi.mukherjee@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},      
        {'name': 'Susmita Bharat Bhosale', 'email': 'susmita.bhosale@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},    
        {'name': 'Suyash Kumbhar', 'email': 'suyash.kumbhar@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Swapna Prakash Ghatge', 'email': 'swapna.ghatge@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},    
        {'name': 'Swapnaja Deshpande', 'email': 'swapnaja.deshpande@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},     
        {'name': 'Swapnil Gaur', 'email': 'swapnil.gaur@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Director'},
        {'name': 'Swapnil Kasar', 'email': 'swapnil.kasar@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Swapnil Mahalle', 'email': 'swapnil.mahalle@riaadvisory.com', 'department': 'Developer', 'designation': 'Technical Consulting Manager'},
        {'name': 'Swapnil Shinde', 'email': 'swapnil.shinde@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Swathi Kolanupaka', 'email': 'swathi.kolanupaka@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Principal Consultant'},
        {'name': 'Swati Srinivasan', 'email': 'swati.srinivasan@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Technical Trainer'},  
        {'name': 'Tamaghna Roy', 'email': 'tamaghna.roy@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Tanmay Bargal', 'email': 'tanmay.bargal@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Tanvi Bhusari', 'email': 'tanvi.bhusari@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Tanvi Kulkarni', 'email': 'tanvi.kulkarni@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Tejas Ashok Kanojia', 'email': 'tejas.kanojia@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Tejaswini Mariyada', 'email': 'tejaswini.mariyada@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},     
        {'name': 'Terin Yohannan', 'email': 'terin.yohannan@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Tushar Deshmukh', 'email': 'tushar.deshmukh@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},        
        {'name': 'Ujjwal Sinha', 'email': 'ujjwal.sinha@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Ali Ulvi Kasapoglu', 'email': 'ali.ulvi.kasapoglu@riaadvisory.com', 'department': 'Developer', 'designation': 'Technical Architect'},   
        {'name': 'Vaibhav Lande', 'email': 'vaibhav.lande@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Vaibhav Vaman Patil', 'email': 'vaibhav.patil@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Vaidik kishor Sharma', 'email': 'vaidik.sharma@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},     
        {'name': 'Varsha Bothe', 'email': 'varsha.bothe@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Varun Sasi', 'email': 'varun.sasi@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consulting Technical Manager'},   
        {'name': 'Chandrakanth Vasa', 'email': 'vasa.chandrakanth@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},       
        {'name': 'Vedangi Joshi', 'email': 'vedangi.joshi@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Veena Krishnan', 'email': 'veena.krishnan@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Principal Software Engineer (SDE5)'},
        {'name': 'Venkateswara Reddy Guddeti', 'email': 'venky.guddeti@riaadvisory.com', 'department': 'Developer', 'designation': 'Consulting Technical Director'},
        {'name': 'Vijay Jadhav', 'email': 'vijay.jadhav@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Vijay Kamlakar Kamble', 'email': 'vijay.kamble@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},        
        {'name': 'Vijay Nagendra Karchi', 'email': 'vijay.karchi@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Manager'},
        {'name': 'Vijayshri Ganesh Jejurkar', 'email': 'vijayshri.jejurkar@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},     
        {'name': 'Vikas Govind Jadhav', 'email': 'vikas.jadhav@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Vikas Khindkar', 'email': 'vikas.khindkar@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Vinay Ramesh Patil', 'email': 'vinay.patil@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Vinay Patil', 'email': 'vinayprakash.patil@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Vipin Khobragade', 'email': 'vipin.khobragade@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},
        {'name': 'Vipul Bajaj', 'email': 'vipul.bajaj@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Vishnupriya Jayaprakash', 'email': 'vishnupriya.jayaprakash@riaadvisory.com', 'department': 'Developer', 'designation': 'Director - Product Development'},
        {'name': 'Vishwajit Devidas Gadge', 'email': 'vishwajit.gadge@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Vitthal Sagde', 'email': 'vitthal.sagde@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Vrushali Vasant Vasekar', 'email': 'vrushali.vasekar@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Consultant'},  
        {'name': 'Vyankatesh Pawar', 'email': 'vyankatesh.pawar@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Thomas Warren Elizer', 'email': 'warren.elizer@riaadvisory.com', 'department': 'Developer', 'designation': 'Managing Director'},        
        {'name': 'Xanea Kryzen', 'email': 'xanea.caraig@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Consultant'},
        {'name': 'Yasasvi Ramsagar', 'email': 'yasasvi.ramsagar@riaadvisory.com', 'department': 'Developer', 'designation': 'Data Analytics Associate'},  
        {'name': 'Yash Bantthia', 'email': 'yash.bantthia@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Yash Vishwas Desai', 'email': 'yash.desai@riaadvisory.com', 'department': 'Developer', 'designation': 'Associate Consultant'},
        {'name': 'Yash Kulkarni', 'email': 'yash.kulkarni@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Yesha Agrawal', 'email': 'yesha.agrawal@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Yogesh Gupta', 'email': 'yogesh.gupta@riaadvisory.com', 'department': 'Developer', 'designation': 'Head – Offshore Delivery'},
        {'name': 'Zaid Sayyad', 'email': 'zaid.sayyad@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Zainab Sajid Shaikh', 'email': 'zainab.shaikh@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Mitra Shyamkant Barve', 'email': 'mitra.barve@riaadvisory.com', 'department': 'Developer', 'designation': 'Intern'},
        {'name': 'Aishwarya Umesh Gadikar', 'email': 'aishwarya.gadikar@riaadvisory.com', 'department': 'Developer', 'designation': 'Intern'},
        {'name': 'Swapnil Gupta', 'email': 'swapnil.gupta@riaadvisory.com', 'department': 'Developer', 'designation': 'Director - Product Development'},  
        {'name': 'Kaustubh Mohan Kale', 'email': 'kaustubh.kale@riaadvisory.com', 'department': 'Developer', 'designation': 'Director - Product Development'},
        {'name': 'Rishabh Nanda', 'email': 'rishabh.nanda@riaadvisory.com', 'department': 'Developer', 'designation': 'Director - Product Development'},  
        {'name': 'Himanshu Rajpurohit', 'email': 'himanshu.rajpurohit@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Sadul Khod', 'email': 'sadul.khod@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Akash Thomas', 'email': 'akash.thomas@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Software Development Engineer (SDE4)'},
        {'name': 'Madhura Kale', 'email': 'madhura.kale@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Mubin Mulani', 'email': 'mubin.mulani@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Amol Pathade', 'email': 'amol.pathade@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Mayuresh Bhangale', 'email': 'mayuresh.bhangale@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Vaishnavi Sanajy Mundhe', 'email': 'vaishnavi.mundhe@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Abhinav Kumar', 'email': 'abhinav.kumar@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Darshan S', 'email': 'darshan.s@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},    
        {'name': 'Nivita Kaniampal', 'email': 'nivita.kaniampal@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Software Development Engineer (SDE4)'},
        {'name': 'Vishnu V L', 'email': 'vishnu.v@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Shubham Shirore', 'email': 'shubham.shirore@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Harshal Medhe', 'email': 'harshal.medhe@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Ashish Karmarkar', 'email': 'ashish.karmarkar@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Development Manager'},
        {'name': 'Chaitanya Shivaji Nehe', 'email': 'chaitanya.nehe@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Manasi Kale', 'email': 'manasi.kale@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Pratik Machhindra Hajare', 'email': 'pratik.hajare@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Sachin Rupnawar', 'email': 'sachin.rupnawar@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Tushar Sunil Harel', 'email': 'tushar.harel@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Priyanka Vitthal Walunj', 'email': 'priyanka.walunj@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Atharva Jaiswal', 'email': 'atharva.jaiswal@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Software Development Engineer (SDE4)'},
        {'name': 'Kishor Prakash Patil', 'email': 'kishor.patil@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal Software Development Engineer (SDE4)'},
        {'name': 'Dipak Desai', 'email': 'dipak.desai@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Nilesh Landge', 'email': 'nilesh.landge@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Engineer (SDE3)'},
        {'name': 'Kailas Satale', 'email': 'kailas.satale@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Advait Purohit', 'email': 'advait.purohit@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Development Manager'},    
        {'name': 'Harsh Agarwal', 'email': 'harsh.agarwal@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Vaishali Khedekar', 'email': 'vaishali.khedekar@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Software Development Manager'},
        {'name': 'Aditya Kathula', 'email': 'aditya.kathula@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Principal - Banking Solutions'},
        {'name': 'Mohd Aslam', 'email': 'mohd.aslam@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Rahul Yadav', 'email': 'rahul.yadav@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Shivraj Sangappa Menkale', 'email': 'shivraj.menkale@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Kirti Shrinath', 'email': 'kirti.shrinath@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Mahesh Bhamare', 'email': 'mahesh.bhamare@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Tanveer Pendhari', 'email': 'tanveer.pendhari@riaadvisory.com', 'department': 'Developer', 'designation': 'Software Development Engineer (SDE2)'},
        {'name': 'Vishal Gade', 'email': 'vishal.gade@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Pratik Tanawade', 'email': 'pratik.tanawade@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Adwait Deshmukh', 'email': 'adwait.deshmukh@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Prasad Gosavi', 'email': 'prasad.gosavi@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Ashwini Kurhe', 'email': 'ashwini.kurhe@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Vrushabh Babasaheb Khatik', 'email': 'vrushabh.khatik@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Mohammed Bhaila', 'email': 'mohammed.bhaila@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Omkar Parshuram Waghmode', 'email': 'omkar.waghmode@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Atharva Ravindra Joshi', 'email': 'atharva.joshi@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Avinash Laxman Maharnavar', 'email': 'avinash.maharnavar@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Sujit Jagatrao Patil', 'email': 'sujit.patil@riaadvisory.com', 'department': 'Developer', 'designation': 'Junior Software Development Engineer (SDE1)'},
        {'name': 'Nageswara Sanika', 'email': 'nageswara.sanika@riaadvisory.com', 'department': 'Developer', 'designation': 'Principal AI/ML Architect'}, 
        {'name': 'Darren Cherry', 'email': 'darren.cherry@riaadvisory.com', 'department': 'Developer', 'designation': 'Consultant'},
        {'name': 'Rohit Chawla', 'email': 'rohit.chawla@riaadvisory.com', 'department': 'Developer', 'designation': 'Intern'},
        {'name': 'Sai Gokul Krishna Reddy Talla', 'email': 'gokul.talla@riaadvisory.com', 'department': 'Developer', 'designation': 'Intern'},
        {'name': 'Luke Bowman', 'email': 'luke.bowman@riaadvisory.com', 'department': 'Developer', 'designation': 'Intern'},
        {'name': 'Helen Nicole Pavalko', 'email': 'helen.pavalko@riaadvisory.com', 'department': 'Developer', 'designation': 'Vice President Business Development'},
        {'name': 'Lexi Grissman', 'email': 'lexi.grissman@riaadvisory.com', 'department': 'Developer', 'designation': 'Senior Business Analyst'},
        {'name': 'John Andersen', 'email': 'john.andersen@riaadvisory.com', 'department': 'Developer', 'designation': 'VP Strategic Product & Sales'},    
        {'name': 'Sanjay Francis Kottaram', 'email': 'sanjay.kottaram@riaadvisory.com', 'department': 'Developer', 'designation': 'Vice President Business Development'},
        {"name": "Krishna Chaudhari", "email": "krishna.chaudhari@riaadvisory.com",
            "department": "Internal IT and Cloud Ops", "designation": "Associate Consultant"},
        {"name": "Deepak Nichani", "email": "deepak.nichani@riaadvisory.com",
            "department": "Operations", "designation": "Senior Consultant - Admin"},
    ]

    # colleagues = [Colleagues(name=data['name'], email=data['email'],
    #                          designation=data['designation']) for data in colleagues_data]

    for data in colleagues_data:
        existing_colleague = Colleagues.query.filter_by(
            email=data['email']).first()
        if not existing_colleague:
            colleague = Colleagues(
                name=data['name'], email=data['email'], department=data['department'], designation=data['designation'])
            db.session.add(colleague)

    users_data = [
        {"email": "tech@kvqaindia.com",
            "username": "tech@kvqaindia", "password": "asdfgh"}
    ]

    for data in users_data:
        existing_user = User.query.filter_by(email=data['email']).first()
        if not existing_user:
            user = User(email=data['email'], username=data['username'])
            user.set_password(data['password'])
            db.session.add(user)

    db.session.commit()


with app.app_context():
    # create_database()
    db.create_all()
    insert_dummy_data()


class EmailTemplate:
    def __init__(self, template_file):

        with open(template_file, 'r') as file:
            self.template = file.read()

    def generate_email(self, sender_name, sender_email, recipient_name, subject):

        email_content = self.template
        email_content = email_content.replace('{{sender_name}}', sender_name)
        email_content = email_content.replace('{{sender_email}}', sender_email)
        email_content = email_content.replace(
            '{{recipient_name}}', recipient_name)
        email_content = email_content.replace('{{subject}}', subject)

        email_content = email_content.replace('\n', '<br>')
        email_content = email_content.replace('\n\n', '</p><p>')
        email_content = f"<p>{email_content}</p>"

        return email_content


@app.route('/')
def home():
    return 'Hello World'


@app.route('/register', methods=['POST'])
# def register():
#     data = request.json
#     email = data.get('email')
#     username = data.get('username')
#     password = data.get('password')
#     if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
#         return jsonify({'message': 'User with this email or username already exists!'}), 409
#     new_user = User(email=email, username=username)
#     new_user.set_password(password)
#     db.session.add(new_user)
#     db.session.commit()
#     return jsonify({'message': 'User registered successfully'}), 201
def register():
    data = request.get_json()

    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({"message": "All fields are required."}), 400

    # Check if the user already exists
    existing_user = User.query.filter(
        (User.email == email) | (User.username == username)).first()
    if existing_user:
        return jsonify({"message": "User with this email or username already exists."}), 400

    try:
        # Create a new user
        new_user = User(email=email, username=username,
                        password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error registering user: {str(e)}"}), 500


@app.route('/login', methods=['POST'])
def login():
    credentials = request.json
    username = credentials.get('username')
    password = credentials.get('password')

    user = User.query.filter_by(
        username=username).first()

    if user and user.check_password(password):
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(
            payload, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"message": "Login Successful", "access_token": token}), 200

    return jsonify({"message": "Invalid username or password"}), 401


@app.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "Logged out successfully"}), 200


emailed_candidates = []


# @app.route('/send_email', methods=['GET', 'POST'])
# def send_email():
#     global emailed_candidates
#     emailed_candidates = []

#     templates_dir = os.path.join(os.path.dirname(__file__), 'templates')

#     colleagues = Colleagues.query.all()

#     # part_size = len(colleagues) // 3
#     # group1 = colleagues[:part_size]
#     # group2 = colleagues[part_size:2*part_size]
#     # group3 = colleagues[2*part_size:]

#     part_size = len(colleagues) // 4
#     group1 = colleagues[:part_size]
#     group2 = colleagues[part_size:2*part_size]
#     group3 = colleagues[2*part_size:3*part_size]
#     group4 = colleagues[3*part_size:]

#     department_config = {
#         'HR': {
#             'email': os.getenv('HR_EMAIL'),
#             'password': os.getenv('HR_PASSWORD'),
#             'template': 'hr_email_template.html',
#             'subject': "Update Your Payroll Information for Q4",
#             'action_name': "Update Payroll Information"
#         },
#         'Leadership': {
#             'email': os.getenv('LEADERSHIP_EMAIL'),
#             'password': os.getenv('LEADERSHIP_PASSWORD'),
#             'template': 'leadership_template.html',
#             'subject': "Strategic Plan Review for Q4 - Action Required",
#             'action_name': "Review Strategic Plan"
#         },
#         'Developer': {
#             'email': os.getenv('DEVELOPER_EMAIL'),
#             'password': os.getenv('DEVELOPER_PASSWORD'),
#             'template': 'developer_template.html',
#             'subject': "Security Patch Deployment for Development Tools",
#             'action_name': "Download Security Patch"
#         },

#         'Account': {
#             'email': os.getenv('ACCOUNT_EMAIL'),
#             'password': os.getenv('ACCOUNT_PASSWORD'),
#             'template': 'accounts_email_template.html',
#             'subject': "System Update for new Compliance Standards",
#             'action_name': "Update Credential"
#         }
#     }

#     # send_group_email(group1, department_config['HR'], templates_dir)
#     # send_group_email(group2, department_config['Leadership'], templates_dir)
#     # send_group_email(group3, department_config['Developer'], templates_dir)

#     # return jsonify({'message': 'Phishing emails sent to colleagues.'})

#     try:
#         send_group_email(group1, department_config['HR'], templates_dir)
#         send_group_email(
#             group2, department_config['Leadership'], templates_dir)
#         send_group_email(group3, department_config['Developer'], templates_dir)
#         send_group_email(group4, department_config['Account'], templates_dir)

#         return jsonify({
#             'message': 'Phishing emails sent to colleagues.',
#             'emailed_candidates': emailed_candidates
#         }), 200

#     except Exception as e:
#         return jsonify({'message': f'Error sending emails: {str(e)}'}), 500


# def send_group_email(group, config, templates_dir):
#     """Helper function to send emails to a group with specific department config."""
#     from_email = config['email']
#     password = config['password']
#     email_subject = config['subject']
#     action_name = config['action_name']

#     with open(os.path.join(templates_dir, config['template'])) as f:
#         email_template = f.read()

#     for colleague in group:
#         tracking_link = f"https://ria-app.vercel.app/phishing_test/{colleague.id}"

#         print(f"Generated tracking link for {colleague.name}: {tracking_link}")

#         to_email = colleague.email
#         msg = MIMEMultipart('related')
#         msg['Subject'] = email_subject
#         msg['From'] = from_email
#         msg['To'] = to_email

#         body = email_template.replace("{{recipient_name}}", colleague.name)
#         body = body.replace("{{action_link}}", tracking_link)
#         body = body.replace("{{action_name}}", action_name)
#         body = body.replace("{{email_subject}}", email_subject)

#         html_content = f"""
#         <html>
#             <body>
#                 {body}
#             </body>
#         </html>
#         """
#         msg.attach(MIMEText(html_content, 'html'))

#         try:
#             # with smtplib.SMTP('smtp.gmail.com', 587) as server:
#             #     server.starttls()
#             #     server.login(from_email, password)
#             #     server.send_message(msg)
#             # print(f"Email sent to {colleague.email}")

#             # with smtplib.SMTP_SSL('smtp.secureserver.net', 465) as server:
#             #     server.login(from_email, password)
#             #     server.send_message(msg)
#             # print(f"Email sent to {colleague.email}")

#             with smtplib.SMTP('smtpout.secureserver.net', 587) as server:
#                 server.starttls()
#                 server.login(from_email, password)
#                 server.send_message(msg)
#             print(f"Email sent to {colleague.email}")

#             # emailed_candidates.append({
#             #     'name': colleague.name,
#             #     'email': colleague.email,
#             #     'designation': colleague.designation
#             # })
#             update_email_log(colleague)
#             emailed_candidates.append({
#                 'name': colleague.name,
#                 'email': colleague.email,
#                 'designation': colleague.designation
#             })
#             print("Emailed candidates list after sending:", emailed_candidates)

#         except Exception as e:
#             print(f"Failed to send email to {colleague.email}: {str(e)}")

# @app.route('/send_email', methods=['GET', 'POST'])
# def send_email():
#     global emailed_candidates
#     emailed_candidates = []

#     templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
#     colleagues = Colleagues.query.all()

#     part_size = len(colleagues) // 4
#     group1 = colleagues[:part_size]
#     group2 = colleagues[part_size:2*part_size]
#     group3 = colleagues[2*part_size:3*part_size]
#     group4 = colleagues[3*part_size:]

#     department_config = {
#         'HR': {
#             'email': os.getenv('HR_EMAIL'),
#             'password': os.getenv('HR_PASSWORD'),
#             'template': 'hr_email_template.html',
#             'subject': "Update Your Payroll Information for Q4",
#             'action_name': "Update Payroll Information"
#         },
#         'Leadership': {
#             'email': os.getenv('LEADERSHIP_EMAIL'),
#             'password': os.getenv('LEADERSHIP_PASSWORD'),
#             'template': 'leadership_template.html',
#             'subject': "Strategic Plan Review for Q4 - Action Required",
#             'action_name': "Review Strategic Plan"
#         },
#         'Developer': {
#             'email': os.getenv('DEVELOPER_EMAIL'),
#             'password': os.getenv('DEVELOPER_PASSWORD'),
#             'template': 'developer_template.html',
#             'subject': "Security Patch Deployment for Development Tools",
#             'action_name': "Download Security Patch"
#         },
#         'Account': {
#             'email': os.getenv('ACCOUNT_EMAIL'),
#             'password': os.getenv('ACCOUNT_PASSWORD'),
#             'template': 'accounts_email_template.html',
#             'subject': "System Update for new Compliance Standards",
#             'action_name': "Update Credential"
#         }
#     }

#     try:
#         send_group_email(group1, department_config['HR'], templates_dir)
#         send_group_email(
#             group2, department_config['Leadership'], templates_dir)
#         send_group_email(group3, department_config['Developer'], templates_dir)
#         send_group_email(group4, department_config['Account'], templates_dir)

#         return jsonify({
#             'message': 'Emails sent to colleagues.',
#             'emailed_candidates': emailed_candidates
#         }), 200

#     except Exception as e:
#         return jsonify({'message': f'Error sending emails: {str(e)}'}), 500


# def send_group_email(group, config, templates_dir, batch_size=10, delay=10):
#     """Helper function to send emails to a group in small batches."""
#     from_email = config['email']
#     password = config['password']
#     email_subject = config['subject']
#     action_name = config['action_name']

#     with open(os.path.join(templates_dir, config['template'])) as f:
#         email_template = f.read()

#     try:
#         with smtplib.SMTP('smtpout.secureserver.net', 587) as server:
#             server.starttls()
#             server.login(from_email, password)

#             for i in range(0, len(group), batch_size):
#                 batch = group[i:i + batch_size]

#                 for colleague in batch:
#                     # tracking_link = f"https://ria-app.vercel.app/phishing_test/{colleague.id}"
#                     tracking_link = f"https://trial-ria-app.vercel.app/phishing_test/{colleague.id}"
#                     to_email = colleague.email
#                     msg = MIMEMultipart('related')
#                     msg['Subject'] = email_subject
#                     msg['From'] = from_email
#                     msg['To'] = to_email

#                     body = email_template.replace(
#                         "{{recipient_name}}", colleague.name)
#                     body = body.replace("{{action_link}}", tracking_link)
#                     body = body.replace("{{action_name}}", action_name)
#                     body = body.replace("{{email_subject}}", email_subject)

#                     html_content = f"""
#                     <html>
#                         <body>
#                             {body}
#                         </body>
#                     </html>
#                     """
#                     msg.attach(MIMEText(html_content, 'html'))

#                     try:
#                         server.send_message(msg)
#                         print(f"Email sent to {colleague.email}")

#                         update_email_log(colleague)
#                         emailed_candidates.append({
#                             'name': colleague.name,
#                             'email': colleague.email,
#                             'designation': colleague.designation
#                         })

#                     except Exception as e:
#                         print(
#                             f"Failed to send email to {colleague.email}: {str(e)}")

#                 # Delay between each batch to manage CPU load
#                 time.sleep(delay)
#                 cpu_usage, memory_usage = log_system_usage()
#                 if memory_usage > 80:  # If memory usage exceeds 80%, trigger garbage collection
#                     print("High memory usage, performing garbage collection.")
#                     gc.collect()

#     except Exception as e:
#         print(f"Error in connecting or sending emails: {str(e)}")


#######

# @app.route('/send_email', methods=['GET', 'POST'])
# def send_email():
#     global emailed_candidates
#     emailed_candidates = []

#     templates_dir = os.path.join(os.path.dirname(__file__), 'templates')

#     # Define group sizes
#     groups = [
#         {'start': 0, 'end': 400, 'config': 'Developer'},
#         {'start': 400, 'end': 788, 'config': 'Developer'},
#         {'start': 788, 'end': 802, 'config': 'Leadership'},
#         {'start': 802, 'end': 986, 'config': 'HR'},
#         {'start': 986, 'end': 1000, 'config': 'Account'}
#     ]

#     department_config = {
#         'HR': {
#             'email': os.getenv('HR_EMAIL'),
#             'password': os.getenv('HR_PASSWORD'),
#             'template': 'hr_email_template.html',
#             'subject': "Update Your Payroll Information for Q4",
#             'action_name': "Update Payroll Information"
#         },
#         'Leadership': {
#             'email': os.getenv('LEADERSHIP_EMAIL'),
#             'password': os.getenv('LEADERSHIP_PASSWORD'),
#             'template': 'leadership_template.html',
#             'subject': "Strategic Plan Review for Q4 - Action Required",
#             'action_name': "Review Strategic Plan"
#         },
#         'Developer': {
#             'email': os.getenv('DEVELOPER_EMAIL'),
#             'password': os.getenv('DEVELOPER_PASSWORD'),
#             'template': 'developer_template.html',
#             'subject': "Security Patch Deployment for Development Tools",
#             'action_name': "Download Security Patch"
#         },
#         'Account': {
#             'email': os.getenv('ACCOUNT_EMAIL'),
#             'password': os.getenv('ACCOUNT_PASSWORD'),
#             'template': 'accounts_email_template.html',
#             'subject': "System Update for new Compliance Standards",
#             'action_name': "Update Credential"
#         }
#     }

#     try:
#         # Process each group separately
#         for group in groups:
#             send_group_email_in_batches(
#                 start_idx=group['start'],
#                 end_idx=group['end'],
#                 config=department_config[group['config']],
#                 templates_dir=templates_dir
#             )

#         return jsonify({
#             'message': 'Emails sent to colleagues.',
#             'emailed_candidates': emailed_candidates
#         }), 200

#     except Exception as e:
#         return jsonify({'message': f'Error sending emails: {str(e)}'}), 500


# def send_group_email_in_batches(start_idx, end_idx, config, templates_dir, batch_size=5, delay=15):
#     """Send emails to a subset of the database in small batches."""
#     from_email = config['email']
#     password = config['password']
#     email_subject = config['subject']
#     action_name = config['action_name']

#     with open(os.path.join(templates_dir, config['template'])) as f:
#         email_template = f.read()

#     try:
#         with smtplib.SMTP('smtpout.secureserver.net', 587) as server:
#             server.starttls()
#             server.login(from_email, password)

#             # Load the data in small batches
#             for i in range(start_idx, end_idx, batch_size):
#                 batch = Colleagues.query.filter(
#                     Colleagues.id >= i + 1,
#                     Colleagues.id < i + batch_size + 1
#                 ).all()

#                 if not batch:
#                     break  # Stop if there are no more records

#                 for colleague in batch:
#                     tracking_link = f"https://trial-ria-app.vercel.app/phishing_test/{colleague.id}"
#                     to_email = colleague.email
#                     msg = MIMEMultipart('related')
#                     msg['Subject'] = email_subject
#                     msg['From'] = from_email
#                     msg['To'] = to_email

#                     body = email_template.replace(
#                         "{{recipient_name}}", colleague.name)
#                     body = body.replace("{{action_link}}", tracking_link)
#                     body = body.replace("{{action_name}}", action_name)
#                     body = body.replace("{{email_subject}}", email_subject)

#                     html_content = f"""
#                     <html>
#                         <body>
#                             {body}
#                         </body>
#                     </html>
#                     """
#                     msg.attach(MIMEText(html_content, 'html'))

#                     try:
#                         server.send_message(msg)
#                         print(f"Email sent to {colleague.email}")

#                         update_email_log(colleague)
#                         emailed_candidates.append({
#                             'name': colleague.name,
#                             'email': colleague.email,
#                             'designation': colleague.designation
#                         })

#                     except Exception as e:
#                         print(
#                             f"Failed to send email to {colleague.email}: {str(e)}")

#                 # Delay between each batch to manage CPU load
#                 time.sleep(delay)
#                 cpu_usage, memory_usage = log_system_usage()
#                 if memory_usage > 70:  # If memory usage exceeds 70%, trigger garbage collection
#                     print("High memory usage, performing garbage collection.")
#                     gc.collect()

#     except Exception as e:
#         print(f"Error in connecting or sending emails: {str(e)}")


#######


# groups = [
#     {'start': 0, 'end': 400, 'config': 'Developer'},
#     {'start': 400, 'end': 788, 'config': 'Developer'},
#     {'start': 788, 'end': 802, 'config': 'Leadership'},
#     {'start': 802, 'end': 986, 'config': 'HR'},
#     {'start': 986, 'end': 1000, 'config': 'Account'}
# ]

# department_config = {
#     'HR': {
#         'email': os.getenv('HR_EMAIL'),
#         'password': os.getenv('HR_PASSWORD'),
#         'template': 'hr_email_template.html',
#         'subject': "Update Your Payroll Information for Q4",
#         'action_name': "Update Payroll Information"
#     },
#     'Leadership': {
#         'email': os.getenv('LEADERSHIP_EMAIL'),
#         'password': os.getenv('LEADERSHIP_PASSWORD'),
#         'template': 'leadership_template.html',
#         'subject': "Strategic Plan Review for Q4 - Action Required",
#         'action_name': "Review Strategic Plan"
#     },
#     'Developer': {
#         'email': os.getenv('DEVELOPER_EMAIL'),
#         'password': os.getenv('DEVELOPER_PASSWORD'),
#         'template': 'developer_template.html',
#         'subject': "Security Patch Deployment for Development Tools",
#         'action_name': "Download Security Patch"
#     },
#     'Account': {
#         'email': os.getenv('ACCOUNT_EMAIL'),
#         'password': os.getenv('ACCOUNT_PASSWORD'),
#         'template': 'accounts_email_template.html',
#         'subject': "System Update for new Compliance Standards",
#         'action_name': "Update Credential"
#     }
# }

# templates_dir = os.path.join(os.path.dirname(__file__), 'templates')


# @app.route('/send_email', methods=['GET', 'POST'])
# def send_email():
#     """API to trigger email sending process."""
#     global emailed_candidates
#     emailed_candidates = []  # Reset the emailed candidates log

#     try:
#         # Call the function to send emails group by group
#         send_emails_by_group(groups, department_config, templates_dir)

#         return jsonify({'message': 'Emails are being sent successfully.', 'status': 'success'}), 200

#     except Exception as e:
#         return jsonify({'message': f'Error: {str(e)}', 'status': 'error'}), 500


# def send_emails_by_group(groups, department_config, templates_dir):
#     """Send emails group by group."""
#     global emailed_candidates

#     for group in groups:
#         config = department_config[group['config']]
#         print(f"Processing group: {group['config']}")

#         # Load the template for the group
#         with open(os.path.join(templates_dir, config['template'])) as f:
#             email_template = f.read()

#         send_emails_in_batches(
#             start_idx=group['start'],
#             end_idx=group['end'],
#             config=config,
#             templates_dir=templates_dir,
#             email_template=email_template,
#             batch_size=5,  # 5 emails per batch
#             email_delay=2,  # 2 seconds between emails
#             batch_delay=15  # 15 seconds between batches
#         )

#         # Clean up after finishing a group
#         gc.collect()  # Release memory
#         time.sleep(10)  # 10 seconds delay before the next group


# def send_emails_in_batches(start_idx, end_idx, config, templates_dir, email_template, batch_size, email_delay, batch_delay):
#     """Send emails in smaller batches with delays."""
#     from_email = config['email']
#     password = config['password']
#     email_subject = config['subject']
#     action_name = config['action_name']
#     training_link = "https://trial-ria-app.vercel.app/phishing_test/common_training_link"  # Common link

#     try:
#         with smtplib.SMTP('smtpout.secureserver.net', 587) as server:
#             server.starttls()
#             server.login(from_email, password)

#             for i in range(start_idx, end_idx, batch_size):
#                 # Query the batch
#                 batch = Colleagues.query.filter(
#                     Colleagues.id >= i + 1,
#                     Colleagues.id < i + batch_size + 1
#                 ).options(load_only(Colleagues.id, Colleagues.name, Colleagues.email, Colleagues.designation)).all()

#                 if not batch:
#                     break  # Stop if no more records

#                 for colleague in batch:
#                     to_email = colleague.email
#                     msg = MIMEMultipart('related')
#                     msg['Subject'] = email_subject
#                     msg['From'] = from_email
#                     msg['To'] = to_email

#                     # Replace placeholders in the email template
#                     body = email_template.replace(
#                         "{{recipient_name}}", colleague.name)
#                     body = body.replace("{{action_link}}", training_link)
#                     body = body.replace("{{action_name}}", action_name)
#                     body = body.replace("{{email_subject}}", email_subject)

#                     html_content = f"""
#                     <html>
#                         <body>
#                             {body}
#                         </body>
#                     </html>
#                     """
#                     msg.attach(MIMEText(html_content, 'html'))

#                     try:
#                         server.send_message(msg)
#                         print(f"Email sent to {colleague.email}")

#                         # Log email sent
#                         update_email_log(colleague)
#                         emailed_candidates.append({
#                             'name': colleague.name,
#                             'email': colleague.email,
#                             'designation': colleague.designation
#                         })

#                     except Exception as e:
#                         print(
#                             f"Failed to send email to {colleague.email}: {str(e)}")

#                     # Delay between emails
#                     time.sleep(email_delay)

#                 # Clean up after processing a batch
#                 gc.collect()
#                 time.sleep(batch_delay)

#     except Exception as e:
#         print(f"Error in sending emails: {str(e)}")


# New code

groups = [
    # {'start': 0, 'end': 376, 'config': 'Developer'},
    {'start': 374, 'end': 376, 'config': 'Developer_1'},
    # {'start': 788, 'end': 802, 'config': 'Leadership'},
    # {'start': 802, 'end': 986, 'config': 'HR'},
    # {'start': 986, 'end': 1001, 'config': 'Account'}
]

# groups = [
#     {'start': 0, 'end': 40, 'config': 'Developer'},
#     # {'start': 400, 'end': 788, 'config': 'Developer'},
#     {'start': 40, 'end': 78, 'config': 'Leadership'},
#     {'start': 78, 'end': 94, 'config': 'HR'},
#     {'start': 94, 'end': 120, 'config': 'Account'}
# ]

department_config = {
    'HR': {
        'email': os.getenv('HR_EMAIL'),
        'password': os.getenv('HR_PASSWORD'),
        'template': 'hr_email_template.html',
        'subject': "Update Your Payroll Information for Q4",
        'action_name': "Update Payroll Information"
    },
    'Leadership': {
        'email': os.getenv('LEADERSHIP_EMAIL'),
        'password': os.getenv('LEADERSHIP_PASSWORD'),
        'template': 'leadership_template.html',
        'subject': "Strategic Plan Review for Q4 - Action Required",
        'action_name': "Review Strategic Plan"
    },
    'Developer': {
        'email': os.getenv('DEVELOPER_EMAIL'),
        'password': os.getenv('DEVELOPER_PASSWORD'),
        'template': 'developer_template.html',
        'subject': "Security Patch Deployment for Development Tools",
        'action_name': "Download Security Patch"
    },
    'Developer_1': {
        'email': os.getenv('DEVELOPER_1_EMAIL'),
        'password': os.getenv('DEVELOPER_1_PASSWORD'),
        'template': 'developer_template.html',
        'subject': "Security Patch Deployment for Development Tools",
        'action_name': "Download Security Patch"
    },
    'Account': {
        'email': os.getenv('ACCOUNT_EMAIL'),
        'password': os.getenv('ACCOUNT_PASSWORD'),
        'template': 'accounts_email_template.html',
        'subject': "System Update for new Compliance Standards",
        'action_name': "Update Credential"
    }
}

templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
# common_training_link = "https://trial-ria-app.vercel.app/phishing_test/common_training_link"
# common_training_link = f"https://trial-ria-app.vercel.app/phishing_test/{colleague.id}"


# @app.route('/send_email', methods=['GET', 'POST'])
# def send_email():
#     """API to trigger email sending process."""
#     try:
#         # Process each group
#         for group in groups:
#             config = department_config[group['config']]
#             print(f"Processing group: {group['config']}")

#             # Load the email template once per group
#             with open(os.path.join(templates_dir, config['template'])) as f:
#                 email_template = f.read()

#             # SMTP connection setup
#             with smtplib.SMTP('smtpout.secureserver.net', 587) as server:
#                 server.starttls()
#                 server.login(config['email'], config['password'])

#                 # Process emails in batches
#                 for i in range(group['start'], group['end'], 5):  # Batch size = 5
#                     # Query a batch of emails
#                     batch = Colleagues.query.filter(
#                         Colleagues.id >= i + 1,
#                         Colleagues.id < i + 6  # 5 emails per batch
#                     ).with_entities(Colleagues.id, Colleagues.name, Colleagues.email, Colleagues.designation).yield_per(5)

#                     if not batch:
#                         break  # No more records in the group

#                     for colleague in batch:
#                         to_email = colleague.email
#                         msg = MIMEMultipart('related')
#                         msg['Subject'] = config['subject']
#                         msg['From'] = config['email']
#                         msg['To'] = to_email

#                         # Replace placeholders in the email template
#                         body = email_template.replace(
#                             "{{recipient_name}}", colleague.name)
#                         body = body.replace("{{action_link}}", common_training_link)
#                         body = body.replace("{{action_name}}", config['action_name'])
#                         body = body.replace("{{email_subject}}", config['subject'])

#                         html_content = f"""
#                         <html>
#                             <body>
#                                 {body}
#                             </body>
#                         </html>
#                         """
#                         msg.attach(MIMEText(html_content, 'html'))

#                         try:
#                             server.send_message(msg)
#                             print(f"Email sent to {colleague.email}")

#                             # Log email sent (store in database or a file)
#                             update_email_log(colleague)
#                             emailed_candidates.append({
#                                 'name': colleague.name,
#                                 'email': colleague.email,
#                                 'designation': colleague.designation
#                             })

#                         except Exception as e:
#                             print(f"Failed to send email to {colleague.email}: {str(e)}")

#                         # Delay between emails
#                         time.sleep(dynamic_delay())

#                     # Clean up batch from memory
#                     del batch
#                     gc.collect()
#                     time.sleep(15)  # Batch delay

#             # Clean up group from memory
#             del email_template
#             gc.collect()
#             time.sleep(10)  # Group delay

#         return jsonify({'message': 'Emails have been sent successfully.', 'status': 'success'}), 200

#     except Exception as e:
#         return jsonify({'message': f'Error: {str(e)}', 'status': 'error'}), 500


# @app.route('/send_email', methods=['POST'])
# def send_email():
#     try:
#         emails_sent = []  # Keep track of sent emails
#         failed_emails = []  # Track failed emails for debugging

#         # SMTP connection setup
#         with smtplib.SMTP('smtpout.secureserver.net', 587) as server:
#             server.starttls()
#             server.login(os.getenv('DEVELOPER_1_EMAIL'), os.getenv('DEVELOPER_1_PASSWORD'))
#               # Adjust based on department

#             # server.login(os.getenv('ACCOUNT_EMAIL'), os.getenv('ACCOUNT_PASSWORD'))

#             # Fetch emails from the database for a specific group
#             for colleague in Colleagues.query.filter(Colleagues.id >= 1, Colleagues.id <= 400):  # Adjust range for each group
#                 to_email = colleague.email
#                 config = department_config['Developer_1']  # Adjust based on group
#                 msg = MIMEMultipart('related')
#                 msg['Subject'] = config['subject']
#                 msg['From'] = config['email']
#                 msg['To'] = to_email

#                 # Prepare the email body
#                 with open(os.path.join('templates', config['template'])) as f:
#                     email_template = f.read()

#                 common_training_link = f"https://trial-ria-app.vercel.app/phishing_test/{colleague.id}"

#                 body = email_template.replace("{{recipient_name}}", colleague.name)
#                 body = body.replace("{{action_link}}", common_training_link)
#                 body = body.replace("{{action_name}}", config['action_name'])
#                 body = body.replace("{{email_subject}}", config['subject'])

#                 html_content = f"<html><body>{body}</body></html>"
#                 msg.attach(MIMEText(html_content, 'html'))

#                 try:
#                     # Send the email
#                     server.send_message(msg)
#                     emails_sent.append(colleague.email)  # Track successful email

#                     # Log the email in the database
#                     update_email_log(colleague)

#                     # Log progress with a print statement (to avoid Gunicorn timeout)
#                     print(f"Email successfully sent to: {colleague.email}")

#                     # Optional: delay to avoid too rapid sending
#                     time.sleep(1)  # Small delay between emails

#                 except Exception as e:
#                     print(f"Failed to send email to {colleague.email}: {str(e)}")
#                     failed_emails.append(colleague.email)  # Track failed email

#         # After processing all emails, print a completion log
#         print(f"All emails processed. Sent: {len(emails_sent)}, Failed: {len(failed_emails)}")

#         return jsonify({
#             'message': 'Emails sent successfully.',
#             'status': 'success',
#             'emails_sent': emails_sent,
#             'failed_emails': failed_emails
#         }), 200

#     except Exception as e:
#         print(f"Error occurred: {str(e)}")
#         return jsonify({'message': f"Error: {str(e)}", 'status': 'error'}), 500

# Send mail code with dynamic group selection

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        emails_sent = []  # Keep track of sent emails
        failed_emails = []  # Track failed emails for debugging

        # SMTP connection setup
        with smtplib.SMTP('smtpout.secureserver.net', 587) as server:
            server.starttls()

            # Iterate through groups and send emails for each group
            for group in groups:
                start, end, department = group['start'], group['end'], group['config']
                config = department_config[department]

                # Log in to the SMTP server with the current department's credentials
                try:
                    server.login(config['email'], config['password'])
                except Exception as e:
                    print(f"Login failed for {config['email']}: {str(e)}")
                    return jsonify({
                        'message': f"SMTP login failed for {config['email']}",
                        'status': 'error',
                        'error': str(e)
                    }), 500

                # Fetch colleagues in the current group
                colleagues = Colleagues.query.filter(
                    Colleagues.id >= start, Colleagues.id < end).all()

                for colleague in colleagues:
                    to_email = colleague.email
                    msg = MIMEMultipart('related')
                    msg['Subject'] = config['subject']
                    msg['From'] = config['email']
                    msg['To'] = to_email

                    # Prepare the email body
                    with open(os.path.join('templates', config['template'])) as f:
                        email_template = f.read()

                    common_training_link = f"https://trial-ria-app-tech1.vercel.app/phishing_test/{colleague.id}"

                    body = email_template.replace(
                        "{{recipient_name}}", colleague.name)
                    body = body.replace(
                        "{{action_link}}", common_training_link)
                    body = body.replace(
                        "{{action_name}}", config['action_name'])
                    body = body.replace("{{email_subject}}", config['subject'])

                    html_content = f"<html><body>{body}</body></html>"
                    msg.attach(MIMEText(html_content, 'html'))

                    try:
                        # Send the email
                        server.send_message(msg)
                        # Track successful email
                        emails_sent.append(colleague.email)

                        # Log the email in the database
                        update_email_log(colleague)

                        # Log progress
                        print(f"Email successfully sent to: {colleague.email}")

                        # Optional: delay to avoid rapid sending
                        time.sleep(1)  # Small delay between emails

                    except Exception as e:
                        print(
                            f"Failed to send email to {colleague.email}: {str(e)}")
                        # Track failed email
                        failed_emails.append(colleague.email)

        # After processing all groups, print a completion log
        print(
            f"All emails processed. Sent: {len(emails_sent)}, Failed: {len(failed_emails)}")

        return jsonify({
            'message': 'Emails sent successfully.',
            'status': 'success',
            'emails_sent': emails_sent,
            'failed_emails': failed_emails
        }), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'message': f"Error: {str(e)}", 'status': 'error'}), 500


def dynamic_delay():
    """Calculate delay based on system resource usage."""
    memory_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent(interval=0.1)
    if memory_usage > 80 or cpu_usage > 80:
        return 15  # Increase delay under high load
    elif memory_usage < 50 and cpu_usage < 50:
        return 10  # Decrease delay under low load
    return 5  # Default delay


# def send_group_email(group, config, templates_dir, batch_size=10, delay=10):
#     from_email = config['email']
#     password = config['password']
#     email_subject = config['subject']
#     action_name = config['action_name']

#     with open(os.path.join(templates_dir, config['template'])) as f:
#         email_template = f.read()

#     with smtplib.SMTP('smtpout.secureserver.net', 587) as server:
#         server.starttls()
#         server.login(from_email, password)

#         for i in range(0, len(group), batch_size):
#             batch = group[i:i + batch_size]  # Process emails in batches
#             for colleague in batch:
#                 tracking_link = f"https://ria-app.vercel.app/phishing_test/{colleague.id}"
#                 body = email_template.replace(
#                     "{{recipient_name}}", colleague.name)
#                 body = body.replace("{{action_link}}", tracking_link)
#                 body = body.replace("{{action_name}}", action_name)
#                 body = body.replace("{{email_subject}}", email_subject)

#                 msg = MIMEMultipart('related')
#                 msg['Subject'] = email_subject
#                 msg['From'] = from_email
#                 msg['To'] = colleague.email
#                 msg.attach(MIMEText(body, 'html'))

#                 try:
#                     server.send_message(msg)
#                     print(f"Email sent to {colleague.email}")
#                 except Exception as e:
#                     print(
#                         f"Failed to send email to {colleague.email}: {str(e)}")
#                 finally:
#                     del msg  # Explicitly delete the message object to free memory

#             time.sleep(delay)  # Delay before the next batch

# def log_system_usage():
#     # CPU Usage
#     cpu_usage = psutil.cpu_percent()  # Overall CPU usage as a percentage
#     cpu_count = psutil.cpu_count()  # Total number of CPU cores

#     # Memory Usage
#     memory = psutil.virtual_memory()
#     memory_usage = memory.percent  # Memory usage as a percentage
#     memory_total = memory.total  # Total memory (in bytes)
#     memory_available = memory.available  # Available memory (in bytes)
#     memory_used = memory.used  # Used memory (in bytes)

#     print(f"CPU Usage: {cpu_usage}%")
#     print(f"Number of CPU cores: {cpu_count}")
#     print(f"Memory Usage: {memory_usage}%")
#     print(f"Total Memory: {memory_total / (1024 ** 3):.2f} GB")
#     print(f"Used Memory: {memory_used / (1024 ** 3):.2f} GB")
#     print(f"Available Memory: {memory_available / (1024 ** 3):.2f} GB")

# return cpu_usage, cpu_count, memory_usage, memory_total, memory_used, memory_available

def log_system_usage():
    # CPU Usage
    cpu_usage = psutil.cpu_percent()  # Overall CPU usage as a percentage

    # Memory Usage
    memory = psutil.virtual_memory()
    memory_usage = memory.percent  # Memory usage as a percentage

    print(f"CPU Usage: {cpu_usage}%")
    print(f"Memory Usage: {memory_usage}%")

    return cpu_usage, memory_usage

# Send email function
# def send_group_email(group, config, templates_dir, batch_size=10, delay=10):
#     """Helper function to send emails to a group in small batches."""
#     from_email = config['email']
#     password = config['password']
#     email_subject = config['subject']
#     action_name = config['action_name']

#     # Load the email template from cache or file
#     email_template = cache.get('email_template')
#     if email_template is None:
#         with open(os.path.join(templates_dir, config['template'])) as f:
#             email_template = f.read()
#         cache.set('email_template', email_template)

#     try:
#         # Connect to the SMTP server
#         with smtplib.SMTP('smtpout.secureserver.net', 587) as server:
#             server.starttls()
#             server.login(from_email, password)

#             # Process emails in batches
#             for i in range(0, len(group), batch_size):
#                 batch = group[i:i + batch_size]

#                 for colleague in batch:
#                     tracking_link = f"https://ria-app.vercel.app/phishing_test/{colleague.id}"
#                     to_email = colleague.email
#                     msg = MIMEMultipart('related')
#                     msg['Subject'] = email_subject
#                     msg['From'] = from_email
#                     msg['To'] = to_email

#                     # Customize the email body with the colleague's name and tracking link
#                     body = email_template.replace("{{recipient_name}}", colleague.name)
#                     body = body.replace("{{action_link}}", tracking_link)
#                     body = body.replace("{{action_name}}", action_name)
#                     body = body.replace("{{email_subject}}", email_subject)

#                     html_content = f"""
#                     <html>
#                         <body>
#                             {body}
#                         </body>
#                     </html>
#                     """
#                     msg.attach(MIMEText(html_content, 'html'))

#                     try:
#                         server.send_message(msg)
#                         print(f"Email sent to {colleague.email}")

#                         # Log the sent email details
#                         update_email_log(colleague)

#                     except Exception as e:
#                         print(f"Failed to send email to {colleague.email}: {str(e)}")

#                 # Delay between batches to prevent overloading the CPU
#                 time.sleep(delay)

#                 # Log system usage and perform garbage collection
#                 cpu_usage, memory_usage = log_system_usage()
#                 if memory_usage > 80:  # If memory usage exceeds 80%, trigger garbage collection
#                     print("High memory usage, performing garbage collection.")
#                     gc.collect()

#     except Exception as e:
#         print(f"Error in connecting or sending emails: {str(e)}")

# # Email sending route
# @app.route('/send_email', methods=['GET', 'POST'])
# def send_email():
#     global emailed_candidates
#     emailed_candidates = []

#     templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
#     colleagues = Colleagues.query.all()

#     # Define groupings
#     part_size = len(colleagues) // 5
#     group1 = colleagues[:8]
#     group2 = colleagues[8:13]
#     group3 = colleagues[13:18]
#     group4 = colleagues[18:20]
#     group5 = colleagues[20:]

#     # Department configuration
#     department_config = {
#         'HR': {
#             'email': os.getenv('HR_EMAIL'),
#             'password': os.getenv('HR_PASSWORD'),
#             'template': 'hr_email_template.html',
#             'subject': "Update Your Payroll Information for Q4",
#             'action_name': "Update Payroll Information"
#         },
#         'Leadership': {
#             'email': os.getenv('LEADERSHIP_EMAIL'),
#             'password': os.getenv('LEADERSHIP_PASSWORD'),
#             'template': 'leadership_template.html',
#             'subject': "Strategic Plan Review for Q4 - Action Required",
#             'action_name': "Review Strategic Plan"
#         },
#         'Developer': {
#             'email': os.getenv('DEVELOPER_EMAIL'),
#             'password': os.getenv('DEVELOPER_PASSWORD'),
#             'template': 'developer_template.html',
#             'subject': "Security Patch Deployment for Development Tools",
#             'action_name': "Download Security Patch"
#         },

#         'Developer_1': {
#             'email': os.getenv('DEVELOPER_EMAIL_1'),
#             'password': os.getenv('DEVELOPER_PASSWORD_1'),
#             'template': 'developer_template.html',
#             'subject': "Security Patch Deployment for Development Tools",
#             'action_name': "Download Security Patch"
#         },


#         'Account': {
#             'email': os.getenv('ACCOUNT_EMAIL'),
#             'password': os.getenv('ACCOUNT_PASSWORD'),
#             'template': 'accounts_email_template.html',
#             'subject': "System Update for new Compliance Standards",
#             'action_name': "Update Credential"
#         }
#     }

#     try:
#         # Send emails for each group
#         send_group_email(group1, department_config['Developer'], templates_dir)
#         send_group_email(group2, department_config['Developer_1'], templates_dir)
#         send_group_email(group3, department_config['HR'], templates_dir)
#         send_group_email(group4, department_config['Account'], templates_dir)
#         send_group_email(group5, department_config['Leadership'], templates_dir)

#         return jsonify({
#             'message': 'Emails sent to colleagues.',
#             'emailed_candidates': emailed_candidates
#         }), 200

#     except Exception as e:
#         return jsonify({'message': f'Error sending emails: {str(e)}'}), 500


# def send_group_email(group_start, group_end, config, templates_dir, batch_size=10, delay=10):
#     """Helper function to send emails to a group in small batches."""
#     from_email = config['email']
#     password = config['password']
#     email_subject = config['subject']
#     action_name = config['action_name']

#     # Load the email template from cache or file
#     email_template = cache.get('email_template')
#     if email_template is None:
#         with open(os.path.join(templates_dir, config['template'])) as f:
#             email_template = f.read()
#         cache.set('email_template', email_template)

#     try:
#         # Connect to the SMTP server
#         with smtplib.SMTP('smtpout.secureserver.net', 587) as server:
#             server.starttls()
#             server.login(from_email, password)

#             # Query the database for the batch of colleagues
#             session = Session()
#             colleagues = session.query(Colleagues).slice(group_start, group_end).all()

#             # Process emails in batches
#             for i in range(0, len(colleagues), batch_size):
#                 batch = colleagues[i:i + batch_size]

#                 for colleague in batch:
#                     tracking_link = f"https://ria-app.vercel.app/phishing_test/{colleague.id}"
#                     to_email = colleague.email
#                     msg = MIMEMultipart('related')
#                     msg['Subject'] = email_subject
#                     msg['From'] = from_email
#                     msg['To'] = to_email

#                     # Customize the email body with the colleague's name and tracking link
#                     body = email_template.replace("{{recipient_name}}", colleague.name)
#                     body = body.replace("{{action_link}}", tracking_link)
#                     body = body.replace("{{action_name}}", action_name)
#                     body = body.replace("{{email_subject}}", email_subject)

#                     html_content = f"""
#                     <html>
#                         <body>
#                             {body}
#                         </body>
#                     </html>
#                     """
#                     msg.attach(MIMEText(html_content, 'html'))

#                     try:
#                         server.send_message(msg)
#                         print(f"Email sent to {colleague.email}")

#                         # Log the sent email details
#                         update_email_log(colleague)

#                     except Exception as e:
#                         print(f"Failed to send email to {colleague.email}: {str(e)}")

#                 # Delay between batches to prevent overloading the CPU
#                 time.sleep(delay)

#                 # Log system usage and perform garbage collection
#                 cpu_usage, memory_usage = log_system_usage()
#                 if memory_usage > 80:  # If memory usage exceeds 80%, trigger garbage collection
#                     print("High memory usage, performing garbage collection.")
#                     gc.collect()

#     except Exception as e:
#         print(f"Error in connecting or sending emails: {str(e)}")

# # Email sending route
# @app.route('/send_email', methods=['GET', 'POST'])
# def send_email():
#     global emailed_candidates
#     emailed_candidates = []

#     templates_dir = os.path.join(os.path.dirname(__file__), 'templates')

#     # Define the range of colleagues for each group based on your specified ranges
#     group_ranges = [
#         (1, 8),    # Group 1 (First 400 colleagues)
#         (8, 14),  # Group 2 (Next 388 colleagues)
#         (14, 18),  # Group 3 (Next 14 colleagues)
#         (18, 20),  # Group 4 (Next 184 colleagues)
#         (20, 21)  # Group 5 (Remaining 14 colleagues)
#     ]

#     # Department configuration
#     department_config = {
#         'HR': {
#             'email': os.getenv('HR_EMAIL'),
#             'password': os.getenv('HR_PASSWORD'),
#             'template': 'hr_email_template.html',
#             'subject': "Update Your Payroll Information for Q4",
#             'action_name': "Update Payroll Information"
#         },
#         'Leadership': {
#             'email': os.getenv('LEADERSHIP_EMAIL'),
#             'password': os.getenv('LEADERSHIP_PASSWORD'),
#             'template': 'leadership_template.html',
#             'subject': "Strategic Plan Review for Q4 - Action Required",
#             'action_name': "Review Strategic Plan"
#         },
#         'Developer': {
#             'email': os.getenv('DEVELOPER_EMAIL'),
#             'password': os.getenv('DEVELOPER_PASSWORD'),
#             'template': 'developer_template.html',
#             'subject': "Security Patch Deployment for Development Tools",
#             'action_name': "Download Security Patch"
#         },
#         'Account': {
#             'email': os.getenv('ACCOUNT_EMAIL'),
#             'password': os.getenv('ACCOUNT_PASSWORD'),
#             'template': 'accounts_email_template.html',
#             'subject': "System Update for new Compliance Standards",
#             'action_name': "Update Credential"
#         }
#     }

#     try:
#         # Send emails for each group
#         send_group_email(group_ranges[0][0], group_ranges[0][1], department_config['Developer'], templates_dir)
#         send_group_email(group_ranges[1][0], group_ranges[1][1], department_config['Developer'], templates_dir)
#         send_group_email(group_ranges[2][0], group_ranges[2][1], department_config['HR'], templates_dir)
#         send_group_email(group_ranges[3][0], group_ranges[3][1], department_config['Account'], templates_dir)
#         send_group_email(group_ranges[4][0], group_ranges[4][1], department_config['Leadership'], templates_dir)

#         return jsonify({
#             'message': 'Emails sent to colleagues.',
#             'emailed_candidates': emailed_candidates
#         }), 200

#     except Exception as e:
#         return jsonify({'message': f'Error sending emails: {str(e)}'}), 500


# def update_email_log(colleague):
#     """Single function to update the record in the EmailLogs table."""
#     try:
#         # Create a new email log entry
#         email_log = EmailLogs(
#             colleague_id=colleague.id,
#             email_address=colleague.email
#         )
#         db.session.add(email_log)
#         db.session.commit()
#         print(f"Email log added for {colleague.name}")
#     except Exception as e:
#         db.session.rollback()
#         print(f"Failed to log email for {colleague.name}: {str(e)}")


def update_email_log(colleague):
    """Function to update the record in the EmailLogs table."""
    try:
        # Capture the current time for when the email is sent
        sent_date = datetime.utcnow()

        # Create a new email log entry with colleague's details and sent date
        email_log = EmailLogs(
            colleague_id=colleague.id,
            email_address=colleague.email,
            sent_date=sent_date  # Store the sent date
        )

        # Add to session and commit to save it in the database
        db.session.add(email_log)
        db.session.commit()
        print(f"Email log added for {colleague.name}")

    except Exception as e:
        db.session.rollback()
        print(f"Failed to log email for {colleague.name}: {str(e)}")


@app.route('/phishing_test/<int:colleague_id>', methods=['GET'])
def phishing_test(colleague_id):
    print(f'Phishing test accessed for colleague ID: {colleague_id}')

    colleague = Colleagues.query.get(colleague_id)
    if not colleague:
        return jsonify({'error': 'Colleague not found.'}), 404

    return jsonify({'message': 'Tracking link accessed successfully', 'colleague_id': colleague_id})


# @app.route('/generate_emailed_candidates_report', methods=['GET', 'POST'])
# def generate_emailed_candidates_report():
#     global emailed_candidates

#     if not emailed_candidates:
#         print("No candidates in emailed_candidates:",
#               emailed_candidates)
#         return jsonify({'error': 'No successfully emailed candidates.'}), 400

#     print("Generating CSV for:", emailed_candidates)

#     try:
#         csv_file_path = "emailed_candidates_report.csv"
#         with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
#             fieldnames = ['name', 'email', 'department',
#                           'designation', 'clicked_date']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#             writer.writeheader()
#             writer.writerows(emailed_candidates)

#         return send_file(csv_file_path, as_attachment=True)
#     except Exception as e:
#         print(f"Error generating report: {str(e)}")
#         return jsonify({'error': str(e)}), 500


@app.route('/generate_emailed_candidates_report', methods=['GET'])
def generate_emailed_candidates_report():
    try:
        # Fetch all email logs
        email_logs = EmailLogs.query.all()
        if not email_logs:
            return jsonify({'error': 'No candidates have been emailed yet.'}), 400

        # Prepare list of emailed candidates with additional fields
        emailed_candidates = []
        for log in email_logs:
            colleague = log.colleague  # Get colleague related to the log
            emailed_candidates.append({
                'name': colleague.name,  # Get colleague name
                'email': log.email_address,  # Get email from log
                'department': colleague.department,  # Get department from colleague model
                'designation': colleague.designation,  # Get designation from colleague model
                # Format sent date
                # 'sent_date': log.sent_date.strftime('%Y-%m-%d %H:%M:%S')
                'sent_date': log.sent_date.strftime('%Y-%m-%d')
            })

        # Generate CSV report
        csv_file_path = "emailed_candidates_report.csv"
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'email', 'department',
                          'designation', 'sent_date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(emailed_candidates)

        # Return the CSV file as download
        return send_file(csv_file_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/users')
def users():
    user = Colleagues.query.all()
    return jsonify([{'id': u.id, 'name': u.name, 'email': u.email, 'department': u.department, 'designation': u.designation} for u in user])


@app.route('/phising_click/<int:colleague_id>', methods=['POST'])
def phising_click(colleague_id):
    print(f'Received request for colleague ID: {colleague_id}')

    colleague = Colleagues.query.get(colleague_id)
    if not colleague:
        return jsonify({'error': 'Colleague not found.'}), 404

    report = Reports.query.filter_by(colleague_id=colleague_id).first()

    if report:
        report.clicked = True
        report.clicked_date = datetime.now()
        print(
            f"Updated clicked_date for existing report: {report.clicked_date}")

    else:
        report = Reports(
            colleague_id=colleague_id,
            clicked=True,
            clicked_date=datetime.now(),
            answered=False,
            answers={}
        )
        db.session.add(report)
        print(f"Created new report with clicked_date: {report.clicked_date}")

    db.session.commit()

    candidate_data = {
        'id': colleague.id,
        'name': colleague.name,
        'email': colleague.email,
        'department': colleague.department,
        'designation': colleague.designation
    }

    return jsonify({'message': 'Click recorded', 'candidate': candidate_data})


@app.route('/reports', methods=['GET'])
def get_reports():
    reports = Reports.query.all()
    report_data = [{'id': r.id, 'colleague_id': r.colleague_id, 'clicked': r.clicked,
                    'answered': r.answered, 'answers': r.answers, 'status': r.status, 'score': r.score, 'clicked_date': r.clicked_date} for r in reports]
    return jsonify(report_data)


@app.route('/phishing_opened/<int:colleague_id>', methods=['GET'])
def phishing_opened(colleague_id):
    report = Reports.query.filter_by(colleague_id=colleague_id).first()
    print(
        f'Processing click for colleague ID: {colleague_id} | Existing report: {report}')

    if report:
        report.clicked = True
        print(f'Updated existing report for ID {colleague_id} to clicked=True')
    else:
        report = Reports(colleague_id=colleague_id,
                         clicked=True, answered=False, answers={}, clicked_date=datetime.now())
        db.session.add(report)
        print(f'Created new report for ID {colleague_id} with clicked=True')

    db.session.commit()
    return jsonify({'message': 'Thank you for participating in our phishing awareness program.', 'showPopup': True})


@app.route('/generate_reports', methods=['GET', 'POST'])
def generate_reports():
    try:
        reports = Reports.query.all()
        report_data = []

        for report in reports:
            colleague = Colleagues.query.get(report.colleague_id)
            report_entry = {
                'Colleague Name': colleague.name,
                'Colleague Email': colleague.email,
                'Department': colleague.department,
                'Designation': colleague.designation,
                'Link Clicked': 'Yes' if report.clicked else 'No',
                'Score': report.score,
                'Status': report.status,
                'Completion Date': report.clicked_date.strftime('%Y-%m-%d') if report.clicked_date else None,
            }
            report_data.append(report_entry)

        csv_file_path = "candidate_reports.csv"
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Colleague Name', 'Colleague Email', 'Department',
                          'Designation', 'Link Clicked', 'Score',
                          'Status', 'Completion Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for data in report_data:
                writer.writerow(data)

        return send_file(csv_file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/upload_colleagues_data', methods=['POST'])
def upload_colleagues_data():
    try:
        db.session.query(Colleagues).delete()

        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
            for _, row in df.iterrows():
                colleague = Colleagues(
                    name=row['Full Name'],
                    email=row['Work Email'],
                    department=row['Department'],
                    designation=row['Job Title']
                )
                db.session.add(colleague)

            db.session.commit()
            return jsonify({'message': 'Data uploaded successfully'}), 200
        else:
            return jsonify({'message': 'Invalid file format. Please upload an .xlsx file.'}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error processing file: {str(e)}'}), 500


@app.route('/get_all_reports', methods=['GET'])
def get_all_reports():
    try:
        reports = Reports.query.all()
        report_data = [{'id': r.id, 'colleague_id': r.colleague_id, 'clicked': r.clicked,
                        'answered': r.answered, 'answers': r.answers, 'status': r.status, 'score': r.score, 'clicked_date': r.clicked_date} for r in reports]
        return jsonify({'reports': report_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/generate_dashboard_clicked_report', methods=['GET'])
def generate_dashboard_clicked_report():
    clicked_reports = Reports.query.filter_by(clicked=True).all()

    if not clicked_reports:
        return jsonify({'error': 'No candidates have clicked the link.'}), 400

    clicked_candidates = []
    for report in clicked_reports:
        colleague = report.colleague
        clicked_candidates.append({
            'name': colleague.name,
            'email': colleague.email,
            'department': colleague.department,
            'designation': colleague.designation,
            'clicked_date': report.clicked_date.strftime('%Y-%m-%d') if report.clicked_date else None
        })

    try:
        csv_file_path = "dashboard_clicked_candidates_report.csv"
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'email', 'department',
                          'designation', 'clicked_date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(clicked_candidates)

        return send_file(csv_file_path, as_attachment=True)

    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

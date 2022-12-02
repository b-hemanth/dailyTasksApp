import flask
from flask import request, jsonify, Flask, render_template, flash, redirect, url_for, session, logging
from flask_cors import CORS
import json
import os
import sys
import time
import datetime
import requests
import pandas as pd

app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# read db from csv, creating it if it doesn't exist
def read_db():
	if not os.path.exists('db.csv'):
		# create db with projectName, projectType, taskType, expectedHours, dueDate columns
		db = pd.DataFrame(columns=['projectName', 'projectType', 'taskType', 'expectedHours', 'dueDate'])
		db.to_csv('db.csv', index=False)
	else:
		db = pd.read_csv('db.csv')
	return db

# route to run before the first request
@app.before_first_request
def before_first_request():
	global db
	db = read_db()

# route to run once a day
@app.before_request
def before_request():
	# check if timer.txt is today
	if not os.path.exists('timer.txt'):
		with open('timer.txt', 'w') as f:
			f.write('0')
	with open('timer.txt', 'r') as f:
		timer = f.read()
	if timer != str(datetime.datetime.now().date()):
		# reset timer.txt
		with open('timer.txt', 'w') as f:
			f.write(str(datetime.datetime.now().date()))
		# reset db.csv
		global db
		db = pd.read_csv('db.csv')
		# calculate hours to allocate
		today = split_hours_day(db, 8)
		# subtract the hours allocated from the expected hours in db
		db['expectedHours'] = db['expectedHours'] - today['hoursAllocated']
		# round to integer
		db['expectedHours'] = db['expectedHours'].round(0)
		# remove any less than 1e-10
		db['expectedHours'] = db['expectedHours'].apply(lambda x: 0 if x < 1e-10 else x)
		# remove 0s
		db = db[db['expectedHours'] != 0]
		db.to_csv('db.csv', index=False)

def split_hours_day(db, max_hours):
	today = db
	today['daysLeft'] = (pd.to_datetime(today['dueDate']) - pd.to_datetime(datetime.datetime.now().date())).dt.days
    # Weights of tasks based on each project's expectedHours and daysLeft
	today['weight'] = today['expectedHours'] / today['daysLeft']
	total_weight = today['weight'].sum()
	today['weight'] = today['weight'] / total_weight
	# Multiply by max hours
	today['hoursAllocated'] = today['weight'] * max_hours
	today['minutesAllocated'] = today['hoursAllocated'] * 60	
	# round everything to 2 decimal places
	today = today.round(2)
	return today
	

from wtforms import StringField, SubmitField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf import FlaskForm

class TaskForm(FlaskForm):
	projectName = StringField('Project Name', validators=[DataRequired(), Length(min=2, max=20)])
	projectType = StringField('Project Type', validators=[DataRequired(), Length(min=2, max=20)])
	taskType = StringField('Task Type', validators=[DataRequired(), Length(min=2, max=20)])
	expectedHours = IntegerField('Expected Hours', validators=[DataRequired(), NumberRange(min=1, max=100)])
	dueDate = DateField('Due Date', validators=[DataRequired()])
	submit = SubmitField('Add Task')

@app.route('/', methods=['GET', 'POST'])
def home():
	# redirect to the today page
	return flask.redirect('/today')


@app.route('/submit', methods=['POST'])
def submit():
	form = TaskForm()
	if form.validate_on_submit():
		# add to db
		global db
		# check if projectName exists in db already
		db = pd.read_csv('db.csv')
		if form.projectName.data in db['projectName'].values:
			# update the row
			db.loc[db['projectName'] == form.projectName.data, 'projectType'] = form.projectType.data
			db.loc[db['projectName'] == form.projectName.data, 'taskType'] = form.taskType.data
			db.loc[db['projectName'] == form.projectName.data, 'expectedHours'] = form.expectedHours.data
			db.loc[db['projectName'] == form.projectName.data, 'dueDate'] = form.dueDate.data
		else:
			# add a new row
			new_row = pd.DataFrame({'projectName': [form.projectName.data], 'projectType': [form.projectType.data], 'taskType': [form.taskType.data], 'expectedHours': [form.expectedHours.data], 'dueDate': [form.dueDate.data]})
			db = db.append(new_row, ignore_index=True)
			for rows in db.iterrows():
				flash(rows)
		# save to db
		db.to_csv('db.csv', index=False)
		flash('Task added, sucker!!', 'success')
		return redirect(url_for('today'))
	else:
		flash('Form not valid!', 'danger')
		return redirect(url_for('add_edit'))

@app.route('/add_edit', methods=['GET', 'POST'])
def add_edit():	
	form = TaskForm()
	return render_template('add_edit.html', form=form)


@app.route('/today', methods=['GET'])
def today():
	db = pd.read_csv('db.csv')
	# get the max hours from the request
	max_hours = request.args.get('max_hours')
	if max_hours is None:
		max_hours = 3
	
	# calculate hours to allocate
	today = split_hours_day(db, int(max_hours))
	# sort by due date
	today = today.sort_values(by=['dueDate'])
	# send to today.html
	return render_template('today.html', today=today)

@app.route('/myTasks', methods=['GET'])
def myTasks():
	return render_template('currentTasks.html', title='Current Tasks', tasks=db)

# run the app with debug mode
if __name__ == '__main__':
	app.run(debug=True)
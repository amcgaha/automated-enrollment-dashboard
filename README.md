# Automated Enrollment Dashboard
A summer camp wants to know how many campers have applied so far this year. After creating a historical model for comparison, I built an a dashboard with Google Sheets that shows how many cumulative applications have been submitted each day. The data is [automatatically updated using this Python script](https://github.com/amcgaha/automated-enrollment-dashboard/blob/main/auto_enrollment_dashboard.py). 

This image shows an example of one of the dashboard views. Other views include different performance indicators and a forecast based on the historical model.

![Image](https://github.com/amcgaha/automated-enrollment-dashboard/blob/main/images/dashboard_preview.png)

## Context
In the summer camp industry, a key performance indicator is the number of camper applications received so far.

## Business Problem
The leadership of a summer camp wants to know how well their sessions are filling for the summer. However, their data management system doesn’t make this clear. We’d like some more accurate and readable plots. This dashboard answers the question: How many applications have we received for each session, and how typical is that pattern so far?

## Data
Using Python, I transformed cluttered camp records into a clean table that reveals the distribution of applications across each year. I then calculated summary statistics to create a historical model of our application pattern.

## Product
After completing the historical model, I set up a dashboard on Google Sheets that compares current application numbers to the model and visualizes them in a number of charts. Finally, I wrote a script in Python that automatically updates the dashboard with the latest data.

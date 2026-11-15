Aviral Handa

https://youtu.be/sWTIYGg516U

## Project Structure
```text
question-1/
├── db/
│   └── schema_and_seed.sql    # creates the students table and adds 3 students
├── src/
│   ├── app.py                 # Flask backend with the CRUD functions
│   ├── setup_db.py            # creates the database/table if they're missing
│   ├── static/
│   │   └── app.js             # frontend JavaScript (uses fetch)
│   └── templates/
│       └── index.html         # the HTML page
├── requirements.txt
└── README.md
```

## What you need
- Python 3
- PostgreSQL
- pgAdmin or DataGrip if you want to look at the database (I used DataGrip)

## How to run it

1. Make sure PostgreSQL is running first. If it isn't, the page will show a "Connection refused" error on port 5432.

2. Install the packages from the project folder:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. The app connects to a database called `university_db` on localhost:5432 with user `postgres` and password `root`. If your password is different, change it in `DB_CONFIG` at the top of `src/app.py`.

4. Start the app:
   ```bash
   python3 src/app.py
   ```
   Then go to http://127.0.0.1:5001 in your browser. Leave the terminal open while you use it.

You don't have to create the database yourself. When the app starts it runs `setup_db.py`, which creates `university_db` and runs `db/schema_and_seed.sql` if the table isn't there yet. If you'd rather do it by hand, create `university_db` in pgAdmin or DataGrip and run the SQL file on it. In DataGrip, make sure the data source is PostgreSQL and not MySQL.

I'm using port 5001 instead of 5000 because on a Mac, port 5000 is taken by AirPlay and just gives a blank 403 page.

## CRUD functions (in `src/app.py`)
- `getAllStudents()` - gets all students from the table, ordered by student_id
- `addStudent(first_name, last_name, email, enrollment_date)` - adds a new student
- `updateStudentEmail(student_id, new_email)` - changes a student's email
- `deleteStudent(student_id)` - deletes a student by their id

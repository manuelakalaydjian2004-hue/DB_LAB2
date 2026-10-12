1. Team Members
Name: Manuela Kalaydjian id 2304053
Name: Sandra Rafik Tobia id 2304045

2. Technology Stack
Back End: Python (Flask)
Front End: HTML, CSS
Database: MySQL

3. How to Run
Install Python and MySQL on your machine.
Run the database script in MySQL Workbench: database/schema.sql
Copy .env.example to .env and fill in your real MySQL password and a secret key.
Install Python libraries: pip install flask pymysql bcrypt python-dotenv
Start the server: py app.py
Open your browser and go to: http://localhost:5000


4. Features Built
R1: Register with name, email, password, confirm password.....Duplicate emails show Email Already Exists Auto-login after register

R2: Login with email/password. Wrong credentials show Invalid email or password Logout works

R3: The to-do list is private. Redirects to login if not logged in. Users only see their own tasks

R4: Add a to-do

R5: Edit a to-do title

R6: Mark a to-do done or not done

R7: Delete a to-do with confirmation

R8: Server-side validation for all forms with exact messages

R9: Passwords stored as bcrypt hashes. All SQL uses parameterized queries (%s). user_id taken from session only
R10: Clean, consistent UI with CSS

5. Screenshots
Register page with error messages
Login page
To-Do list with some items one done, one not done

6. Database Questions
(a) Why do UPDATE and DELETE contain AND user_id = ?, and what changes if you remove it?

3ashan security... law shelnaha ay user ydar yb3t id bta3 task bta3 7ad tany w yms7ha w y3mlha edit  b "AND user_id = " bt2aked eno el query ht3ml edit bs 3la tasks bto3o howa bs

(b) What happens if you insert a to-do for a user_id that does not exist, and which constraint of the lecture is that?

MySQL hyrg3 error (Foreign Key Constraint)  w da esmo Referential Integrity y3ni msh mknoosh yb2a fe to-do mn 8eer user asly mawgood

(c) Why do you store a hash and not the password?

3ashan security bardo... law el database ethackaret el hacker msh hy2dar y3rf el passwords 3ashan el hash one-way w salted law 7attena el password 3ady el hacker hy3rfha w yd5ol biha 3la kol 7ad.

(d) The name column is NOT NULL: why did you still need your own check for an empty name?

3ashan NOT NULL btd3mn eno el value msh "NULL" bs el empty string '' (y3ni fady) msh NULL da value 3ady w MySQL by2blo 3ashan kda lazm n3ml check bl Python (application-level) nrfod el empty names
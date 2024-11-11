from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mohith123'

def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',      # Update with your MySQL host
        user='root',  # Update with your MySQL username
        password='mohith123',  # Update with your MySQL password
        database='banking_db'     # Update with your MySQL database name
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM Users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if user:
            cursor.close()
            conn.close()
            return "Username already exists, please choose another one."
        
        cursor.execute(
            'INSERT INTO Users (username, password, email) VALUES (%s, %s, %s)',
            (username, password, email)
        )
        conn.commit()
        
        
        user_id = cursor.lastrowid
        
        cursor.execute(
            'INSERT INTO Accounts (user_id, balance) VALUES (%s, %s)', 
            (user_id, 0.0)
        )
        conn.commit()
        
        print(f"User {username} registered with user_id {user_id} and account created.")
        
        cursor.close()
        conn.close()
        
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM Users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            print(f"User found: {user}")
        else:
            print("No user found with that username.")
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            print("Login successful")
            return redirect(url_for('dashboard'))
        else:
            print("Login failed: Incorrect username or password")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT username FROM Users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()

    cursor.execute('SELECT * FROM Accounts WHERE user_id = %s', (session['user_id'],))
    user_account = cursor.fetchone()

    if user_account:
        cursor.execute('SELECT * FROM Transactions WHERE account_id = %s ORDER BY date DESC', (user_account['id'],))
        transactions = cursor.fetchall()
    else:
        transactions = []
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', username=user['username'], account=user_account, transactions=transactions)



@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT username FROM Users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if request.method == 'POST':
        amount = float(request.form['amount'])
        transaction_type = request.form['transaction_type']
        recipient_account_id = request.form.get('recipient_account_id') 
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        
        cursor.execute('SELECT * FROM Accounts WHERE user_id = %s', (session['user_id'],))
        sender_account = cursor.fetchone()
        
        if sender_account is None:
            cursor.close()
            conn.close()
            return "No account found for the user."
        
        if transaction_type == 'deposit':
            
            new_balance = sender_account['balance'] + amount
            cursor.execute('UPDATE Accounts SET balance = %s WHERE id = %s', (new_balance, sender_account['id']))
            
            
            cursor.execute(
                'INSERT INTO Transactions (account_id, type, amount, date) VALUES (%s, %s, %s, %s)',
                (sender_account['id'], 'deposit', amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
        
        elif transaction_type == 'withdraw':
            
            if sender_account['balance'] >= amount:
                new_balance = sender_account['balance'] - amount
                cursor.execute('UPDATE Accounts SET balance = %s WHERE id = %s', (new_balance, sender_account['id']))
                
                
                cursor.execute(
                    'INSERT INTO Transactions (account_id, type, amount, date) VALUES (%s, %s, %s, %s)',
                    (sender_account['id'], 'withdraw', amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                )
            else:
                cursor.close()
                conn.close()
                return "Insufficient funds."
        
        elif transaction_type == 'transfer' and recipient_account_id:
            
            recipient_account_id = int(recipient_account_id)
            
            
            if sender_account['balance'] >= amount:
               
                cursor.execute('SELECT * FROM Accounts WHERE id = %s', (recipient_account_id,))
                recipient_account = cursor.fetchone()
                
                if recipient_account:
                    
                    new_sender_balance = sender_account['balance'] - amount
                    cursor.execute('UPDATE Accounts SET balance = %s WHERE id = %s', (new_sender_balance, sender_account['id']))
                    
                    
                    new_recipient_balance = recipient_account['balance'] + amount
                    cursor.execute('UPDATE Accounts SET balance = %s WHERE id = %s', (new_recipient_balance, recipient_account['id']))
                    
                    
                    cursor.execute(
                        'INSERT INTO Transactions (account_id, type, amount, date) VALUES (%s, %s, %s, %s)',
                        (sender_account['id'], 'transfer_out', amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    )
                    cursor.execute(
                        'INSERT INTO Transactions (account_id, type, amount, date) VALUES (%s, %s, %s, %s)',
                        (recipient_account['id'], 'transfer_in', amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    )
                else:
                    cursor.close()
                    conn.close()
                    return "Recipient account not found."
            else:
                cursor.close()
                conn.close()
                return "Insufficient funds for transfer."
                

        else:
            cursor.close()
            conn.close()
            return "Invalid transaction type or missing recipient for transfer."
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('dashboard'))

    return render_template('transaction.html', username=user['username'])


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

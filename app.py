import os
import sqlite3
from datetime import date, datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'habits.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')


def get_db_connection():
    conn=sqlite3.connect(DATABASE_PATH)
    conn.row_factory=sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    if os.path.exists(DATABASE_PATH):
        return
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql=f.read()
    conn=get_db_connection()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()


def calculate_streak(habit_id):
    conn=get_db_connection()
    rows=conn.execute(
        'SELECT completed_date FROM completions '
        'WHERE habit_id = ? ORDER BY completed_date DESC',
        (habit_id,)
    ).fetchall()
    conn.close()
    if not rows:
        return 0
    dates=[datetime.strptime(r['completed_date'], '%Y-%m-%d').date() for r in rows]
    today = date.today()
    yesterday=today - timedelta(days=1)
    if dates[0]!=today and dates[0]!=yesterday:
        return 0
    streak=1
    for i in range(1, len(dates)):
        if dates[i]==dates[i-1]-timedelta(days=1):
            streak+=1
        else:
            break
    return streak


def get_flower_stage(streak):
    if streak == 0:
        return '🌰'
    elif streak <=2:
        return '🌱'
    elif streak <=5:
        return '🌿'
    elif streak <=10:
        return '🌸'
    else:
        return '🌻'


def is_completed_today(habit_id):
    today_str=date.today().isoformat()
    conn=get_db_connection()
    row=conn.execute(
        'SELECT 1 FROM completions WHERE habit_id = ? AND completed_date = ?',
        (habit_id, today_str)
    ).fetchone()
    conn.close()
    return row is not None


def count_completions(habit_id):
    conn=get_db_connection()
    row=conn.execute(
        'SELECT COUNT(*) AS total FROM completions WHERE habit_id = ?',
        (habit_id,)
    ).fetchone()
    conn.close()
    return row['total']


@app.route('/')
def index():
    conn=get_db_connection()
    habits_rows=conn.execute(
        'SELECT id, title, created_at FROM habits ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    habits = []
    for h in habits_rows:
        streak = calculate_streak(h['id'])
        habits.append({
            'id': h['id'],
            'title': h['title'],
            'created_at': h['created_at'],
            'streak': streak,
            'total': count_completions(h['id']),
            'flower': get_flower_stage(streak),
            'done_today': is_completed_today(h['id']),
        })
    habits.sort(key=lambda x: x['done_today'])
    return render_template('index.html', habits=habits)


@app.route('/add', methods=['GET', 'POST'])
def add_habit():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if title:
            created_at = date.today().isoformat()
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO habits (title, created_at) VALUES (?, ?)',
                (title, created_at)
            )
            conn.commit()
            conn.close()

        return redirect(url_for('index'))
    return render_template('add_habit.html')


@app.route('/complete/<int:habit_id>', methods=['POST'])
def complete_habit(habit_id):
    today_str = date.today().isoformat()
    conn = get_db_connection()
    conn.execute(
        'INSERT OR IGNORE INTO completions (habit_id, completed_date) VALUES (?, ?)',
        (habit_id, today_str)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/delete/<int:habit_id>', methods=['POST'])
def delete_habit(habit_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM completions WHERE habit_id = ?', (habit_id,))
    conn.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/stats')
def stats():
    conn = get_db_connection()
    habits_rows = conn.execute(
        'SELECT id, title, created_at FROM habits ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    habits = []
    best_streak = 0
    total_completions = 0

    for h in habits_rows:
        streak = calculate_streak(h['id'])
        total = count_completions(h['id'])
        habits.append({
            'id': h['id'],
            'title': h['title'],
            'created_at': h['created_at'],
            'streak': streak,
            'total': total,
            'flower': get_flower_stage(streak),
            'done_today': is_completed_today(h['id']),
        })
        total_completions += total
        if streak>best_streak:
            best_streak = streak
    summary = {
        'habits_count': len(habits),
        'total_completions': total_completions,
        'best_streak': best_streak,
    }
    return render_template('stats.html', habits=habits, summary=summary)



if __name__ == '__main__':
    init_db()
    app.run()

#!/usr/bin/env python3
"""
VulnShop — Intentionally Vulnerable Demo App
SecureScope Demo Target | Port: 8888
INTENTIONALLY VULNERABLE — for demo/testing only. Never deploy publicly.

Vulnerable endpoints:
  GET /search?q=           → Reflected XSS
  GET /product?id=         → SQL Injection (error-based)
  GET /category?name=      → SQL Injection (union-based)
  GET /user?id=            → SQL Injection (boolean-blind)
  GET /review?post_id=     → Stored XSS pattern
  GET /profile?username=   → SQL Injection (time-based)
  POST /login              → No rate limiting, verbose errors
"""

import sqlite3
import time
from flask import Flask, request, Response, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DB = '/tmp/vulnshop.db'


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT,
            password TEXT,
            role TEXT
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL,
            description TEXT
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            post_id INTEGER,
            author TEXT,
            content TEXT
        );
        DELETE FROM users;
        DELETE FROM products;
        DELETE FROM reviews;
    ''')
    c.executemany("INSERT INTO users VALUES (?,?,?,?,?)", [
        (1, 'admin',   'admin@vulnshop.com',   'admin123',    'admin'),
        (2, 'alice',   'alice@vulnshop.com',   'alice456',    'user'),
        (3, 'bob',     'bob@vulnshop.com',     'bob789',      'user'),
        (4, 'charlie', 'charlie@vulnshop.com', 'charlie000',  'user'),
    ])
    c.executemany("INSERT INTO products VALUES (?,?,?,?,?)", [
        (1, 'MacBook Pro',    'laptops',     1299.99, 'Apple M3 chip, 16GB RAM'),
        (2, 'Dell XPS 15',    'laptops',      999.99, 'Intel i7, 32GB RAM'),
        (3, 'iPhone 15 Pro',  'phones',       999.99, 'A17 Pro chip, 256GB'),
        (4, 'Samsung S24',    'phones',       799.99, 'Snapdragon 8 Gen 3'),
        (5, 'Sony WH-1000XM5','headphones',   349.99, 'Industry-leading ANC'),
        (6, 'AirPods Pro',    'headphones',   249.99, 'Active noise cancellation'),
        (7, 'iPad Air',       'tablets',      599.99, 'M2 chip, 10.9 inch'),
        (8, 'Surface Pro 9',  'tablets',      999.99, 'Intel Core i5, 8GB RAM'),
    ])
    c.executemany("INSERT INTO reviews VALUES (?,?,?,?)", [
        (1, 1, 'alice',   'Great laptop, very fast!'),
        (2, 1, 'bob',     'Worth every penny.'),
        (3, 3, 'charlie', 'Best phone I have ever used.'),
    ])
    conn.commit()
    conn.close()


CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; color: #1a1a1a; }
header { background: #1a1a2e; color: white; padding: 0 40px; height: 60px; display: flex; align-items: center; justify-content: space-between; }
header .logo { font-size: 20px; font-weight: 700; color: #e94560; letter-spacing: -0.5px; }
header nav a { color: #ccc; text-decoration: none; margin-left: 24px; font-size: 14px; }
header nav a:hover { color: white; }
.container { max-width: 1100px; margin: 0 auto; padding: 32px 20px; }
.hero { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 60px 40px; text-align: center; }
.hero h1 { font-size: 36px; font-weight: 800; margin-bottom: 12px; }
.hero p { color: #aaa; font-size: 16px; margin-bottom: 28px; }
.search-bar { display: flex; gap: 8px; max-width: 500px; margin: 0 auto; }
.search-bar input { flex: 1; padding: 12px 16px; border-radius: 8px; border: none; font-size: 14px; outline: none; }
.search-bar button { padding: 12px 24px; background: #e94560; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 14px; }
.section-title { font-size: 20px; font-weight: 700; margin-bottom: 20px; color: #1a1a1a; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
.card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.card h3 { font-size: 15px; font-weight: 600; margin-bottom: 6px; }
.card .price { color: #e94560; font-weight: 700; font-size: 18px; margin-bottom: 8px; }
.card .desc { color: #666; font-size: 13px; margin-bottom: 12px; }
.card a { display: inline-block; padding: 8px 16px; background: #1a1a2e; color: white; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 500; }
.card a:hover { background: #e94560; }
.cats { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 28px; }
.cat-btn { padding: 8px 18px; border-radius: 20px; background: white; border: 1px solid #ddd; text-decoration: none; color: #333; font-size: 13px; font-weight: 500; }
.cat-btn:hover, .cat-btn.active { background: #1a1a2e; color: white; border-color: #1a1a2e; }
.result-box { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-top: 20px; }
.result-box h2 { font-size: 18px; font-weight: 700; margin-bottom: 16px; }
table { width: 100%; border-collapse: collapse; }
th { background: #f8f8f8; padding: 10px 14px; text-align: left; font-size: 13px; color: #666; font-weight: 600; border-bottom: 1px solid #eee; }
td { padding: 10px 14px; font-size: 14px; border-bottom: 1px solid #f0f0f0; }
tr:last-child td { border-bottom: none; }
.error-box { background: #fff5f5; border: 1px solid #fecaca; border-radius: 8px; padding: 16px; margin-top: 16px; font-family: monospace; font-size: 12px; color: #dc2626; white-space: pre-wrap; word-break: break-all; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; color: #555; margin-bottom: 6px; }
.form-group input { width: 100%; padding: 10px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; }
.form-group input:focus { border-color: #1a1a2e; }
.btn { padding: 10px 24px; background: #1a1a2e; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 14px; }
.btn:hover { background: #e94560; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-admin { background: #fef3c7; color: #92400e; }
.badge-user  { background: #dbeafe; color: #1e40af; }
.warning-bar { background: #fef3c7; border: 1px solid #fcd34d; padding: 10px 16px; border-radius: 8px; font-size: 12px; color: #92400e; margin-bottom: 20px; }
footer { background: #1a1a2e; color: #666; text-align: center; padding: 24px; font-size: 13px; margin-top: 60px; }
"""

def page(title, body, active_nav=''):
    nav_links = [
        ('/', 'Home'), ('/category?name=laptops', 'Laptops'),
        ('/category?name=phones', 'Phones'), ('/category?name=headphones', 'Headphones'),
        ('/search?q=', 'Search'), ('/login', 'Login'),
    ]
    nav_html = ''.join(
        f'<a href="{href}" {"style=color:white;font-weight:600" if href == active_nav else ""}>{label}</a>'
        for href, label in nav_links
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — VulnShop</title>
  <style>{CSS}</style>
</head>
<body>
  <header>
    <div class="logo">🛒 VulnShop</div>
    <nav>{nav_html}</nav>
  </header>
  {body}
  <footer>VulnShop Demo © 2024 — Intentionally Vulnerable Application for SecureScope Demo</footer>
</body>
</html>"""


@app.route('/')
def index():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, name, price, description FROM products LIMIT 8")
    products = c.fetchall()
    conn.close()

    cards = ''.join(f"""
        <div class="card">
          <h3>{p[1]}</h3>
          <div class="price">${p[2]:.2f}</div>
          <div class="desc">{p[3]}</div>
          <a href="/product?id={p[0]}">View Details</a>
        </div>""" for p in products)

    body = f"""
    <div class="hero">
      <h1>Welcome to VulnShop</h1>
      <p>Find the best deals on electronics, phones, and more.</p>
      <form class="search-bar" method="get" action="/search">
        <input type="text" name="q" placeholder="Search products...">
        <button type="submit">Search</button>
      </form>
    </div>
    <div class="container">
      <div class="warning-bar">⚠️ This is an intentionally vulnerable demo application for SecureScope security testing.</div>
      <div class="cats">
        <a href="/category?name=laptops"    class="cat-btn">💻 Laptops</a>
        <a href="/category?name=phones"     class="cat-btn">📱 Phones</a>
        <a href="/category?name=headphones" class="cat-btn">🎧 Headphones</a>
        <a href="/category?name=tablets"    class="cat-btn">📟 Tablets</a>
      </div>
      <p class="section-title">Featured Products</p>
      <div class="grid">{cards}</div>
    </div>"""
    return page('Home', body, '/')


@app.route('/search')
def search():
    """VULNERABLE: Reflected XSS — q echoed without encoding"""
    q = request.args.get('q', '')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("SELECT id, name, price, description FROM products WHERE name LIKE ?", (f'%{q}%',))
        results = c.fetchall()
    except Exception:
        results = []
    conn.close()

    cards = ''.join(f"""
        <div class="card">
          <h3>{p[1]}</h3>
          <div class="price">${p[2]:.2f}</div>
          <div class="desc">{p[3]}</div>
          <a href="/product?id={p[0]}">View</a>
        </div>""" for p in results) if results else '<p style="color:#666">No products found.</p>'

    # VULNERABLE: q injected directly into HTML without escaping
    body = f"""
    <div class="container">
      <form class="search-bar" method="get" action="/search" style="margin-bottom:24px;max-width:100%">
        <input type="text" name="q" value="{q}" placeholder="Search products...">
        <button type="submit">Search</button>
      </form>
      <div class="result-box">
        <h2>Search results for: {q}</h2>
        <div class="grid" style="margin-top:16px">{cards}</div>
      </div>
    </div>"""
    return Response(page('Search', body, '/search?q='), mimetype='text/html')


@app.route('/product')
def product():
    """VULNERABLE: SQL Injection error-based — id concatenated directly"""
    pid = request.args.get('id', '1')
    body = f"""
    <div class="container">
      <div class="result-box">
        <h2>Product Details</h2>"""
    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        # VULNERABLE: direct concatenation
        query = f"SELECT id, name, category, price, description FROM products WHERE id = {pid}"
        c.execute(query)
        row = c.fetchone()
        conn.close()
        if row:
            body += f"""
            <table>
              <tr><th>ID</th><th>Name</th><th>Category</th><th>Price</th><th>Description</th></tr>
              <tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>${row[3]:.2f}</td><td>{row[4]}</td></tr>
            </table>
            <div style="margin-top:20px">
              <a href="/review?post_id={row[0]}" class="cat-btn">View Reviews</a>
            </div>"""
        else:
            body += '<p style="color:#666">Product not found.</p>'
    except Exception as e:
        # VULNERABLE: exposes SQL error and query
        body += f'<div class="error-box">OperationalError: {str(e)}\nQuery: {query}</div>'
    body += '</div></div>'
    return page('Product', body)


@app.route('/category')
def category():
    """VULNERABLE: SQL Injection union-based — name concatenated directly"""
    name = request.args.get('name', 'laptops')
    body = f"""
    <div class="container">
      <div class="cats">
        <a href="/category?name=laptops"    class="cat-btn {'active' if name=='laptops' else ''}">💻 Laptops</a>
        <a href="/category?name=phones"     class="cat-btn {'active' if name=='phones' else ''}">📱 Phones</a>
        <a href="/category?name=headphones" class="cat-btn {'active' if name=='headphones' else ''}">🎧 Headphones</a>
        <a href="/category?name=tablets"    class="cat-btn {'active' if name=='tablets' else ''}">📟 Tablets</a>
      </div>
      <div class="result-box">
        <h2>Category: {name}</h2>"""
    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        # VULNERABLE: direct concatenation
        query = f"SELECT id, name, price, description FROM products WHERE category = '{name}'"
        c.execute(query)
        rows = c.fetchall()
        conn.close()
        if rows:
            body += '<div class="grid" style="margin-top:16px">'
            for p in rows:
                body += f"""<div class="card">
                  <h3>{p[1]}</h3>
                  <div class="price">${p[2]:.2f}</div>
                  <div class="desc">{p[3]}</div>
                  <a href="/product?id={p[0]}">View Details</a>
                </div>"""
            body += '</div>'
        else:
            body += '<p style="color:#666;margin-top:16px">No products in this category.</p>'
    except Exception as e:
        body += f'<div class="error-box">OperationalError: {str(e)}\nQuery: {query}</div>'
    body += '</div></div>'
    return page(f'Category: {name}', body)


@app.route('/user')
def user():
    """VULNERABLE: SQL Injection boolean-blind — id concatenated directly"""
    uid = request.args.get('id', '1')
    body = f"""
    <div class="container">
      <div class="result-box">
        <h2>User Profile</h2>
        <form method="get" action="/user" style="margin-bottom:16px;display:flex;gap:8px">
          <input type="text" name="id" value="{uid}" placeholder="User ID" style="padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px">
          <button type="submit" class="btn">Lookup</button>
        </form>"""
    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        # VULNERABLE: direct concatenation
        query = f"SELECT id, username, email, role FROM users WHERE id = {uid}"
        c.execute(query)
        rows = c.fetchall()
        conn.close()
        if rows:
            body += '<table><tr><th>ID</th><th>Username</th><th>Email</th><th>Role</th></tr>'
            for r in rows:
                badge = f'<span class="badge badge-{"admin" if r[3]=="admin" else "user"}">{r[3]}</span>'
                body += f'<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{badge}</td></tr>'
            body += '</table>'
        else:
            body += '<p style="color:#666">No user found.</p>'
    except Exception as e:
        body += f'<div class="error-box">OperationalError: {str(e)}\nQuery: SELECT * FROM users WHERE id = {uid}</div>'
    body += '</div></div>'
    return page('User Profile', body)


@app.route('/review')
def review():
    """VULNERABLE: Stored XSS pattern — content stored and rendered unescaped"""
    post_id = request.args.get('post_id', '1')
    body = f"""
    <div class="container">
      <div class="result-box">
        <h2>Product Reviews</h2>"""
    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT author, content FROM reviews WHERE post_id = ?", (post_id,))
        rows = c.fetchall()
        conn.close()
        if rows:
            body += '<div style="display:flex;flex-direction:column;gap:12px;margin-top:8px">'
            for r in rows:
                # VULNERABLE: content rendered without escaping
                body += f"""<div style="background:#f8f8f8;padding:14px;border-radius:8px">
                  <strong style="font-size:13px">{r[0]}</strong>
                  <p style="margin-top:6px;font-size:14px;color:#444">{r[1]}</p>
                </div>"""
            body += '</div>'
        else:
            body += '<p style="color:#666">No reviews yet.</p>'
    except Exception as e:
        body += f'<div class="error-box">Error: {str(e)}</div>'
    body += '</div></div>'
    return Response(page('Reviews', body), mimetype='text/html')


@app.route('/profile')
def profile():
    """VULNERABLE: SQL Injection time-based — username concatenated directly"""
    username = request.args.get('username', 'alice')
    body = f"""
    <div class="container">
      <div class="result-box">
        <h2>User Profile Search</h2>
        <form method="get" action="/profile" style="margin-bottom:16px;display:flex;gap:8px">
          <input type="text" name="username" value="{username}" placeholder="Username" style="padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px">
          <button type="submit" class="btn">Search</button>
        </form>"""
    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        # VULNERABLE: direct concatenation — time-based SQLi possible
        query = f"SELECT id, username, email, role FROM users WHERE username = '{username}'"
        c.execute(query)
        rows = c.fetchall()
        conn.close()
        if rows:
            body += '<table><tr><th>ID</th><th>Username</th><th>Email</th><th>Role</th></tr>'
            for r in rows:
                badge = f'<span class="badge badge-{"admin" if r[3]=="admin" else "user"}">{r[3]}</span>'
                body += f'<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{badge}</td></tr>'
            body += '</table>'
        else:
            body += '<p style="color:#666">No user found.</p>'
    except Exception as e:
        body += f'<div class="error-box">OperationalError: {str(e)}\nQuery: {query}</div>'
    body += '</div></div>'
    return page('Profile Search', body)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """VULNERABLE: verbose error messages, no rate limiting"""
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        try:
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", (username, password))
            user = c.fetchone()
            conn.close()
            if user:
                error = f'✓ Login successful! Welcome {user[1]} ({user[2]})'
            else:
                # VULNERABLE: reveals whether username exists
                conn2 = sqlite3.connect(DB)
                c2 = conn2.cursor()
                c2.execute("SELECT id FROM users WHERE username = ?", (username,))
                exists = c2.fetchone()
                conn2.close()
                if exists:
                    error = '✗ Incorrect password for this account.'
                else:
                    error = f'✗ No account found with username "{username}".'
        except Exception as e:
            error = f'Database error: {str(e)}'

    color = '#16a34a' if error.startswith('✓') else '#dc2626'
    body = f"""
    <div class="container" style="max-width:420px">
      <div class="result-box">
        <h2 style="margin-bottom:20px">Login</h2>
        {'<p style="color:' + color + ';font-size:13px;margin-bottom:16px;padding:10px;background:#f8f8f8;border-radius:6px">' + error + '</p>' if error else ''}
        <form method="post" action="/login">
          <div class="form-group">
            <label>Username</label>
            <input type="text" name="username" placeholder="Enter username" autocomplete="off">
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" name="password" placeholder="Enter password">
          </div>
          <button type="submit" class="btn" style="width:100%">Login</button>
        </form>
        <p style="margin-top:16px;font-size:12px;color:#999">
          Demo accounts: admin/admin123 · alice/alice456 · bob/bob789
        </p>
      </div>
    </div>"""
    return page('Login', body, '/login')


@app.route('/health')
def health():
    from flask import jsonify
    return jsonify({'status': 'healthy', 'service': 'VulnShop', 'port': 8888})


if __name__ == '__main__':
    init_db()
    print("\n" + "="*55)
    print("🛒  VULNSHOP — SecureScope Demo Target")
    print("="*55)
    print("📍  http://localhost:8888")
    print("⚠️   INTENTIONALLY VULNERABLE — demo only")
    print("="*55)
    print("\nVulnerable endpoints:")
    print("  /search?q=          → Reflected XSS")
    print("  /product?id=        → SQLi (error-based)")
    print("  /category?name=     → SQLi (union-based)")
    print("  /user?id=           → SQLi (boolean-blind)")
    print("  /review?post_id=    → Stored XSS pattern")
    print("  /profile?username=  → SQLi (time-based)")
    print("  /login              → Verbose auth errors")
    print()
    app.run(host='0.0.0.0', port=8888, debug=False, use_reloader=False)

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)


# ==============================================================
# TEMPLATES — create each file inside app/templates/
# ==============================================================


# ===== FILE: app/templates/base.html =====
"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Insurance EDA – {{ title if title else 'Portal' }}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background: #f4f6f9; }
    .navbar { background: #1a3a5c !important; }
    .navbar-brand, .nav-link { color: #fff !important; }
    .card { box-shadow: 0 2px 8px rgba(0,0,0,.08); border: none; }
    .risk-high { color: #dc3545; font-weight: bold; }
    .risk-mid  { color: #fd7e14; }
    .risk-low  { color: #198754; }
  </style>
</head>
<body>
<nav class="navbar navbar-expand-lg mb-4">
  <div class="container">
    <a class="navbar-brand fw-bold" href="/">🛡️ Insurance EDA</a>
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a class="nav-link" href="/">Dashboard</a></li>
        <li class="nav-item"><a class="nav-link" href="/quote">New Quote</a></li>
      </ul>
    </div>
  </div>
</nav>
<div class="container pb-5">
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% for cat, msg in messages %}
      <div class="alert alert-{{ cat }} alert-dismissible fade show">{{ msg }}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      </div>
    {% endfor %}
  {% endwith %}
  {% block content %}{% endblock %}
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
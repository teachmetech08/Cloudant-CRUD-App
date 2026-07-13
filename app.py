from flask import Flask, render_template_string, request, redirect
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os

app = Flask(__name__)

# We will fill these two strings in the next step using your cloud credentials!
API_KEY = "UC_EywMYDfYZMGwttITPHt0tvyX4hlcGSWdGhqWfc0B5"
COUCHDB_URL = "https://apikey-v2-17e5b87p1j9xlblerxhmuly09p97gi5prjwvbmp3opam:1d5049d8daafe88faa5efa36e3327fed@42444d93-f4f6-487b-af42-949fb7fa9847-bluemix.cloudantnosqldb.appdomain.cloud"
DB_NAME = "task-db"


authenticator = IAMAuthenticator(API_KEY)
client = CloudantV1(authenticator=authenticator)
client.set_service_url(COUCHDB_URL)

# Ensure Database exists
try:
    client.put_database(db=DB_NAME).get_result()
except Exception:
    pass 


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alphatech Cloud | Task Manager</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --accent: #3b82f6;
            --accent-hover: #2563eb;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --danger: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, sans-serif; }
        body { background-color: var(--bg-primary); color: var(--text-main); min-height: 100vh; padding: 2rem 1rem; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 650px; }
        header { margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 1rem; }
        header h1 { font-size: 1.5rem; font-weight: 600; color: var(--text-main); display: flex; align-items: center; gap: 0.5rem; }
        header h1 i { color: var(--accent); }
        .badge { background: rgba(59, 130, 246, 0.1); color: var(--accent); padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(59, 130, 246, 0.2); }
        
        .analytics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2rem; }
        .kpi-card { background: var(--bg-secondary); border: 1px solid #334155; border-radius: 12px; padding: 1rem; display: flex; flex-direction: column; gap: 0.25rem; }
        .kpi-title { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 600; }
        .kpi-value { font-size: 1.5rem; font-weight: 700; color: var(--text-main); }
        .kpi-card.critical { border-color: rgba(239, 68, 68, 0.4); background: linear-gradient(180deg, var(--bg-secondary) 0%, rgba(239, 68, 68, 0.05) 100%); }
        .kpi-card.critical .kpi-value { color: var(--danger); }
        .kpi-card.active-job .kpi-value { color: var(--accent); }

        .form-container { background: var(--bg-secondary); padding: 1.25rem; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 2rem; display: flex; flex-direction: column; gap: 1rem; }
        .input-row { display: flex; gap: 0.75rem; }
        .input-row input { flex: 1; background: var(--bg-primary); border: 1px solid #334155; outline: none; color: var(--text-main); font-size: 1rem; padding: 0.6rem 0.75rem; border-radius: 8px; }
        .input-row input:focus { border-color: var(--accent); }
        .input-row button { background: var(--accent); color: white; border: none; padding: 0.6rem 1.4rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 0.5rem; }
        .input-row button:hover { background: var(--accent-hover); transform: translateY(-1px); }
        
        .options-row { display: flex; gap: 1.5rem; padding: 0 0.25rem; }
        .options-row label { color: var(--text-muted); font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem; }
        .options-row select, .options-row input { background: var(--bg-primary); color: var(--text-main); border: 1px solid #334155; padding: 0.35rem 0.5rem; border-radius: 6px; font-size: 0.85rem; outline: none; }
        
        .task-list { list-style: none; display: flex; flex-direction: column; gap: 0.75rem; }
        .task-item { background: var(--bg-secondary); padding: 1rem 1.25rem; border-radius: 12px; border: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; animation: fadeIn 0.3s ease; transition: all 0.2s; }
        .task-item:hover { border-color: #475569; }
        .task-text { color: var(--text-main); font-size: 1rem; font-weight: 500; }
        
        .delete-btn { color: var(--text-muted); text-decoration: none; padding: 0.5rem; border-radius: 6px; transition: all 0.2s; display: flex; align-items: center; justify-content: center; }
        .delete-btn:hover { color: var(--danger); background: rgba(239, 68, 68, 0.1); }
        .empty-state { text-align: center; padding: 3rem 1rem; color: var(--text-muted); display: flex; flex-direction: column; align-items: center; gap: 1rem; }
        .empty-state i { font-size: 2.5rem; color: #334155; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1><i class="fa-solid fa-server"></i> Cloudant Task Engine</h1>
            <span class="badge">IBM Cloud Connected</span>
        </header>

        <div class="analytics-grid">
            <div class="kpi-card">
                <span class="kpi-title">Total Cluster Logs</span>
                <span class="kpi-value">{{ total_logs }}</span>
            </div>
            <div class="kpi-card active-job">
                <span class="kpi-title">Pending Tasks</span>
                <span class="kpi-value">{{ pending_ops }}</span>
            </div>
            <div class="kpi-card critical">
                <span class="kpi-title">Critical Issues</span>
                <span class="kpi-value">{{ critical_issues }}</span>
            </div>
        </div>

        <form action="/add" method="POST" class="form-container">
            <div class="input-row">
                <input type="text" name="task" placeholder="Deploy new microservice, update documentation..." required autocomplete="off">
                <button type="submit"><i class="fa-solid fa-plus"></i> Add</button>
            </div>
            <div class="options-row">
                <label>
                    Priority:
                    <select name="priority">
                        <option value="Low">Low</option>
                        <option value="Medium" selected>Medium</option>
                        <option value="High">High</option>
                    </select>
                </label>
                <label>
                    Due Date:
                    <input type="date" name="due_date">
                </label>
            </div>
        </form>

        <ul class="task-list">
            {% for doc in tasks %}
                <li class="task-item" style="{% if doc.status == 'completed' %}opacity: 0.45; border-color: #1e293b;{% endif %}">
                    <div style="display: flex; gap: 1rem; align-items: flex-start; flex: 1;">
                        <a href="/toggle/{{ doc._id }}" style="color: {% if doc.status == 'completed' %}var(--accent){% else %}var(--text-muted){% endif %}; font-size: 1.2rem; margin-top: 2px; text-decoration: none;">
                            {% if doc.status == 'completed' %}
                                <i class="fa-solid fa-circle-check"></i>
                            {% else %}
                                <i class="fa-regular fa-circle"></i>
                            {% endif %}
                        </a>

                        <div style="display: flex; flex-direction: column; gap: 0.35rem;">
                            <span class="task-text" style="{% if doc.status == 'completed' %}text-decoration: line-through; color: var(--text-muted);{% endif %}">
                                {{ doc.task }}
                            </span>
                            <div style="display: flex; gap: 0.75rem; font-size: 0.75rem; align-items: center;">
                                <span style="color: {% if doc.priority == 'High' %}#ef4444{% elif doc.priority == 'Medium' %}#f59e0b{% else %}#10b981{% endif %}; font-weight: bold;">
                                    ● {{ doc.priority|default('Medium') }} Priority
                                </span>
                                {% if doc.due_date %}
                                    <span style="color: var(--text-muted);"><i class="fa-regular fa-calendar" style="margin-right: 2px;"></i> {{ doc.due_date }}</span>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    <a href="/delete/{{ doc._id }}/{{ doc._rev }}" class="delete-btn" title="Delete Task">
                        <i class="fa-regular fa-trash-can"></i>
                    </a>
                </li>
            {% endfor %}
        </ul>

        {% if not tasks %}
            <div class="empty-state">
                <i class="fa-solid fa-list-check"></i>
                <p>No active cluster operations tracked. Add a task to initiate logging.</p>
            </div>
        {% endif %}
    </div>
<!-- Grid-Breaking Full-Width Footer -->
<footer style="grid-column: 1 / -1; width: 100%; clear: both; display: block; margin-top: 80px; padding: 30px 0; border-top: 1px solid #1e293b; color: #94a3b8; font-family: sans-serif; text-align: center;">
    <p style="margin: 0 0 10px 0;">&copy; 2026 Cloudant Task Engine. All Rights Reserved.</p>
    <p style="margin: 0 0 15px 0;">Designed & Engineered Originally by <strong>Vansh Agarwal</strong></p>
    
    <!-- Social Identity Icons -->
    <div style="display: flex; justify-content: center; gap: 20px; align-items: center; margin-top: 10px;">
        <!-- GitHub Link -->
        <a href="https://github.com/teachmetech08" target="_blank" title="GitHub Profile" style="color: #38bdf8; text-decoration: none; display: flex; align-items: center; gap: 6px; font-weight: bold;">
            <svg height="20" width="20" viewBox="0 0 16 16" fill="currentColor" style="display: inline-block; vertical-align: middle;">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
            </svg>
            GitHub
        </a>

        <!-- LinkedIn Link -->
        <a href="https://www.linkedin.com/in/vansh-agarwal-techpluss08" target="_blank" title="LinkedIn Profile" style="color: #38bdf8; text-decoration: none; display: flex; align-items: center; gap: 6px; font-weight: bold;">
            <svg height="20" width="20" viewBox="0 0 24 24" fill="currentColor" style="display: inline-block; vertical-align: middle;">
                <path d="M22.23 0H1.77C.8 0 0 .77 0 1.72v20.56C0 23.23.8 24 1.77 24h20.46c.98 0 1.77-.77 1.77-1.72V1.72C24 .77 23.2 0 22.23 0zM7.12 20.45H3.56V9H7.12v11.45zM5.34 7.43c-1.14 0-2.06-.92-2.06-2.06 0-1.14.92-2.06 2.06-2.06 1.14 0 2.06.92 2.06 2.06 0 1.14-.92 2.06-2.06 2.06zm15.11 13.02h-3.56v-5.6c0-1.34-.03-3.05-1.86-3.05-1.86 0-2.14 1.45-2.14 2.95v5.7h-3.56V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29z"/>
            </svg>
            LinkedIn
        </a>
    </div>
</footer>
</body>
</html>
"""


@app.route('/')
def index():
    response = client.post_all_docs(db=DB_NAME, include_docs=True).get_result()
    tasks = [row['doc'] for row in response['rows'] if 'task' in row['doc']]
    
    total_logs = len(tasks)
    critical_issues = sum(1 for t in tasks if t.get('priority') == 'High')
    pending_ops = sum(1 for t in tasks if t.get('status', 'pending') == 'pending')
    
    return render_template_string(
        HTML_TEMPLATE, 
        tasks=tasks, 
        total_logs=total_logs, 
        critical_issues=critical_issues,
        pending_ops=pending_ops
    )


@app.route('/add', methods=['POST'])
def add_task():
    task_text = request.form.get('task')
    task_priority = request.form.get('priority')
    task_due_date = request.form.get('due_date')
    
    task_doc = {
        'task': task_text,
        'priority': task_priority,
        'due_date': task_due_date,
        'status': 'pending'
    }
    
    client.post_document(db=DB_NAME, document=task_doc).get_result()
    return redirect('/')


@app.route('/toggle/<doc_id>')
def toggle_task(doc_id):
    doc = client.get_document(db=DB_NAME, doc_id=doc_id).get_result()
    current_status = doc.get('status', 'pending')
    doc['status'] = 'completed' if current_status == 'pending' else 'pending'
    
    client.post_document(db=DB_NAME, document=doc).get_result()
    return redirect('/')


@app.route('/delete/<doc_id>/<rev>')
def delete_task(doc_id, rev):
    client.delete_document(db=DB_NAME, doc_id=doc_id, rev=rev).get_result()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
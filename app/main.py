import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Job Hunt Application Dashboard")

# Points directly to your serverless repository database file
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "applications.json")
if not os.path.exists(DATA_FILE):
    # Fallback search if running directly from root folder context
    DATA_FILE = "applications.json"

def load_applications():
    """Loads application records seamlessly from the free serverless JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    # Read the data written by your GitHub background action script
    applications = load_applications()
    total_apps = len(applications)
    
    # Calculate simple internal metrics dynamically without heavy SQL aggregations
    interview_count = sum(1 for app in applications if app.get("status", "").lower() == "interview")
    rejected_count = sum(1 for app in applications if app.get("status", "").lower() == "rejected")
    applied_count = total_apps - interview_count - rejected_count

    # UI Template injection (Standard HTML string layout fallback)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Job Hunt Pro Dashboard</title>
        <link rel="stylesheet" href="https://jsdelivr.net">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="row mb-4">
                <div class="col">
                    <h1 class="display-5 text-dark fw-bold">🚀 Job Application Dashboard</h1>
                    <p class="text-muted">Serverless Stack powered by GitHub Actions & Student Resources</p>
                </div>
            </div>
            
            <!-- Metric Counter Cards -->
            <div class="row mb-4 text-center">
                <div class="col-md-3"><div class="card p-3 shadow-sm bg-primary text-white"><h5>Total Applications</h5><h2>{total_apps}</h2></div></div>
                <div class="col-md-3"><div class="card p-3 shadow-sm bg-warning text-dark"><h5>Applied / In Review</h5><h2>{applied_count}</h2></div></div>
                <div class="col-md-3"><div class="card p-3 shadow-sm bg-success text-white"><h5>Interviews</h5><h2>{interview_count}</h2></div></div>
                <div class="col-md-3"><div class="card p-3 shadow-sm bg-danger text-white"><h5>Rejections</h5><h2>{rejected_count}</h2></div></div>
            </div>

            <!-- Detailed Ingestion Tracking Table -->
            <div class="card shadow-sm">
                <div class="card-header bg-white fw-bold">Recent Sync Pipeline Log History</div>
                <div class="card-body p-0">
                    <table class="table table-striped table-hover mb-0">
                        <thead class="table-dark">
                            <tr>
                                <th>ID</th>
                                <th>Company</th>
                                <th>Target Role</th>
                                <th>Status State</th>
                                <th>Ingestion Timestamp</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    if not applications:
        html_content += """
                            <tr>
                                <td colspan="5" class="text-center text-muted p-4">
                                    No applications tracked yet. Your background sync cron jobs will populate items here!
                                </td>
                            </tr>
        """
    else:
        for app in reversed(applications):  # Show newest applications at the top
            status_badge = "bg-warning text-dark"
            if app.get("status").lower() == "interview": status_badge = "bg-success"
            elif app.get("status").lower() == "rejected": status_badge = "bg-danger"
            
            html_content += f"""
                            <tr>
                                <td>{app.get('id')}</td>
                                <td class="fw-bold">{app.get('company')}</td>
                                <td>{app.get('role')}</td>
                                <td><span class="badge {status_badge}">{app.get('status')}</span></td>
                                <td class="text-muted">{app.get('date_logged')}</td>
                            </tr>
            """

    html_content += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

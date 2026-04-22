import sqlite3
import pandas as pd
from flask import Flask, render_template_string, request
import plotly.express as px
import plotly.graph_objects as go
import json

app = Flask(__name__)
DB_PATH = "/root/.openclaw/workspace/github_projects/prospect-intelligence/apie_v10.db"

def get_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM queue", conn)
        conn.close()
        
        def extract_adm(row_data):
            if not row_data: return "N/A"
            try:
                d = json.loads(row_data)
                return d.get("Administración Local", d.get("Administracion Local", "N/A"))
            except: return "N/A"

        def check_legal(osint_data):
            if not osint_data: return False
            try:
                d = json.loads(osint_data)
                return d.get('legal_issues', {}).get('has_reconsiderations', False)
            except: return False
            
        df['adm_local'] = df['data'].apply(extract_adm)
        df['has_legal_issue'] = df['osint_data'].apply(check_legal)
        df['last_update'] = pd.to_datetime(df['last_update'])
        return df
    except Exception as e:
        print(f"Error reading DB: {e}")
        return pd.DataFrame()

@app.route('/')
def dashboard():
    df_raw = get_data()
    if df_raw.empty:
        return "<h1>Error: Base de datos no disponible</h1>"
    
    selected_plazo = request.args.get('plazo', 'all')
    selected_adm = request.args.get('adm', 'all')
    selected_category = request.args.get('category', 'all')
    selected_legal = request.args.get('legal', 'all')
    
    df = df_raw.copy()
    
    if selected_plazo != 'all': df = df[df['plazo'] == selected_plazo]
    if selected_adm != 'all': df = df[df['adm_local'] == selected_adm]
    if selected_category != 'all': df = df[df['category'] == selected_category]
    if selected_legal == 'yes': df = df[df['has_legal_issue'] == True]

    def calculate_priority(row):
        score = 0
        if row['has_legal_issue']: score += 150 # Prioridad Máxima (Punto de Dolor Legal)
        if row['plazo'] == '15 de mayo 2025': score += 100 # Prioridad Crítica (Próxima fecha DGII)
        if row['plazo'] == '15 de noviembre 2025': score += 60
        if row['category'] == 'AI_CHATBOT_UPSKLLING': score += 50 # Alta prioridad chatbot
        if row['category'] == 'VENTAX_MIPYMES': score += 30
        if row['real_email'] and row['real_email'] != 'NOT_FOUND': score += 20
        return score
    
    df['priority_score'] = df.apply(calculate_priority, axis=1)
    display_df = df.sort_values(by=['priority_score', 'last_update'], ascending=[False, False]).head(500)

    # Gráficos
    fig_legal = px.pie(df_raw[df_raw['status']=='SUCCESS'], names='has_legal_issue', 
                      title='Prospectos con Conflictos/Reconsideraciones DGII',
                      color='has_legal_issue', color_discrete_map={True:'#e11d48', False:'#cbd5e1'})

    fig_plazo = px.histogram(df_raw, x='plazo', color='category', 
                            title='Distribución por Plazo DGII y Categoría',
                            barmode='group')

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>ARMULTIS Sales Intelligence V4 - Dashboard Estratégico</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ background-color: #f8fafc; font-family: 'Segoe UI', sans-serif; }}
            .sidebar {{ height: 100vh; background: #0f172a; color: white; padding: 20px; position: fixed; width: 300px; overflow-y: auto; }}
            .main-content {{ margin-left: 300px; padding: 40px; }}
            .card-legal {{ border-left: 8px solid #e11d48 !important; background-color: #fff1f2; }}
            .card-mayo {{ border-left: 8px solid #f59e0b !important; background-color: #fffbeb; }}
            .priority-badge {{ font-size: 0.7rem; font-weight: 800; padding: 4px 8px; border-radius: 4px; }}
            .legal-source {{ font-size: 0.75rem; color: #e11d48; text-decoration: underline; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 class="text-primary mb-4">Aiara V4 🛡️</h2>
            <form action="/">
                <div class="mb-3">
                    <label class="small fw-bold text-muted">PLAZO DGII</label>
                    <select name="plazo" class="form-select bg-dark text-white" onchange="this.form.submit()">
                        <option value="all">Ver Todos</option>
                        {"".join([f'<option value="{p}" {"selected" if selected_plazo==p else ""}>{p}</option>' for p in sorted(df_raw['plazo'].dropna().unique())])}
                    </select>
                </div>
                <div class="mb-3">
                    <label class="small fw-bold text-muted">CONFLICTO LEGAL</label>
                    <select name="legal" class="form-select bg-dark text-white" onchange="this.form.submit()">
                        <option value="all">Ver Todos</option>
                        <option value="yes" {"selected" if selected_legal=="yes" else ""}>Solo Reconsideraciones DGII</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="small fw-bold text-muted">ÁREA DE NEGOCIO</label>
                    <select name="category" class="form-select bg-dark text-white" onchange="this.form.submit()">
                        <option value="all">Todas</option>
                        {"".join([f'<option value="{c}" {"selected" if selected_category==c else ""}>{c}</option>' for c in sorted(df_raw['category'].dropna().unique())])}
                    </select>
                </div>
                <hr>
                <div class="d-grid"><a href="/" class="btn btn-outline-info btn-sm">Limpiar Filtros</a></div>
            </form>
        </div>
        <div class="main-content">
            <h1 class="fw-bold">Inteligencia de Prospección Estratégica</h1>
            <p class="text-muted">Segmentación por Plazos DGII, Chatbots y Dealers MiPyMEs</p>
            
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card p-4 text-center mb-3">
                        <div class="text-muted small fw-bold">PLAZO MAYO 2025</div>
                        <div class="h2 fw-bold text-warning">{len(df_raw[df_raw['plazo']=='15 de mayo 2025'])}</div>
                    </div>
                    <div class="card p-4 text-center">
                        <div class="text-muted small fw-bold">CHATBOTS / UPSKILLING</div>
                        <div class="h2 fw-bold text-info">{len(df_raw[df_raw['category']=='AI_CHATBOT_UPSKLLING'])}</div>
                    </div>
                </div>
                <div class="col-md-9">
                    <div class="card p-3 mb-3">{fig_plazo.to_html(full_html=False, include_plotlyjs='cdn')}</div>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card p-4 text-center">
                        <div class="text-muted small fw-bold">CRÍTICOS (CON SITUACIÓN DGII)</div>
                        <div class="h2 fw-bold text-danger">{len(df_raw[df_raw['has_legal_issue']==True])}</div>
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="card p-3">{fig_legal.to_html(full_html=False, include_plotlyjs='cdn')}</div>
                </div>
            </div>

            <div class="card">
                <div class="card-header bg-white fw-bold">🎯 Matriz de Abordaje (Prioridad Mayo 2025 + Chatbots)</div>
                <div class="card-body p-0">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th class="ps-4">Empresa / RNC</th>
                                <th>Situación / Plazo</th>
                                <th>Área</th>
                                <th>Contacto</th>
                                <th class="pe-4 text-center">Estrategia</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join([f"""<tr class='{"card-legal" if r['has_legal_issue'] else ("card-mayo" if r['plazo']=='15 de mayo 2025' else "")}'>
                                <td class="ps-4">
                                    <div class="fw-bold">{r['razon_social'][:60]}</div>
                                    <small class="text-muted">RNC: {r['rnc']}</small>
                                </td>
                                <td>
                                    {f'<span class="badge bg-danger mb-1">RECONSIDERACIÓN</span><br>' if r['has_legal_issue'] else ''}
                                    <span class="badge {"bg-warning text-dark" if r['plazo']=='15 de mayo 2025' else "bg-light text-dark"}">{r['plazo']}</span>
                                </td>
                                <td><span class="badge bg-secondary">{r['category']}</span></td>
                                <td><code>{r['real_email']}</code></td>
                                <td class="pe-4 text-center">
                                    {f'<span class="priority-badge bg-danger text-white">CIERRE FORZADO</span>' if r['has_legal_issue'] else (f'<span class="priority-badge bg-warning text-dark">ALTA PRIORIDAD</span>' if r['plazo']=='15 de mayo 2025' else '<span class="priority-badge bg-light border text-dark">ESTÁNDAR</span>')}
                                </td>
                            </tr>""" for _, r in display_df.iterrows()])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

# report_builder.py

class HTMLReportBuilder:
    def __init__(self, filename="Monster_Dashboard_English.html"):
        self.filename = filename

    def generate(self, kpis, charts, ab_winner):
        ab_html = f"<div style='background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; font-size:12px; margin-top:5px;'>Winner: <b>{ab_winner}</b></div>" if ab_winner != "N/A" else ""

        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Marketing Dashboard v9.1</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
            <style>
                :root {{ --bg: #0b0c15; --card: #151621; --accent: #6c5ce7; --text: #dfe6e9; --green: #00b894; }}
                body {{ font-family: 'Inter', sans-serif; background-color: var(--bg); color: var(--text); margin: 0; padding: 20px; }}
                .container {{ max-width: 1800px; margin: 0 auto; }}
                
                .grid-6 {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 20px; margin-bottom: 20px; }}
                .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
                .grid-2 {{ display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 20px; }}
                .grid-2-equal {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
                
                .card {{ background: var(--card); border-radius: 16px; padding: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.05); }}
                .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(90deg, var(--card), #1e202e); border-radius: 16px; border-left: 5px solid var(--accent); }}
                h1 {{ font-family: 'Space Grotesk', sans-serif; margin: 0; font-size: 26px; }}
                h2 {{ font-size: 18px; color: var(--accent); margin: 40px 0 20px 0; border-bottom: 1px solid #333; padding-bottom: 10px; }}
                
                .kpi-card {{ background: linear-gradient(135deg, #1e202e, #151621); padding: 20px; border-radius: 12px; text-align: center; border-bottom: 3px solid var(--green); }}
                .kpi-val {{ font-family: 'Space Grotesk'; font-size: 28px; font-weight: bold; color: #fff; }}
                .kpi-lbl {{ font-size: 11px; text-transform: uppercase; color: #b2bec3; margin-top: 5px; }}

                .sim-box {{ display: flex; flex-direction: column; justify-content: center; height: 100%; }}
                .input-group {{ display: flex; align-items: center; justify-content: space-between; background: #2d3436; padding: 10px; border-radius: 8px; margin-bottom: 15px; }}
                input[type=range] {{ width: 60%; accent-color: var(--accent); }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div>
                        <h1>Marketing Dashboard v9.1</h1>
                        <span style="color: #b2bec3; font-size: 14px;">Operational: Cohort Analysis, CR Metric & All Modules Active</span>
                    </div>
                    <div style="background: var(--accent); padding: 5px 15px; border-radius: 20px; font-weight: bold;">ALL FEATURES</div>
                </div>

                <h2>Executive Summary (KPIs)</h2>
                <div class="grid-6">
                    <div class="kpi-card"><div class="kpi-val">${kpis['total_spend']:,.0f}</div><div class="kpi-lbl">Total Spend</div></div>
                    <div class="kpi-card"><div class="kpi-val">{kpis['total_clicks']:,}</div><div class="kpi-lbl">Total Clicks</div></div>
                    <div class="kpi-card"><div class="kpi-val">{kpis['total_conversions']:,}</div><div class="kpi-lbl">Total Conversions</div></div>
                    <div class="kpi-card"><div class="kpi-val">${kpis['avg_cpc']:.2f}</div><div class="kpi-lbl">Avg CPC</div></div>
                    <div class="kpi-card"><div class="kpi-val">{kpis['avg_ctr']:.2f}%</div><div class="kpi-lbl">Avg CTR</div></div>
                    <div class="kpi-card"><div class="kpi-val">${kpis['avg_cpm']:.2f}</div><div class="kpi-lbl">Avg CPM</div></div>
                </div>

                <h2>Performance & Efficiency Trends</h2>
                <div class="grid-3">
                    <div class="card">{charts['trend'].to_html(full_html=False, include_plotlyjs='cdn')}</div>
                    <div class="card">{charts['cpm'].to_html(full_html=False, include_plotlyjs=False)}</div>
                    <div class="card">{charts['ctr'].to_html(full_html=False, include_plotlyjs=False)}</div>
                </div>

                <h2>Decision Support (AI & Simulators)</h2>
                <div class="grid-3">
                    <div class="card">{charts['anomaly'].to_html(full_html=False, include_plotlyjs=False)}</div>
                    
                    <div class="card sim-box">
                        <h3>Budget Simulator</h3>
                        <div class="input-group">
                            <label>Budget Adj.</label>
                            <input type="range" id="budgetRange" min="-50" max="100" value="0" oninput="updateSim()">
                            <span id="rangeVal" style="font-weight:bold; color: var(--accent);">0%</span>
                        </div>
                        <div style="display:flex; justify-content:space-around;">
                            <div style="text-align:center"><div style="font-size:12px; color:#b2bec3">New Spend</div><div id="newSpend" style="font-size:20px; font-weight:bold;">${kpis['total_spend']:,.0f}</div></div>
                            <div style="text-align:center"><div style="font-size:12px; color:#b2bec3">New Clicks</div><div id="newClicks" style="font-size:20px; font-weight:bold; color:var(--green)">{kpis['total_clicks']:,}</div></div>
                        </div>
                    </div>

                    <div class="card">
                        {charts['ab_gauge'].to_html(full_html=False, include_plotlyjs=False)}
                        {ab_html}
                    </div>
                </div>

                <h2>Advanced Data Science (Cohort, Attribution & Sentiment)</h2>
                <div class="grid-3">
                    <div class="card">{charts['cohort'].to_html(full_html=False, include_plotlyjs=False)}</div>
                    <div class="card">{charts['sankey'].to_html(full_html=False, include_plotlyjs=False)}</div>
                    <div class="card">{charts['sentiment'].to_html(full_html=False, include_plotlyjs=False)}</div>
                </div>

                <h2>Fundamentals (Funnel & Breakdown)</h2>
                <div class="grid-2-equal">
                    <div class="card">{charts['funnel'].to_html(full_html=False, include_plotlyjs=False)}</div>
                    <div class="card">{charts['sunburst'].to_html(full_html=False, include_plotlyjs=False)}</div>
                </div>

                <h2>Strategic Insights (Geo & Forecast)</h2>
                <div class="grid-2">
                    <div class="card">{charts['forecast'].to_html(full_html=False, include_plotlyjs=False)}</div>
                    <div class="card">{charts['map'].to_html(full_html=False, include_plotlyjs=False)}</div>
                </div>

                <h2>Deep Dive (Audience & NLP)</h2>
                <div class="grid-2-equal">
                    <div class="card">{charts['audience'].to_html(full_html=False, include_plotlyjs=False)}</div>
                    <div class="card">{charts['nlp'].to_html(full_html=False, include_plotlyjs=False)}</div>
                </div>

            </div>
            
            <script>
                const baseSpend = {kpis['total_spend']};
                const avgCpc = {kpis['avg_cpc']};
                function updateSim() {{
                    let percent = document.getElementById('budgetRange').value;
                    document.getElementById('rangeVal').innerText = (percent > 0 ? "+" : "") + percent + "%";
                    let factor = 1 + (percent / 100);
                    let newSpend = baseSpend * factor;
                    let cpcPenalty = percent > 0 ? (1 + (percent * 0.002)) : 1; 
                    let newClicks = newSpend / (avgCpc * cpcPenalty);
                    document.getElementById('newSpend').innerText = "$" + newSpend.toLocaleString(undefined, {{maximumFractionDigits: 0}});
                    document.getElementById('newClicks').innerText = Math.round(newClicks).toLocaleString();
                }}
            </script>
        </body>
        </html>
        """
        
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write(html_template)
        print(f"Report successfully generated: {self.filename}")
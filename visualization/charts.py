# visualizer.py
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class DashboardCharts:
    def __init__(self, template='plotly_dark'):
        self.template = template

    def create_trends_chart(self, trends_df):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=trends_df['Date'], y=trends_df['CPC'], name="CPC ($)", line=dict(color='#00cec9')), secondary_y=False)
        fig.add_trace(go.Scatter(x=trends_df['Date'], y=trends_df['CTR'], name="CTR (%)", line=dict(color='#fdcb6e', dash='dot')), secondary_y=True)
        fig.update_layout(title='Efficiency Trends', template=self.template, height=350)
        return fig

    def create_platform_bar_charts(self, plat_df):
        fig_cpm = px.bar(plat_df, x='Platform', y='CPM', color='Platform', title='Cost Per Mille (CPM)', template=self.template)
        fig_ctr = px.bar(plat_df, x='Platform', y='CTR', color='Platform', title='Click-Through Rate (CTR)', template=self.template)
        return fig_cpm, fig_ctr

    def create_funnel(self, kpis, df_reach):
        funnel_data = dict(
            number=[kpis['total_impressions'], int(df_reach), kpis['total_clicks'], kpis['total_conversions']], 
            stage=["Impressions", "Reach", "Clicks", "Conversions"]
        )
        return px.funnel(funnel_data, x='number', y='stage', title='Conversion Funnel', template=self.template)

    def create_cohort_heatmap(self, weeks, matrix):
        if len(weeks) > 0:
            weeks_str = [w.strftime('%Y-%m-%d') for w in weeks]
            fig = go.Figure(data=go.Heatmap(z=matrix, x=[f"Week {i}" for i in range(len(weeks))], y=weeks_str, colorscale='Blues'))
            fig.update_layout(title='Cohort Retention', template=self.template)
            return fig
        return go.Figure().update_layout(title="No Cohort Data", template=self.template)

    def create_sankey(self, nodes, src, tgt, vals):
        fig = go.Figure(data=[go.Sankey(
            node = dict(pad = 15, thickness = 20, line = dict(color = "black", width = 0.5), label = nodes, color = "blue"),
            link = dict(source = src, target = tgt, value = vals))])
        fig.update_layout(title="Attribution Flow", template=self.template)
        return fig

    def create_sentiment_gauge(self, avg_sentiment):
        score = int((avg_sentiment + 1) * 50)
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = score, title = {'text': "Sentiment Score"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "green" if score > 60 else "red"}}
        ))
        fig.update_layout(template=self.template, height=250, margin=dict(t=60,b=20,l=20,r=20))
        return fig

    def create_audience_scatter(self, audience_df):
        """
        Deep Dive / Audience grafiği:
        - X: Age
        - Y: CR (%)  (Conversion Rate)
        - Bubble size: Clicks
        - Color: Gender (varsa), yoksa tek renk

        Beklenen kolonlar:
        Age, Clicks, Conversions, CR, (opsiyonel) Gender, CPC
        """
        import plotly.graph_objects as go
        import plotly.express as px

        # Veri yoksa "no data" yazılı boş bir grafik dön
        if audience_df is None or audience_df.empty:
            fig = go.Figure()
            fig.update_layout(
                title="Audience Conversion by Age & Gender (no data)",
                template=self.template,
                height=350,
            )
            return fig

        df = audience_df.copy()

        # Gerekli kolonlar var mı?
        if "Age" not in df.columns or "CR" not in df.columns or "Clicks" not in df.columns:
            fig = go.Figure()
            fig.update_layout(
                title="Audience Conversion (unsupported schema)",
                template=self.template,
                height=350,
            )
            return fig

        # Hover'da göstermek için mevcut kolonlardan seç
        hover_cols = [c for c in ["Clicks", "Conversions", "CPC", "Spend"] if c in df.columns]

        # Gender varsa renk olarak kullan
        color_arg = "Gender" if "Gender" in df.columns else None

        fig = px.scatter(
            df,
            x="Age",
            y="CR",
            size="Clicks",
            color=color_arg,
            hover_data=hover_cols,
            title="Audience Conversion by Age & Gender",
            template=self.template,
        )

        fig.update_layout(
            yaxis_title="Conversion Rate (%)",
            xaxis_title="Age",
            height=350,
        )

        return fig


    def create_forecast_chart(self, daily, f_dates, f_vals):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily['Date'], y=daily['Cum'], mode='lines', name='Actual', line_color='#0984e3'))
        if len(f_dates) > 0: 
            fig.add_trace(go.Scatter(x=f_dates, y=f_vals, mode='lines', name='Forecast', line=dict(dash='dash', color='#e17055')))
        fig.update_layout(title="Budget Forecast", template=self.template)
        return fig

    def create_sunburst(self, df_break):
        return px.sunburst(df_break, path=['Platform', 'Device', 'Placement'], values='Spend', title="Device Breakdown", template=self.template)

    def create_anomaly_chart(self, anom_df):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=anom_df['Date'], y=anom_df['Upper'], mode='lines', line_color='rgba(255,255,255,0.1)', name='Limit'))
        fig.add_trace(go.Scatter(x=anom_df['Date'], y=anom_df['CPC'], mode='lines', line_color='#00b894', name='CPC'))
        anomalies = anom_df[anom_df['Is_Anomaly']]
        fig.add_trace(go.Scatter(x=anomalies['Date'], y=anomalies['CPC'], mode='markers', marker=dict(color='red', size=8), name='Anomaly'))
        fig.update_layout(title="Anomaly Detection", template=self.template, height=350)
        return fig

    def create_map(self, geo_df):
        return px.choropleth(geo_df, locations="Country", locationmode="ISO-3", color="CPC", hover_name="Country", color_continuous_scale="Blues", title="Global Cost Efficiency", template=self.template)

    def create_nlp_chart(self, nlp_df):
        """
        Magic Words grafiği:
        analyzer.analyze_nlp() -> kolonlar: Keyword, Total_Clicks

        Burada en basit ve anlamlı görsel:
        - X: Keyword
        - Y: Total_Clicks
        """
        import plotly.graph_objects as go
        import plotly.express as px

        if nlp_df is None or nlp_df.empty:
            fig = go.Figure()
            fig.update_layout(
                title="Magic Words (no data)",
                template=self.template,
                height=300,
            )
            return fig

        # Beklenen kolonlar varsa bar chart çizelim
        if "Keyword" in nlp_df.columns and "Total_Clicks" in nlp_df.columns:
            df_plot = nlp_df.sort_values("Total_Clicks", ascending=False)

            fig = px.bar(
                df_plot,
                x="Keyword",
                y="Total_Clicks",
                title="Magic Words (Top Keywords by Clicks)",
                template=self.template,
            )
            fig.update_layout(
                xaxis_tickangle=-45,
                height=350,
            )
            return fig

        # Fallback: şema uymuyorsa boş grafik
        fig = go.Figure()
        fig.update_layout(
            title="Magic Words (unsupported data schema)",
            template=self.template,
            height=300,
        )
        return fig


    def create_ab_gauge(self, confidence, c1_name="Camp A", c2_name="Camp B"):
        # İsimler çok uzunsa grafiği bozmaması için ilk 15 karakteri alıp '...' koyabiliriz
        c1_display = (c1_name[:15] + '..') if len(c1_name) > 15 else c1_name
        c2_display = (c2_name[:15] + '..') if len(c2_name) > 15 else c2_name

        fig = go.Figure(go.Indicator(
            mode = "gauge+number", 
            value = confidence, 
            # Başlığın altına HTML ile daha küçük ve gri renkte kampanya isimlerini ekliyoruz
            title = {'text': f"A/B Confidence<br><span style='font-size:12px; color:#b2bec3'>{c1_display} vs {c2_display}</span>"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#00cec9"}}
        ))
        
        # Başlık artık 2 satır olduğu için t=80 yaparak üst boşluğu artırdık
        fig.update_layout(template=self.template, height=270, margin=dict(t=80, b=20, l=20, r=20))
        return fig
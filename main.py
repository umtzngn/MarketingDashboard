# main.py
from core.data_loader import DataLoader
from core.analyzer import MarketingAnalyzer
from visualization.charts import DashboardCharts
from visualization.report_generator import HTMLReportBuilder

def main():
    # 1. Load Data
    loader = DataLoader(data_folder='.')
    df = loader.load_data()

    if df is None or df.empty:
        print("Error: No data available to analyze.")
        return

    # 2. Analyze
    analyzer = MarketingAnalyzer(df)
    kpis = analyzer.get_kpis()
    
    # Run all analysis modules
    trends = analyzer.analyze_trends()
    plat_eff = analyzer.analyze_platform_efficiency()
    cohort_weeks, cohort_matrix = analyzer.analyze_cohort()
    nodes, src, tgt, vals = analyzer.analyze_attribution()
    cp = analyzer.analyze_conversion_prob()
    daily, f_dates, f_vals = analyzer.analyze_forecast()
    anom = analyzer.analyze_anomalies()
    breakdown = analyzer.analyze_breakdown()
    geo = analyzer.analyze_geo()
    nlp = analyzer.analyze_nlp()
    ab_conf, ab_winner, ab_details = analyzer.analyze_ab_stats()
    freq = analyzer.analyze_frequency()

    # 3. Visualize
    viz = DashboardCharts()
    charts = {}
    
    charts['trend'] = viz.create_trends_chart(trends)
    charts['cpm'], charts['ctr'] = viz.create_platform_bar_charts(plat_eff)
    charts['funnel'] = viz.create_funnel(kpis, df['Reach'].sum())
    charts['cohort'] = viz.create_cohort_heatmap(cohort_weeks, cohort_matrix)
    charts['sankey'] = viz.create_sankey(nodes, src, tgt, vals)
    charts['sentiment'] = viz.create_sentiment_gauge(kpis['avg_sentiment'])
    charts['audience'] = viz.create_audience_scatter(cp)
    charts['forecast'] = viz.create_forecast_chart(daily, f_dates, f_vals)
    charts['sunburst'] = viz.create_sunburst(breakdown)
    charts['anomaly'] = viz.create_anomaly_chart(anom)
    charts['map'] = viz.create_map(geo)
    charts['nlp'] = viz.create_nlp_chart(nlp)
    c1_name = ab_details.get('c1', '?')
    c2_name = ab_details.get('c2', '?')
    charts['ab_gauge'] = viz.create_ab_gauge(ab_conf, c1_name, c2_name)
    creative_fatigue = analyzer.analyze_creative_fatigue()
    charts['creative_fatigue'] = viz.create_creative_fatigue_chart(creative_fatigue)
    charts['frequency'] = viz.create_frequency_chart(freq)
    


    # 4. Generate Report
    builder = HTMLReportBuilder()
    builder.generate(kpis, charts, ab_winner)

if __name__ == "__main__":
    main()
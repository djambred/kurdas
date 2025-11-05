import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.database import db
from models.predictive_models import PredictiveAnalytics, AdvancedAnalytics

def show_predictive_analytics():
    st.title("🤖 Predictive Analytics")
    
    predictive_engine = PredictiveAnalytics(db)
    advanced_engine = AdvancedAnalytics(db)
    
    # Tab untuk berbagai jenis analisis
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 PLO Trend Prediction", 
        "⚠️ Risk Assessment", 
        "🎓 Graduation Readiness",
        "📊 Advanced Analytics"
    ])
    
    with tab1:
        st.header("Prediksi Trend PLO")
        
        plo_data = db.get_all_plo()
        selected_plo = st.selectbox("Pilih PLO untuk Prediksi:", plo_data['kode_plo'].tolist())
        
        periods = st.slider("Jumlah Periode Prediksi:", 1, 4, 2)
        
        if st.button("Lakukan Prediksi", type="primary"):
            with st.spinner("Menganalisis data dan membuat prediksi..."):
                prediction = predictive_engine.predict_plo_trend(selected_plo, periods)
                
                if "error" in prediction:
                    st.error(prediction["error"])
                else:
                    # Display current performance
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Performa Saat Ini", f"{prediction['current_performance']:.2f}%")
                    with col2:
                        next_pred = prediction['predictions'][0]['predicted_score']
                        diff = next_pred - prediction['current_performance']
                        st.metric("Prediksi Periode Berikut", f"{next_pred:.2f}%", f"{diff:+.2f}%")
                    with col3:
                        st.metric("Confidence Score", f"{prediction['confidence']:.3f}")
                    
                    # Visualisasi prediksi
                    st.subheader("📊 Visualisasi Trend dan Prediksi")
                    
                    # Prepare data for visualization
                    historical_data = predictive_engine.prepare_plo_timeseries_data()
                    plo_historical = historical_data[historical_data['kode_plo'] == selected_plo]
                    
                    # Create figure
                    fig = go.Figure()
                    
                    # Historical data
                    fig.add_trace(go.Scatter(
                        x=plo_historical['periode'],
                        y=plo_historical['nilai_rata_rata'],
                        mode='lines+markers',
                        name='Data Historis',
                        line=dict(color='blue', width=3)
                    ))
                    
                    # Predictions
                    pred_periods = [p['periode'] for p in prediction['predictions']]
                    pred_scores = [p['predicted_score'] for p in prediction['predictions']]
                    
                    fig.add_trace(go.Scatter(
                        x=pred_periods,
                        y=pred_scores,
                        mode='lines+markers',
                        name='Prediksi',
                        line=dict(color='red', width=3, dash='dash')
                    ))
                    
                    fig.update_layout(
                        title=f"Trend dan Prediksi {selected_plo}",
                        xaxis_title="Periode",
                        yaxis_title="Nilai Rata-rata (%)",
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Detail prediksi
                    st.subheader("📅 Detail Prediksi per Periode")
                    pred_df = pd.DataFrame(prediction['predictions'])
                    st.dataframe(pred_df, use_container_width=True)
    
    with tab2:
        st.header("Risk Assessment PLO")
        
        if st.button("Hitung Risk Assessment", type="primary"):
            with st.spinner("Menganalisis risiko PLO..."):
                risk_data = predictive_engine.calculate_plo_risk_assessment()
                
                if risk_data.empty:
                    st.warning("Data tidak cukup untuk analisis risiko")
                else:
                    # Display risk summary
                    col1, col2, col3 = st.columns(3)
                    high_risk = len(risk_data[risk_data['tingkat_risiko'] == 'Tinggi'])
                    medium_risk = len(risk_data[risk_data['tingkat_risiko'] == 'Sedang'])
                    low_risk = len(risk_data[risk_data['tingkat_risiko'] == 'Rendah'])
                    
                    with col1:
                        st.metric("PLO Berisiko Tinggi", high_risk)
                    with col2:
                        st.metric("PLO Berisiko Sedang", medium_risk)
                    with col3:
                        st.metric("PLO Berisiko Rendah", low_risk)
                    
                    # Risk visualization
                    st.subheader("📊 Distribusi Tingkat Risiko")
                    fig = px.pie(risk_data, names='tingkat_risiko', 
                                title='Distribusi Tingkat Risiko PLO')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed risk table
                    st.subheader("📋 Detail Risk Assessment")
                    
                    # Style the dataframe based on risk level
                    def color_risk_level(val):
                        if val == 'Tinggi':
                            return 'background-color: #ffcccc'
                        elif val == 'Sedang':
                            return 'background-color: #fff4cc'
                        else:
                            return 'background-color: #ccffcc'
                    
                    styled_risk_data = risk_data.style.applymap(color_risk_level, subset=['tingkat_risiko'])
                    st.dataframe(styled_risk_data, use_container_width=True)
    
    with tab3:
        st.header("Kesiapan Kelulusan")
        
        # Simulasi data mahasiswa
        st.info("Fitur ini membutuhkan data performa individual mahasiswa")
        
        # Contoh implementasi sederhana
        if st.button("Analisis Kesiapan Kelulusan", type="primary"):
            # Dalam implementasi nyata, ini akan menggunakan data riil mahasiswa
            sample_student_data = pd.DataFrame({
                'kode_plo': ['PLO1', 'PLO2', 'PLO3', 'PLO8', 'PLO10', 'PLO11'],
                'nilai_rata_rata': [85, 78, 82, 75, 80, 72]
            })
            
            readiness_score = predictive_engine.predict_graduation_readiness(sample_student_data)
            
            st.metric("Skor Kesiapan Kelulusan", f"{readiness_score:.1f}%")
            
            # Progress bar
            st.progress(readiness_score / 100)
            
            if readiness_score >= 80:
                st.success("✅ Mahasiswa siap untuk lulus")
            elif readiness_score >= 70:
                st.warning("⚠️ Mahasiswa membutuhkan improvement di beberapa area")
            else:
                st.error("❌ Mahasiswa membutuhkan bantuan signifikan")
    
    with tab4:
        st.header("Advanced Analytics")
        
        if st.button("Jalankan Cluster Analysis", type="primary"):
            with st.spinner("Melakukan analisis clustering..."):
                cluster_results = advanced_engine.cluster_program_performance()
                
                if cluster_results is not None:
                    st.subheader("📊 Hasil Clustering Mata Kuliah")
                    
                    # Visualize clusters
                    fig = px.scatter(cluster_results, x='avg_score', y='score_std',
                                    color='cluster_label', size='avg_students',
                                    hover_data=['kode_mk'],
                                    title='Cluster Analysis Mata Kuliah')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.subheader("📋 Detail Cluster")
                    st.dataframe(cluster_results, use_container_width=True)
                else:
                    st.warning("Data tidak cukup untuk clustering analysis")
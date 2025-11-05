import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.database import OBEDatabase
from models.predictive_models import PredictiveAnalytics, AdvancedAnalytics
from utils.reporting import ReportGenerator
import warnings
warnings.filterwarnings('ignore')

# Konfigurasi halaman
st.set_page_config(
    page_title="Sistem OBE - Program Studi Sistem Informasi",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inisialisasi database dan utilities
@st.cache_resource
def init_database():
    return OBEDatabase()

@st.cache_resource
def init_predictive_analytics(database):
    return PredictiveAnalytics(database)

@st.cache_resource
def init_report_generator(database):
    return ReportGenerator(database)

db = init_database()
predictive_engine = init_predictive_analytics(db)
report_generator = init_report_generator(db)

# CSS Custom
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .risk-high { background-color: #ffcccc; padding: 5px; border-radius: 5px; }
    .risk-medium { background-color: #fff4cc; padding: 5px; border-radius: 5px; }
    .risk-low { background-color: #ccffcc; padding: 5px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar Navigation
    st.sidebar.title("🎓 OBE System")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio("Navigasi", [
        "Dashboard Utama",
        "Matriks PLO-CLO", 
        "Matriks IPO",
        "Manajemen Kurikulum",
        "Assessment & Analytics",
        "Predictive Analytics",
        "Automated Reporting"
    ])
    
    # Quick Actions di Sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Quick Actions")
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_resource.clear()
        st.rerun()
    
    if st.sidebar.button("📊 Generate Quick Report"):
        with st.spinner("Generating report..."):
            excel_report = report_generator.generate_excel_report()
            st.sidebar.download_button(
                label="📥 Download Excel Report",
                data=excel_report,
                file_name=f"obe_report_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    # Main App Logic
    if page == "Dashboard Utama":
        show_dashboard()
    elif page == "Matriks PLO-CLO":
        show_plo_clo_matrix()
    elif page == "Matriks IPO":
        show_ipo_matrix()
    elif page == "Manajemen Kurikulum":
        show_curriculum_management()
    elif page == "Assessment & Analytics":
        show_assessment_analytics()
    elif page == "Predictive Analytics":
        show_predictive_analytics()
    elif page == "Automated Reporting":
        show_automated_reporting()

def show_dashboard():
    st.markdown('<div class="main-header">🏠 Dashboard Sistem OBE</div>', unsafe_allow_html=True)
    
    # Load data
    plo_data = db.get_all_plo()
    mk_data = db.get_all_mata_kuliah()
    assessment_data = db.get_assessment_data()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total PLO", len(plo_data), "12 target")
    with col2:
        st.metric("Mata Kuliah", len(mk_data), f"{len(mk_data)} aktif")
    with col3:
        avg_achievement = calculate_avg_plo_achievement()
        st.metric("Pencapaian PLO", f"{avg_achievement}%", "±2% from target")
    with col4:
        st.metric("Tingkat Kepuasan", "4.2/5", "0.1 from last period")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Pencapaian PLO per Kategori")
        achievement_by_category = calculate_plo_achievement_by_category()
        if not achievement_by_category.empty:
            fig = px.bar(achievement_by_category, x='kategori', y='pencapaian_rata_rata',
                        color='pencapaian_rata_rata', color_continuous_scale='Viridis',
                        title='Rata-rata Pencapaian PLO per Kategori')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Risk Assessment PLO")
        risk_data = predictive_engine.calculate_plo_risk_assessment()
        if not risk_data.empty:
            risk_count = risk_data['tingkat_risiko'].value_counts()
            fig = px.pie(values=risk_count.values, names=risk_count.index,
                        title='Distribusi Tingkat Risiko PLO')
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent Assessments
    st.subheader("📈 Assessment Terbaru")
    if not assessment_data.empty:
        recent_assessments = assessment_data.nlargest(10, 'tahun')
        st.dataframe(recent_assessments[['kode_mk', 'kode_clo', 'tahun', 'semester', 'nilai_rata_rata']], 
                    use_container_width=True)
    else:
        st.info("Belum ada data assessment")

def calculate_avg_plo_achievement():
    """Menghitung rata-rata pencapaian PLO"""
    assessment_data = db.get_assessment_data()
    if assessment_data.empty:
        return 0
    return round(assessment_data['nilai_rata_rata'].mean(), 2)

def calculate_plo_achievement_by_category():
    """Menghitung pencapaian PLO per kategori"""
    assessment_data = db.get_assessment_data()
    plo_data = db.get_all_plo()
    
    if assessment_data.empty or plo_data.empty:
        return pd.DataFrame()
    
    # Merge data untuk analisis
    matrix_data = db.get_plo_clo_matrix()
    merged_data = pd.merge(assessment_data, matrix_data, on=['kode_mk', 'kode_clo'])
    
    achievement_by_category = merged_data.groupby('kategori')['nilai_rata_rata'].mean().reset_index()
    achievement_by_category.columns = ['kategori', 'pencapaian_rata_rata']
    achievement_by_category['pencapaian_rata_rata'] = achievement_by_category['pencapaian_rata_rata'].round(2)
    
    return achievement_by_category

# Implement other page functions similarly...

if __name__ == "__main__":
    main()
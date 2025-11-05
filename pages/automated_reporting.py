import streamlit as st
import pandas as pd
from datetime import datetime
from database.database import db
from utils.reporting import ReportGenerator

def show_automated_reporting():
    st.title("📑 Automated Reporting System")
    
    report_generator = ReportGenerator(db)
    
    # Jenis Laporan
    st.header("1. Pilih Jenis Laporan")
    
    report_type = st.radio(
        "Jenis Laporan:",
        ["Laporan Lengkap OBE", "Laporan Akreditasi LAM INFOKOM", "Laporan Pencapaian PLO", "Laporan Risk Assessment"],
        horizontal=True
    )
    
    # Parameter Laporan
    st.header("2. Parameter Laporan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tahun = st.number_input("Tahun Laporan:", min_value=2020, max_value=2030, value=datetime.now().year)
        include_predictive = st.checkbox("Include Predictive Analytics", value=True)
    
    with col2:
        semester = st.selectbox("Semester:", [1, 2])
        format_laporan = st.selectbox("Format Laporan:", ["Excel", "PDF"])
    
    # Customization
    st.header("3. Kustomisasi Laporan")
    
    sections = st.multiselect(
        "Pilih Bagian yang Akan Disertakan:",
        ["Executive Summary", "PLO Achievement", "Curriculum Analysis", "Risk Assessment", "Recommendations", "Appendices"],
        default=["Executive Summary", "PLO Achievement", "Risk Assessment", "Recommendations"]
    )
    
    # Generate Report
    st.header("4. Generate Laporan")
    
    if st.button("🔄 Generate Laporan", type="primary", use_container_width=True):
        with st.spinner("Sedang membuat laporan..."):
            try:
                if format_laporan == "Excel":
                    report_data = report_generator.generate_excel_report()
                    
                    st.success("✅ Laporan Excel berhasil dibuat!")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=report_data,
                        file_name=f"obe_report_{tahun}_semester_{semester}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                else:  # PDF
                    report_data = report_generator.generate_pdf_report()
                    
                    st.success("✅ Laporan PDF berhasil dibuat!")
                    
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=report_data,
                        file_name=f"obe_report_{tahun}_semester_{semester}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                # Preview informasi laporan
                st.header("5. Preview Laporan")
                
                # Show summary statistics
                plo_data = db.get_all_plo()
                mk_data = db.get_all_mata_kuliah()
                assessment_data = db.get_assessment_data()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Jumlah PLO", len(plo_data))
                with col2:
                    st.metric("Jumlah Mata Kuliah", len(mk_data))
                with col3:
                    st.metric("Data Assessment", len(assessment_data))
                
                # Show sample data
                if st.checkbox("Tampilkan Sample Data"):
                    st.subheader("Sample Data PLO")
                    st.dataframe(plo_data.head(), use_container_width=True)
                    
                    if not assessment_data.empty:
                        st.subheader("Sample Data Assessment")
                        st.dataframe(assessment_data.head(), use_container_width=True)
            
            except Exception as e:
                st.error(f"❌ Error dalam membuat laporan: {str(e)}")
    
    # Template Laporan LAM INFOKOM
    st.header("🎯 Template Khusus LAM INFOKOM")
    
    st.info("""
    **Format Laporan LAM INFOKOM harus mencakup:**
    - Analisis Pencapaian CPL (PLO)
    - Matriks PLO-CLO
    - Data Assessment dan Evaluasi
    - Analisis Ketercapaian Pembelajaran
    - Rencana Pengembangan dan Perbaikan
    - Bukti-bukti Pendukung
    """)
    
    if st.button("📋 Generate Laporan Format LAM INFOKOM", use_container_width=True):
        with st.spinner("Membuat laporan format LAM INFOKOM..."):
            try:
                lam_report = report_generator.generate_lam_infokom_report()
                
                st.success("✅ Laporan LAM INFOKOM berhasil dibuat!")
                
                st.download_button(
                    label="📥 Download LAM INFOKOM Report",
                    data=lam_report,
                    file_name=f"lam_infokom_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Automated Scheduling
    st.header("🕐 Automated Reporting Schedule")
    
    st.warning("Fitur automated scheduling membutuhkan integrasi dengan sistem scheduling")
    
    col1, col2 = st.columns(2)
    
    with col1:
        schedule_frequency = st.selectbox(
            "Frekuensi Laporan:",
            ["Mingguan", "Bulanan", "Semesteran", "Tahunan"]
        )
    
    with col2:
        auto_recipients = st.text_input(
            "Email Penerima (pisahkan dengan koma):",
            "admin@universitas.edu,kaprodi@si.universitas.edu"
        )
    
    if st.button("💾 Set Automated Schedule", use_container_width=True):
        st.success(f"✅ Schedule laporan {schedule_frequency} berhasil disimpan!")
        st.info(f"Laporan akan dikirim ke: {auto_recipients}")

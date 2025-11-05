import pandas as pd
import numpy as np
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Image
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

class ReportGenerator:
    def __init__(self, database):
        self.db = database
    
    def generate_excel_report(self):
        """Generate comprehensive Excel report untuk akreditasi"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Summary Dashboard
            summary_data = self._prepare_summary_data()
            summary_df = pd.DataFrame([summary_data])
            summary_df.to_excel(writer, sheet_name='Dashboard Summary', index=False)
            
            # Sheet 2: PLO Data
            plo_data = self.db.get_all_plo()
            plo_data.to_excel(writer, sheet_name='Data PLO', index=False)
            
            # Sheet 3: PLO-CLO Matrix
            matrix_data = self.db.get_plo_clo_matrix()
            matrix_data.to_excel(writer, sheet_name='Matriks PLO-CLO', index=False)
            
            # Sheet 4: Assessment Data
            assessment_data = self.db.get_assessment_data()
            assessment_data.to_excel(writer, sheet_name='Data Assessment', index=False)
            
            # Sheet 5: IPO Data
            ipo_data = self.db.get_ipo_data()
            ipo_data.to_excel(writer, sheet_name='Matriks IPO', index=False)
            
            # Sheet 6: Predictive Analytics
            predictive = PredictiveAnalytics(self.db)
            risk_data = predictive.calculate_plo_risk_assessment()
            if not risk_data.empty:
                risk_data.to_excel(writer, sheet_name='Analisis Risiko PLO', index=False)
            
            # Sheet 7: Recommendations
            recommendations = self._generate_recommendations()
            rec_df = pd.DataFrame(recommendations, columns=['Kategori', 'Rekomendasi', 'Prioritas'])
            rec_df.to_excel(writer, sheet_name='Rekomendasi', index=False)
        
        output.seek(0)
        return output
    
    def generate_pdf_report(self):
        """Generate professional PDF report untuk LAM INFOKOM"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        title = Paragraph("LAPORAN SISTEM OBE PROGRAM STUDI SISTEM INFORMASI", title_style)
        story.append(title)
        
        # Executive Summary
        story.append(Paragraph("1. Ringkasan Eksekutif", styles['Heading2']))
        summary = self._prepare_summary_data()
        
        summary_table_data = [
            ['Metric', 'Nilai'],
            ['Total PLO', summary['total_plo']],
            ['Total Mata Kuliah', summary['total_mk']],
            ['Rata-rata Pencapaian PLO', f"{summary['avg_plo_achievement']}%"],
            ['Tingkat Kepuasan Stakeholder', f"{summary['stakeholder_satisfaction']}/5"],
            ['Status Akreditasi', summary['accreditation_status']]
        ]
        
        summary_table = Table(summary_table_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.25*inch))
        
        # PLO Achievement
        story.append(Paragraph("2. Pencapaian Program Learning Outcomes", styles['Heading2']))
        plo_data = self.db.get_all_plo()
        assessment_data = self.db.get_assessment_data()
        
        if not assessment_data.empty:
            # Calculate PLO achievement
            matrix_data = self.db.get_plo_clo_matrix()
            merged_data = pd.merge(assessment_data, matrix_data, on=['kode_mk', 'kode_clo'])
            plo_achievement = merged_data.groupby('kode_plo')['nilai_rata_rata'].mean().reset_index()
            plo_achievement = pd.merge(plo_achievement, plo_data, on='kode_plo')
            plo_achievement.columns = ['Kode PLO', 'Pencapaian', 'Deskripsi', 'Kategori']
            plo_achievement['Pencapaian'] = plo_achievement['Pencapaian'].round(2)
            
            # Create table for PDF
            plo_table_data = [['Kode PLO', 'Deskripsi', 'Pencapaian (%)']]
            for _, row in plo_achievement.iterrows():
                plo_table_data.append([row['Kode PLO'], row['Deskripsi'], row['Pencapaian']])
            
            plo_table = Table(plo_table_data, colWidths=[1*inch, 3*inch, 1.5*inch])
            plo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))
            story.append(plo_table)
        
        story.append(Spacer(1, 0.25*inch))
        
        # Recommendations
        story.append(Paragraph("3. Rekomendasi Perbaikan", styles['Heading2']))
        recommendations = self._generate_recommendations()
        
        for i, rec in enumerate(recommendations[:5], 1):  # Show top 5 recommendations
            story.append(Paragraph(f"{i}. {rec['Kategori']}: {rec['Rekomendasi']}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _prepare_summary_data(self):
        """Mempersiapkan data summary untuk reporting"""
        plo_data = self.db.get_all_plo()
        mk_data = self.db.get_all_mata_kuliah()
        assessment_data = self.db.get_assessment_data()
        
        # Calculate average PLO achievement
        avg_achievement = 75.0  # Default
        if not assessment_data.empty:
            matrix_data = self.db.get_plo_clo_matrix()
            merged_data = pd.merge(assessment_data, matrix_data, on=['kode_mk', 'kode_clo'])
            avg_achievement = merged_data['nilai_rata_rata'].mean()
        
        return {
            'total_plo': len(plo_data),
            'total_mk': len(mk_data),
            'avg_plo_achievement': round(avg_achievement, 2),
            'stakeholder_satisfaction': 4.2,  # This would come from survey data
            'accreditation_status': 'Terakreditasi B',
            'report_date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def _generate_recommendations(self):
        """Generate rekomendasi berdasarkan analisis data"""
        predictive = PredictiveAnalytics(self.db)
        risk_data = predictive.calculate_plo_risk_assessment()
        
        recommendations = []
        
        if not risk_data.empty:
            high_risk_plo = risk_data[risk_data['tingkat_risiko'] == 'Tinggi']
            for _, row in high_risk_plo.iterrows():
                recommendations.append({
                    'Kategori': f"PLO {row['kode_plo']}",
                    'Rekomendasi': row['rekomendasi'],
                    'Prioritas': 'Tinggi'
                })
        
        # Add general recommendations
        recommendations.extend([
            {
                'Kategori': 'Kurikulum',
                'Rekomendasi': 'Review dan update kurikulum berdasarkan feedback industri',
                'Prioritas': 'Sedang'
            },
            {
                'Kategori': 'Assessment',
                'Rekomendasi': 'Implementasi assessment berbasis project untuk PLO praktikal',
                'Prioritas': 'Tinggi'
            },
            {
                'Kategori': 'Infrastruktur',
                'Rekomendasi': 'Upgrade laboratorium untuk mendukung emerging technologies',
                'Prioritas': 'Sedang'
            }
        ])
        
        return recommendations
    
    def generate_lam_infokom_report(self):
        """Generate report khusus format LAM INFOKOM"""
        # This would include specific templates and formats required by LAM INFOKOM
        return self.generate_pdf_report()
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class PredictiveAnalytics:
    def __init__(self, database):
        self.db = database
    
    def prepare_plo_timeseries_data(self):
        """Mempersiapkan data time series untuk analisis PLO"""
        assessment_data = self.db.get_assessment_data()
        
        if assessment_data.empty:
            return pd.DataFrame()
        
        # Agregasi data per PLO per periode
        plo_matrix = self.db.get_plo_clo_matrix()
        
        merged_data = pd.merge(assessment_data, plo_matrix, 
                             on=['kode_mk', 'kode_clo'], how='left')
        
        # Group by PLO dan periode
        plo_timeseries = merged_data.groupby(['kode_plo', 'tahun', 'semester']).agg({
            'nilai_rata_rata': 'mean',
            'jumlah_mahasiswa': 'sum'
        }).reset_index()
        
        # Create time index
        plo_timeseries['periode'] = plo_timeseries['tahun'] + (plo_timeseries['semester'] - 1) / 2
        plo_timeseries = plo_timeseries.sort_values(['kode_plo', 'periode'])
        
        return plo_timeseries
    
    def predict_plo_trend(self, kode_plo, periods=2):
        """Memprediksi trend PLO untuk periode mendatang"""
        data = self.prepare_plo_timeseries_data()
        plo_data = data[data['kode_plo'] == kode_plo]
        
        if len(plo_data) < 3:
            return {"error": "Data tidak cukup untuk prediksi"}
        
        # Prepare features
        X = plo_data[['periode']].values
        y = plo_data['nilai_rata_rata'].values
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict future
        last_period = plo_data['periode'].max()
        future_periods = [last_period + 0.5 * (i+1) for i in range(periods)]
        
        predictions = model.predict(np.array(future_periods).reshape(-1, 1))
        
        # Ensure predictions are within reasonable bounds
        predictions = np.clip(predictions, 0, 100)
        
        result = {
            'plo': kode_plo,
            'current_performance': y[-1],
            'predictions': [
                {
                    'periode': future_periods[i],
                    'tahun': int(future_periods[i]),
                    'semester': 1 if (future_periods[i] % 1) < 0.5 else 2,
                    'predicted_score': round(float(predictions[i]), 2),
                    'trend': 'naik' if predictions[i] > y[-1] else 'turun'
                }
                for i in range(len(predictions))
            ],
            'confidence': round(r2_score(y, model.predict(X)), 3)
        }
        
        return result
    
    def calculate_plo_risk_assessment(self):
        """Menilai risiko pencapaian PLO"""
        data = self.prepare_plo_timeseries_data()
        
        if data.empty:
            return pd.DataFrame()
        
        risk_assessment = []
        
        for plo in data['kode_plo'].unique():
            plo_data = data[data['kode_plo'] == plo]
            
            if len(plo_data) < 2:
                continue
            
            # Calculate metrics
            current_score = plo_data['nilai_rata_rata'].iloc[-1]
            trend = np.polyfit(plo_data['periode'], plo_data['nilai_rata_rata'], 1)[0]
            volatility = plo_data['nilai_rata_rata'].std()
            participation_rate = plo_data['jumlah_mahasiswa'].mean()
            
            # Risk score calculation
            risk_score = 0
            if current_score < 70:
                risk_score += 3
            elif current_score < 75:
                risk_score += 2
            elif current_score < 80:
                risk_score += 1
            
            if trend < -1:
                risk_score += 3
            elif trend < 0:
                risk_score += 2
            elif trend < 0.5:
                risk_score += 1
            
            if volatility > 10:
                risk_score += 2
            elif volatility > 5:
                risk_score += 1
            
            # Risk level
            if risk_score >= 5:
                risk_level = "Tinggi"
            elif risk_score >= 3:
                risk_level = "Sedang"
            else:
                risk_level = "Rendah"
            
            # Recommendations
            recommendations = []
            if current_score < 75:
                recommendations.append("Perbaikan metode pembelajaran")
            if trend < 0:
                recommendations.append("Review kurikulum dan assessment")
            if volatility > 8:
                recommendations.append("Konsistensi penilaian perlu ditingkatkan")
            
            risk_assessment.append({
                'kode_plo': plo,
                'skor_terkini': round(current_score, 2),
                'trend': round(trend, 3),
                'volatilitas': round(volatility, 2),
                'partisipasi_rata': round(participation_rate, 0),
                'skor_risiko': risk_score,
                'tingkat_risiko': risk_level,
                'rekomendasi': "; ".join(recommendations) if recommendations else "Tidak ada rekomendasi khusus"
            })
        
        return pd.DataFrame(risk_assessment)
    
    def predict_graduation_readiness(self, mahasiswa_data):
        """Memprediksi kesiapan lulus berdasarkan performa PLO"""
        # This is a simplified version - in real implementation, you'd use more sophisticated models
        readiness_scores = []
        
        for plo in mahasiswa_data['kode_plo'].unique():
            plo_scores = mahasiswa_data[mahasiswa_data['kode_plo'] == plo]['nilai_rata_rata']
            avg_score = plo_scores.mean()
            
            # Weight based on PLO importance
            weight = 1.0
            if plo in ['PLO8', 'PLO10', 'PLO11']:  # PLO kunci untuk Sistem Informasi
                weight = 1.5
            
            readiness = min(100, (avg_score / 80) * 100 * weight)  # Normalize to 80 as target
            readiness_scores.append(readiness)
        
        overall_readiness = np.mean(readiness_scores) if readiness_scores else 0
        return min(100, overall_readiness)  # Cap at 100%

class AdvancedAnalytics:
    def __init__(self, database):
        self.db = database
    
    def cluster_program_performance(self):
        """Clustering performa program berdasarkan berbagai metrik"""
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        
        data = self.db.get_assessment_data()
        if data.empty:
            return None
        
        # Prepare features for clustering
        features = data.groupby('kode_mk').agg({
            'nilai_rata_rata': ['mean', 'std', 'count'],
            'jumlah_mahasiswa': 'mean'
        }).reset_index()
        
        features.columns = ['kode_mk', 'avg_score', 'score_std', 'assessment_count', 'avg_students']
        
        # Handle missing values
        features = features.fillna(features.mean())
        
        # Scale features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features[['avg_score', 'score_std', 'assessment_count', 'avg_students']])
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(scaled_features)
        
        features['cluster'] = clusters
        features['cluster_label'] = features['cluster'].map({
            0: 'Performa Tinggi',
            1: 'Performa Sedang', 
            2: 'Performa Rendah'
        })
        
        return features
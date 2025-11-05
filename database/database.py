import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

class OBEDatabase:
    def __init__(self, db_path="database/obe_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Membuat koneksi database"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database dengan tabel-tabel yang diperlukan"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabel PLO (Program Learning Outcomes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode_plo TEXT UNIQUE,
                deskripsi TEXT,
                kategori TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel Mata Kuliah
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mata_kuliah (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode_mk TEXT UNIQUE,
                nama_mk TEXT,
                semester INTEGER,
                sks INTEGER,
                deskripsi TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel CLO (Course Learning Outcomes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode_mk TEXT,
                kode_clo TEXT,
                deskripsi_clo TEXT,
                tingkat_taksonomi TEXT,
                FOREIGN KEY (kode_mk) REFERENCES mata_kuliah (kode_mk),
                UNIQUE(kode_mk, kode_clo)
            )
        ''')
        
        # Tabel PLO-CLO Mapping
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plo_clo_mapping (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode_mk TEXT,
                kode_clo TEXT,
                kode_plo TEXT,
                tingkat_penguasaan TEXT, -- I, R, M
                bobot NUMERIC,
                FOREIGN KEY (kode_mk) REFERENCES mata_kuliah (kode_mk),
                FOREIGN KEY (kode_clo) REFERENCES clo (kode_clo),
                FOREIGN KEY (kode_plo) REFERENCES plo (kode_plo)
            )
        ''')
        
        # Tabel Assessment
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assessment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode_mk TEXT,
                kode_clo TEXT,
                tahun INTEGER,
                semester INTEGER,
                jenis_assessment TEXT,
                nilai_rata_rata NUMERIC,
                jumlah_mahasiswa INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel IPO (Input-Process-Output)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ipo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                komponen TEXT,
                kategori TEXT, -- Input, Process, Output/Outcome
                bobot_lam INTEGER,
                target_pencapaian NUMERIC,
                pencapaian_aktual NUMERIC,
                status TEXT,
                catatan TEXT,
                tahun INTEGER,
                semester INTEGER
            )
        ''')
        
        # Tabel Mahasiswa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mahasiswa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nim TEXT UNIQUE,
                nama TEXT,
                angkatan INTEGER,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Insert sample data jika tabel kosong
        self.insert_sample_data()
    
    def insert_sample_data(self):
        """Insert sample data untuk testing"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Cek jika data sudah ada
        cursor.execute("SELECT COUNT(*) FROM plo")
        if cursor.fetchone()[0] == 0:
            # Insert sample PLO
            plo_data = [
                ('PLO1', 'Integritas dan Etika Profesional', 'Sikap'),
                ('PLO2', 'Kewirausahaan dan Inovasi', 'Sikap'),
                ('PLO3', 'Pengetahuan Fundamental TI', 'Pengetahuan'),
                ('PLO4', 'Manajemen Proyek TI', 'Pengetahuan'),
                ('PLO5', 'Komunikasi Efektif', 'Umum'),
                ('PLO6', 'Kerjasama Tim', 'Umum'),
                ('PLO7', 'Penelitian dan Analisis', 'Umum'),
                ('PLO8', 'Analisis Sistem Informasi', 'Khusus'),
                ('PLO9', 'Manajemen Layanan TI', 'Khusus'),
                ('PLO10', 'Pengembangan Aplikasi', 'Khusus'),
                ('PLO11', 'Analisis Data', 'Khusus'),
                ('PLO12', 'Keamanan Informasi', 'Khusus')
            ]
            cursor.executemany("INSERT INTO plo (kode_plo, deskripsi, kategori) VALUES (?, ?, ?)", plo_data)
            
            # Insert sample mata kuliah
            mk_data = [
                ('CSF101', 'Algoritma dan Pemrograman', 1, 3, 'Mata kuliah dasar pemrograman'),
                ('CSF102', 'Sistem Informasi Berbasis Data', 1, 3, 'Pengenalan sistem informasi'),
                ('CSF209', 'Basis Data', 3, 3, 'Konsep dan implementasi basis data'),
                ('G35444', 'Analisis dan Perancangan SI', 4, 3, 'Analisis dan perancangan sistem'),
                ('G35442', 'Pemrograman Web', 4, 3, 'Pemrograman web modern'),
                ('G35358', 'Infrastruktur TI', 5, 3, 'Manajemen infrastruktur TI')
            ]
            cursor.executemany("INSERT INTO mata_kuliah (kode_mk, nama_mk, semester, sks, deskripsi) VALUES (?, ?, ?, ?, ?)", mk_data)
        
        conn.commit()
        conn.close()
    
    # CRUD Operations untuk PLO
    def get_all_plo(self):
        conn = self.get_connection()
        df = pd.read_sql("SELECT * FROM plo ORDER BY kode_plo", conn)
        conn.close()
        return df
    
    def add_plo(self, kode_plo, deskripsi, kategori):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO plo (kode_plo, deskripsi, kategori) VALUES (?, ?, ?)",
                (kode_plo, deskripsi, kategori)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    # CRUD Operations untuk Mata Kuliah
    def get_all_mata_kuliah(self):
        conn = self.get_connection()
        df = pd.read_sql("SELECT * FROM mata_kuliah ORDER BY semester, kode_mk", conn)
        conn.close()
        return df
    
    def add_mata_kuliah(self, kode_mk, nama_mk, semester, sks, deskripsi):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO mata_kuliah (kode_mk, nama_mk, semester, sks, deskripsi) VALUES (?, ?, ?, ?, ?)",
                (kode_mk, nama_mk, semester, sks, deskripsi)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    # Operations untuk PLO-CLO Mapping
    def get_plo_clo_matrix(self):
        conn = self.get_connection()
        query = """
        SELECT 
            mk.kode_mk, mk.nama_mk, mk.semester,
            clo.kode_clo, clo.deskripsi_clo,
            plo.kode_plo, plo.deskripsi as deskripsi_plo,
            map.tingkat_penguasaan, map.bobot
        FROM plo_clo_mapping map
        JOIN mata_kuliah mk ON map.kode_mk = mk.kode_mk
        JOIN clo ON map.kode_clo = clo.kode_clo AND map.kode_mk = clo.kode_mk
        JOIN plo ON map.kode_plo = plo.kode_plo
        ORDER BY mk.semester, mk.kode_mk, clo.kode_clo
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    
    def add_plo_clo_mapping(self, kode_mk, kode_clo, kode_plo, tingkat_penguasaan, bobot=1.0):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO plo_clo_mapping 
                (kode_mk, kode_clo, kode_plo, tingkat_penguasaan, bobot) 
                VALUES (?, ?, ?, ?, ?)""",
                (kode_mk, kode_clo, kode_plo, tingkat_penguasaan, bobot)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    # Operations untuk Assessment
    def get_assessment_data(self, tahun=None, semester=None):
        conn = self.get_connection()
        query = "SELECT * FROM assessment"
        params = []
        if tahun:
            query += " WHERE tahun = ?"
            params.append(tahun)
        if semester:
            query += " AND semester = ?" if tahun else " WHERE semester = ?"
            params.append(semester)
        
        query += " ORDER BY tahun DESC, semester DESC"
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df
    
    def add_assessment(self, kode_mk, kode_clo, tahun, semester, jenis_assessment, nilai_rata_rata, jumlah_mahasiswa):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO assessment 
                (kode_mk, kode_clo, tahun, semester, jenis_assessment, nilai_rata_rata, jumlah_mahasiswa) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (kode_mk, kode_clo, tahun, semester, jenis_assessment, nilai_rata_rata, jumlah_mahasiswa)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            conn.close()
    
    # Operations untuk IPO
    def get_ipo_data(self):
        conn = self.get_connection()
        df = pd.read_sql("SELECT * FROM ipo ORDER BY kategori, komponen", conn)
        conn.close()
        return df
    
    def update_ipo_pencapaian(self, komponen, pencapaian_aktual, status, catatan):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE ipo SET pencapaian_aktual = ?, status = ?, catatan = ? WHERE komponen = ?",
                (pencapaian_aktual, status, catatan, komponen)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            conn.close()

# Global database instance
db = OBEDatabase()
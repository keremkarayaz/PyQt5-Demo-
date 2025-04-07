import sys
import os
import csv
from datetime import datetime
from collections import defaultdict
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QMessageBox,
    QComboBox, QInputDialog, QDialog, QFormLayout, QDialogButtonBox,
    QGroupBox, QDateEdit, QTabWidget, QFileDialog
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QPalette, QIcon
import xlsxwriter
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kullanıcı Girişi")
        self.setWindowIcon(QIcon('login_icon.png'))
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Kullanıcı Adı")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Şifre")
        self.password.setEchoMode(QLineEdit.Password)

        form_layout = QFormLayout()
        form_layout.addRow("Kullanıcı Adı:", self.username)
        form_layout.addRow("Şifre:", self.password)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def accept(self):
        # Basit bir kullanıcı doğrulama
        if self.username.text() == "admin" and self.password.text() == "1234":
            super().accept()
        else:
            QMessageBox.warning(self, "Hata", "Geçersiz kullanıcı adı veya şifre!")
            self.password.clear()


class GrafikRapor(QDialog):
    def __init__(self, stok_verileri):
        super().__init__()
        self.setWindowTitle("Grafiksel Raporlar")
        self.setWindowIcon(QIcon('chart_icon.png'))
        self.setGeometry(200, 200, 800, 600)

        self.stok_verileri = stok_verileri

        self.tabs = QTabWidget()

        # Kategori grafiği sekmesi
        self.kategori_tab = QWidget()
        self.kategori_grafik_olustur()
        self.tabs.addTab(self.kategori_tab, "Kategori Dağılımı")

        # Zaman grafiği sekmesi
        self.zaman_tab = QWidget()
        self.zaman_grafik_olustur()
        self.tabs.addTab(self.zaman_tab, "Zaman Serisi")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def kategori_grafik_olustur(self):
        # Kategorilere göre toplam stok değerini hesapla
        kategori_toplam = defaultdict(float)
        for veri in self.stok_verileri:
            kategori = veri["kategori"]
            toplam = float(veri["toplam"])
            kategori_toplam[kategori] += toplam

        # Grafik oluştur
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(kategori_toplam.values(), labels=kategori_toplam.keys(), autopct='%1.1f%%')
        ax.set_title("Kategori Bazlı Stok Dağılımı")

        # Grafiği pencereye ekle
        canvas = FigureCanvas(fig)
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        self.kategori_tab.setLayout(layout)

    def zaman_grafik_olustur(self):
        # Tarihlere göre stok girişlerini grupla
        tarih_toplam = defaultdict(float)
        for veri in self.stok_verileri:
            tarih = datetime.strptime(veri["tarih"], "%Y-%m-%d %H:%M:%S").date()
            tarih_str = tarih.strftime("%Y-%m-%d")
            toplam = float(veri["toplam"])
            tarih_toplam[tarih_str] += toplam

        # Grafik oluştur
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(list(tarih_toplam.keys()), list(tarih_toplam.values()), marker='o')
        ax.set_title("Zaman İçinde Stok Girişleri")
        ax.set_xlabel("Tarih")
        ax.set_ylabel("Toplam Değer (₺)")
        plt.xticks(rotation=45)

        # Grafiği pencereye ekle
        canvas = FigureCanvas(fig)
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        self.zaman_tab.setLayout(layout)


class StokUygulamasi(QWidget):
    def __init__(self):
        super().__init__()
        # Kullanıcı giriş kontrolü
        self.login = LoginWindow()
        if not self.login.exec_():
            sys.exit()

        self.setWindowTitle("Ürün Stok Takip Sistemi")
        self.setWindowIcon(QIcon('stock_icon.png'))
        self.setGeometry(300, 100, 1000, 700)

        # Arka plan rengi
        self.setStyleSheet("""
            background-color: #f0f0f0;
            font-family: Arial;
        """)

        # Layoutlar
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Filtreleme grubu
        self.filtre_grubu = QGroupBox("Gelişmiş Filtreleme")
        self.filtre_grubu.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                margin-top: 10px;
            }
        """)
        filtre_layout = QHBoxLayout()

        # Temel arama
        self.arama_input = QLineEdit()
        self.arama_input.setPlaceholderText("Ürün adıyla ara...")
        self.arama_input.textChanged.connect(self.urun_filtrele)

        # Kategori filtreleme
        self.kategori_filtre = QComboBox()
        self.kategori_filtre.addItem("Tüm Kategoriler")
        self.kategori_filtre.addItems(["Gıda", "Temizlik", "Elektronik", "Giyim", "Ofis", "Diğer"])
        self.kategori_filtre.currentIndexChanged.connect(self.urun_filtrele)

        # Tarih filtreleme
        self.baslangic_tarih = QDateEdit()
        self.baslangic_tarih.setDate(QDate.currentDate().addMonths(-1))
        self.baslangic_tarih.setCalendarPopup(True)
        self.baslangic_tarih.dateChanged.connect(self.urun_filtrele)

        self.bitis_tarih = QDateEdit()
        self.bitis_tarih.setDate(QDate.currentDate())
        self.bitis_tarih.setCalendarPopup(True)
        self.bitis_tarih.dateChanged.connect(self.urun_filtrele)

        filtre_layout.addWidget(QLabel("Arama:"))
        filtre_layout.addWidget(self.arama_input)
        filtre_layout.addWidget(QLabel("Kategori:"))
        filtre_layout.addWidget(self.kategori_filtre)
        filtre_layout.addWidget(QLabel("Başlangıç:"))
        filtre_layout.addWidget(self.baslangic_tarih)
        filtre_layout.addWidget(QLabel("Bitiş:"))
        filtre_layout.addWidget(self.bitis_tarih)

        self.filtre_grubu.setLayout(filtre_layout)
        self.main_layout.addWidget(self.filtre_grubu)

        # Giriş alanları
        self.giris_layout = QHBoxLayout()

        self.urun_adi_input = QLineEdit()
        self.urun_adi_input.setPlaceholderText("Ürün Adı")

        self.miktar_input = QLineEdit()
        self.miktar_input.setPlaceholderText("Miktar")

        self.fiyat_input = QLineEdit()
        self.fiyat_input.setPlaceholderText("Birim Fiyat (₺)")

        self.kategori_sec = QComboBox()
        self.kategori_sec.addItems(["Seçiniz", "Gıda", "Temizlik", "Elektronik", "Giyim", "Ofis", "Diğer"])

        self.ekle_button = QPushButton("Ürün Ekle")
        self.ekle_button.clicked.connect(self.urun_ekle)

        # Widget stilleri
        input_style = """
            background-color: #ffffff;
            border: 1px solid #dcdcdc;
            padding: 10px;
            font-size: 14px;
            border-radius: 5px;
        """
        button_style = """
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            font-size: 14px;
            border-radius: 5px;
            min-width: 100px;
        """

        for widget in [self.urun_adi_input, self.miktar_input, self.fiyat_input, self.kategori_sec]:
            widget.setStyleSheet(input_style)

        self.ekle_button.setStyleSheet(button_style)

        self.giris_layout.addWidget(self.urun_adi_input)
        self.giris_layout.addWidget(self.miktar_input)
        self.giris_layout.addWidget(self.fiyat_input)
        self.giris_layout.addWidget(self.kategori_sec)
        self.giris_layout.addWidget(self.ekle_button)

        self.main_layout.addLayout(self.giris_layout)

        # Tablo
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(6)
        self.tablo.setHorizontalHeaderLabels(["Ürün Adı", "Miktar", "Birim Fiyat", "Toplam", "Tarih", "Kategori"])
        self.tablo.setSelectionBehavior(QTableWidget.SelectRows)
        self.tablo.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tablo.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                font-size: 14px;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
                border: none;
            }
        """)
        self.tablo.horizontalHeader().setStretchLastSection(True)
        self.main_layout.addWidget(self.tablo)

        # Alt panel
        self.bottom_layout = QHBoxLayout()

        self.toplam_label = QLabel("Toplam Stok Tutarı: 0 ₺")
        self.toplam_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
        """)
        self.bottom_layout.addWidget(self.toplam_label)

        self.kategori_label = QLabel("Kategori Bazlı: ")
        self.kategori_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
        """)
        self.bottom_layout.addWidget(self.kategori_label)

        # Grafik butonu
        self.grafik_button = QPushButton("Grafik Rapor")
        self.grafik_button.clicked.connect(self.grafik_rapor_goster)
        self.grafik_button.setStyleSheet("""
            background-color: #9C27B0;
            color: white;
            padding: 10px;
            border: none;
            font-size: 14px;
            border-radius: 5px;
        """)
        self.bottom_layout.addWidget(self.grafik_button)

        self.kaydet_button = QPushButton("CSV Kaydet")
        self.kaydet_button.clicked.connect(self.kaydet_csv)
        self.kaydet_button.setStyleSheet("""
            background-color: #2196F3;
            color: white;
            padding: 10px;
            border: none;
            font-size: 14px;
            border-radius: 5px;
        """)
        self.bottom_layout.addWidget(self.kaydet_button)

        self.xlsx_button = QPushButton("XLSX Kaydet")
        self.xlsx_button.clicked.connect(self.kaydet_xlsx)
        self.xlsx_button.setStyleSheet("""
            background-color: #FF9800;
            color: white;
            padding: 10px;
            border: none;
            font-size: 14px;
            border-radius: 5px;
        """)
        self.bottom_layout.addWidget(self.xlsx_button)

        self.satis_button = QPushButton("Ürün Sat")
        self.satis_button.clicked.connect(self.urun_sat)
        self.satis_button.setStyleSheet("""
            background-color: #f44336;
            color: white;
            padding: 10px;
            border: none;
            font-size: 14px;
            border-radius: 5px;
        """)
        self.bottom_layout.addWidget(self.satis_button)

        self.main_layout.addLayout(self.bottom_layout)

        # Masaüstü yolu ve veri dosyası
        self.masaustu_yolu = os.path.join(os.path.expanduser("~"), "Desktop")
        self.veri_dosyasi = os.path.join(self.masaustu_yolu, "stok_verileri.json")

        # Verileri yükle
        self.verileri_yukle()

    def urun_ekle(self):
        urun_adi = self.urun_adi_input.text().strip()
        if not urun_adi:
            QMessageBox.warning(self, "Hata", "Ürün adı boş olamaz!")
            return

        try:
            miktar = int(self.miktar_input.text())
            fiyat = float(self.fiyat_input.text())
        except ValueError:
            QMessageBox.warning(self, "Hata", "Miktar ve fiyat sayısal olmalıdır.")
            return

        kategori = self.kategori_sec.currentText()
        if kategori == "Seçiniz":
            QMessageBox.warning(self, "Hata", "Lütfen bir kategori seçin.")
            return

        # Tarih ve saat
        tarih_saat = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        toplam = miktar * fiyat

        # Veriyi tabloya ekle
        satir = self.tablo.rowCount()
        self.tablo.insertRow(satir)
        self.tablo.setItem(satir, 0, QTableWidgetItem(urun_adi))
        self.tablo.setItem(satir, 1, QTableWidgetItem(str(miktar)))
        self.tablo.setItem(satir, 2, QTableWidgetItem(f"{fiyat:.2f}"))
        self.tablo.setItem(satir, 3, QTableWidgetItem(f"{toplam:.2f}"))
        self.tablo.setItem(satir, 4, QTableWidgetItem(tarih_saat))
        self.tablo.setItem(satir, 5, QTableWidgetItem(kategori))

        # Verileri dosyaya kaydet
        self.verileri_kaydet()

        # Giriş alanlarını temizle
        self.urun_adi_input.clear()
        self.miktar_input.clear()
        self.fiyat_input.clear()
        self.kategori_sec.setCurrentIndex(0)

        self.toplami_guncelle()

    def urun_filtrele(self):
        arama_metni = self.arama_input.text().lower()
        secili_kategori = self.kategori_filtre.currentText()
        baslangic_tarih = self.baslangic_tarih.date().toString("yyyy-MM-dd")
        bitis_tarih = self.bitis_tarih.date().toString("yyyy-MM-dd")

        for satir in range(self.tablo.rowCount()):
            urun_adi = self.tablo.item(satir, 0).text().lower()
            kategori = self.tablo.item(satir, 5).text()
            tarih = self.tablo.item(satir, 4).text().split()[0]  # Sadece tarih kısmını al

            # Filtreleme koşulları
            kategori_kosul = (secili_kategori == "Tüm Kategoriler") or (kategori == secili_kategori)
            arama_kosul = arama_metni in urun_adi
            tarih_kosul = (tarih >= baslangic_tarih) and (tarih <= bitis_tarih)

            # Tüm koşullar sağlanıyorsa göster, değilse gizle
            self.tablo.setRowHidden(satir, not (arama_kosul and kategori_kosul and tarih_kosul))

    def toplami_guncelle(self):
        toplam_deger = 0
        kategori_toplamlari = defaultdict(float)

        for satir in range(self.tablo.rowCount()):
            if not self.tablo.isRowHidden(satir):  # Sadece görünür satırları say
                try:
                    toplam = float(self.tablo.item(satir, 3).text())
                    kategori = self.tablo.item(satir, 5).text()
                    toplam_deger += toplam
                    kategori_toplamlari[kategori] += toplam
                except:
                    pass

        self.toplam_label.setText(f"Toplam Stok Tutarı: {toplam_deger:.2f} ₺")

        kategori_yazisi = "Kategori Bazlı: " + ", ".join(
            [f"{k}: {v:.2f}₺" for k, v in kategori_toplamlari.items()]
        )
        self.kategori_label.setText(kategori_yazisi)

    def kaydet_csv(self):
        dosya_yolu, _ = QFileDialog.getSaveFileName(self, "CSV Olarak Kaydet",
                                                    os.path.join(self.masaustu_yolu, "stok_verileri.csv"),
                                                    "CSV Dosyaları (*.csv)")
        if not dosya_yolu:
            return

        try:
            with open(dosya_yolu, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(["Ürün Adı", "Miktar", "Birim Fiyat", "Toplam", "Tarih", "Kategori"])
                for satir in range(self.tablo.rowCount()):
                    if not self.tablo.isRowHidden(satir):  # Sadece görünür satırları kaydet
                        urun_adi = self.tablo.item(satir, 0).text()
                        miktar = self.tablo.item(satir, 1).text()
                        birim_fiyat = self.tablo.item(satir, 2).text()
                        toplam = self.tablo.item(satir, 3).text()
                        tarih = self.tablo.item(satir, 4).text()
                        kategori = self.tablo.item(satir, 5).text()
                        writer.writerow([urun_adi, miktar, birim_fiyat, toplam, tarih, kategori])
            QMessageBox.information(self, "Başarılı", "Veriler CSV olarak kaydedildi.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya kaydedilemedi: {str(e)}")

    def kaydet_xlsx(self):
        dosya_yolu, _ = QFileDialog.getSaveFileName(self, "XLSX Olarak Kaydet",
                                                    os.path.join(self.masaustu_yolu, "stok_verileri.xlsx"),
                                                    "Excel Dosyaları (*.xlsx)")
        if not dosya_yolu:
            return

        try:
            workbook = xlsxwriter.Workbook(dosya_yolu)
            worksheet = workbook.add_worksheet()

            # Başlıklar
            headers = ["Ürün Adı", "Miktar", "Birim Fiyat", "Toplam", "Tarih", "Kategori"]
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)

            # Veriler
            row = 1
            for satir in range(self.tablo.rowCount()):
                if not self.tablo.isRowHidden(satir):  # Sadece görünür satırları kaydet
                    worksheet.write(row, 0, self.tablo.item(satir, 0).text())
                    worksheet.write(row, 1, self.tablo.item(satir, 1).text())
                    worksheet.write(row, 2, float(self.tablo.item(satir, 2).text()))
                    worksheet.write(row, 3, float(self.tablo.item(satir, 3).text()))
                    worksheet.write(row, 4, self.tablo.item(satir, 4).text())
                    worksheet.write(row, 5, self.tablo.item(satir, 5).text())
                    row += 1

            workbook.close()
            QMessageBox.information(self, "Başarılı", "Veriler XLSX olarak kaydedildi.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya kaydedilemedi: {str(e)}")

    def urun_sat(self):
        selected_row = self.tablo.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen satılacak ürünü seçin!")
            return

        urun_adi = self.tablo.item(selected_row, 0).text()
        miktar, ok = QInputDialog.getInt(self, "Ürün Sat",
                                         f"{urun_adi} ürününden kaç adet satılacak?",
                                         min=1, max=int(self.tablo.item(selected_row, 1).text()))

        if ok:
            yeni_miktar = int(self.tablo.item(selected_row, 1).text()) - miktar
            if yeni_miktar <= 0:
                self.tablo.removeRow(selected_row)
            else:
                self.tablo.item(selected_row, 1).setText(str(yeni_miktar))
                birim_fiyat = float(self.tablo.item(selected_row, 2).text())
                self.tablo.item(selected_row, 3).setText(f"{yeni_miktar * birim_fiyat:.2f}")

            self.verileri_kaydet()
            self.toplami_guncelle()

    def grafik_rapor_goster(self):
        # Tablodaki verileri al
        veriler = []
        for satir in range(self.tablo.rowCount()):
            veriler.append({
                "urun_adi": self.tablo.item(satir, 0).text(),
                "miktar": self.tablo.item(satir, 1).text(),
                "birim_fiyat": self.tablo.item(satir, 2).text(),
                "toplam": self.tablo.item(satir, 3).text(),
                "tarih": self.tablo.item(satir, 4).text(),
                "kategori": self.tablo.item(satir, 5).text()
            })

        if not veriler:
            QMessageBox.warning(self, "Uyarı", "Grafik oluşturmak için yeterli veri yok!")
            return

        self.grafik_rapor = GrafikRapor(veriler)
        self.grafik_rapor.exec_()

    def verileri_kaydet(self):
        veriler = []
        for satir in range(self.tablo.rowCount()):
            veriler.append({
                "urun_adi": self.tablo.item(satir, 0).text(),
                "miktar": self.tablo.item(satir, 1).text(),
                "birim_fiyat": self.tablo.item(satir, 2).text(),
                "toplam": self.tablo.item(satir, 3).text(),
                "tarih": self.tablo.item(satir, 4).text(),
                "kategori": self.tablo.item(satir, 5).text()
            })

        with open(self.veri_dosyasi, "w", encoding='utf-8') as f:
            json.dump(veriler, f, ensure_ascii=False, indent=4)

    def verileri_yukle(self):
        if os.path.exists(self.veri_dosyasi):
            try:
                with open(self.veri_dosyasi, "r", encoding='utf-8') as f:
                    veriler = json.load(f)
                    for veri in veriler:
                        satir = self.tablo.rowCount()
                        self.tablo.insertRow(satir)
                        self.tablo.setItem(satir, 0, QTableWidgetItem(veri["urun_adi"]))
                        self.tablo.setItem(satir, 1, QTableWidgetItem(veri["miktar"]))
                        self.tablo.setItem(satir, 2, QTableWidgetItem(veri["birim_fiyat"]))
                        self.tablo.setItem(satir, 3, QTableWidgetItem(veri["toplam"]))
                        self.tablo.setItem(satir, 4, QTableWidgetItem(veri["tarih"]))
                        self.tablo.setItem(satir, 5, QTableWidgetItem(veri["kategori"]))

                    self.toplami_guncelle()
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Veri dosyası okunamadı: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Daha modern bir görünüm için

    # Pencereyi göster
    window = StokUygulamasi()
    window.show()

    sys.exit(app.exec_())




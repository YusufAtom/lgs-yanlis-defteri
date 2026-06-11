import os
import streamlit as st
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

IMAGE_DIR = "yanlis_sorular"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

if "sorular" not in st.session_state:
    st.session_state.sorular = []

st.set_page_config(page_title="LGS Yanlış Defterim", page_icon="📚", layout="centered")

st.title("📚 LGS Yanlış Defteri")
st.write("Soruyu tablet/telefondan çek, hafta sonu bilgisayardan PDF çıktı al!")

tab_ekle, tab_incele, tab_pdf = st.tabs(["➕ Soru Ekle", "🧐 İncele", "🖨️ PDF Üret"])

with tab_ekle:
    st.subheader("Yeni Yanlış Soru Fotoğrafı")
    dersler = ["Matematik", "Fen Bilimleri", "Türkçe", "T.C. İnkılap Tarihi", "Din Kültürü", "İngilizce"]
    secilen_ders = st.selectbox("Ders Seçin", dersler)
    
    kameralı_yukleme = st.radio("Yükleme Yöntemi", ["📸 Kamerayı Aç (Anlık Çek)", "📁 Galeriden / Dosyalardan Seç"])
    
    uploaded_file = None
    if kameralı_yukleme == "📸 Kamerayı Aç (Anlık Çek)":
        uploaded_file = st.camera_input("Sorunun fotoğrafını çekin")
    else:
        uploaded_file = st.file_uploader("Galeriden fotoğraf seçin", type=["jpg", "jpeg", "png"])
        
    notlar = st.text_input("Not veya Doğru Cevap (Opsiyonel)")

    if st.button("Soruyu Deftere Kaydet", use_container_width=True):
        if uploaded_file is not None:
            img_path = os.path.join(IMAGE_DIR, f"{secilen_ders}_{len(st.session_state.sorular)+1}.png")
            image = Image.open(uploaded_file)
            image.save(img_path)
            
            st.session_state.sorular.append({
                "ders": secilen_ders,
                "resim_yolu": img_path,
                "not": notlar
            })
            st.success(f"✅ {secilen_ders} sorusu kaydedildi!")
        else:
            st.error("Lütfen önce fotoğraf çekin veya yükleyin.")

with tab_incele:
    st.subheader("Biriken Sorularınız")
    if not st.session_state.sorular:
        st.info("Henüz soru eklenmemiş.")
    else:
        filtre_ders = st.selectbox("Ders Filtresi", ["Hepsi"] + dersler)
        for idx, soru in enumerate(st.session_state.sorular):
            if filtre_ders != "Hepsi" and soru["ders"] != filtre_ders:
                continue
            st.write(f"**Soru {idx+1} - {soru['ders']}**")
            st.image(soru["resim_yolu"], use_column_width=True)
            if soru["not"]:
                st.info(f"📝 Not: {soru['not']}")
            st.divider()

with tab_pdf:
    st.subheader("Hafta Sonu Çıktısı Al")
    if not st.session_state.sorular:
        st.warning("PDF üretmek için soru olmalı.")
    else:
        pdf_filename = "Hafta_Sonu_Yanlis_Defteri.pdf"
        if st.button("📄 PDF Kitapçığı Oluştur", use_container_width=True):
            doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=TA_CENTER, spaceAfter=20)
            story.append(Paragraph("<b>HAFTA SONU YANLIŞ TEKRAR KİTAPÇIĞI</b>", title_style))
            
            for idx, soru in enumerate(st.session_state.sorular):
                story.append(Paragraph(f"<b>Soru {idx+1} ({soru['ders']})</b>", styles['Normal']))
                story.append(Spacer(1, 10))
                story.append(RLImage(soru["resim_yolu"], width=350, height=280, kind='bound'))
                story.append(Spacer(1, 40))
            
            doc.build(story)
            
            with open(pdf_filename, "rb") as f:
                st.download_button(
                    label="📥 PDF'i İndir",
                    data=f,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    use_container_width=True
                )
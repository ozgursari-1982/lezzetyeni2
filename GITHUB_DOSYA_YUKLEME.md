# GitHub'a Dosya Yükleme Rehberi

Bu rehber, elinizdeki dosyaları GitHub repository'sine nasıl yükleyeceğinizi adım adım açıklamaktadır.

## İçindekiler
1. [Git ve GitHub Nedir?](#git-ve-github-nedir)
2. [Gerekli Hazırlık](#gerekli-hazırlık)
3. [Yöntem 1: Web Arayüzü ile Dosya Yükleme](#yöntem-1-web-arayüzü-ile-dosya-yükleme)
4. [Yöntem 2: Git Komut Satırı ile Dosya Yükleme](#yöntem-2-git-komut-satırı-ile-dosya-yükleme)
5. [.gitignore - Hangi Dosyalar Yüklenmemeli?](#gitignore---hangi-dosyalar-yüklenmemeli)
6. [Sık Karşılaşılan Sorunlar](#sık-karşılaşılan-sorunlar)
7. [Faydalı Git Komutları](#faydalı-git-komutları)

---

## Git ve GitHub Nedir?

**Git**: Dosyalarınızdaki değişiklikleri takip eden bir versiyon kontrol sistemidir.

**GitHub**: Git repository'lerini (proje dosyalarınızı) bulutta saklayan ve paylaşmanıza olanak tanıyan bir platformdur.

---

## Gerekli Hazırlık

### 1. Git Kurulumu
Git'in bilgisayarınızda kurulu olup olmadığını kontrol edin:

```bash
git --version
```

Eğer kurulu değilse:
- **Windows**: [git-scm.com](https://git-scm.com/download/win) adresinden indirin
- **Mac**: `brew install git` veya [git-scm.com](https://git-scm.com/download/mac)
- **Linux**: `sudo apt-get install git` (Ubuntu/Debian) veya `sudo yum install git` (CentOS/RHEL)

### 2. Git Yapılandırması
İlk kez kullanıyorsanız, kimlik bilgilerinizi ayarlayın:

```bash
git config --global user.name "Adınız Soyadınız"
git config --global user.email "email@example.com"
```

### 3. GitHub Hesabı
[GitHub.com](https://github.com) adresinden ücretsiz bir hesap oluşturun.

---

## Yöntem 1: Web Arayüzü ile Dosya Yükleme

Bu yöntem **tek veya birkaç dosya** yüklemek için uygundur.

### Adım 1: Repository'nize Gidin
1. GitHub'da oturum açın
2. Dosya yüklemek istediğiniz repository'ye gidin (örn: `kullanici-adi/proje-adi`)

### Adım 2: Dosya Ekleyin
1. **"Add file"** düğmesine tıklayın
2. **"Upload files"** seçeneğini seçin
3. Dosyalarınızı sürükle-bırak yapın veya **"choose your files"** ile seçin

### Adım 3: Commit Edin
1. Commit mesajı yazın (örn: "Menü resimleri eklendi")
2. İsteğe bağlı açıklama ekleyin
3. **"Commit changes"** düğmesine tıklayın

✅ **Avantajlar**: Basit ve hızlı
❌ **Dezavantajlar**: Çok sayıda dosya veya klasör için uygun değil

---

## Yöntem 2: Git Komut Satırı ile Dosya Yükleme

Bu yöntem **çok sayıda dosya veya tüm proje** için önerilir.

### İlk Defa Kullanıyorsanız: Repository'yi Clone Edin

```bash
# Repository'yi bilgisayarınıza indirin
git clone https://github.com/kullanici-adi/proje-adi.git

# Proje klasörüne girin
cd proje-adi
```

### Dosyalarınızı Ekleyin

#### 1. Dosyalarınızı Proje Klasörüne Kopyalayın
Yüklemek istediğiniz dosyaları proje klasörünüze kopyalayın.

Örnek:
```
proje-adi/
├── app/
├── database/
├── yeni_menu.pdf          ← Yeni dosyanız
├── resimler/              ← Yeni klasörünüz
│   ├── yemek1.jpg
│   └── yemek2.jpg
└── README.md
```

#### 2. Dosyaları Git'e Ekleyin

```bash
# Tüm yeni/değişen dosyaları ekle
git add .

# Veya belirli dosyaları ekle
git add yeni_menu.pdf
git add resimler/yemek1.jpg
```

#### 3. Değişiklikleri Kaydedin (Commit)

```bash
git commit -m "Menü ve yemek resimleri eklendi"
```

#### 4. GitHub'a Yükleyin (Push)

```bash
git push origin main
```

veya branch'iniz farklıysa:
```bash
git push origin master
```

### 🎯 Tüm İşlem Özeti (Hızlı Referans)

```bash
# 1. Repository'yi clone edin (sadece ilk kez)
git clone https://github.com/kullanici-adi/proje-adi.git
cd proje-adi

# 2. Dosyalarınızı kopyalayın

# 3. Git'e ekleyin ve yükleyin
git add .
git commit -m "Açıklayıcı mesajınız"
git push origin main
```

### Varolan Bir Repository'de Çalışıyorsanız

Eğer proje zaten bilgisayarınızda varsa:

```bash
# 1. Proje klasörüne gidin
cd proje-adi

# 2. En son değişiklikleri çekin
git pull origin main

# 3. Dosyalarınızı ekleyin

# 4. Git'e ekleyin ve yükleyin
git add .
git commit -m "Açıklayıcı mesajınız"
git push origin main
```

---

## .gitignore - Hangi Dosyalar Yüklenmemeli?

Bazı dosyalar GitHub'a yüklenmemelidir. Bu dosyaları `.gitignore` dosyasına ekleyin.

### Yüklenmemesi Gereken Dosyalar:

1. **Hassas Bilgiler**
   - `.env` (şifreler, API anahtarları)
   - Veritabanı dosyaları (kullanıcı bilgileri içerenler)
   - Konfigürasyon dosyaları (gerçek şifreler içerenler)

2. **Sistem Dosyaları**
   - `.DS_Store` (Mac)
   - `Thumbs.db` (Windows)
   - `.idea/`, `.vscode/` (IDE ayarları)

3. **Geçici ve Oluşturulan Dosyalar**
   - `__pycache__/`, `*.pyc` (Python derlenmiş dosyaları)
   - `node_modules/` (JavaScript bağımlılıkları)
   - `venv/`, `env/` (Python sanal ortamı)
   - `*.log` (log dosyaları)
   - `dist/`, `build/` (build dosyaları)

### Örnek .gitignore Dosyası:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Flask
instance/
.env
*.db

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Build
dist/
build/
```

### .gitignore Nasıl Kullanılır?

```bash
# 1. Proje kök dizininde .gitignore oluşturun
touch .gitignore

# 2. Yukarıdaki içeriği ekleyin

# 3. Git'e kaydedin
git add .gitignore
git commit -m "gitignore eklendi"
git push origin main
```

---

## Sık Karşılaşılan Sorunlar

### 1. "Permission denied" Hatası

**Sorun**: GitHub'a push yaparken yetki hatası

**Çözüm**:
```bash
# SSH key oluşturun ve GitHub'a ekleyin
ssh-keygen -t ed25519 -C "email@example.com"
cat ~/.ssh/id_ed25519.pub  # Bu çıktıyı GitHub Settings > SSH Keys'e ekleyin
```

veya HTTPS ile Personal Access Token kullanın:
- GitHub Settings > Developer settings > Personal access tokens
- Token oluşturun ve şifre yerine kullanın

### 2. "Files are too large" Hatası

**Sorun**: Dosya boyutu 100MB'dan büyük

**Çözüm**:
- Git LFS (Large File Storage) kullanın
- Veya dosyayı dış bir depolama servisinde saklayın (Google Drive, Dropbox vb.)

```bash
# Git LFS kurulumu
git lfs install
git lfs track "*.psd"  # Büyük dosya tipini belirtin
git add .gitattributes
```

### 3. "Merge Conflict" Hatası

**Sorun**: Aynı dosyada farklı değişiklikler yapılmış

**Çözüm**:
```bash
# En son değişiklikleri çekin
git pull origin main

# Çakışan dosyaları düzenleyin
# <<<<<<<, =======, >>>>>>> işaretlerini temizleyin

# Düzeltmeleri kaydedin
git add .
git commit -m "Merge conflict çözüldü"
git push origin main
```

### 4. "Already tracked file" - .gitignore Çalışmıyor

**Sorun**: Dosya zaten Git'te takip ediliyor

**Çözüm**:
```bash
# Dosyayı Git cache'inden kaldırın
git rm -r --cached .
git add .
git commit -m "gitignore düzeltmesi"
git push origin main
```

### 5. Yanlış Dosya Yüklendi

**Sorun**: Hassas bilgi içeren dosya yüklendi

**Çözüm (ACİL)**:
```bash
# Dosyayı hemen silin
git rm dosya_adi
git commit -m "Hassas dosya silindi"
git push origin main

# Not: Dosya geçmişte hala var!
# Tam silmek için: GitHub'da repository settings'den yardım alın
```

---

## Faydalı Git Komutları

```bash
# Durumu kontrol et
git status

# Değişiklikleri görüntüle
git diff

# Commit geçmişini görüntüle
git log --oneline

# Son commit'i geri al (dosyalar kalır)
git reset --soft HEAD~1

# Belirli bir dosyayı geri al
git checkout -- dosya_adi

# Branch oluştur ve geç
git checkout -b yeni-branch-adi

# Branch'ler arası geçiş
git checkout main
git checkout yeni-branch-adi

# Değişiklikleri başka bir branch'e aktar
git pull origin main
git push origin yeni-branch-adi
```

---

## Sonuç

Bu rehberi kullanarak dosyalarınızı güvenli bir şekilde GitHub'a yükleyebilirsiniz. 

### Hangi Yöntemi Seçmeliyim?

- **Web Arayüzü**: Tek dosya veya birkaç dosya için
- **Git Komut Satırı**: Çok sayıda dosya, klasör veya düzenli güncellemeler için

### Önemli Hatırlatmalar:

✅ Hassas bilgileri (şifreler, API anahtarları) asla GitHub'a yüklemeyin  
✅ `.gitignore` dosyasını kullanın  
✅ Anlamlı commit mesajları yazın  
✅ Düzenli olarak `git pull` yaparak güncel kalın  
✅ Büyük dosyalar için Git LFS kullanın  

---

## Ek Kaynaklar

- [Git Resmi Dokümantasyonu](https://git-scm.com/doc)
- [GitHub Rehberleri](https://guides.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Türkçe Git Kitabı](https://git-scm.com/book/tr/v2)

---

**Sorularınız için**: GitHub Issues'da soru açabilir veya ozgursari1982@gmail.com adresinden iletişime geçebilirsiniz.

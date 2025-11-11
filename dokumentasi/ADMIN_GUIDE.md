
# Panduan Administrator Hurtrock Music Store

## Daftar Isi
- [Pendahuluan](#pendahuluan)
- [Akses Admin Panel](#akses-admin-panel)
- [Dashboard Overview](#dashboard-overview)
- [Manajemen Produk](#manajemen-produk)
- [Manajemen Kategori](#manajemen-kategori)
- [Manajemen User](#manajemen-user)
- [Sistem Chat dan Customer Service](#sistem-chat-dan-customer-service)
- [Manajemen Pesanan](#manajemen-pesanan)
- [Konfigurasi Pembayaran](#konfigurasi-pembayaran)
- [Pengaturan Pengiriman](#pengaturan-pengiriman)
- [Manajemen Supplier](#manajemen-supplier)
- [Sistem Restock](#sistem-restock)
- [Laporan dan Analytics](#laporan-dan-analytics)
- [Pengaturan Toko](#pengaturan-toko)
- [Keamanan dan Backup](#keamanan-dan-backup)

## Pendahuluan

Selamat datang di panel administrasi Hurtrock Music Store. Panduan ini akan membantu administrator dalam mengelola seluruh aspek toko online, mulai dari manajemen produk hingga customer service.

### Hak Akses Admin
- **Admin**: Akses penuh ke semua fitur
- **Staff**: Akses terbatas (produk, chat, pesanan)
- **Buyer**: Akses customer biasa

### Akun Admin Default
- **Email**: admin@hurtrock.com
- **Password**: admin123 *(ganti segera)*

## Akses Admin Panel

### Login Admin

1. **Buka Website**: Akses halaman utama Hurtrock Music Store
2. **Login**: Klik "Login" dan masukkan kredensial admin
3. **Dashboard**: Setelah login, klik nama pengguna > "Dashboard Admin"
4. **URL Langsung**: `/admin/dashboard`

### Navigation Sidebar

Panel admin memiliki sidebar dengan menu:
- **Dashboard**: Overview dan statistik
- **Produk**: Manajemen katalog produk
- **Kategori**: Pengaturan kategori produk
- **Users**: Manajemen pengguna
- **Chat**: Customer service dan komunikasi
- **Pesanan**: Manajemen order dan fulfillment
- **Payment**: Konfigurasi payment gateway
- **Pengiriman**: Setup jasa kirim
- **Supplier**: Manajemen pemasok
- **Restock**: Sistem pengadaan barang
- **Pengaturan**: Konfigurasi toko

## Dashboard Overview

Dashboard admin menampilkan ringkasan performa toko:

### Widget Utama
- **Total Pesanan**: Jumlah order hari ini/bulan ini
- **Revenue**: Pendapatan periode tertentu
- **Produk Terjual**: Top selling products
- **Chat Aktif**: Jumlah chat yang perlu direspon
- **User Baru**: Registrasi pengguna baru
- **Stok Rendah**: Produk yang perlu restock

### Grafik Analytics
- **Sales Chart**: Trend penjualan harian/bulanan
- **Category Performance**: Performa per kategori
- **User Growth**: Pertumbuhan jumlah user
- **Payment Method**: Distribusi metode pembayaran

### Quick Actions
- **Tambah Produk Baru**
- **Lihat Chat Pending**
- **Process Orders**
- **Generate Report**

## Manajemen Produk

### Menambah Produk Baru

1. **Navigasi**: Dashboard > Produk > "Tambah Produk"
2. **Informasi Dasar**:
   - **Nama Produk**: Nama yang jelas dan deskriptif
   - **Kategori**: Pilih dari dropdown
   - **Brand**: Merek produk
   - **Model**: Model/seri produk
   - **SKU**: Kode unik produk

3. **Pricing & Stock**:
   - **Harga**: Harga jual (Rupiah)
   - **Stok**: Jumlah tersedia
   - **Minimum Stock**: Batas minimum untuk alert restock

4. **Deskripsi**:
   - **Deskripsi Singkat**: 1-2 kalimat ringkasan
   - **Deskripsi Detail**: Spesifikasi lengkap, fitur, keunggulan

5. **Media**:
   - **Upload Gambar**: Maksimal 5MB, format JPG/PNG
   - **URL Gambar**: Alternatif menggunakan URL eksternal

6. **Dimensi & Shipping**:
   - **Berat**: Dalam gram (untuk kalkulasi ongkir)
   - **Dimensi**: Panjang x Lebar x Tinggi (cm)
   - **Supplier**: Pilih supplier produk

7. **Status**: Aktif/Non-aktif, Featured/Non-featured

### Mengedit Produk

1. **Navigasi**: Dashboard > Produk
2. **Cari Produk**: Gunakan search atau filter
3. **Edit**: Klik tombol edit
4. **Update**: Ubah data yang diperlukan
5. **Simpan**: Klik "Update Produk"

### Manajemen Stok

- **Bulk Update**: Update stok multiple produk sekaligus
- **Stock Alert**: Notifikasi otomatis untuk stok rendah
- **Stock History**: Tracking perubahan stok
- **Auto Deduct**: Stok otomatis berkurang saat ada penjualan

### Featured Products

Produk unggulan yang ditampilkan di homepage:
- **Set Featured**: Centang "Featured" saat edit produk
- **Maksimal 8 produk**: Featured di homepage
- **Rotasi**: Update berkala untuk variasi

## Manajemen Kategori

### Membuat Kategori Baru

1. **Navigasi**: Dashboard > Kategori
2. **Form Kategori**:
   - **Nama**: Nama kategori (contoh: "Gitar Akustik")
   - **Deskripsi**: Penjelasan kategori
   - **Gambar**: Upload gambar kategori
   - **Status**: Aktif/Non-aktif

3. **Simpan**: Klik "Tambah Kategori"

### Kategori Default
- **Gitar**: Akustik, elektrik, bass
- **Drum**: Acoustic, elektrik, perkusi
- **Keyboard**: Piano digital, synthesizer
- **Aksesoris**: Pick, cable, stand, case

### Mengelola Kategori

- **Edit**: Ubah nama, deskripsi, atau gambar
- **Nonaktifkan**: Hide kategori tanpa menghapus
- **Reorder**: Atur urutan tampilan kategori
- **Delete**: Hapus kategori (pastikan tidak ada produk terkait)

## Manajemen User

### Melihat Daftar User

Dashboard > Users menampilkan:
- **Informasi Dasar**: Nama, email, tanggal join
- **Role**: Admin, Staff, Buyer
- **Status**: Aktif/Non-aktif
- **Last Login**: Aktivitas terakhir
- **Total Orders**: Jumlah pesanan user
- **Total Spent**: Total pembelian user

### Menambah User Baru

1. **Navigasi**: Dashboard > Users > "Tambah User"
2. **Form User**:
   - **Nama**: Nama lengkap
   - **Email**: Email unik
   - **Password**: Password default (user wajib ganti)
   - **Role**: Pilih Admin/Staff/Buyer
   - **Status**: Aktif/Non-aktif

### Mengelola User

- **Edit Profile**: Update data user
- **Reset Password**: Generate password baru
- **Change Role**: Upgrade/downgrade hak akses
- **Deactivate**: Nonaktifkan akun tanpa hapus
- **View History**: Lihat riwayat pesanan dan aktivitas

### User Roles Detail

**Admin**:
- Akses penuh semua fitur
- Manage user lain
- Konfigurasi sistem
- Generate laporan

**Staff**:
- Manage produk dan kategori
- Handle customer service
- Process orders
- Manage chat

**Buyer**:
- Browse dan beli produk
- Chat dengan admin
- Manage profile sendiri

## Sistem Chat dan Customer Service

### Dashboard Chat

Dashboard > Chat menampilkan:
- **Active Chats**: Daftar chat yang aktif
- **Pending Messages**: Pesan yang belum direspon
- **Unread Count**: Jumlah pesan belum dibaca
- **Response Time**: Rata-rata waktu respon

### Mengelola Chat

1. **Akses Chat**: Dashboard > Chat
2. **Pilih Room**: Klik pada chat customer
3. **Interface Chat**:
   - **Message History**: Riwayat percakapan
   - **Customer Info**: Profile customer di sidebar
   - **Quick Replies**: Template respon cepat
   - **Product Tagging**: Tag produk untuk rekomendasi

### Fitur Chat Admin

**Product Tagging**:
1. **Klik Tombol Tag** di input chat
2. **Search Produk**: Ketik nama produk yang ingin direkomendasikan
3. **Pilih Produk**: Klik produk dari hasil pencarian
4. **Send Message**: Kirim pesan dengan link produk

**Quick Replies**:
- "Terima kasih telah menghubungi kami! Ada yang bisa kami bantu?"
- "Produk tersedia dengan stok terbatas. Apakah ingin langsung order?"
- "Untuk informasi lebih detail, silakan hubungi WhatsApp kami di 0821-1555-8035"

**Clear Chat**: Hapus riwayat chat (gunakan dengan hati-hati)

### Best Practices Customer Service

1. **Response Time**: Maksimal 5 menit saat online
2. **Friendly Tone**: Gunakan bahasa yang ramah dan profesional
3. **Product Knowledge**: Pahami spec dan fitur produk
4. **Follow Up**: Tanya apakah customer sudah puas dengan jawaban
5. **Escalation**: Forward ke admin jika ada complaint serius

### Template Responses

**Greeting**:
"Halo! Selamat datang di Hurtrock Music Store. Ada alat musik yang sedang dicari?"

**Product Inquiry**:
"Terima kasih atas minatnya pada [nama produk]. Produk ini memiliki fitur [spesifikasi]. Apakah ada pertanyaan spesifik?"

**Stock Inquiry**:
"Produk [nama] saat ini ready stock. Untuk pemesanan bisa langsung checkout di website atau chat kami untuk bantuan."

**Shipping**:
"Kami menggunakan berbagai kurir (JNE, J&T, SiCepat) dengan estimasi 1-3 hari kerja untuk area Jabodetabek."

**Payment**:
"Kami menerima pembayaran via Stripe (kartu kredit) dan Midtrans (transfer bank, e-wallet). Aman dan terpercaya."

## Manajemen Pesanan

### Dashboard Pesanan

Dashboard > Pesanan menampilkan:
- **Order List**: Daftar semua pesanan
- **Filter Status**: Pending, Paid, Shipped, Delivered, Cancelled
- **Search**: Cari berdasarkan nomor order atau nama customer
- **Export**: Download laporan pesanan

### Status Order Workflow

1. **Pending**: Pesanan baru, menunggu pembayaran
2. **Paid**: Pembayaran berhasil, siap diproses
3. **Processing**: Sedang disiapkan untuk pengiriman
4. **Shipped**: Sudah dikirim, nomor resi tersedia
5. **Delivered**: Sudah sampai di customer
6. **Cancelled**: Dibatalkan (refund jika sudah bayar)

### Memproses Pesanan

1. **Akses Detail**: Klik nomor order
2. **Verifikasi Pembayaran**: Cek status payment gateway
3. **Update Status**: Ubah ke "Processing"
4. **Siapkan Barang**: Koordinasi dengan gudang/supplier
5. **Shipping**:
   - Pilih kurir
   - Input nomor resi
   - Update status ke "Shipped"
6. **Follow Up**: Pantau status delivery

### Pengaturan Pengiriman

**Input Resi**:
1. **Edit Order**: Klik order yang akan dikirim
2. **Courier Service**: Pilih kurir (JNE, J&T, dll)
3. **Tracking Number**: Input nomor resi
4. **Update Status**: Otomatis jadi "Shipped"

**Notifikasi Customer**:
- Email otomatis dengan nomor resi
- Update di dashboard customer
- Chat notification (opsional)

### Handling Returns/Refunds

1. **Customer Request**: Via chat atau email
2. **Evaluasi**: Cek alasan dan kondisi produk
3. **Approval**: Setujui atau tolak dengan alasan
4. **Process**:
   - Return: Customer kirim balik produk
   - Refund: Process refund via payment gateway
   - Exchange: Kirim produk pengganti

## Konfigurasi Pembayaran

### Dashboard Payment Config

Dashboard > Payment menampilkan konfigurasi:
- **Stripe Configuration**: Setup kartu kredit internasional
- **Midtrans Configuration**: Setup payment lokal Indonesia
- **Active Methods**: Payment method yang aktif
- **Transaction Logs**: Riwayat transaksi

### Setup Stripe

1. **Create Account**: Daftar di stripe.com
2. **Get API Keys**:
   - **Publishable Key**: Untuk frontend
   - **Secret Key**: Untuk backend
3. **Add Configuration**:
   - Provider: Stripe
   - Environment: Sandbox/Production
   - Input API keys
   - Test transaction

### Setup Midtrans

1. **Create Account**: Daftar di midtrans.com
2. **Get Keys**:
   - **Server Key**: Untuk backend API
   - **Client Key**: Untuk frontend
3. **Configuration**:
   - Provider: Midtrans
   - Environment: Sandbox/Production
   - Input keys
   - Configure webhook URL

### Testing Payment

**Stripe Test Cards**:
- **Success**: 4242 4242 4242 4242
- **Decline**: 4000 0000 0000 0002
- **CVV**: 123, Exp: 12/34

**Midtrans Test**:
- **Virtual Account**: 8000000000000006
- **Credit Card**: 4811 1111 1111 1114

### Payment Monitoring

- **Transaction Status**: Real-time status update
- **Failed Payments**: Alert untuk payment gagal
- **Refund Processing**: Handle refund request
- **Settlement**: Monitoring settlement harian

## Pengaturan Pengiriman

### Manajemen Shipping Services

Dashboard > Shipping untuk mengatur:
- **Courier Services**: JNE, J&T, SiCepat, POS, Kurir Toko
- **Pricing**: Ongkir berdasarkan berat dan volume
- **Coverage Area**: Area yang dilayani
- **Delivery Time**: Estimasi waktu pengiriman

### Menambah Courier Service

1. **Add New Service**:
   - **Name**: Nama kurir (contoh: "JNE REG")
   - **Code**: Kode unik (contoh: "jne_reg")
   - **Base Price**: Harga dasar ongkir
   - **Per KG Price**: Harga per kilogram
   - **Per Volume Price**: Harga per volume (cm3)
   - **Min Days**: Estimasi minimum hari
   - **Max Days**: Estimasi maksimum hari

2. **Coverage Area**: Atur area yang dilayani
3. **Active Status**: Aktifkan service

### Kalkulasi Ongkir

System menghitung ongkir berdasarkan:
- **Base Price**: Harga dasar
- **Weight**: Berat total produk (gram)
- **Volume**: Volume total produk (cm3)
- **Distance**: Jarak ke lokasi customer (opsional)

**Formula**:
```
Total Ongkir = Base Price + (Weight * Per KG Price) + (Volume * Per Volume Price)
```

### Same Day Delivery

Untuk area Jakarta dan sekitarnya:
- **Kurir Toko**: Delivery khusus
- **Cutoff Time**: Order sebelum jam 14:00
- **Extra Charge**: Biaya tambahan
- **Tracking**: Real-time tracking via WhatsApp

## Manajemen Supplier

### Dashboard Supplier

Dashboard > Supplier untuk mengelola:
- **Supplier List**: Daftar semua supplier
- **Contact Information**: Kontak dan alamat
- **Product Assignment**: Produk yang disupply
- **Performance**: Rating dan evaluasi
- **Payment Terms**: Syarat pembayaran

### Menambah Supplier Baru

1. **Company Information**:
   - **Company Name**: Nama perusahaan
   - **Contact Person**: PIC supplier
   - **Email & Phone**: Kontak komunikasi
   - **Address**: Alamat lengkap

2. **Business Details**:
   - **Payment Terms**: NET 30, COD, dll
   - **Minimum Order**: MOQ (Minimum Order Quantity)
   - **Lead Time**: Waktu delivery supplier
   - **Notes**: Catatan khusus

### Assign Products ke Supplier

1. **Edit Product**: Pilih produk yang akan diassign
2. **Supplier Field**: Pilih supplier dari dropdown
3. **Supplier SKU**: Kode produk di supplier
4. **Cost Price**: Harga beli dari supplier

### Supplier Performance

Track performa supplier:
- **Delivery Performance**: Ketepatan waktu kirim
- **Quality Score**: Rating kualitas produk
- **Response Time**: Kecepatan respon komunikasi
- **Payment Compliance**: Kepatuhan syarat bayar

## Sistem Restock

### Restock Management

Dashboard > Restock untuk:
- **Low Stock Alert**: Produk yang perlu restock
- **Create Restock Order**: Buat order ke supplier
- **Track Incoming**: Monitor barang masuk
- **Update Inventory**: Update stok setelah terima barang

### Proses Restock

1. **Identify Low Stock**:
   - System alert untuk produk < minimum stock
   - Manual check inventory level
   - Sales forecast analysis

2. **Create Restock Order**:
   - **Supplier**: Pilih supplier produk
   - **Products**: Pilih produk yang direstock
   - **Quantity**: Tentukan jumlah order
   - **Expected Date**: Estimasi terima barang

3. **Send PO**: Kirim Purchase Order ke supplier
4. **Track Delivery**: Monitor status pengiriman
5. **Receive Goods**: Terima dan cek kualitas barang
6. **Update Stock**: Update stok di system

### Inventory Alerts

Setup alert untuk:
- **Low Stock**: Stok < minimum level
- **Out of Stock**: Stok = 0
- **Overstock**: Stok > maximum level
- **Expiry Alert**: Produk mendekati expired (jika ada)

### Restock Reports

Generate laporan:
- **Restock History**: Riwayat pengadaan
- **Supplier Performance**: Evaluasi supplier
- **Inventory Turnover**: Putaran stok
- **Cost Analysis**: Analisis biaya pengadaan

## Laporan dan Analytics

### Dashboard Analytics

Analytics menampilkan:
- **Sales Report**: Laporan penjualan harian/bulanan
- **Product Performance**: Produk terlaris
- **Customer Analytics**: Behavior dan demografi
- **Financial Report**: Revenue, profit, expenses
- **Inventory Report**: Stok dan movement

### Sales Analytics

**Revenue Metrics**:
- **Daily Revenue**: Pendapatan harian
- **Monthly Trend**: Trend bulanan
- **YoY Growth**: Pertumbuhan year-over-year
- **Average Order Value**: Rata-rata nilai order

**Product Performance**:
- **Top Selling**: Produk terlaris
- **Low Performers**: Produk kurang laku
- **Category Performance**: Performa per kategori
- **Margin Analysis**: Analisis margin profit

### Customer Analytics

**Customer Metrics**:
- **New Customers**: Customer baru per periode
- **Returning Customers**: Customer repeat
- **Customer Lifetime Value**: Nilai lifetime customer
- **Churn Rate**: Rate customer yang berhenti

**Behavior Analysis**:
- **Popular Products**: Produk paling dilihat
- **Conversion Rate**: Rate conversion visitor ke buyer
- **Cart Abandonment**: Rate keranjang ditinggalkan
- **Channel Performance**: Performa traffic source

### Export Reports

1. **Select Report Type**: Pilih jenis laporan
2. **Date Range**: Tentukan periode
3. **Filters**: Apply filter jika perlu
4. **Format**: Excel, PDF, atau CSV
5. **Download**: Export dan download laporan

## Pengaturan Toko

### Store Profile

Dashboard > Settings > Store Profile:
- **Store Name**: Nama toko
- **Tagline**: Slogan toko
- **Description**: Deskripsi singkat
- **Address**: Alamat lengkap toko
- **Contact Information**: Phone, email, website
- **Social Media**: Link sosial media
- **Operating Hours**: Jam operasional

### Business Settings

**General**:
- **Currency**: Rupiah (IDR)
- **Timezone**: Asia/Jakarta
- **Language**: Bahasa Indonesia
- **Tax Settings**: PPN dan pajak lainnya

**Operational**:
- **Order Processing Time**: SLA proses order
- **Shipping Cut-off**: Batas waktu same day shipping
- **Customer Service Hours**: Jam layanan chat
- **Return Policy**: Kebijakan retur dan refund

### Email Templates

Customize email templates:
- **Order Confirmation**: Konfirmasi pesanan
- **Payment Confirmation**: Konfirmasi pembayaran
- **Shipping Notification**: Notifikasi pengiriman
- **Delivery Confirmation**: Konfirmasi sampai
- **Welcome Email**: Email welcome user baru

### Maintenance Mode

Fitur maintenance untuk:
- **System Updates**: Update system tanpa gangguan
- **Scheduled Maintenance**: Maintenance terjadwal
- **Emergency Maintenance**: Maintenance darurat
- **Custom Message**: Pesan custom saat maintenance

## Keamanan dan Backup

### Security Best Practices

**Password Policy**:
- Minimum 8 karakter
- Kombinasi huruf, angka, symbol
- Ganti password berkala
- Tidak menggunakan password yang sama

**Access Control**:
- **2FA**: Two-factor authentication untuk admin
- **IP Whitelist**: Batasi akses dari IP tertentu
- **Session Timeout**: Auto logout setelah idle
- **Role-based Access**: Akses sesuai role

### Monitoring & Logging

**Activity Logs**:
- **User Activity**: Log aktivitas user
- **Admin Actions**: Log aksi admin
- **System Events**: Log event system
- **Error Logs**: Log error dan exception

**Security Monitoring**:
- **Failed Login Attempts**: Monitor login gagal
- **Suspicious Activity**: Aktivitas mencurigakan
- **Data Changes**: Track perubahan data penting
- **Access Violations**: Akses tidak authorized

### Backup Strategy

**Automated Backup**:
- **Database Backup**: Daily backup database
- **File Backup**: Weekly backup files
- **Config Backup**: Backup konfigurasi
- **Retention**: Simpan backup 30 hari

**Manual Backup**:
1. **Access Backup Tool**: Dashboard > Settings > Backup
2. **Select Type**: Database, Files, atau Full backup
3. **Create Backup**: Generate backup manual
4. **Download**: Download backup file

### Disaster Recovery

**Recovery Plan**:
1. **Assess Damage**: Evaluasi kerusakan
2. **Restore Backup**: Restore dari backup terakhir
3. **Validate Data**: Cek integritas data
4. **Test System**: Test semua fungsi
5. **Go Live**: Buka kembali untuk public

**Emergency Contacts**:
- **Developer**: [kontak developer]
- **Hosting Provider**: [kontak hosting]
- **Payment Gateway**: [kontak payment provider]
- **Domain Registrar**: [kontak domain]

---

## Shortcuts dan Tips

### Keyboard Shortcuts
- **Ctrl + /** : Buka search global
- **Ctrl + N**: Tambah produk baru
- **Ctrl + S**: Simpan form
- **Esc**: Tutup modal/popup

### Quick Actions
- **Hover pada produk**: Quick action edit/delete
- **Double click pada order**: Buka detail order
- **Right click pada chat**: Quick reply options

### Performance Tips
- **Image Optimization**: Kompres gambar sebelum upload
- **Bulk Operations**: Gunakan bulk action untuk efisiensi
- **Regular Cleanup**: Hapus data yang tidak perlu
- **Monitor Resources**: Check server resource usage

---

*Panduan ini akan terus diperbarui sesuai dengan penambahan fitur dan perubahan system. Untuk pertanyaan teknis lebih lanjut, hubungi tim developer.*

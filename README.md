https://r2.fivemanage.com/WX5Hv6yMgODTgG2WF6rml/images/backgroundgithub.png

# Bot Discord Search Player Name FiveM

Bot Discord untuk memantau server FiveM secara langsung melalui CFX API. Bot ini bisa menampilkan daftar server, mencari pemain, melihat detail server, daftar pemain online, serta mengelola daftar server langsung dari Discord (khusus admin). Tersedia juga panel **Lobby** berbasis tombol agar semua fitur bisa diakses tanpa mengetik command.

<!-- FOTO: Taruh screenshot tampilan utama / banner bot di sini -->

---

## Daftar Isi

- [Fitur](#fitur)
- [Struktur Proyek](#struktur-proyek)
- [Persyaratan](#persyaratan)
- [Instalasi](#instalasi)
- [Konfigurasi (.env)](#konfigurasi-env)
- [Menjalankan Bot](#menjalankan-bot)
- [Daftar Command](#daftar-command)
- [Fitur Lobby](#fitur-lobby)
- [Validasi Role Admin](#validasi-role-admin)
- [Penyimpanan Data](#penyimpanan-data)

---

## Fitur

- **Cek data real-time** langsung dari CFX API (bukan scraping).
- **Cache 5 menit** per server untuk mengurangi request ke API.
- **Daftar server** lengkap dengan status online/offline, jumlah pemain, dan keyword.
- **Cari pemain** berdasarkan nama di server tertentu.
- **Detail server** dan **daftar pemain online**.
- **Tambah/Hapus server** langsung dari Discord (khusus admin) tanpa mengubah kode.
- **Panel Lobby** berbasis tombol untuk semua fitur di atas.
- **Validasi role admin** berlapis untuk fitur pengelolaan server.
- **Penyimpanan permanen** daftar server ke file `servers.json`.

<!-- FOTO: Taruh screenshot contoh hasil command /servers di sini -->

---

## Struktur Proyek

```
main.py               Entry point: inisialisasi bot, load modul, sync command
config.py             Konfigurasi: token, role admin, API, daftar modul
server_manager.py     Data server, cache, request API, validasi role admin
servers.json          Penyimpanan daftar server (dibuat otomatis)
requirements.txt      Daftar dependency
cogs/
  search_cog.py       Command /search
  servers_cog.py      Command /servers, /serverinfo, /online
  admin_cog.py        Command /addserver, /removeserver
  lobby_cog.py        Command /lobby (panel tombol) + semua komponen UI
```

<!-- FOTO: Taruh screenshot struktur folder di VS Code di sini -->

---

## Persyaratan

- Python 3.10 atau lebih baru.
- Sebuah aplikasi/bot Discord beserta tokennya.
- Intent **Message Content** diaktifkan di Discord Developer Portal.

---

## Instalasi

1. Pasang dependency:

   ```powershell
   pip install -r requirements.txt
   ```

2. Buat file `.env` (lihat bagian Konfigurasi di bawah).

<!-- FOTO: Taruh screenshot proses instalasi / terminal di sini -->

---

## Konfigurasi (.env)

Buat file bernama `.env` di folder utama, lalu isi:

```env
# Token bot Discord (wajib)
DISCORD_TOKEN=masukkan_token_bot_disini

# Role admin - pilih salah satu (atau keduanya)
# Opsi 1: pakai ID role (paling akurat)
ADMIN_ROLE_ID=123456789012345678

# Opsi 2: pakai nama role (default "Admin")
ADMIN_ROLE_NAME=Admin
```

Cara mengambil ID role: aktifkan Developer Mode di Discord, klik kanan role, pilih "Copy Role ID".

<!-- FOTO: Taruh screenshot cara copy Role ID di Discord di sini -->

---

## Menjalankan Bot

```powershell
python main.py
```

Jika berhasil, terminal akan menampilkan log seperti:

```
Bot Discord FiveM (Direct API)
[LOAD] cogs.search_cog
[LOAD] cogs.servers_cog
[LOAD] cogs.admin_cog
[LOAD] cogs.lobby_cog
[SYNC] 6 commands
[READY] Bot: NamaBot#0001
```

<!-- FOTO: Taruh screenshot terminal saat bot berhasil online di sini -->

---

## Daftar Command

| Command | Akses | Keterangan |
|---------|-------|------------|
| `/servers` | Semua | Menampilkan daftar semua server beserta status dan keyword. |
| `/search <server> <nama>` | Semua | Mencari pemain berdasarkan nama di server tertentu. |
| `/serverinfo <server>` | Semua | Menampilkan detail satu server (banner, icon, jumlah online). |
| `/online <server>` | Semua | Menampilkan daftar pemain yang sedang online. |
| `/addserver <nama> <code>` | Admin | Menambah server baru ke daftar. |
| `/removeserver <nama>` | Admin | Menghapus server dari daftar. |
| `/lobby` | Semua | Menampilkan panel lobby berbasis tombol. |

Keterangan parameter:

- `server` / `nama` (pada command server): **keyword** server, contoh `indopride`.
- `code`: kode CFX server, contoh `bak4pl`.

<!-- FOTO: Taruh screenshot hasil command /search di sini -->

---

## Fitur Lobby

Ketik `/lobby` untuk memunculkan panel dengan tombol berikut:

| Tombol | Fungsi |
|--------|--------|
| Daftar Server | Menampilkan semua server + status + keyword. |
| Cari Player | Membuka form (server + nama), lalu menampilkan hasil. |
| Info Server | Memilih server dari dropdown, lalu menampilkan detailnya. |
| Player Online | Memilih server dari dropdown, lalu menampilkan pemain online. |
| Admin Panel | Khusus admin: tambah / hapus server. |

Catatan:

- Semua balasan tombol bersifat **ephemeral** (hanya terlihat oleh yang menekan), sehingga panel tetap rapi.
- Panel lobby bersifat **persistent**, jadi tombol tetap berfungsi meski bot di-restart.

<!-- FOTO: Taruh screenshot panel /lobby di sini -->
<!-- FOTO: Taruh screenshot Admin Panel (tombol Tambah/Hapus Server) di sini -->

---

## Validasi Role Admin

Fitur pengelolaan server (`/addserver`, `/removeserver`, dan tombol Admin Panel) hanya bisa dipakai oleh user yang lolos pengecekan `is_admin`, yaitu salah satu dari:

- Memiliki permission **Administrator** di server Discord, atau
- Memiliki role dengan ID sesuai `ADMIN_ROLE_ID`, atau
- Memiliki role dengan nama sesuai `ADMIN_ROLE_NAME`.

Jika tidak memenuhi syarat, bot menampilkan pesan "Akses Ditolak" secara ephemeral. Pengecekan dilakukan berlapis (saat klik tombol dan saat submit form) untuk mencegah bypass.

<!-- FOTO: Taruh screenshot pesan "Akses Ditolak" di sini -->

---

## Penyimpanan Data

- Daftar server disimpan di file `servers.json` dan dibuat otomatis saat pertama kali bot dijalankan (diisi dari `DEFAULT_SERVERS` di `config.py`).
- Setiap penambahan/penghapusan server (lewat command maupun lobby) langsung disimpan ke file, sehingga data tidak hilang saat bot restart.
- Format file:

  ```json
  {
      "indopride": "bak4pl"
  }
  ```

<!-- FOTO: Taruh screenshot isi file servers.json di sini -->

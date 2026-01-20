# Accessible KBBI

**Accessible KBBI** adalah add-on untuk pembaca layar NVDA yang memungkinkan pengguna untuk mencari arti kata dalam Kamus Besar Bahasa Indonesia (KBBI) secara langsung dan mudah diakses.

Add-on ini mengambil data dari [KBBI Daring](https://kbbi.kemendikdasmen.go.id/) (melalui API pihak ketiga) dan menampilkannya dalam antarmuka yang ramah aksesibilitas.

## Fitur Utama

- **Pencarian Kata**: Cari definisi kata lengkap dengan ejaan, pelafalan, dan label kelas kata (misal: *n* untuk nomina, *v* untuk verba).
- **Kata Hari Ini**: Tampilkan kata pilihan hari ini untuk menambah wawasan kosakata.
- **Kata Acak**: Tampilkan kata acak dari kamus untuk eksplorasi.
- **Pencarian Teks Terpilih**: Cari teks yang sedang diblok/dipilih di mana saja (browser, dokumen Word, dll) langsung ke KBBI tanpa mengetik ulang.
- **Riwayat Pencarian**: Menyimpan 50 pencarian terakhir Anda untuk akses cepat.
- **Kata Ditandai (Favorit)**: Simpan kata-kata penting agar mudah ditemukan kembali.
- **Salin Hasil**: Salin definisi lengkap ke papan klip (clipboard).

## Instalasi

1. Unduh file add-on `.nvda-addon` [terbaru](https://github.com/muhammadGagah/nvda-accessibleKBBI/releases/latest/).
2. Buka file add-on Accessible KBBI atau tekan Enter.
3. Ikuti petunjuk instalasi NVDA (konfirmasi instalasi dan restart NVDA).

## Penggunaan

### Tombol Pintas (Shortcut)

Secara default, add-on ini menggunakan tombol pintas berikut:

- **NVDA + Alt + K**: Membuka dialog utama Accessible KBBI.
- **NVDA + Shift + Alt + K**: Mencari teks yang sedang dipilih (diblok) secara langsung. Jika tidak ada teks yang dipilih, akan muncul  peringatan.

*Catatan: Anda dapat mengubah tombol pintas ini melalui menu **Preferences -> Input gestures** di NVDA.*

### Antarmuka Dialog

Setelah membuka dialog (`NVDA + Alt + K`), Anda akan menemukan elemen berikut:

1.  **Kotak Pencarian**: Ketik kata yang ingin dicari di sini, lalu tekan Enter atau klik tombol **Cari**.
2.  **Tombol Kata Hari Ini**: Menampilkan kata hari ini.
3.  **Tombol Kata Acak**: Menampilkan kata acak.
4.  **Tombol Riwayat**: Membuka daftar kata yang pernah dicari sebelumnya.
5.  **Tombol Ditandai**: Membuka daftar kata yang telah Anda simpan/favoritkan.
6.  **Area Hasil**: Menampilkan definisi lengkap. Anda dapat menggunakan panah untuk membaca baris per baris.
    -   Informasi mencakup: Kata dasar, kata turunan, gabungan kata, peribahasa, dan contoh penggunaan.
7.  **Tombol Tandai/Hapus Tanda**: Menambah atau menghapus kata yang sedang ditampilkan ke daftar favorit.
8.  **Tombol Salin**: Menyalin seluruh teks hasil pencarian ke clipboard.

## Persyaratan Sistem

- NVDA (NonVisual Desktop Access) versi terbaru.
- Koneksi Internet (diperlukan untuk mengambil data KBBI).

## Kredit

Dikembangkan oleh Muhammad.
Menggunakan API KBBI tidak resmi [Unofficial KBBI API](https://github.com/raf555/kbbi-api).

## Lisensi

Add-on ini didistribusikan di bawah lisensi GNU General Public License v2 (GPLv2).

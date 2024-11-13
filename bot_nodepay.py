import cloudscraper
from bs4 import BeautifulSoup
import random
import time
import socks
import socket

# Link referral untuk pendaftaran di Nodepay
referral_url = "https://app.nodepay.ai/register?ref=UNdo7u6fdS6icE3"

# File proxy dan akun hasil pendaftaran
proxy_file = "proxies.txt"
account_file = "created_accounts.txt"

# Fungsi untuk memuat proxy dari file .txt
def load_proxies(filename=proxy_file):
    with open(filename, "r") as file:
        proxies = [line.strip() for line in file if line.strip()]
    return proxies

# Fungsi untuk menghasilkan data akun secara acak
def generate_account_data():
    username = "user" + str(random.randint(10000, 99999))  # Buat username unik
    email = f"{username}@example.com"  # Buat email unik (gunakan email valid atau API temp mail jika perlu)
    password = "StrongPassword123"  # Buat password yang kuat
    return {
        "email": email,
        "username": username,
        "password": password,
        "confirm_password": password
    }

# Fungsi untuk menyimpan akun yang berhasil dibuat ke file
def save_account(account_data, filename=account_file):
    with open(filename, "a") as file:
        file.write(f"Username: {account_data['username']}, Email: {account_data['email']}\n")
    print(f"Akun {account_data['username']} berhasil disimpan ke {filename}")

# Fungsi untuk mengatur proxy SOCKS jika diperlukan
def set_socks_proxy(proxy):
    proxy_parts = proxy.split(":")
    ip = proxy_parts[0]
    port = int(proxy_parts[1])

    # Tentukan jenis proxy SOCKS5 atau SOCKS4
    socks.set_default_proxy(socks.SOCKS5, ip, port)
    socket.socket = socks.socksocket

# Fungsi untuk membuat akun
def create_account(proxy=None):
    # Gunakan cloudscraper untuk bypass Cloudflare
    scraper = cloudscraper.create_scraper()  # membuat scraper yang akan menghindari Cloudflare

    # Jika menggunakan proxy dengan autentikasi atau SOCKS
    if proxy:
        if "@" in proxy:  # Jika proxy membutuhkan autentikasi
            # Format proxy: username:password@ip:port
            auth_proxy = proxy.split("@")
            user_pass = auth_proxy[0]
            ip_port = auth_proxy[1]
            username, password = user_pass.split(":")
            ip, port = ip_port.split(":")

            # Set proxy dengan autentikasi
            scraper.proxies = {
                "http": f"http://{username}:{password}@{ip}:{port}",
                "https": f"http://{username}:{password}@{ip}:{port}"
            }
        else:
            # Set SOCKS5 proxy
            set_socks_proxy(proxy)

    # Ambil halaman registrasi untuk token CSRF jika diperlukan
    try:
        response = scraper.get(referral_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Cari token CSRF (jika ada)
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        csrf_token = csrf_token['value'] if csrf_token else None

        # Data registrasi akun
        account_data = generate_account_data()
        if csrf_token:
            account_data['csrf_token'] = csrf_token

        # URL pendaftaran Nodepay
        register_url = "https://app.nodepay.ai/register"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
        }

        # Kirim permintaan POST untuk mendaftar
        reg_response = scraper.post(register_url, data=account_data, headers=headers)
        if reg_response.ok:
            print(f"Akun berhasil dibuat dengan proxy {proxy}")
            # Simpan akun yang berhasil dibuat
            save_account(account_data)
        else:
            print(f"Gagal membuat akun dengan proxy {proxy}, status: {reg_response.status_code}")
    except requests.RequestException as e:
        print(f"Error saat membuat akun dengan proxy {proxy}: {e}")

# Fungsi utama untuk menjalankan pembuatan akun menggunakan daftar proxy
def main():
    # Muat daftar proxy dari file
    proxies = load_proxies()

    # Periksa apakah ada proxy
    if not proxies:
        print("Tidak ada proxy yang ditemukan di file proxies.txt")
        return

    # Buat akun dengan setiap proxy di daftar
    for proxy in proxies:
        print(f"Menggunakan proxy: {proxy}")
        create_account(proxy=proxy)

        # Tambahkan delay agar tidak terdeteksi sebagai bot
        time.sleep(random.randint(5, 10))  # Delay antara 5 hingga 10 detik

if __name__ == "__main__":
    main()

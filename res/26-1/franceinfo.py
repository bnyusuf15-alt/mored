import os
import re
import requests

playlist_url = "https://hdfauth.ftven.fr/esi/TA?url=https://simulcast-p.ftven.fr/simulcast/France_Info/hls_monde_frinfo/France_Info.m3u8"
output_file = "FR/franceinfo.m3u8"

# Ana m3u8 dosyasını indir
response = requests.get(playlist_url)
response.raise_for_status()

# .m3u8'den sonraki query parametrelerini temizle
cleaned_lines = []
for line in response.text.splitlines():
    if ".m3u8" in line:
        line = line.split("?")[0]
    cleaned_lines.append(line)
stream_url = "\n".join(cleaned_lines)

# stream_url içindeki dosya adını silerek base_url oluştur (örn: .../hls_monde_frinfo/)
base_url = stream_url.rsplit("/", 1)[0] + "/"

# Referans verilen alt m3u8 / içerik dosyasını indir
stream_response = requests.get(stream_url)
stream_response.raise_for_status()

# İçeriği satır satır işleyerek mutlak URL'lere dönüştür
processed_lines = []
for line in stream_response.text.splitlines():
  line = line.strip()
  if not line:
    continue

  if line.startswith("#"):
    # AUDIO, SUBTITLES vb. için URI= veya URL= içeren kısımları yakala
    if "URI=" in line or "URL=" in line:

      def fix_url(match):
        prefix = match.group(1)  # Örn: URI=" veya URL=
        val = match.group(2)  # İçindeki adres
        quote = match.group(3)  # Kapanış tırnağı (varsa)

        # Eğer http:// veya https:// ile başlamıyorsa base_url ekle
        if not val.startswith(("http://", "https://")):
          val = base_url + val

        return f"{prefix}{val}{quote}"

      # Tırnaklı veya tırnaksız URI/URL yapılarını esnek bir şekilde yakalar
      line = re.sub(r'((?:URI|URL)=["\']?)([^"\']*)(["\']?)', fix_url, line)

    processed_lines.append(line)
  else:
    # # ile başlamayan satırlar (ts, m4s veya alt m3u8 segmentleri)
    if not line.startswith(("http://", "https://")):
      line = base_url + line
    processed_lines.append(line)

os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
  f.write("\n".join(processed_lines))

print(f"Saved to {output_file}")

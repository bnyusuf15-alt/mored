import os
import re
import requests

playlist_url = "https://hdfauth.ftven.fr/esi/TA?url=https://simulcast-p.ftven.fr/simulcast/France_Info/hls_monde_frinfo/France_Info.m3u8"
output_file = "res/26-1/franceinfo.m3u8"

# Tarayıcı gibi görünmek için User-Agent tanımlıyoruz
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
}

# Ana m3u8 dosyasını indir
response = requests.get(playlist_url, headers=headers)
response.raise_for_status()

# .m3u8'den sonraki query parametrelerini temizle
cleaned_lines = []
for line in response.text.splitlines():
    if ".m3u8" in line:
        line = line.split("?")[0]
    cleaned_lines.append(line)
stream_url = "\n".join(cleaned_lines)

# stream_url içindeki dosya adını silerek base_url oluştur
base_url = stream_url.rsplit("/", 1)[0] + "/"

# Referans verilen alt m3u8 / içerik dosyasını indir (aynı header ile)
stream_response = requests.get(stream_url, headers=headers)
stream_response.raise_for_status()

# İçeriği satır satır işleyerek mutlak URL'lere dönüştür
processed_lines = []
for line in stream_response.text.splitlines():
  line = line.strip()
  if not line:
    continue

  if line.startswith("#"):
    if "URI=" in line or "URL=" in line:
      def fix_url(match):
        prefix = match.group(1)
        val = match.group(2)
        quote = match.group(3)

        if not val.startswith(("http://", "https://")):
          val = base_url + val

        return f"{prefix}{val}{quote}"

      line = re.sub(r'((?:URI|URL)=["\']?)([^"\']*)(["\']?)', fix_url, line)

    processed_lines.append(line)
  else:
    if not line.startswith(("http://", "https://")):
      line = base_url + line
    processed_lines.append(line)

os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
  f.write("\n".join(processed_lines))

print(f"Saved to {output_file}")

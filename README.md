# Demo Job Queue dengan Celery

Contoh ini memindahkan simulasi broker-worker pada tugas socket ke Celery. Producer mengirim `app_id`, tipe pekerjaan (`SHORT`/`LONG`), dan pesan. RabbitMQ menjadi broker; Celery worker mengambil dan menjalankan task secara asynchronous.

## Persiapan

Kebutuhan: Python 3.10+ dan Docker Compose.

```bash
cd ~/Downloads/celery-kbj
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
docker compose up -d
```

RabbitMQ Management UI tersedia di http://localhost:15672 (akun demo: `guest` / `guest`). Jalankan worker di terminal pertama:

```bash
celery -A celery_app:app worker --loglevel=INFO --queues=default,fanout.audit,fanout.analytics,topic.short,topic.long,wildcard.one,wildcard.many
```

Jalankan producer di terminal kedua:

```bash
python producer.py --mode all --count 4
```

Mode terpisah tersedia: `fanout`, `topic`, dan `wildcard`. Output producer menyertakan task ID; hasil pemrosesan terlihat di log worker. `SHORT` memproses echo sederhana, sedangkan `LONG` mensimulasikan pekerjaan lebih lama.

Untuk monitoring opsional, jalankan di terminal lain:

```bash
celery -A celery_app:app flower --port=5555
```

Flower tersedia di http://localhost:5555. Hentikan worker dan Flower dengan `Ctrl+C`, lalu hentikan broker dengan `docker compose down`.

## Perbedaan skema pesan

| Skema | Cara kerja | Hasil demo |
| --- | --- | --- |
| Fan-Out | Exchange menyalin setiap pesan ke semua queue yang terikat; routing key diabaikan. | Satu pesan diproses satu kali pada `fanout.audit` dan satu kali pada `fanout.analytics`. Duplikasi ini memang perilaku fan-out. |
| Topic | Exchange mencocokkan routing key bertitik dengan binding queue. | `job.short.created` masuk ke queue yang binding-nya cocok, seperti `topic.short`. |
| Wildcard | Bukan tipe exchange terpisah: wildcard adalah pola binding pada topic exchange. `*` mencocokkan tepat satu segmen, `#` mencocokkan nol atau lebih segmen. | `job.*.created` cocok dengan `job.short.created`, tetapi tidak dengan `job.created`; `job.#` cocok dengan keduanya serta `job.short.completed`. |

Demo memakai exchange fanout `kbj.fanout` dan topic `kbj.topic`. Queue `topic.short` dan `topic.long` menunjukkan routing berdasar jenis pekerjaan; `wildcard.one` dan `wildcard.many` memperlihatkan efek `*` serta `#` pada pesan yang sama. Bila sebuah routing key cocok dengan beberapa binding, pesan akan disalin ke setiap queue yang cocok.

## Struktur kode

- `celery_app.py`: broker, exchange, queue, dan binding.
- `tasks.py`: implementasi task `SHORT`/`LONG`.
- `producer.py`: input generator dan pengiriman task untuk tiga pola routing.
- `docker-compose.yml`: broker RabbitMQ lokal dengan management UI.

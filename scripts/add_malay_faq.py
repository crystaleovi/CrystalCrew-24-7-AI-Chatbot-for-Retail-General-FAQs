import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('prod-chatbot-faq')

# Malay FAQ translations
malay_faq = [
    {
        'category': 'general',
        'question': 'Apakah waktu operasi kedai anda?',
        'answer': 'Kedai kami buka Isnin-Sabtu 9AM-9PM, Ahad 10AM-6PM.'
    },
    {
        'category': 'general', 
        'question': 'Di mana lokasi kedai anda?',
        'answer': 'Kami mempunyai beberapa lokasi. Sila lawati pencari kedai di laman web kami untuk lokasi terdekat.'
    },
    {
        'category': 'shipping',
        'question': 'Berapa lama masa penghantaran?',
        'answer': 'Penghantaran standard mengambil masa 3-5 hari bekerja. Penghantaran ekspres mengambil masa 1-2 hari bekerja.'
    },
    {
        'category': 'shipping',
        'question': 'Adakah anda menawarkan penghantaran percuma?',
        'answer': 'Ya! Kami menawarkan penghantaran standard percuma untuk pesanan melebihi RM200.'
    },
    {
        'category': 'returns',
        'question': 'Apakah polisi pemulangan anda?',
        'answer': 'Kami menerima pemulangan dalam tempoh 30 hari dari pembelian dengan resit asal dan tag masih melekat.'
    },
    {
        'category': 'returns',
        'question': 'Bagaimana cara memulangkan item?',
        'answer': 'Anda boleh memulangkan item di kedai atau menghantar balik menggunakan label pemulangan prabayar kami.'
    },
    {
        'category': 'payment',
        'question': 'Kaedah pembayaran apa yang anda terima?',
        'answer': 'Kami menerima semua kad kredit utama, PayPal, Apple Pay, dan Google Pay.'
    },
    {
        'category': 'products',
        'question': 'Adakah anda mempunyai panduan saiz?',
        'answer': 'Ya, anda boleh mendapatkan panduan saiz di setiap halaman produk atau di bahagian saiz kami.'
    }
]

def add_malay_faq():
    """Add Malay FAQ translations"""
    try:
        with table.batch_writer() as batch:
            for item in malay_faq:
                batch.put_item(Item=item)
        
        print(f"Successfully added {len(malay_faq)} Malay FAQ items")
        
    except Exception as e:
        print(f"Error adding Malay FAQ data: {e}")

if __name__ == "__main__":
    add_malay_faq()

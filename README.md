# 📦 Uygulamanın Özellikleri:

## Kullanıcı girişi
Uygulama, sabit bir kullanıcı adı ve şifre (admin / 1234) ile oturum açma desteği sunar. Bu yapı ilerleyen sürümlerde harici bir dosyadan veya veritabanından kontrol edilecek şekilde geliştirilebilir.

## Stok giriş alanı
Kullanıcılar; ürün adı, miktar, birim fiyat ve kategori bilgilerini girerek yeni stok kayıtları oluşturabilir. Giriş alanları sade ve kullanıcı dostu olacak şekilde tasarlanmıştır.

## Stokların tablo görünümü
Girilen tüm ürünler, tablo şeklinde listelenerek görsel olarak kolay bir şekilde izlenebilir. Tablo dinamik olarak güncellenir ve sıralama/yenileme desteklidir.

## Gelişmiş filtreleme
Kullanıcılar; ürün adı, kategori ve tarih aralığı gibi kriterlere göre filtreleme yaparak ilgili ürünleri hızlıca görüntüleyebilir. Filtreleme işlemi gerçek zamanlı olarak çalışır.

## Toplam stok değeri hesaplama
Stokta bulunan tüm ürünlerin miktar ve fiyat bilgilerine göre toplam stok değeri anlık olarak hesaplanır ve kullanıcıya gösterilir.

## Kategori bazlı ve tarih bazlı grafik raporlama
Matplotlib kütüphanesiyle entegre çalışan sistem sayesinde, kullanıcılar stoklarını kategori bazında pasta grafikleriyle, tarihsel gelişimi ise çizgi grafiklerle takip edebilir.

## CSV’ye kaydetme özelliği
Uygulama, mevcut stok listesini tek tıkla CSV formatında dışa aktarma imkanı sunar. Bu sayede veriler yedeklenebilir ya da başka platformlarda analiz edilebilir.

## Şık ve sade bir UI tasarımı
Uygulamada kullanılan widget’lar özel stylesheet tanımlamalarıyla sade, modern ve kullanıcı odaklı bir arayüz sunar. Renk paleti, okunabilirlik ve sadelik esas alınarak belirlenmiştir.

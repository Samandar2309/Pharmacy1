import { Link } from 'react-router-dom';
import { Search, Package, Shield, Truck, Clock } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="animate-fade-in">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary-500 to-primary-600 text-white">
        <div className="container mx-auto px-4 py-20">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-5xl font-bold mb-6">
                Dorilarni onlayn buyurtma qiling
              </h1>
              <p className="text-xl mb-8 text-primary-100">
                Uydan chiqmasdan kerakli dorilaringizni toping va eshigingizgacha yetkazib oling
              </p>
              <div className="flex flex-wrap gap-4">
                <Link to="/products" className="btn bg-white text-primary-600 hover:bg-gray-100">
                  Mahsulotlarni ko'rish
                </Link>
                <Link to="/register" className="btn border-2 border-white text-white hover:bg-white hover:text-primary-600">
                  Ro'yxatdan o'tish
                </Link>
              </div>
            </div>
            <div className="hidden md:block">
              <img
                src="/hero-illustration.svg"
                alt="Online Pharmacy"
                className="w-full"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Bizning afzalliklarimiz</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="card text-center">
              <div className="inline-flex p-4 bg-primary-100 rounded-full mb-4">
                <Search className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold mb-2">Oson qidirish</h3>
              <p className="text-gray-600">
                Dorilarni nomi yoki kategoriyasi bo'yicha tez toping
              </p>
            </div>

            <div className="card text-center">
              <div className="inline-flex p-4 bg-primary-100 rounded-full mb-4">
                <Shield className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold mb-2">Xavfsizlik</h3>
              <p className="text-gray-600">
                Barcha dorilar sertifikatlangan va nazorat qilingan
              </p>
            </div>

            <div className="card text-center">
              <div className="inline-flex p-4 bg-primary-100 rounded-full mb-4">
                <Truck className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold mb-2">Tez yetkazish</h3>
              <p className="text-gray-600">
                Buyurtmangizni 1-2 soat ichida yetkazib beramiz
              </p>
            </div>

            <div className="card text-center">
              <div className="inline-flex p-4 bg-primary-100 rounded-full mb-4">
                <Clock className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-bold mb-2">24/7 Xizmat</h3>
              <p className="text-gray-600">
                Istalgan vaqtda buyurtma berishingiz mumkin
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4 text-center">
          <Package className="w-16 h-16 mx-auto mb-6 text-primary-600" />
          <h2 className="text-3xl font-bold mb-4">Buyurtma berishga tayyor misiz?</h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Minglab dorilardan kerakligini tanlang va uyingizgacha yetkazib oling
          </p>
          <Link to="/products" className="btn btn-primary text-lg px-8">
            Boshlash
          </Link>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">5000+</div>
              <div className="text-gray-600">Mahsulotlar</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">10k+</div>
              <div className="text-gray-600">Mijozlar</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">50k+</div>
              <div className="text-gray-600">Buyurtmalar</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">4.9</div>
              <div className="text-gray-600">Reyting</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

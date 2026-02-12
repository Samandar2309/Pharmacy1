import { Link } from 'react-router-dom';
import { Phone, Mail, MapPin, Facebook, Instagram, Send } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* About */}
          <div>
            <h3 className="text-white font-bold text-lg mb-4">Dorixona</h3>
            <p className="text-sm mb-4">
              Onlayn dori do'koni. Dorilarni uydan chiqmasdan buyurtma qiling.
            </p>
            <div className="flex space-x-3">
              <a href="#" className="hover:text-primary-400 transition">
                <Facebook className="w-5 h-5" />
              </a>
              <a href="#" className="hover:text-primary-400 transition">
                <Instagram className="w-5 h-5" />
              </a>
              <a href="#" className="hover:text-primary-400 transition">
                <Send className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-white font-bold text-lg mb-4">Tezkor havolalar</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/products" className="hover:text-primary-400 transition">
                  Mahsulotlar
                </Link>
              </li>
              <li>
                <Link to="/orders" className="hover:text-primary-400 transition">
                  Buyurtmalar
                </Link>
              </li>
              <li>
                <Link to="/prescriptions" className="hover:text-primary-400 transition">
                  Retseptlar
                </Link>
              </li>
              <li>
                <Link to="/profile" className="hover:text-primary-400 transition">
                  Profil
                </Link>
              </li>
            </ul>
          </div>

          {/* Info */}
          <div>
            <h3 className="text-white font-bold text-lg mb-4">Ma'lumot</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#" className="hover:text-primary-400 transition">
                  Biz haqimizda
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-400 transition">
                  Yetkazib berish
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-400 transition">
                  To'lov usullari
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-primary-400 transition">
                  Maxfiylik siyosati
                </a>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-white font-bold text-lg mb-4">Aloqa</h3>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start space-x-2">
                <Phone className="w-5 h-5 mt-0.5 flex-shrink-0" />
                <div>
                  <p>+998 90 123 45 67</p>
                  <p>+998 90 765 43 21</p>
                </div>
              </li>
              <li className="flex items-start space-x-2">
                <Mail className="w-5 h-5 mt-0.5 flex-shrink-0" />
                <p>info@dorixona.uz</p>
              </li>
              <li className="flex items-start space-x-2">
                <MapPin className="w-5 h-5 mt-0.5 flex-shrink-0" />
                <p>Toshkent shahar, Chilonzor tumani</p>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm">
          <p>&copy; 2026 Dorixona. Barcha huquqlar himoyalangan.</p>
        </div>
      </div>
    </footer>
  );
}

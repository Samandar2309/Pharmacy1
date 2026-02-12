import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Star, Heart, ShoppingCart, ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';
import { productsAPI, cartAPI } from '../services/api';
import { useCartStore } from '../store';

export default function ProductDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [alternatives, setAlternatives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [addingToCart, setAddingToCart] = useState(false);
  const { setCart } = useCartStore();

  useEffect(() => {
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    try {
      const response = await productsAPI.getById(id);
      setProduct(response.data);

      // Fetch alternatives
      const altResponse = await productsAPI.getAlternatives(id);
      setAlternatives(altResponse.data);
    } catch (error) {
      toast.error('Mahsulot topilmadi');
      navigate('/products');
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async () => {
    setAddingToCart(true);
    try {
      const response = await cartAPI.add({
        product_id: parseInt(id),
        quantity: quantity,
      });
      
      // Update cart store
      if (response.data && response.data.items) {
        setCart(response.data.items);
      }
      
      toast.success(`${quantity} ta mahsulot savatga qo'shildi`);
      setQuantity(1);
    } catch (error) {
      toast.error('Savatchaga qo\'shishda xato');
    } finally {
      setAddingToCart(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-600 border-t-transparent"></div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="card text-center">
          <p className="text-gray-500">Mahsulot topilmadi</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <button
        onClick={() => navigate('/products')}
        className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-8"
      >
        <ArrowLeft size={20} />
        Orqaga
      </button>

      <div className="grid md:grid-cols-2 gap-8 mb-12">
        {/* Image */}
        <div className="card">
          <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
            {product.image ? (
              <img
                src={product.image}
                alt={product.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                No Image
              </div>
            )}
          </div>
        </div>

        {/* Details */}
        <div>
          <h1 className="text-3xl font-bold mb-2">{product.name}</h1>
          
          <div className="flex items-center gap-4 mb-6">
            <div className="flex items-center">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  size={20}
                  className="text-yellow-400 fill-yellow-400"
                />
              ))}
            </div>
            <span className="text-gray-600">(150 sharh)</span>
          </div>

          <div className="text-4xl font-bold text-primary-600 mb-6">
            {product.price.toLocaleString()} so'm
          </div>

          <div className="bg-gray-50 p-6 rounded-lg mb-6 space-y-3">
            <div>
              <p className="text-sm text-gray-600">Ishlab chiqaruvchi</p>
              <p className="font-semibold">{product.manufacturer}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">SKU</p>
              <p className="font-semibold">{product.sku}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Holat</p>
              <p className="font-semibold">
                {product.stock > 0 ? `✅ Mavjud (${product.stock})` : '❌ Tugagan'}
              </p>
            </div>
            {product.is_prescription_required && (
              <div className="bg-yellow-50 p-3 rounded border border-yellow-200">
                <p className="text-sm text-yellow-800">
                  ⚠️ Bu mahsulot retsept talab qiladi
                </p>
              </div>
            )}
          </div>

          {/* Description */}
          <div className="mb-6">
            <h2 className="font-bold text-lg mb-2">Tavsifi</h2>
            <p className="text-gray-700">{product.description}</p>
          </div>

          {/* Usage */}
          <div className="mb-6">
            <h2 className="font-bold text-lg mb-2">Qanday ishlatiladi</h2>
            <p className="text-gray-700">{product.usage}</p>
          </div>

          {/* Cart Section */}
          <div className="card sticky bottom-0">
            <div className="flex gap-2 mb-4">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                disabled={product.stock === 0}
                className="btn btn-secondary"
              >
                -
              </button>
              <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                min="1"
                max={product.stock}
                className="input flex-1 text-center"
              />
              <button
                onClick={() => setQuantity(quantity + 1)}
                disabled={product.stock === 0 || quantity >= product.stock}
                className="btn btn-secondary"
              >
                +
              </button>
            </div>

            <button
              onClick={addToCart}
              disabled={product.stock === 0 || addingToCart}
              className="w-full btn btn-primary mb-2"
            >
              <ShoppingCart size={20} className="inline mr-2" />
              {addingToCart ? 'Qo\'shilmoqda...' : 'Savatga qo\'shish'}
            </button>

            <button className="w-full btn btn-secondary">
              <Heart size={20} className="inline mr-2" />
              Yoqtirilganlar
            </button>
          </div>
        </div>
      </div>

      {/* Alternatives */}
      {alternatives.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold mb-6">Muqobil dorilar</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {alternatives.map((alt) => (
              <div key={alt.id} className="card cursor-pointer hover:shadow-lg transition">
                <div
                  onClick={() => navigate(`/products/${alt.id}`)}
                  className="aspect-square bg-gray-100 rounded-lg mb-3 overflow-hidden"
                >
                  {alt.image ? (
                    <img
                      src={alt.image}
                      alt={alt.name}
                      className="w-full h-full object-cover hover:scale-105 transition"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      No Image
                    </div>
                  )}
                </div>

                <h3 className="font-semibold text-sm mb-2">{alt.name}</h3>
                <p className="text-primary-600 font-bold mb-2">
                  {alt.price.toLocaleString()} so'm
                </p>

                <button
                  onClick={() => {
                    navigate(`/products/${alt.id}`);
                  }}
                  className="w-full btn btn-secondary text-sm"
                >
                  Ko'rish
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

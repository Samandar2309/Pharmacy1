import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Trash2, Plus, Minus, ShoppingCart } from 'lucide-react';
import toast from 'react-hot-toast';
import { cartAPI, ordersAPI } from '../services/api';
import { useCartStore } from '../store';

export default function CartPage() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const navigate = useNavigate();
  const { clearCart } = useCartStore();

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const response = await cartAPI.get();
      setCart(response.data);
    } catch (error) {
      toast.error('Savatchani yuklashda xato');
    } finally {
      setLoading(false);
    }
  };

  const removeItem = async (itemId) => {
    setUpdating(true);
    try {
      await cartAPI.remove(itemId);
      await fetchCart();
      toast.success("O'chirildi");
    } catch (error) {
      toast.error('Xatolik yuz berdi');
    } finally {
      setUpdating(false);
    }
  };

  const updateQuantity = async (itemId, quantity) => {
    if (quantity <= 0) return;
    
    setUpdating(true);
    try {
      const response = await cartAPI.update(itemId, { quantity });
      setCart(response.data);
    } catch (error) {
      toast.error('Xatolik yuz berdi');
    } finally {
      setUpdating(false);
    }
  };

  const handleCheckout = () => {
    if (!cart?.items?.length) {
      toast.error('Savatcha bo\'sh');
      return;
    }
    navigate('/checkout', { state: { cart } });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-600 border-t-transparent"></div>
      </div>
    );
  }

  const items = cart?.items || [];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Savatcha</h1>

      {items.length === 0 ? (
        <div className="card text-center py-12">
          <ShoppingCart className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p className="text-gray-500 text-lg mb-4">Savatcha bo'sh</p>
          <button
            onClick={() => navigate('/products')}
            className="btn btn-primary"
          >
            Mahsulot qidirish
          </button>
        </div>
      ) : (
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            {items.map((item) => (
              <div key={item.id} className="card flex gap-4">
                <div className="w-24 h-24 bg-gray-100 rounded-lg overflow-hidden">
                  {item.product.image ? (
                    <img
                      src={item.product.image}
                      alt={item.product.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      No Image
                    </div>
                  )}
                </div>

                <div className="flex-1">
                  <h3 className="font-semibold text-lg">{item.product.name}</h3>
                  <p className="text-gray-600 text-sm mb-2">
                    {item.product.manufacturer}
                  </p>
                  <p className="text-primary-600 font-bold text-lg">
                    {item.product.price.toLocaleString()} so'm
                  </p>
                </div>

                <div className="flex flex-col items-end justify-between">
                  <button
                    onClick={() => removeItem(item.id)}
                    disabled={updating}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 size={20} />
                  </button>

                  <div className="flex items-center gap-2 border border-gray-300 rounded-lg p-2">
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      disabled={updating || item.quantity <= 1}
                      className="text-gray-600 hover:text-gray-900 disabled:opacity-50"
                    >
                      <Minus size={16} />
                    </button>
                    <span className="w-8 text-center font-semibold">
                      {item.quantity}
                    </span>
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      disabled={updating}
                      className="text-gray-600 hover:text-gray-900"
                    >
                      <Plus size={16} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Summary */}
          <div className="card h-fit">
            <h2 className="text-xl font-bold mb-4">Umumiy narx</h2>
            
            <div className="space-y-3 mb-6 border-t border-b py-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Mahsulotlar:</span>
                <span className="font-semibold">
                  {items.reduce((sum, item) => sum + item.quantity, 0)} ta
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Jami:</span>
                <span className="text-2xl font-bold text-primary-600">
                  {items.reduce((sum, item) => sum + (item.product.price * item.quantity), 0).toLocaleString()} so'm
                </span>
              </div>
            </div>

            <button
              onClick={handleCheckout}
              disabled={updating}
              className="w-full btn btn-primary mb-2"
            >
              Checkout
            </button>
            <button
              onClick={() => navigate('/products')}
              className="w-full btn btn-secondary"
            >
              Davom etish
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

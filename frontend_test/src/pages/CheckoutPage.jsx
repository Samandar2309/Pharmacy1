import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { MapPin, Phone, DollarSign } from 'lucide-react';
import toast from 'react-hot-toast';
import { ordersAPI, paymentsAPI } from '../services/api';
import { useAuthStore, useCartStore } from '../store';

export default function CheckoutPage() {
  const [loading, setLoading] = useState(false);
  const [orderCreated, setOrderCreated] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuthStore();
  const { clearCart } = useCartStore();
  const cart = location.state?.cart;

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      delivery_address: user?.address || '',
      phone: user?.phone_number || '',
    }
  });

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      // Create order
      const orderResponse = await ordersAPI.checkout({
        delivery_address: data.delivery_address,
      });

      const order = orderResponse.data.data;
      setOrderCreated(order);
      clearCart();
      toast.success('Buyurtma yaratildi!');

      // Agar payment kerak bo'lsa
      if (order.status === 'awaiting_payment') {
        setTimeout(() => navigate(`/orders/${order.id}`), 2000);
      } else {
        setTimeout(() => navigate('/orders'), 2000);
      }

    } catch (error) {
      console.error('Checkout error:', error.response?.data);
      toast.error('Buyurtma yaratishda xato');
    } finally {
      setLoading(false);
    }
  };

  if (!cart?.items?.length) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="card text-center">
          <p className="text-gray-500 mb-4">Savatcha bo'sh</p>
          <button
            onClick={() => navigate('/cart')}
            className="btn btn-primary"
          >
            Savatga qaytish
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Buyurtmani yakunlash</h1>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Form */}
        <div className="lg:col-span-2">
          <div className="card">
            <h2 className="text-xl font-bold mb-6">Yetkazib berish manzili</h2>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Manzil
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-3 text-gray-400" size={20} />
                  <textarea
                    placeholder="Tashkent, Chilonzor, 1-1-1"
                    className="input pl-10"
                    rows="3"
                    {...register('delivery_address', {
                      required: 'Manzil majburiy'
                    })}
                  />
                </div>
                {errors.delivery_address && (
                  <p className="text-red-500 text-sm mt-1">
                    {errors.delivery_address.message}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Telefon raqam
                </label>
                <div className="relative">
                  <Phone className="absolute left-3 top-3 text-gray-400" size={20} />
                  <input
                    type="tel"
                    readOnly
                    value={user?.phone_number || ''}
                    className="input pl-10 bg-gray-100"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full btn btn-primary"
              >
                {loading ? 'Kuting...' : 'Buyurtmani yaratish'}
              </button>
            </form>
          </div>
        </div>

        {/* Summary */}
        <div className="card h-fit">
          <h2 className="text-xl font-bold mb-6">Buyurtma mazmuni</h2>

          <div className="space-y-3 mb-6 pb-6 border-b">
            {cart.items.map((item) => (
              <div key={item.id} className="flex justify-between">
                <div>
                  <p className="font-medium">{item.product.name}</p>
                  <p className="text-sm text-gray-500">
                    {item.quantity} x {item.product.price.toLocaleString()}
                  </p>
                </div>
                <p className="font-semibold">
                  {(item.quantity * item.product.price).toLocaleString()} so'm
                </p>
              </div>
            ))}
          </div>

          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Subtotal:</span>
              <span>
                {cart.items.reduce((sum, item) => sum + (item.quantity * item.product.price), 0).toLocaleString()} so'm
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Yetkazish:</span>
              <span>Bepul</span>
            </div>
            <div className="border-t pt-3 flex justify-between">
              <span className="font-bold">Jami:</span>
              <span className="text-2xl font-bold text-primary-600">
                {cart.items.reduce((sum, item) => sum + (item.quantity * item.product.price), 0).toLocaleString()} so'm
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

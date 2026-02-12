import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Package, MapPin, DollarSign } from 'lucide-react';
import toast from 'react-hot-toast';
import { ordersAPI, paymentsAPI, prescriptionsAPI } from '../services/api';

const statusBadges = {
  draft: 'bg-gray-100 text-gray-800',
  awaiting_prescription: 'bg-yellow-100 text-yellow-800',
  awaiting_payment: 'bg-orange-100 text-orange-800',
  paid: 'bg-blue-100 text-blue-800',
  preparing: 'bg-purple-100 text-purple-800',
  ready_for_delivery: 'bg-indigo-100 text-indigo-800',
  on_the_way: 'bg-cyan-100 text-cyan-800',
  delivered: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
};

const statusLabels = {
  draft: 'Yaratildi',
  awaiting_prescription: 'Retsept kutilmoqda',
  awaiting_payment: 'To\'lov kutilmoqda',
  paid: 'To\'landi',
  preparing: 'Tayyorlanmoqda',
  ready_for_delivery: 'Yetkazishga tayyor',
  on_the_way: 'Yo\'lda',
  delivered: 'Yetkazildi',
  cancelled: 'Bekor qilindi',
};

export default function OrderDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [prescriptionFile, setPrescriptionFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchOrder();
  }, [id]);

  const fetchOrder = async () => {
    try {
      const response = await ordersAPI.getById(id);
      setOrder(response.data);
    } catch (error) {
      toast.error('Buyurtmani yuklashda xato');
      navigate('/orders');
    } finally {
      setLoading(false);
    }
  };

  const handlePrescriptionUpload = async () => {
    if (!prescriptionFile) {
      toast.error('Rasm tanlang');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('order_id', id);
      formData.append('images', prescriptionFile);

      await prescriptionsAPI.create(formData);
      toast.success('Retsept yuklandi');
      setPrescriptionFile(null);
      await fetchOrder();
    } catch (error) {
      console.error('Upload error:', error.response?.data);
      toast.error('Retsept yuklashda xato');
    } finally {
      setUploading(false);
    }
  };

  const handlePayment = async (provider) => {
    try {
      const response = await paymentsAPI.create({
        order_id: id,
        provider: provider,
      });

      toast.success('To\'lov tayyorlandi');
      await fetchOrder();
    } catch (error) {
      toast.error('To\'lov yaratishda xato');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-600 border-t-transparent"></div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="card text-center">
          <p className="text-gray-500">Buyurtma topilmadi</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button
          onClick={() => navigate('/orders')}
          className="btn btn-secondary"
        >
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1 className="text-3xl font-bold">Buyurtma #{order.id}</h1>
          <span className={`badge ${statusBadges[order.status]}`}>
            {statusLabels[order.status]}
          </span>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main */}
        <div className="lg:col-span-2 space-y-6">
          {/* Items */}
          <div className="card">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Package size={24} /> Mahsulotlar
            </h2>
            <div className="space-y-3">
              {order.items?.map((item) => (
                <div key={item.id} className="flex justify-between p-3 bg-gray-50 rounded">
                  <div>
                    <p className="font-medium">{item.product?.name}</p>
                    <p className="text-sm text-gray-600">
                      {item.quantity} x {item.price?.toLocaleString()} so'm
                    </p>
                  </div>
                  <p className="font-bold">
                    {(item.quantity * item.price)?.toLocaleString()} so'm
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Delivery Address */}
          <div className="card">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <MapPin size={24} /> Yetkazish manzili
            </h2>
            <p className="text-gray-700">{order.delivery_address}</p>
          </div>

          {/* Prescription Section */}
          {order.status === 'awaiting_prescription' && (
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Retsept yuklash</h2>
              <p className="text-gray-600 mb-4">
                Bu buyurtma uchun retsept talab qilinadi. Iltimos, retsept rasmini yuklang.
              </p>
              <div className="space-y-4">
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setPrescriptionFile(e.target.files[0])}
                  className="input"
                />
                <button
                  onClick={handlePrescriptionUpload}
                  disabled={!prescriptionFile || uploading}
                  className="w-full btn btn-primary"
                >
                  {uploading ? 'Yuklanmoqda...' : 'Retsept yuklash'}
                </button>
              </div>
            </div>
          )}

          {/* Payment Section */}
          {order.status === 'awaiting_payment' && (
            <div className="card">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <DollarSign size={24} /> To'lov
              </h2>
              <p className="text-gray-600 mb-6">
                Buyurtmani yakunlash uchun to'lov qiling
              </p>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => handlePayment('click')}
                  className="btn btn-primary"
                >
                  Click orqali
                </button>
                <button
                  onClick={() => handlePayment('payme')}
                  className="btn btn-primary"
                >
                  Payme orqali
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="card h-fit">
          <h2 className="text-xl font-bold mb-6">Buyurtma ma'lumoti</h2>

          <div className="space-y-4 text-sm">
            <div>
              <p className="text-gray-600">Buyurtma raqami</p>
              <p className="font-semibold">#{order.id}</p>
            </div>

            <div>
              <p className="text-gray-600">Holat</p>
              <p className="font-semibold">{statusLabels[order.status]}</p>
            </div>

            <div>
              <p className="text-gray-600">Yaratilgan vaqt</p>
              <p className="font-semibold">
                {order.created_at ? new Date(order.created_at).toLocaleString('uz-UZ') : 'N/A'}
              </p>
            </div>

            <hr />

            <div>
              <p className="text-gray-600">Subtotal</p>
              <p className="font-semibold">
                {order.total_price?.toLocaleString()} so'm
              </p>
            </div>

            <div>
              <p className="text-gray-600">Yetkazish</p>
              <p className="font-semibold">Bepul</p>
            </div>

            <div className="border-t pt-4">
              <p className="text-gray-600 mb-1">Jami</p>
              <p className="text-2xl font-bold text-primary-600">
                {order.total_price?.toLocaleString()} so'm
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

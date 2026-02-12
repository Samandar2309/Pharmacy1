import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Package, Eye, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { ordersAPI } from '../services/api';

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

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await ordersAPI.getAll();
      setOrders(response.data);
    } catch (error) {
      toast.error('Buyurtmalarni yuklashda xato');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-600 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Mening buyurtmalarim</h1>

      {orders.length === 0 ? (
        <div className="card text-center py-12">
          <Package className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p className="text-gray-500 text-lg mb-4">Hali buyurtma yo'q</p>
          <Link to="/products" className="btn btn-primary inline-block">
            Mahsulot qidirish
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {orders.map((order) => (
            <div key={order.id} className="card">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-4 mb-2">
                    <h3 className="font-bold text-lg">
                      Buyurtma #{order.id}
                    </h3>
                    <span className={`badge ${statusBadges[order.status]}`}>
                      {statusLabels[order.status]}
                    </span>
                  </div>

                  <p className="text-gray-600 text-sm mb-2">
                    {order.created_at ? new Date(order.created_at).toLocaleString('uz-UZ') : 'N/A'}
                  </p>

                  <p className="text-gray-600 mb-2">
                    📍 {order.delivery_address}
                  </p>

                  <div className="flex items-center gap-4">
                    <span className="font-bold text-primary-600">
                      {order.total_price.toLocaleString()} so'm
                    </span>
                    <span className="text-sm text-gray-500">
                      {order.items?.length || 0} mahsulot
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => setSelectedOrder(order)}
                  className="btn btn-secondary"
                >
                  <Eye size={20} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-screen overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6 flex justify-between items-center">
              <h2 className="text-2xl font-bold">
                Buyurtma #{selectedOrder.id}
              </h2>
              <button
                onClick={() => setSelectedOrder(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X size={24} />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Status */}
              <div>
                <h3 className="font-bold mb-2">Holat</h3>
                <span className={`badge ${statusBadges[selectedOrder.status]}`}>
                  {statusLabels[selectedOrder.status]}
                </span>
              </div>

              {/* Items */}
              <div>
                <h3 className="font-bold mb-4">Mahsulotlar</h3>
                <div className="space-y-2">
                  {selectedOrder.items?.map((item) => (
                    <div key={item.id} className="flex justify-between p-2 bg-gray-50 rounded">
                      <div>
                        <p className="font-medium">{item.product?.name || 'N/A'}</p>
                        <p className="text-sm text-gray-600">
                          {item.quantity} x {item.price?.toLocaleString() || 'N/A'} so'm
                        </p>
                      </div>
                      <p className="font-bold">
                        {(item.quantity * item.price)?.toLocaleString() || 'N/A'} so'm
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Totals */}
              <div className="border-t pt-4">
                <div className="flex justify-between mb-2">
                  <span>Subtotal:</span>
                  <span>{selectedOrder.total_price?.toLocaleString() || 'N/A'} so'm</span>
                </div>
                <div className="flex justify-between text-lg font-bold">
                  <span>Jami:</span>
                  <span className="text-primary-600">
                    {selectedOrder.total_price?.toLocaleString() || 'N/A'} so'm
                  </span>
                </div>
              </div>

              {/* Delivery Address */}
              <div>
                <h3 className="font-bold mb-2">Yetkazish manzili</h3>
                <p className="text-gray-600">{selectedOrder.delivery_address}</p>
              </div>

              {/* Close Button */}
              <button
                onClick={() => setSelectedOrder(null)}
                className="w-full btn btn-secondary"
              >
                Yopish
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

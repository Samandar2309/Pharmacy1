import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, Package, DollarSign } from 'lucide-react';
import toast from 'react-hot-toast';
import { dashboardAPI } from '../services/api';
import { useAuthStore } from '../store';

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuthStore();

  useEffect(() => {
    fetchDashboard();
  }, [user?.role]);

  const fetchDashboard = async () => {
    try {
      let response;

      if (user?.role === 'admin') {
        response = await dashboardAPI.admin();
      } else if (user?.role === 'operator') {
        response = await dashboardAPI.operator();
      } else if (user?.role === 'courier') {
        response = await dashboardAPI.courier();
      } else {
        response = await dashboardAPI.customer();
      }

      setDashboard(response.data.data);
    } catch (error) {
      console.error('Dashboard error:', error.response?.data);
      toast.error('Dashboard yuklashda xato');
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

  if (!dashboard) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="card text-center">
          <p className="text-gray-500">Dashboard ma'lumoti topilmadi</p>
        </div>
      </div>
    );
  }

  const renderAdminDashboard = () => {
    const stats = dashboard.global_stats || {};
    const orderStats = dashboard.order_stats || {};
    const revenueStats = dashboard.revenue_stats || {};

    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Jami foydalanuvchi</p>
                <p className="text-3xl font-bold text-primary-600">
                  {stats.total_users || 0}
                </p>
              </div>
              <Users className="w-12 h-12 text-primary-100" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Jami buyurtma</p>
                <p className="text-3xl font-bold text-primary-600">
                  {orderStats.total_orders || 0}
                </p>
              </div>
              <Package className="w-12 h-12 text-primary-100" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Jami tushum</p>
                <p className="text-3xl font-bold text-primary-600">
                  {(revenueStats.total_revenue || 0).toLocaleString()} so'm
                </p>
              </div>
              <DollarSign className="w-12 h-12 text-primary-100" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Bugun tushum</p>
                <p className="text-3xl font-bold text-primary-600">
                  {(revenueStats.today_revenue || 0).toLocaleString()} so'm
                </p>
              </div>
              <TrendingUp className="w-12 h-12 text-primary-100" />
            </div>
          </div>
        </div>

        {/* Details */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Order Stats */}
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Buyurtma statistikasi</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Bugun:</span>
                <span className="font-bold">{orderStats.today_orders || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Haftali:</span>
                <span className="font-bold">{orderStats.weekly_orders || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Oylik:</span>
                <span className="font-bold">{orderStats.monthly_orders || 0}</span>
              </div>
            </div>
          </div>

          {/* Revenue Stats */}
          <div className="card">
            <h2 className="text-xl font-bold mb-4">To'lov statistikasi</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Muvaffaqiyatli:</span>
                <span className="font-bold text-green-600">
                  {revenueStats.successful_payments || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Xatoli:</span>
                <span className="font-bold text-red-600">
                  {revenueStats.failed_payments || 0}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderCustomerDashboard = () => {
    const orderSummary = dashboard.order_summary || {};
    const prescriptionSummary = dashboard.prescription_summary || {};
    const purchaseStats = dashboard.purchase_stats || {};

    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Mening Dashboard</h1>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card text-center">
            <p className="text-gray-600 text-sm">Yangi</p>
            <p className="text-2xl font-bold text-primary-600">
              {orderSummary.new || 0}
            </p>
          </div>
          <div className="card text-center">
            <p className="text-gray-600 text-sm">Yo'lda</p>
            <p className="text-2xl font-bold text-primary-600">
              {orderSummary.on_the_way || 0}
            </p>
          </div>
          <div className="card text-center">
            <p className="text-gray-600 text-sm">Yetkazildi</p>
            <p className="text-2xl font-bold text-green-600">
              {orderSummary.delivered || 0}
            </p>
          </div>
          <div className="card text-center">
            <p className="text-gray-600 text-sm">Bekor</p>
            <p className="text-2xl font-bold text-red-600">
              {orderSummary.cancelled || 0}
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Retseptlar</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Tekshirilmoqda:</span>
                <span className="font-bold">
                  {prescriptionSummary.pending || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Tasdiqlandi:</span>
                <span className="font-bold text-green-600">
                  {prescriptionSummary.approved || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Rad etildi:</span>
                <span className="font-bold text-red-600">
                  {prescriptionSummary.rejected || 0}
                </span>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-bold mb-4">Xarid statistikasi</h2>
            <div>
              <p className="text-gray-600 text-sm">Jami sarflangan</p>
              <p className="text-3xl font-bold text-primary-600">
                {(purchaseStats.total_spent || 0).toLocaleString()} so'm
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {user?.role === 'admin'
        ? renderAdminDashboard()
        : renderCustomerDashboard()}
    </div>
  );
}

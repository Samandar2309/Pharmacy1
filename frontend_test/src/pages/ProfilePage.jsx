import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { User, Mail, MapPin, Phone, Save } from 'lucide-react';
import toast from 'react-hot-toast';
import { authAPI } from '../services/api';
import { useAuthStore } from '../store';

export default function ProfilePage() {
  const [loading, setLoading] = useState(false);
  const { user, updateUser } = useAuthStore();
  const { register, handleSubmit, formState: { errors }, reset } = useForm({
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      address: user?.address || '',
    }
  });

  useEffect(() => {
    if (user) {
      reset({
        first_name: user.first_name,
        last_name: user.last_name,
        address: user.address,
      });
    }
  }, [user, reset]);

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      const response = await authAPI.updateProfile(data);
      const updatedUser = response.data.data;
      updateUser(updatedUser);
      toast.success('Profil yangilandi');
    } catch (error) {
      console.error('Update error:', error.response?.data);
      toast.error('Profilni yangilashda xato');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="card text-center">
          <p className="text-gray-500">Kiring</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Mening profil</h1>

      <div className="max-w-2xl">
        <div className="card mb-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">
                {user.first_name} {user.last_name}
              </h2>
              <p className="text-gray-600">{user.phone_number}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="text-sm text-gray-600">Rol</p>
              <p className="font-semibold capitalize">{user.role}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <p className="font-semibold">
                {user.is_verified ? '✅ Tasdiqlangan' : '❌ Tasdiqlanmagan'}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold mb-6">Profilni tahrirlash</h2>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ism
                </label>
                <input
                  type="text"
                  className="input"
                  {...register('first_name', { required: 'Ism majburiy' })}
                />
                {errors.first_name && (
                  <p className="text-red-500 text-sm mt-1">
                    {errors.first_name.message}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Familiya
                </label>
                <input
                  type="text"
                  className="input"
                  {...register('last_name', { required: 'Familiya majburiy' })}
                />
                {errors.last_name && (
                  <p className="text-red-500 text-sm mt-1">
                    {errors.last_name.message}
                  </p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Manzil
              </label>
              <textarea
                className="input"
                rows="3"
                placeholder="Tashkent, Chilonzor, 1-1-1"
                {...register('address')}
              />
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Telefon raqam</p>
              <p className="font-semibold">{user.phone_number}</p>
              <p className="text-xs text-gray-500 mt-2">
                Telefon raqamni o'zgartirish uchun admin bilan bog'laning
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn btn-primary"
            >
              <Save size={20} className="inline mr-2" />
              {loading ? 'Saqlanmoqda...' : 'Saqlash'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

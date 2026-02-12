import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { LogIn, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';
import { authAPI } from '../services/api';
import { useAuthStore } from '../store';

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      const response = await authAPI.login({
        phone_number: data.phone,
        password: data.password,
      });

      const { access, refresh, user } = response.data.data;
      
      localStorage.setItem('authToken', access);
      localStorage.setItem('refreshToken', refresh);
      
      setAuth(user, access);
      
      toast.success('Xush kelibsiz!');
      navigate('/');
    } catch (error) {
      console.error('Login error:', error.response?.data);
      
      const errorMsg = error.response?.data?.data?.phone_number?.[0] ||
                       error.response?.data?.data?.detail ||
                       error.response?.data?.detail ||
                       'Kirish xatosi. Telefon va parolni tekshiring.';
      
      if (errorMsg.includes('tasdiq')) {
        toast.error('❌ Telefon raqam tasdiqlanmagan. Avval ro\'yxatdan o\'ting.');
      } else {
        toast.error(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      <div className="bg-white rounded-2xl shadow-2xl p-8">
        <div className="text-center mb-8">
          <div className="inline-flex p-4 bg-primary-100 rounded-full mb-4">
            <LogIn className="w-8 h-8 text-primary-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Kirish</h1>
          <p className="text-gray-600">Hisobingizga kiring</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Telefon raqam
            </label>
            <input
              type="tel"
              placeholder="+998901234567"
              className="input"
              {...register('phone', {
                required: 'Telefon raqam majburiy',
                pattern: {
                  value: /^\+998\d{9}$/,
                  message: 'Format: +998XXXXXXXXX',
                },
              })}
            />
            {errors.phone && (
              <p className="text-red-500 text-sm mt-1">{errors.phone.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Parol
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                className="input pr-10"
                {...register('password', {
                  required: 'Parol majburiy',
                  minLength: {
                    value: 6,
                    message: 'Parol kamida 6 ta belgidan iborat bo\'lishi kerak',
                  },
                })}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            {errors.password && (
              <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn btn-primary"
          >
            {loading ? 'Kuting...' : 'Kirish'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Hisobingiz yo'qmi?{' '}
            <Link to="/register" className="text-primary-600 hover:text-primary-700 font-medium">
              Ro'yxatdan o'ting
            </Link>
          </p>
        </div>

        {/* Test Info */}
        <div className="mt-6 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-xs text-blue-800 font-semibold mb-2">TEST CREDENTIALS:</p>
          <p className="text-xs text-blue-700">📱 +998901234567</p>
          <p className="text-xs text-blue-700">🔐 password123</p>
        </div>
      </div>
    </div>
  );
}


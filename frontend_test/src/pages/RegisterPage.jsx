import { useState } from 'react';
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { UserPlus, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';
import { authAPI } from '../services/api';

export default function RegisterPage() {
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [registrationData, setRegistrationData] = useState(null);
  const [showOtpStep, setShowOtpStep] = useState(false);
  const navigate = useNavigate();
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm();

  const password = watch('password');

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      // Step 1: Register user
      const registerResponse = await authAPI.register({
        phone_number: data.phone,
        password: data.password,
        first_name: data.firstName,
        last_name: data.lastName,
      });

      // Save registration data and move to OTP step
      setRegistrationData({
        phone_number: data.phone,
        password: data.password,
        first_name: data.firstName,
        last_name: data.lastName,
      });
      
      setShowOtpStep(true);
      toast.success('SMS kod yuborildi!');

    } catch (error) {
      console.error('Register error:', error.response?.data);
      
      // Get detailed error message
      let errorMsg = 'Ro\'yxatdan o\'tish xatosi';
      
      if (error.response?.data?.errors) {
        // Multiple field errors
        const errors = error.response.data.errors;
        errorMsg = Object.values(errors)
          .flat()
          .map(e => typeof e === 'string' ? e : e.message)
          .join(', ');
      } else if (error.response?.data?.error) {
        errorMsg = error.response.data.error;
      } else if (error.response?.data?.message) {
        errorMsg = error.response.data.message;
      } else if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail;
      }
      
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  if (showOtpStep) {
    return <OtpVerificationPage registrationData={registrationData} />;
  }

  return (
    <div className="w-full max-w-md">
      <div className="bg-white rounded-2xl shadow-2xl p-8">
        <div className="text-center mb-8">
          <div className="inline-flex p-4 bg-primary-100 rounded-full mb-4">
            <UserPlus className="w-8 h-8 text-primary-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Ro'yxatdan o'tish</h1>
          <p className="text-gray-600">Yangi hisob yarating</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* First Name & Last Name */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ism
              </label>
              <input
                type="text"
                placeholder="Ali"
                className="input"
                {...register('firstName', { required: 'Ism majburiy' })}
              />
              {errors.firstName && (
                <p className="text-red-500 text-sm mt-1">{errors.firstName.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Familiya
              </label>
              <input
                type="text"
                placeholder="Valiyev"
                className="input"
                {...register('lastName', { required: 'Familiya majburiy' })}
              />
              {errors.lastName && (
                <p className="text-red-500 text-sm mt-1">{errors.lastName.message}</p>
              )}
            </div>
          </div>

          {/* Phone */}
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

          {/* Password */}
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

          {/* Confirm Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Parolni tasdiqlash
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                className="input pr-10"
                {...register('confirmPassword', {
                  required: 'Parolni tasdiqlang',
                  validate: (value) => value === password || 'Parollar mos emas',
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
            {errors.confirmPassword && (
              <p className="text-red-500 text-sm mt-1">{errors.confirmPassword.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn btn-primary"
          >
            {loading ? 'Kuting...' : 'Ro\'yxatdan o\'tish'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Hisobingiz bormi?{' '}
            <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">
              Kirish
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

// ============================================
// OTP VERIFICATION COMPONENT
// ============================================

function OtpVerificationPage({ registrationData }) {
  const [otp, setOtp] = useState(['', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [resendTimer, setResendTimer] = useState(60);
  const [canResend, setCanResend] = useState(false);
  const navigate = useNavigate();

  // Auto-focus next input
  const handleOtpChange = (value, index) => {
    if (!/^\d*$/.test(value)) return;
    
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-focus next input
    if (value && index < 3) {
      document.getElementById(`otp-${index + 1}`)?.focus();
    }
  };

  // Handle backspace
  const handleKeyDown = (e, index) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      document.getElementById(`otp-${index - 1}`)?.focus();
    }
  };

  // Countdown timer
  React.useEffect(() => {
    if (resendTimer > 0) {
      const timer = setTimeout(() => setResendTimer(resendTimer - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      setCanResend(true);
    }
  }, [resendTimer]);

  const handleVerifyOtp = async () => {
    const code = otp.join('');
    
    if (code.length !== 4) {
      toast.error('Kodni to\'liq kiriting');
      return;
    }

    setLoading(true);
    try {
      // Verify OTP
      const verifyResponse = await authAPI.verifyOTP({
        phone_number: registrationData.phone_number,
        code: code,
      });

      if (verifyResponse.data.data?.access) {
        // Save token
        localStorage.setItem('authToken', verifyResponse.data.data.access);
        localStorage.setItem('refreshToken', verifyResponse.data.data.refresh);

        toast.success('Ro\'yxatdan o\'ttingiz!');
        
        // Redirect to home after 2 seconds
        setTimeout(() => {
          navigate('/');
          window.location.reload();
        }, 2000);
      }
    } catch (error) {
      console.error('OTP verify error:', error.response?.data);
      toast.error(
        error.response?.data?.data?.code?.[0] ||
        error.response?.data?.detail ||
        'Kod noto\'g\'ri yoki muddati o\'tgan'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    setCanResend(false);
    setResendTimer(60);
    setOtp(['', '', '', '']);

    try {
      // Resend OTP
      await authAPI.register({
        phone_number: registrationData.phone_number,
        password: registrationData.password,
        first_name: registrationData.first_name,
        last_name: registrationData.last_name,
      });

      toast.success('Kod qayta yuborildi');
      document.getElementById('otp-0')?.focus();
    } catch (error) {
      toast.error('Kod qayta yuborishda xato');
      setCanResend(true);
    }
  };

  return (
    <div className="w-full max-w-md">
      <div className="bg-white rounded-2xl shadow-2xl p-8">
        <div className="text-center mb-8">
          <div className="inline-flex p-4 bg-primary-100 rounded-full mb-4">
            <UserPlus className="w-8 h-8 text-primary-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Tasdiqlash</h1>
          <p className="text-gray-600">
            Telefon raqamingizga yuborilgan kodni kiriting
          </p>
          <p className="text-gray-500 text-sm mt-2">
            {registrationData.phone_number}
          </p>
        </div>

        <div className="mb-8">
          <label className="block text-sm font-medium text-gray-700 mb-4">
            4 xonali kod
          </label>

          <div className="flex gap-3 justify-center">
            {otp.map((digit, index) => (
              <input
                key={index}
                id={`otp-${index}`}
                type="text"
                maxLength="1"
                value={digit}
                onChange={(e) => handleOtpChange(e.target.value, index)}
                onKeyDown={(e) => handleKeyDown(e, index)}
                className="w-14 h-14 text-center text-2xl font-bold border-2 border-gray-300 rounded-lg focus:border-primary-600 focus:ring-2 focus:ring-primary-100 transition"
                inputMode="numeric"
              />
            ))}
          </div>
        </div>

        <button
          onClick={handleVerifyOtp}
          disabled={loading}
          className="w-full btn btn-primary mb-4"
        >
          {loading ? 'Tekshirilmoqda...' : 'Tasdiqlash'}
        </button>

        <div className="text-center">
          {canResend ? (
            <button
              onClick={handleResendOtp}
              className="text-primary-600 hover:text-primary-700 font-medium text-sm"
            >
              Kodini qayta yuborish
            </button>
          ) : (
            <p className="text-gray-600 text-sm">
              Kodini qayta yuborish uchun{' '}
              <span className="font-bold text-primary-600">{resendTimer}s</span> kuting
            </p>
          )}
        </div>
      </div>
    </div>
  );
}


import { useState, useEffect } from 'react';
import { FileText, Upload, CheckCircle, XCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { prescriptionsAPI } from '../services/api';

const statusBadges = {
  pending: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
};

const statusLabels = {
  pending: 'Tekshirilmoqda',
  approved: 'Tasdiqlandi',
  rejected: 'Rad etildi',
};

export default function PrescriptionsPage() {
  const [prescriptions, setPrescriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [prescriptionFiles, setPrescriptionFiles] = useState([]);
  const [orderId, setOrderId] = useState('');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchPrescriptions();
  }, []);

  const fetchPrescriptions = async () => {
    try {
      const response = await prescriptionsAPI.getAll();
      setPrescriptions(response.data);
    } catch (error) {
      toast.error('Retseptlarni yuklashda xato');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 5) {
      toast.error('Maksimum 5 ta rasm yuklasa bo\'ladi');
      return;
    }
    setPrescriptionFiles(files);
  };

  const handleUpload = async () => {
    if (!orderId || prescriptionFiles.length === 0) {
      toast.error('Buyurtma ID va rasmlarni tanlang');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('order_id', orderId);
      prescriptionFiles.forEach((file) => {
        formData.append('images', file);
      });

      await prescriptionsAPI.create(formData);
      toast.success('Retsept yuklandi');
      
      setOrderId('');
      setPrescriptionFiles([]);
      await fetchPrescriptions();
    } catch (error) {
      console.error('Upload error:', error.response?.data);
      toast.error('Retsept yuklashda xato');
    } finally {
      setUploading(false);
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
      <h1 className="text-3xl font-bold mb-8">Retseptlar</h1>

      {/* Upload Section */}
      <div className="card mb-8">
        <h2 className="text-xl font-bold mb-6">Yangi retsept yuklash</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Buyurtma raqami
            </label>
            <input
              type="number"
              value={orderId}
              onChange={(e) => setOrderId(e.target.value)}
              placeholder="1"
              className="input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Retsept rasmlari (1-5 ta)
            </label>
            <input
              type="file"
              multiple
              accept="image/*"
              onChange={handleFileChange}
              className="input"
            />
            {prescriptionFiles.length > 0 && (
              <p className="text-sm text-gray-600 mt-2">
                {prescriptionFiles.length} ta fayl tanlandi
              </p>
            )}
          </div>

          <button
            onClick={handleUpload}
            disabled={!orderId || prescriptionFiles.length === 0 || uploading}
            className="w-full btn btn-primary"
          >
            <Upload size={20} className="inline mr-2" />
            {uploading ? 'Yuklanmoqda...' : 'Yuklash'}
          </button>
        </div>
      </div>

      {/* Prescriptions List */}
      {prescriptions.length === 0 ? (
        <div className="card text-center py-12">
          <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p className="text-gray-500 text-lg">Hali retsept yo'q</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {prescriptions.map((prescription) => (
            <div key={prescription.id} className="card">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-4 mb-2">
                    <h3 className="font-bold text-lg">
                      Retsept #{prescription.id}
                    </h3>
                    <span className={`badge ${statusBadges[prescription.status]}`}>
                      {statusLabels[prescription.status]}
                    </span>
                  </div>

                  <p className="text-gray-600 text-sm mb-2">
                    Buyurtma: #{prescription.order_id}
                  </p>

                  <p className="text-gray-600 text-sm mb-2">
                    📅 {prescription.created_at ? new Date(prescription.created_at).toLocaleString('uz-UZ') : 'N/A'}
                  </p>

                  {prescription.rejection_reason && (
                    <div className="mt-2 p-3 bg-red-50 rounded-lg border border-red-200">
                      <p className="text-sm text-red-700">
                        <strong>Rad etish sababi:</strong> {prescription.rejection_reason}
                      </p>
                    </div>
                  )}

                  {prescription.images && prescription.images.length > 0 && (
                    <div className="mt-4">
                      <p className="text-sm font-semibold text-gray-700 mb-2">
                        Rasmlar ({prescription.images.length}):
                      </p>
                      <div className="grid grid-cols-4 gap-2">
                        {prescription.images.map((img, idx) => (
                          <a
                            key={idx}
                            href={img.image}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="aspect-square bg-gray-100 rounded-lg overflow-hidden hover:opacity-75"
                          >
                            <img
                              src={img.image}
                              alt={`Rasm ${idx + 1}`}
                              className="w-full h-full object-cover"
                            />
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div>
                  {prescription.status === 'approved' && (
                    <CheckCircle className="w-8 h-8 text-green-500" />
                  )}
                  {prescription.status === 'rejected' && (
                    <XCircle className="w-8 h-8 text-red-500" />
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

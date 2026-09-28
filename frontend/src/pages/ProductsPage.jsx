import React, { useState, useEffect, useMemo } from 'react';
import productAPI from '../api/productAPI';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import ProductList from '../components/product/ProductList';
import ProductForm from '../components/product/ProductForm';
import Modal from '../components/common/Modal';
import Loader from '../components/common/Loader';
import { Search, Plus } from 'lucide-react';

export const ProductsPage = () => {
  const { isAdmin } = useAuth();
  const { toastSuccess, toastError } = useNotification();

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchProducts = async () => {
    try {
      const res = await productAPI.getProducts();
      const list = res.products || res.data || (Array.isArray(res) ? res : []);
      setProducts(list);
    } catch (err) {
      toastError(err.message || 'Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleOpenAdd = () => {
    setEditingProduct(null);
    setModalOpen(true);
  };

  const handleOpenEdit = (prod) => {
    setEditingProduct(prod);
    setModalOpen(true);
  };

  const handleDelete = async (prod) => {
    if (!window.confirm(`Are you sure you want to delete ${prod.model_name}?`)) return;
    try {
      await productAPI.deleteProduct(prod.id);
      toastSuccess(`Product ${prod.model_name} removed.`);
      fetchProducts();
    } catch (err) {
      toastError(err.message || 'Failed to delete product');
    }
  };

  const handleSubmit = async (formData) => {
    setActionLoading(true);
    try {
      if (editingProduct) {
        await productAPI.updateProduct(editingProduct.id, formData);
        toastSuccess('Product successfully updated.');
      } else {
        await productAPI.createProduct(formData);
        toastSuccess('Product added to catalog.');
      }
      setModalOpen(false);
      fetchProducts();
    } catch (err) {
      toastError(err.message || 'Failed to save product');
    } finally {
      setActionLoading(false);
    }
  };

  const filteredProducts = useMemo(() => {
    if (!searchQuery) return products;
    const lowerQ = searchQuery.toLowerCase();
    return products.filter(p => 
      (p.brand && p.brand.toLowerCase().includes(lowerQ)) ||
      (p.model_name && p.model_name.toLowerCase().includes(lowerQ)) ||
      (p.category && p.category.toLowerCase().includes(lowerQ))
    );
  }, [products, searchQuery]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-pulse">
          <div className="space-y-2">
            <div className="h-8 w-48 bg-slate-200 dark:bg-slate-800 rounded-lg"></div>
            <div className="h-4 w-64 bg-slate-200 dark:bg-slate-800 rounded-lg"></div>
          </div>
          <div className="h-10 w-full sm:w-64 bg-slate-200 dark:bg-slate-800 rounded-xl"></div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6 mt-6">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-48 rounded-2xl bg-slate-200 dark:bg-slate-800 animate-pulse"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white">
            Product Catalog
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Browse registered warranty-eligible products
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search products..."
              className="pl-10 pr-4 py-2 w-full sm:w-64 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 dark:text-white shadow-sm"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          </div>
          {/* Remove the duplicate Add Product button from here */}
        </div>
      </div>

      <ProductList
        products={filteredProducts}
        isAdmin={isAdmin}
        onAddNew={handleOpenAdd}
        onEditProduct={handleOpenEdit}
        onDeleteProduct={handleDelete}
      />

      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingProduct ? 'Edit Product Model' : 'Register New Product Model'}
      >
        <ProductForm
          initialData={editingProduct || {}}
          onSubmit={handleSubmit}
          onCancel={() => setModalOpen(false)}
          loading={actionLoading}
        />
      </Modal>
    </div>
  );
};

export default ProductsPage;